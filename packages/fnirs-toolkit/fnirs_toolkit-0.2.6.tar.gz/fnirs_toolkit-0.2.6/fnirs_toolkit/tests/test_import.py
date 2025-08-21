# 功能：测试所有功能函数


import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from nirs_io.raw_io import raw_intensity_import
from nirs_io.converters import raw_intensity_to_od, od_beerlambert
from nirs_io.hb_io import hb_import
from nirs_analysis.integration import hb_time_average
import pandas as pd


### =========================== 数据的读取和转化 ================================
# 测试01：读取原始光强数据
## 测试01-1：读取原始光强数据（csv）
print("测试01-1：读取 csv 格式的原始光强数据 ================================")
raw_df = raw_intensity_import(r"fnirs_toolkit/data/raw/raw_sample01.csv")
print(raw_df)

## 测试01-2：读取原始光强数据（measure）
print("测试01-2：读取 measure 格式的原始光强数据 ================================")
raw_df = raw_intensity_import(r"fnirs_toolkit/data/raw/raw_sample01.measure")
print(raw_df)

# 测试02：将原始光强数据转换为光密度数据 
## 测试02-1：默认 base10 对数
print("测试02-1：将原始光强数据转换为光密度数据（Base 10） ================================")
od_df_base10 = raw_intensity_to_od(raw_df)
print(od_df_base10)

## 测试02-2：以自然对数为底
print("测试02-2：将原始光强数据转换为光密度数据（自然对数） ================================")
od_df_natural = raw_intensity_to_od(raw_df, base="natural")
print(od_df_natural)

# 测试03: 光密度数据转换为血氧数据
## 测试03-1：光密度数据转换为血氧数据（Base 10）
print("测试03-1：光密度数据转换为血氧数据（Base 10） ================================")
HB_df_base10 = od_beerlambert(od_df_base10, [690, 830], base='base10')
print(HB_df_base10)

## 测试03-2：光密度数据转换为血氧数据（自然对数）
print("测试03-2：光密度数据转换为血氧数据（自然对数） ================================")
HB_df_natural = od_beerlambert(od_df_natural, [690, 830], base='natural')
print(HB_df_natural)

# 测试04：导入血氧数据
print("测试04：导入血氧数据 ================================")
HB_df = hb_import(r"fnirs_toolkit/data/HB/HB_sample02.csv")
print(HB_df)


### =========================== 数据的处理 ================================
# 测试01：计算指定时间段下的平均值
## 测试01-1：计算指定时间段0-10s下的平均值
print("测试01-1：计算指定时间段下的平均值 ================================")
HB_df_time_avg_0_10 = hb_time_average(HB_df, freq=10, start_time=0, end_time=10)
print(HB_df_time_avg_0_10)

## 测试01-2：计算指定时间段10-20s下的平均值
print("测试01-2：计算指定时间段10-20s下的平均值 ================================")
HB_df_time_avg_10_20 = hb_time_average(HB_df, freq=10, start_time=10, end_time=20)
print(HB_df_time_avg_10_20)

## 测试01-3：计算全时间段下的平均值（自然对数）
print("测试01-3：计算全时间段下的平均值 ================================")
HB_df_time_avg_all = hb_time_average(HB_df, freq=10)
print(HB_df_time_avg_all)

## 测试02：计算指定脑区下的通道拟合平均
# TODO: 添加测试相关用例


