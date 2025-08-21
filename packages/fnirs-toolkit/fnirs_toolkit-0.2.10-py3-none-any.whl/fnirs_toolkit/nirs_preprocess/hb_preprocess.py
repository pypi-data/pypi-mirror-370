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
from ..utils.helper import get_channel_columns, get_sfreq
from mne.filter import filter_data


def hb_cut(HB_df, time_range):
    """
    # TODO: 根据时间戳截取血氧数据
    """
    if time_range is None:
        raise ValueError("time_range 不能为 None")
    
    sfreq = get_sfreq(HB_df)
    pass

def hb_detrend(HB_df: pd.DataFrame, order: int = 1) -> pd.DataFrame:
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
    oxy_cols = get_channel_columns(HB_df, type="oxy")
    deoxy_cols = get_channel_columns(HB_df, type="deoxy")

    for col in oxy_cols + deoxy_cols:
        y = HB_df[col].values
        x = np.arange(1, tp + 1)

        # 多项式拟合
        p = np.polyfit(x, y, order)
        trend = np.polyval(p, x)

        # 去趋势
        df_detrended[col] = y - trend

    return df_detrended


def hb_filter(HB_df: pd.DataFrame, sfreq: float,
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
