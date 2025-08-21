import logging
import os
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from functools import partial
from scipy.signal import butter, filtfilt, resample, welch
from scipy.ndimage import uniform_filter1d
from sklearn.decomposition import PCA
from typing import Optional
from ..utils.helper import extract_channel_id, get_channel_columns

def _parse_time_any(s: str) -> datetime:
    s = str(s)
    fmts = ("%H:%M:%S.%f", "%H:%M:%S", "%M:%S.%f", "%M:%S", "%S.%f", "%S")
    for fmt in fmts:
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue
    # last resort: pandas mixed-format inference
    try:
        return pd.to_datetime(s, format="mixed").to_pydatetime()
    except Exception:
        raise ValueError(f"无法解析时间格式：{s!r}")
    
def od_resample(
    od_df: pd.DataFrame,
    sfreq: float,
    target_freq: float = 10,
    filter_cutoff: Optional[float] = None,
    filter_order: int = 4
) -> pd.DataFrame:
    """
    光密度数据重采样处理函数。

    - 若原始采样率 > 目标采样率：进行滤波 + 降采样。
    - 若原始采样率 == 目标采样率：仅滤波。
    - 若原始采样率 ∈ [5Hz, 10Hz)：仅滤波，不重采样。
    - 若原始采样率 < 5Hz：不建议处理，直接返回原始数据。
    """

    # 1. 确定抗混叠滤波截止
    if filter_cutoff is None:
        filter_cutoff = target_freq / 2

    # 2. 判断是否需要降采样
    if sfreq > target_freq:
        do_resample = True
    elif sfreq >= 5:
        do_resample = False
    else:
        print(f"❌ 原始采样率 {sfreq:.2f}Hz 太低，直接返回原始数据")
        return od_df.copy()

    # 3. 设计 Butterworth 低通
    nyquist = sfreq / 2
    if filter_cutoff >= nyquist:
        filter_cutoff = 0.8 * nyquist
        print(f"⚠️ filter_cutoff 超过 Nyquist，已调整为 {filter_cutoff:.2f}Hz")
    norm_cutoff = filter_cutoff / nyquist
    b, a = butter(filter_order, norm_cutoff, btype='low')

    # 4. 分离通道／非通道列
    channel_cols = [c for c in od_df.columns if re.match(r'^CH\d+\(', c)]
    non_channel_cols = [c for c in od_df.columns if c not in channel_cols]

    # 5. 先对通道数据做双向滤波
    filtered_data = filtfilt(b, a, od_df[channel_cols].values, axis=0)

    if not do_resample:
        # 只滤波
        od_df[channel_cols] = filtered_data
        print(f"仅完成滤波，采样率保持 {sfreq:.2f}Hz")
        return od_df

    # 6. 降采样：先在通道上
    n_samples = int(len(od_df) * target_freq / sfreq)
    resampled_ch = resample(filtered_data, n_samples, axis=0)
    df_ch = pd.DataFrame(resampled_ch, columns=channel_cols)

    # 7. 生成新的 Time 列
    # 7. 生成新的 Time 列
    res_info = {}
    if "Time" in non_channel_cols:
        # 取原始第一行的时间字符串
        t0_dt = _parse_time_any(od_df["Time"].iloc[0])
        dt = 1.0 / target_freq
        res_info["Time"] = [
            (t0_dt + timedelta(seconds=i * dt)).strftime("%H:%M:%S.%f")[:-3]
            for i in range(n_samples)
        ]

    # 8. 处理其它非通道列
    for col in non_channel_cols:
        if col == "Time":
            continue
        series = od_df[col]
        key = col.lower()

        if key.startswith("probe"):
            # —— Probe 列：插值后四舍五入为整数
            xi = np.linspace(0, 1, len(series))
            xo = np.linspace(0, 1, n_samples)
            vals = np.interp(xo, xi, series.astype(float))
            res_info[col] = np.round(vals).astype(int).tolist()

        elif key.startswith("mark"):
            # —— 打点列：贴近最近的新时间格点
            mark_new = [0] * n_samples
            if "Time" in od_df.columns and "Time" in res_info:
                new_times = pd.to_datetime(res_info["Time"], format="%H:%M:%S.%f")
                events = od_df.loc[series.notnull() & (series != 0), ["Time", col]]
                for _, ev in events.iterrows():
                    orig_t = _parse_time_any(ev["Time"])  # <-- robust parser here
                    j = int(np.argmin(np.abs(new_times - orig_t)))
                    mark_new[j] = ev[col]
            res_info[col] = mark_new

        elif pd.api.types.is_numeric_dtype(series):
            # —— 其它数值列：线性插值
            xi = np.linspace(0, 1, len(series))
            xo = np.linspace(0, 1, n_samples)
            res_info[col] = np.interp(xo, xi, series.astype(float)).tolist()

        else:
            # —— 其它文本列：全部填第一个值
            res_info[col] = [series.iloc[0]] * n_samples

    # 9. 拼回完整表格并保持原列顺序
    df_info = pd.DataFrame(res_info)
    full = pd.concat([df_info, df_ch], axis=1)[od_df.columns]

    print(f"滤波+降采样完成：{sfreq:.2f}Hz → {target_freq}Hz，共 {n_samples} 行")
    return full

