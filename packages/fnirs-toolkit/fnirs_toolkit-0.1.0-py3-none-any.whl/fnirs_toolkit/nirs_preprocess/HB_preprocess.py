# 作者：@Jamie
# 日期：2025-06-25
# 描述：血氧数据预处理步骤，包括
# 1. 去漂移
# 2. TDDR 去运动伪迹
# 3. 信号滤波


import pandas as pd
import numpy as np
import re
from scipy.signal import butter, filtfilt
from functools import partial
from functions.helper import extract_channel_id, get_sfreq
from mne.filter import filter_data


def HB_cut(HB_df, time_range):
    """
    # TODO: 根据时间戳截取血氧数据
    """
    if time_range is None:
        raise ValueError("time_range 不能为 None")
    
    sfreq = get_sfreq(HB_df)
    pass


def HB_detrend(HB_df: pd.DataFrame, order: int = 1) -> pd.DataFrame:
    """
    对 fNIRS 数据中的 CHx(oxy) 和 CHx(deOxy) 通道进行多项式去趋势处理。
    
    Parameters
    ----------
    df : pd.DataFrame
        包含 'CHx(oxy)' 和 'CHx(deOxy)' 通道的 DataFrame。
    order : int
        拟合去趋势的多项式阶数（默认线性，1 阶）

    Returns
    -------
    pd.DataFrame
        去趋势后的新 DataFrame（保留原始结构）
    """
    df_detrended = HB_df.copy()
    tp = len(HB_df)

    # 选择 oxy 和 deOxy 通道
    oxy_cols = [col for col in HB_df.columns if re.match(r'CH\d+\(oxy\)', col)]
    deoxy_cols = [col for col in HB_df.columns if re.match(r'CH\d+\(deOxy\)', col)]

    for col in oxy_cols + deoxy_cols:
        y = HB_df[col].values
        x = np.arange(1, tp + 1)

        # 多项式拟合
        p = np.polyfit(x, y, order)
        trend = np.polyval(p, x)

        # 去趋势
        df_detrended[col] = y - trend

    return df_detrended


def HB_TDDR(HB_df: pd.DataFrame, sfreq: float) -> pd.DataFrame:
    """
    对 fNIRS 数据中的 HbO2 和 HbR 通道执行 TDDR 运动伪影校正。

    Parameters
    ----------
    HB_df : pd.DataFrame
        原始 fNIRS 数据，包含 'CHx(oxy)' 和 'CHx(deOxy)' 通道。
    sfreq : float
        数据采样率（Hz）

    Returns
    -------
    pd.DataFrame
        校正后的 fNIRS 数据（DataFrame 结构保持不变）
    """
    df_tddr = HB_df.copy()
    channel_cols = [col for col in HB_df.columns if re.match(r'CH\d+\((oxy|deOxy)\)', col)]

    for col in channel_cols:
        signal = HB_df[col].values.astype(float)
        signal_mean = np.mean(signal)
        signal -= signal_mean

        # 分离低频与高频
        Fc = 0.5 * 2 / sfreq
        if Fc < 1:
            b, a = butter(3, Fc)
            signal_low = filtfilt(b, a, signal, padlen=0)
        else:
            signal_low = signal
        signal_high = signal - signal_low

        # 初始化导数与权重
        deriv = np.diff(signal_low)
        w = np.ones_like(deriv)
        mu = np.inf
        tune = 4.685
        eps = np.sqrt(np.finfo(signal.dtype).eps)

        # 鲁棒权重迭代
        for _ in range(50):
            mu0 = mu
            mu = np.sum(w * deriv) / np.sum(w)
            dev = np.abs(deriv - mu)
            sigma = 1.4826 * np.median(dev)
            r = dev / (sigma * tune)
            w = ((1 - r**2) * (r < 1)) ** 2
            if abs(mu - mu0) < eps * max(abs(mu), abs(mu0)):
                break

        # 修正导数并积分恢复信号
        new_deriv = w * (deriv - mu)
        signal_low_corr = np.cumsum(np.insert(new_deriv, 0, 0.0))
        signal_low_corr -= np.mean(signal_low_corr)

        # 合并高频 + 修正低频 + 均值
        signal_corr = signal_low_corr + signal_high + signal_mean
        df_tddr[col] = signal_corr

    return df_tddr


def HB_filter(HB_df: pd.DataFrame, sfreq: float,
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
    filtered_df = HB_df.copy()

    # 创建带通滤波器（使用 mne）
    bandpass_filter = partial(filter_data,
                              sfreq=sfreq,
                              l_freq=low_cut,
                              h_freq=high_cut,
                              method='iir',
                              verbose=False)

    # 提取通道列（CHx(oxy)/CHx(deOxy)）
    signal_cols = [col for col in HB_df.columns if re.match(r'CH\d+\((oxy|deOxy)\)', col)]

    for col in signal_cols:
        signal = HB_df[col].values.astype(float)
        filtered_signal = bandpass_filter(signal)
        filtered_df[col] = filtered_signal

    return filtered_df
