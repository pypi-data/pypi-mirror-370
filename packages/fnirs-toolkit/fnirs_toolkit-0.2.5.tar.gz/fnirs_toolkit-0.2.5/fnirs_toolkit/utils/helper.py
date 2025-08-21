"""
fNIRS 数据处理辅助函数模块

本模块提供 fNIRS 数据处理中常用的辅助函数，包括：
1. 通道标识符提取和解析
2. 数据集采样率计算
3. 任务标记索引获取
4. 通道列筛选和验证

主要功能：
- extract_channel_id: 从列名中提取通道编号（如 'CH3(690)' -> 'CH3'）
- get_channel_columns: 获取数据框中所有有效的通道列
- get_sfreq: 基于时间列计算数据集采样率
- get_task_index: 获取任务开始/结束的时间索引

支持设备类型：
- ZLHK: 中科院光电技术研究所设备格式
"""

import re
import pandas as pd
import numpy as np
from typing import List, Optional, Union


def extract_channel_id(colname: str, device_type: str = "ZLHK") -> Optional[str]:
    """
    从列名中提取通道编号
    
    Parameters
    ----------
    colname : str
        通道列名，如 'CH3(690)' 或 'CH3(690.0)'
    device_type : str, default "ZLHK"
        设备类型标识符
    
    Returns
    -------
    str or None
        通道编号（如 'CH3'），如果不匹配则返回 None
        
    Examples
    --------
    >>> extract_channel_id("CH3(690)")
    'CH3'
    >>> extract_channel_id("CH10(830.0)")
    'CH10'
    >>> extract_channel_id("Time")
    None
    """
    if device_type == "ZLHK":
        match = re.match(r'(CH\d+)\(\d+\.?\d*\)', colname.strip())
        return match.group(1) if match else None
    else:
        raise ValueError(f"不支持的设备类型: {device_type}")


def get_channel_columns(df: pd.DataFrame, device_type: str = "ZLHK") -> List[str]:
    """
    获取数据框中所有有效的通道列名
    
    Parameters
    ----------
    df : pd.DataFrame
        包含 fNIRS 数据的数据框
    device_type : str, default "ZLHK"
        设备类型标识符
        
    Returns
    -------
    List[str]
        有效通道列名列表
        
    Examples
    --------
    >>> df = pd.DataFrame({'CH1(690)': [1,2], 'CH1(830)': [3,4], 'Time': [0,1]})
    >>> get_channel_columns(df)
    ['CH1(690)', 'CH1(830)']
    """
    return [col for col in df.columns if extract_channel_id(col, device_type) is not None]


def group_channels_by_id(df: pd.DataFrame, device_type: str = "ZLHK") -> dict:
    """
    按通道编号对列进行分组
    
    Parameters
    ----------
    df : pd.DataFrame
        包含 fNIRS 数据的数据框
    device_type : str, default "ZLHK"
        设备类型标识符
        
    Returns
    -------
    dict
        {通道编号: [对应列名列表]} 的字典
        
    Examples
    --------
    >>> df = pd.DataFrame({'CH1(690)': [1,2], 'CH1(830)': [3,4], 'CH2(690)': [5,6]})
    >>> group_channels_by_id(df)
    {'CH1': ['CH1(690)', 'CH1(830)'], 'CH2': ['CH2(690)']}
    """
    ch_cols = get_channel_columns(df, device_type)
    grouped = {}
    for col in ch_cols:
        ch_id = extract_channel_id(col, device_type)
        grouped.setdefault(ch_id, []).append(col)
    return grouped


