# 作者：@Jamie
# 日期：2025-06-20
# 功能：将血氧数据进行多种整合
# 1. HB_time_avg: 计算指定时间段下的平均值
# 2. HB_brain_integration: 计算指定脑区下的通道拟合平均


import pandas as pd
import re

def hb_time_average(HB_df, freq=10, start_time=None, end_time=None):
    """
    提取 HbO2 / HbR 通道并计算指定时间段内的平均值。

    Parameters
    ----------
    HB_df : pd.DataFrame
        包含 CHx(oxy)/CHx(deOxy) 的原始数据框。
    freq : int
        采样率（Hz），用于根据时间确定起止行，默认为10Hz。
    start_time : float 或 None
        起始时间（秒）。如果为 None，则从头开始。
    end_time : float 或 None
        结束时间（秒）。如果为 None，则到结尾。

    Returns
    -------
    pd.DataFrame
        包含列 ['CH', 'Type', 'Value'] 的长格式结果。
    """
    # 基于 Probe1 列，筛选行
    if 'Probe1' not in HB_df.columns:
        raise ValueError("数据中缺少 'Probe1' 列，无法进行时间段筛选。")

    total_rows = HB_df.shape[0]
    start_row = int(start_time * freq) if start_time is not None else 0
    end_row = int(end_time * freq) if end_time is not None else total_rows

    # 利用 Probe1 行号筛选（假设 Probe1 从 1 开始）
    HB_df_filtered = HB_df[(HB_df['Probe1'] >= start_row + 1) & (HB_df['Probe1'] <= end_row)]

    pattern = re.compile(r'(CH\d+)\((oxy|deOxy)\)')
    records = []

    for col in HB_df_filtered.columns:
        match = pattern.fullmatch(col)
        if match:
            ch, typ = match.groups()
            avg_val = HB_df_filtered[col].mean()
            records.append({'CH': ch, 'Type': typ, 'Value': avg_val})

    result_df = pd.DataFrame(records)
    return result_df.sort_values(by=['CH', 'Type']).reset_index(drop=True)


def hb_brain_integration(HB_df, brain_region_map, hb_type='oxy'):
    """
    计算指定脑区下的通道拟合平均。

    Parameters
    ----------
    HB_df : pd.DataFrame
        包含 CHx(oxy)/CHx(deOxy) 的原始数据框。
    brain_region_map : str
        指定脑区名称与通道的映射字典。
    hb_type : str
        指定血氧类型：'oxy' 或 'deOxy'，默认为 'oxy'。

    Returns
    -------
    pd.DataFrame
        包含列 ['Probe1', 'Region', 'Value'] 的长格式结果，每个脑区一组。
    """
    if 'Probe1' not in HB_df.columns:
        raise ValueError("数据中必须包含 'Probe1' 列以标识时间点。")

    result_list = []

    for region, ch_list in brain_region_map.items():
        target_cols = [f"CH{ch}({hb_type})" for ch in ch_list]
        existing_cols = [col for col in target_cols if col in HB_df.columns]

        if len(existing_cols) == 0:
            continue  # 跳过该脑区

        sub_df = HB_df[['Probe1'] + existing_cols].copy()
        sub_df['Value'] = sub_df[existing_cols].mean(axis=1)
        sub_df['Region'] = region

        result_list.append(sub_df[['Probe1', 'Region', 'Value']])

    if not result_list:
        raise ValueError("未找到任何脑区的有效通道数据。")
    
    # 合并脑区数据的拟合
    long_df = pd.concat(result_list, axis=0, ignore_index=True)

    # 转换为宽格式
    wide_df = long_df.pivot(index='Probe1', columns='Region', values='Value').reset_index()

    return wide_df
    