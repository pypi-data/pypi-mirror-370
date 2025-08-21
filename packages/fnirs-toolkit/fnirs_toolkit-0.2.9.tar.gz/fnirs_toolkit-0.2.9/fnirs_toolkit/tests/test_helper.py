"""
测试辅助函数模块

本模块测试 utils/helper.py 中的所有辅助函数，包括：
1. 通道标识符提取和解析
2. 通道列筛选和分组
3. 数据集采样率计算（多种方法）
4. 任务标记索引获取
5. 时间不连续点检测
"""

import sys
import os
import pandas as pd
import numpy as np
import warnings

# 添加项目根目录到路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 正确导入项目模块
from utils.helper import (
    extract_channel_id, 
    get_channel_columns, 
    group_channels_by_id,
    get_sfreq, 
    get_task_index,
    detect_time_discontinuities,
    _parse_time_to_seconds
)
from nirs_io.raw_io import raw_intensity_import
from nirs_io.converters import raw_intensity_to_od
from nirs_io.hb_io import hb_import


# 测试01：提取通道编号
print("\n" + "="*60)
print("测试01：提取通道编号")
print("="*60)

## 测试01-1：提取通道编号-波长不带小数点的通道
print("测试01-1：提取通道编号-波长不带小数点的通道")
test01_ch = extract_channel_id("CH3(690)")
print(f"输入: 'CH3(690)', 结果: '{test01_ch}'")

## 测试01-2：提取通道编号-波长带小数点的通道
print("\n测试01-2：提取通道编号-波长带小数点的通道")
test02_ch = extract_channel_id("CH3(690.0)")
print(f"输入: 'CH3(690.0)', 结果: '{test02_ch}'")

## 测试01-3：提取通道编号-失败案例
print("\n测试01-3：提取通道编号-失败案例")
test03_ch = extract_channel_id("Probe")
print(f"输入: 'Probe', 结果: '{test03_ch}'")


# 测试02：通道列筛选和分组
print("\n" + "="*60)
print("测试02：通道列筛选和分组")
print("="*60)

## 测试数据集
raw_df = raw_intensity_import(r"fnirs_toolkit/data/raw/raw_sample01.csv")
od_df = raw_intensity_to_od(raw_df)

## 测试02-1：获取通道列
print("测试02-1：获取通道列")
ch_cols = get_channel_columns(od_df)
print(f"通道列: {ch_cols}")

## 测试02-2：按通道ID分组
print("\n测试02-2：按通道ID分组")
grouped = group_channels_by_id(od_df)
print(f"分组结果: {grouped}")


# 测试03：采样率计算
print("\n" + "="*60)
print("测试03：采样率计算")
print("="*60)

## 创建测试数据

# 包含中断的数据
raw_df2 = raw_intensity_import(r"fnirs_toolkit/data/raw/raw_sample04.csv")
od_df2 = raw_intensity_to_od(raw_df2)

## 测试03-1：正常数据的采样率计算
print("测试03-1：正常数据的采样率计算")
print(f"前n个样本法: {get_sfreq(od_df, method='first_n', n_samples=5):.2f} Hz")
print(f"中位数差值法: {get_sfreq(od_df, method='median_diff'):.2f} Hz")
print(f"众数差值法: {get_sfreq(od_df, method='mode_diff'):.2f} Hz")
print(f"稳健估计法: {get_sfreq(od_df, method='robust'):.2f} Hz")

## 测试03-2：中断数据的采样率计算
print("\n测试03-2：中断数据的采样率计算")
print(f"前n个样本法: {get_sfreq(od_df2, method='first_n', n_samples=3):.2f} Hz")
print(f"中位数差值法: {get_sfreq(od_df2, method='median_diff'):.2f} Hz")
print(f"众数差值法: {get_sfreq(od_df2, method='mode_diff'):.2f} Hz")
print(f"稳健估计法: {get_sfreq(od_df2, method='robust'):.2f} Hz")



# 测试04：任务索引获取测试
print("\n" + "="*60)
print("测试04：测试任务索引")
print("="*60)

VFT_start = get_task_index(od_df, task="1", type="start")
print(f"VFT1 任务开始索引: {VFT_start}")

VFT_end = get_task_index(od_df, task="1", type="end", task_duration=60)
print(f"VFT1 任务结束索引: {VFT_end}")