def get_sfreq(df: pd.DataFrame, method: str = "first_n", n_samples: int = 100, 
              min_samples: int = 10, tolerance: float = 0.05) -> float:
    """
    获取数据集的采样率（Hz），支持多种计算方法以应对数据中断情况
    
    Parameters
    ----------
    df : pd.DataFrame
        包含时间列的数据框
    method : str, default "first_n"
        计算方法：
        - "first_n": 使用前n个样本计算
        - "median_diff": 使用时间差的中位数
        - "mode_diff": 使用时间差的众数
        - "robust": 综合多种方法的稳健估计
    n_samples : int, default 100
        使用前n个样本进行计算
    min_samples : int, default 10
        最少需要的样本数
    tolerance : float, default 0.05
        采样率变化的容忍度（用于检测异常）
        
    Returns
    -------
    float
        采样率（每秒采样次数）
        
    Raises
    ------
    ValueError
        当无法找到时间列或计算采样率时
        
    Examples
    --------
    >>> df = pd.DataFrame({'Time': ['00:00:00.000', '00:00:00.100', '00:00:00.200']})
    >>> get_sfreq(df, method="first_n", n_samples=3)
    10.0
    """
    # 找到时间列
    time_cols = [col for col in df.columns if 'Time' in col or 'time' in col.lower()]
    if not time_cols:
        raise ValueError("未找到时间列（列名应包含 'Time' 或 'time'）")
    
    time_col = time_cols[0]
    
    if len(df) < min_samples:
        raise ValueError(f"数据行数 {len(df)} 少于最小要求 {min_samples}")
    
    # 将时间字符串转换为秒数
    time_in_sec = _parse_time_to_seconds(df[time_col])
    
    if method == "first_n":
        return _calc_sfreq_first_n(time_in_sec, n_samples)
    elif method == "median_diff":
        return _calc_sfreq_median_diff(time_in_sec)
    elif method == "mode_diff":
        return _calc_sfreq_mode_diff(time_in_sec)
    elif method == "robust":
        return _calc_sfreq_robust(time_in_sec, n_samples, tolerance)
    else:
        raise ValueError(f"不支持的计算方法: {method}")


def _parse_time_to_seconds(time_series: pd.Series) -> pd.Series:
    """将时间字符串转换为秒数"""
    # 尝试多种时间格式
    formats = ["%H:%M:%S.%f", "%H:%M:%S", "%M:%S.%f", "%M:%S"]
    
    for fmt in formats:
        try:
            time_dt = pd.to_datetime(time_series, format=fmt)
            # 转换为从第一个时间点开始的秒数
            time_in_sec = (
                time_dt.dt.hour * 3600 + 
                time_dt.dt.minute * 60 + 
                time_dt.dt.second + 
                time_dt.dt.microsecond / 1e6
            )
            # 处理跨天情况（如果第二个时间小于第一个时间）
            if len(time_in_sec) > 1 and time_in_sec.iloc[1] < time_in_sec.iloc[0]:
                # 假设跨天，给后续时间加上24小时
                mask = time_in_sec < time_in_sec.iloc[0]
                time_in_sec.loc[mask] += 24 * 3600
            
            return time_in_sec
        except ValueError:
            continue
    
    raise ValueError(f"无法解析时间格式，尝试的格式: {formats}")


def _calc_sfreq_first_n(time_in_sec: pd.Series, n_samples: int) -> float:
    """使用前n个样本计算采样率"""
    n_use = min(n_samples, len(time_in_sec))
    time_subset = time_in_sec.iloc[:n_use]
    
    duration = time_subset.iloc[-1] - time_subset.iloc[0]
    if duration <= 0:
        raise ValueError("时间跨度为0或负数，无法计算采样率")
    
    # 采样率 = (样本数-1) / 时间跨度
    sfreq = (n_use - 1) / duration
    return sfreq


def _calc_sfreq_median_diff(time_in_sec: pd.Series) -> float:
    """使用时间差的中位数计算采样率"""
    time_diffs = time_in_sec.diff().dropna()
    
    # 过滤异常大的时间差（可能是中断点）
    median_diff = time_diffs.median()
    filtered_diffs = time_diffs[time_diffs <= median_diff * 3]  # 过滤超过3倍中位数的差值
    
    if len(filtered_diffs) == 0:
        raise ValueError("无法找到有效的时间间隔")
    
    avg_interval = filtered_diffs.median()
    if avg_interval <= 0:
        raise ValueError("时间间隔为0或负数")
    
    return 1.0 / avg_interval


