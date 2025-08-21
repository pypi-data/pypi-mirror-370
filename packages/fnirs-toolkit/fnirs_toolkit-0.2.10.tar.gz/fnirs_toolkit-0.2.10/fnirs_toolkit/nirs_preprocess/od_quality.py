# 作者：@Boluo, @Jamie
# 日期：2025-06-20
# 描述：计算 fNIRS 光密度信号中各个通道的相关通道质量系数
# 包括：
# 1. 变异系数（CV）
# 2. 头皮耦合指数（SCI）

import numpy as np
import pandas as pd
import re
import os
from scipy.signal import butter, filtfilt, correlate, periodogram, hamming
from ..utils.helper import extract_channel_id, get_channel_columns, group_channels_by_id


def od_CV(od_df, cv_threshold=0.2, use_auto_threshold=False, auto_threshold_quantile=90, verbose=True):
    """
    按通道（CH编号）计算每对波长通道的CV值，支持固定阈值或自动阈值（percentile）。
    """
    cv_table = []
    bad_channels = {}

    # 使用 helper 函数获取通道列
    ch_cols = get_channel_columns(od_df)

    # 使用 helper 函数按通道分组
    grouped = group_channels_by_id(od_df)
    
    cv_dict = {}
    all_cv_values = []

    # 计算每个通道波长的 CV 值
    for ch_id, col_pair in grouped.items():
        for col in col_pair:
            signal = pd.to_numeric(od_df[col], errors='coerce').dropna().values
            mean_signal = np.mean(signal) if len(signal) > 0 else 0

            if len(signal) == 0 or np.isclose(mean_signal, 0):
                cv = np.nan
            else:
                std_signal = np.std(signal)
                cv = std_signal / abs(mean_signal)

            cv_dict[col] = cv
            if not np.isnan(cv):
                all_cv_values.append(cv)

    # 自动或固定阈值
    if use_auto_threshold:
        cv_threshold_value = np.percentile(all_cv_values, auto_threshold_quantile)
        if verbose:
            print(f"自动选择CV阈值: {auto_threshold_quantile}th percentile = {cv_threshold_value:.4f}")
    else:
        cv_threshold_value = float(cv_threshold)
        if verbose:
            print(f"使用固定CV阈值: {cv_threshold_value:.4f}")

    # 正式判断每组通道是否保留
    for ch_id, col_pair in grouped.items():
        cv_values = []
        retain = True

        for col in sorted(col_pair):  # 保证顺序一致
            cv = cv_dict.get(col, np.nan)
            wl_match = re.search(r'\((\d+\.?\d*)\)', col)
            wl = wl_match.group(1) if wl_match else "UNK"
            cv_values.append((wl, cv))

            if np.isnan(cv):
                retain = False
                bad_channels[col] = "无效CV"
            elif cv > cv_threshold_value:
                retain = False
                bad_channels[col] = f"CV过大（CV={cv:.4f}）"

        # 如果波长数目不等于2，也标记异常
        if len(cv_values) != 2:
            retain = False
            bad_channels[ch_id] = "波长数目不足2"

        # 构造记录行
        if len(cv_values) == 2:
            row = {
                "Channel": ch_id,
                "CV_1": cv_values[0][1],
                "CV_2": cv_values[1][1],
                "Retained": retain
            }
        else:
            # 补 NaN 占位
            row = {"Channel": ch_id, "CV_1": np.nan, "CV_2": np.nan, "Retained": False}
        cv_table.append(row)

    # 输出异常信息
    if verbose:
        def ch_key(ch): return int(re.search(r'\d+', ch).group())
        bad_channels_summary = {}

        for ch_wl, reason in bad_channels.items():
            ch_id = extract_channel_id(ch_wl)
            wl_match = re.search(r'\((\d+\.?\d*)\)', ch_wl)
            wl = wl_match.group(1) if wl_match else "UNK"

            if "CV过大" in reason:
                cv_val_match = re.search(r'CV=([\d\.]+)', reason)
                cv_val = cv_val_match.group(1) if cv_val_match else "UNK"
                msg = f"CV过大（波长{wl}，CV={cv_val}）"
            else:
                msg = reason

            bad_channels_summary.setdefault(ch_id, []).append(msg)

        total_channels = len(grouped)
        bad_count = len(bad_channels_summary)
        bad_ratio = bad_count / total_channels if total_channels > 0 else 0

        if bad_channels_summary:
            print("⚠️ 发现异常通道：")
            for ch in sorted(bad_channels_summary.keys(), key=ch_key):
                print(f"  - {ch}: {', '.join(bad_channels_summary[ch])}")
            print(f"\n📊 异常通道数量: {bad_count} / {total_channels} ({bad_ratio:.2%})")
        else:
            print("✅ 所有通道数据正常。")

    # 转换为数据框并进行保存
    cv_df = pd.DataFrame(cv_table)

    return cv_df