def od_TDDR(signal, sample_rate):
    # This function is the reference implementation for the TDDR algorithm for
    #   motion correction of fNIRS data, as described in:
    #
    #   Fishburn F.A., Ludlum R.S., Vaidya C.J., & Medvedev A.V. (2019).
    #   Temporal Derivative Distribution Repair (TDDR): A motion correction
    #   method for fNIRS. NeuroImage, 184, 171-179.
    #   https://doi.org/10.1016/j.neuroimage.2018.09.025
    #
    # Usage:
    #   signals_corrected = TDDR( signals , sample_rate );
    #
    # Inputs:
    #   signals: A [sample x channel] matrix of uncorrected optical density data
    #   sample_rate: A scalar reflecting the rate of acquisition in Hz
    #
    # Outputs:
    #   signals_corrected: A [sample x channel] matrix of corrected optical density data
    signal = np.array(signal)
    if len(signal.shape) != 1:
        for ch in range(signal.shape[1]):
            signal[:, ch] = od_TDDR(signal[:, ch], sample_rate)
        return signal

    # Preprocess: Separate high and low frequencies
    filter_cutoff = .5
    filter_order = 3
    Fc = filter_cutoff * 2/sample_rate
    signal_mean = np.mean(signal)
    signal -= signal_mean
    if Fc < 1:
        fb, fa = butter(filter_order, Fc)
        signal_low = filtfilt(fb, fa, signal, padlen=0)
    else:
        signal_low = signal

    signal_high = signal - signal_low

    # Initialize
    tune = 4.685
    D = np.sqrt(np.finfo(signal.dtype).eps)
    mu = np.inf
    iter = 0

    # Step 1. Compute temporal derivative of the signal
    deriv = np.diff(signal_low)

    # Step 2. Initialize observation weights
    w = np.ones(deriv.shape)

    # Step 3. Iterative estimation of robust weights
    while iter < 100:

        iter = iter + 1
        mu0 = mu

        # Step 3a. Estimate weighted mean
        mu = np.sum(w * deriv) / np.sum(w)

        # Step 3b. Calculate absolute residuals of estimate
        dev = np.abs(deriv - mu)

        # Step 3c. Robust estimate of standard deviation of the residuals
        sigma = 1.4826 * np.median(dev)

        # Step 3d. Scale deviations by standard deviation and tuning parameter
        r = dev / (sigma * tune)

        # Step 3e. Calculate new weights according to Tukey's biweight function
        w = ((1 - r**2) * (r < 1)) ** 2

        # Step 3f. Terminate if new estimate is within machine-precision of old estimate
        if abs(mu - mu0) < D * max(abs(mu), abs(mu0)):
            break

    # Step 4. Apply robust weights to centered derivative
    new_deriv = w * (deriv - mu)

    # Step 5. Integrate corrected derivative
    signal_low_corrected = np.cumsum(np.insert(new_deriv, 0, 0.0))

    # Postprocess: Center the corrected signal
    signal_low_corrected = signal_low_corrected - np.mean(signal_low_corrected)

    # Postprocess: Merge back with uncorrected high frequency component
    signal_corrected = signal_low_corrected + signal_high + signal_mean

    return signal_corrected