def _calc_sfreq_mode_diff(time_in_sec: pd.Series) -> float:
    """使用时间差的众数计算采样率"""
    time_diffs = time_in_sec.diff().dropna()
    
    # 将时间差四舍五入到合理精度（避免浮点数精度问题）
    rounded_diffs = (time_diffs * 10000).round() / 10000
    
    # 找到最常见的时间间隔
    mode_diff = rounded_diffs.mode()
    if len(mode_diff) == 0:
        raise ValueError("无法找到时间间隔的众数")
    
    interval = mode_diff.iloc[0]
    if interval <= 0:
        raise ValueError("时间间隔为0或负数")
    
    return 1.0 / interval


def _calc_sfreq_robust(time_in_sec: pd.Series, n_samples: int, tolerance: float) -> float:
    """稳健的采样率估计，综合多种方法"""
    methods_results = []
    
    # 方法1: 前n个样本
    try:
        sfreq1 = _calc_sfreq_first_n(time_in_sec, n_samples)
        methods_results.append(("first_n", sfreq1))
    except ValueError:
        pass
    
    # 方法2: 中位数差值
    try:
        sfreq2 = _calc_sfreq_median_diff(time_in_sec)
        methods_results.append(("median_diff", sfreq2))
    except ValueError:
        pass
    
    # 方法3: 众数差值
    try:
        sfreq3 = _calc_sfreq_mode_diff(time_in_sec)
        methods_results.append(("mode_diff", sfreq3))
    except ValueError:
        pass
    
    if not methods_results:
        raise ValueError("所有采样率计算方法都失败")
    
    # 检查结果一致性
    sfreqs = [result[1] for result in methods_results]
    median_sfreq = np.median(sfreqs)
    
    # 过滤掉偏差过大的结果
    valid_sfreqs = [s for s in sfreqs if abs(s - median_sfreq) / median_sfreq <= tolerance]
    
    if not valid_sfreqs:
        # 如果所有结果都偏差过大，返回中位数并警告
        import warnings
        warnings.warn(f"采样率计算结果差异较大: {sfreqs}, 返回中位数: {median_sfreq:.2f}")
        return median_sfreq
    
    return np.mean(valid_sfreqs)


def detect_time_discontinuities(df: pd.DataFrame, threshold_factor: float = 3.0) -> List[int]:
    """
    检测时间列中的不连续点
    
    Parameters
    ----------
    df : pd.DataFrame
        包含时间列的数据框
    threshold_factor : float, default 3.0
        判断不连续的阈值因子（相对于正常时间间隔的倍数）
        
    Returns
    -------
    List[int]
        不连续点的索引列表
    """
    time_cols = [col for col in df.columns if 'Time' in col or 'time' in col.lower()]
    if not time_cols:
        return []
    
    time_in_sec = _parse_time_to_seconds(df[time_cols[0]])
    time_diffs = time_in_sec.diff().dropna()
    
    # 计算正常时间间隔
    median_diff = time_diffs.median()
    threshold = median_diff * threshold_factor
    
    # 找到异常大的时间间隔
    discontinuities = time_diffs[time_diffs > threshold].index.tolist()
    
    return discontinuities


def get_task_index(df, task, type, task_duration=None):
    """
    获取任务开始和结束的索引

    Parameters
    ----------
    df: pd.DataFrame
        数据集
    task: str
        任务名称
    type: str
        类型，可选择'start'或'end'
    task_duration: float

    Returns
    ----------
    float
        标签位置（对应Probe列的数值）
    """
    # 获取采样率
    df['Mark'] = df['Mark'].astype(str)
    sfreq = get_sfreq(df)

    # 获取任务开始和结束的索引
    task_index = df.loc[df['Mark'] == task, 'Probe1'].values

    if len(task_index) == 0:
        raise ValueError("没有发现此任务打标。")

    # 获取任务开始和结束的索引
    if type == 'start':
        return task_index[0]
    elif type == 'end':
        return task_index[0] + int(task_duration * sfreq)
    else:
        raise ValueError("类型错误")