def bandpass_filter(data, sfreq, l_freq, h_freq, order=4):
    """
    带通滤波

    Parameters
    ----------
      data: 数据
      sfreq: 采样率
      l_freq: 低频截止频率
      h_freq: 高频截止频率
      order: 滤波器阶数

    Returns
    -------
      filtered_data: 滤波后的数据
    """
    nyq = 0.5 * sfreq
    b, a = butter(order, [l_freq / nyq, h_freq / nyq], btype='band')
    return filtfilt(b, a, data)


def od_sci(od_df, sfreq=10, l_freq=0.5, h_freq=2.5, threshold=0.5):
    """
    计算头皮耦合指数（SCI）
    """
    # 使用 helper 函数获取通道列
    ch_cols = get_channel_columns(od_df)
    
    df = od_df[ch_cols].copy()
    num_cols = len(df.columns)

    # 检查是否为偶数列
    if num_cols % 2 != 0:
        raise ValueError("通道数必须为偶数，每对通道应包含两个波长")
    
    results = []
    retained_cols = []

    # 遍历每一对通道
    for i in range(0, num_cols, 2):
        col1, col2 = df.columns[i], df.columns[i + 1]
        ch_id = extract_channel_id(col1)

        # 进行 0.5 - 2.5Hz 带通滤波，提取心跳耦合波
        sig1 = bandpass_filter(df[col1].values, sfreq, l_freq, h_freq)
        sig2 = bandpass_filter(df[col2].values, sfreq, l_freq, h_freq)

        # 归一化
        sig1 = (sig1 - np.mean(sig1)) / np.std(sig1)
        sig2 = (sig2 - np.mean(sig2)) / np.std(sig2)

        # 计算头皮耦合指数（心跳耦合波之间的相关性）
        r = np.corrcoef(sig1, sig2)[0, 1]
        keep_flag = r > threshold
        results.append({'CH': ch_id, 'SCI': r, 'Retained': keep_flag})

        # 如果头皮耦合指数大于阈值，则保留该通道
        if keep_flag:
            retained_cols.extend([col1, col2])

    sci_df = pd.DataFrame(results)

    return sci_df


def od_psp(od_df, sfreq=10, time_window=10, l_freq=0.5, h_freq=2.5, fcut_max=2.5, threshold=0.1):
    """
    分时间窗口批量计算PSP

    Parameters
    ----------
    od_df : pd.DataFrame
        光密度数据
    sfreq : float
        采样率
    time_window : float
        时间窗口长度 (秒)
    l_freq, h_freq : float
        带通滤波范围
    fcut_max : float
        最大频率
    threshold : float
        阈值

    Returns
    -------
    psp_results : pd.DataFrame
        每个通道每个窗口的PSP及判定
    """
    ch_cols = [col for col in od_df.columns if extract_channel_id(col) is not None]
    df = od_df[ch_cols].copy()
    num_cols = len(df.columns)

    if num_cols % 2 != 0:
        raise ValueError("通道数必须为偶数，每对通道应包含两个波长")

    # 窗口大小 (采样点)
    window_samples = int(np.ceil(time_window * sfreq))
    n_windows = int(np.floor(len(df) / window_samples))

    results = []

    for i in range(0, num_cols, 2):
        col1, col2 = df.columns[i], df.columns[i+1]
        ch_id = extract_channel_id(col1)

        # 带通滤波
        sig1 = bandpass_filter(df[col1].values, sfreq, l_freq, h_freq)
        sig2 = bandpass_filter(df[col2].values, sfreq, l_freq, h_freq)

        # 标准化
        sig1 = (sig1 - np.mean(sig1)) / (np.std(sig1) or 1)
        sig2 = (sig2 - np.mean(sig2)) / (np.std(sig2) or 1)

        for w in range(n_windows):
            start = int(w * window_samples)
            end = start + window_samples

            s1_window = sig1[start:end]
            s2_window = sig2[start:end]

            # 互相关
            c = correlate(s1_window, s2_window, mode="full")
            c = c / window_samples

            # Periodogram
            f, pxx = periodogram(
                c,
                fs=sfreq,
                window="hamming",
                scaling="density"
            )

            # 提取峰值
            mask = f < fcut_max
            psp_val = np.max(pxx[mask])
            psp_freq = f[mask][np.argmax(pxx[mask])]

            keep_flag = psp_val > threshold

            results.append({
                "CH": ch_id,
                "Window": w,
                "PSP": psp_val,
                "PeakFreq": psp_freq,
                "Retained": keep_flag
            })

    psp_df = pd.DataFrame(results)
    return psp_df