# ===== 运动伪迹检测 =====
def od_detect_motion_artifacts(od_df,
                               method_list=("derivative","std","amplitude"),
                               derivative_thresh=0.5,
                               std_window=10, std_thresh=0.2,
                               amplitude_thresh=1.0,
                               interpolate=True, visualize=True,
                               output_dir=None):

    # 先找出所有通道列（CHx(λ)）
    chs = [c for c in od_df.columns if re.match(r'^CH\d+\(', c)]
    data = od_df[chs]  # 仅通道数据

    masks = []

    # 差分法                                
    # 通过计算相邻采样点的一阶差分，当信号突变幅度超过阈值时，认为发生了快速运动伪迹。
    if "derivative" in method_list:
    # HOMER2 软件包中的 hmrMotionArtifact 就采用了类似的“slope‐based”检测，推荐的阈值约 0.1 OD 单位／样本（在 10 Hz 采样下相当于 0.01 OD/ms）
        diff_mask = data.diff().abs() > derivative_thresh
        masks.append(diff_mask)
        bad_count = (diff_mask.mean(axis=0) > 0.1).sum()
        # logger.info(f"差分法: 剔除通道数≈{bad_count}")

    # 滑动标准差法（Sliding‐window STD）        
    # 先计算窗口内（如 10 个点≈1 s）信号的平滑一阶差分的标准差，再与整个通道的全局标准差做比例比较。当局部波动远大于背景抖动时，判定为运动伪迹。
    if "std" in method_list:
        dif = np.abs(np.diff(data.values, axis=0, prepend=data.values[0:1]))
        smooth = uniform_filter1d(dif, size=std_window, axis=0)
        std_mask = smooth > std_thresh * np.std(data.values, axis=0)
        std_mask = pd.DataFrame(std_mask, columns=chs)
        masks.append(std_mask)
        bad_count = (std_mask.mean(axis=0) > 0.05).sum()
        # logger.info(f"滑动std法: 剔除通道数≈{bad_count}")

    # 振幅阈值法（Amplitude threshold）     
    # 直接标记相邻两点振幅差超过某一绝对值（如 0.3 OD），快速筛出大动作导致的剧烈振幅跳变
    if "amplitude" in method_list:
        amp_mask = data.diff().abs() > amplitude_thresh
        masks.append(amp_mask)
        bad_count = (amp_mask.mean(axis=0) > 0.05).sum()
        # logger.info(f"振幅法: 剔除通道数≈{bad_count}")
    # 合并
    combined_mask = np.logical_or.reduce([m.values for m in masks])

    # 3. 只把通道列置为 NaN
    clean = od_df.copy()
    clean_ch = clean[chs].copy()
    clean_ch.values[combined_mask] = np.nan
    clean[chs] = clean_ch

    # 4. 插值
    if interpolate:
        clean[chs] = clean[chs].interpolate(limit_direction="both")
    return clean, combined_mask

# 带通滤波 (0.01–0.2Hz) 
def od_filter(OD_df: pd.DataFrame, sfreq: float,
              low_cut: float = 0.01, high_cut: float = 0.2) -> pd.DataFrame:
    """
    对 fNIRS 数据中的 oxy 和 deOxy 信号进行带通滤波。

    Parameters
    ----------
    HB_df : pd.DataFrame
        原始 fNIRS 数据，包括 CHx(oxy)/CHx(deOxy) 通道。
    sfreq : float
        数据采样率 (Hz)。
    low_cut : float
        高通滤波器截止频率 (Hz)，默认 0.01。
    high_cut : float
        低通滤波器截止频率 (Hz)，默认 0.2。

    Returns
    -------
    pd.DataFrame
        滤波后的 fNIRS 数据（结构与原数据相同）。
    """
    filtered_df = OD_df.copy()

    # 创建带通滤波器（使用 mne）
    bandpass_filter = partial(filtered_df,
                              sfreq=sfreq,
                              l_freq=low_cut,
                              h_freq=high_cut,
                              method='iir',
                              verbose=False)

    # 提取通道列（CHx(oxy)/CHx(deOxy)）
    signal_cols = get_channel_columns(OD_df)

    for col in signal_cols:
        signal = OD_df[col].values.astype(float)
        filtered_signal = bandpass_filter(signal)
        filtered_df[col] = filtered_signal

    return filtered_df

