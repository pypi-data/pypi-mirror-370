# 作者：@Jamie
# 日期：2025-06-23
# 功能：测试所有血氧数据处理相关函数


import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import json
from functions.HB_import import HB_import
from functions.HB_visualize import HB_visualize
from functions.HB_integration import HB_brain_integration
from functions.HB_preprocess import HB_detrend, HB_TDDR, HB_filter
from functions.helper import get_sfreq


# 测试准备：读取血氧数据与脑区映射字典
HB_df = HB_import(r"data/HB/HB_sample02.csv")
region_map = json.load(open(r"data/channel_region_map.json"))
sfreq = get_sfreq(HB_df)

# 测试01：血氧数据预处理流程
## 测试01-1：去漂移
print("测试01-1：去漂移 ========================================")
HB_visualize(data=HB_df, file_name="HB预处理测试-01-1-HB_Before_Detrend", output_path="output/figure",
             title="去漂移之前的血氧数据", mode='both', path_corrected=False)
HB_df_detrended = HB_detrend(HB_df)
print(HB_df_detrended)
HB_visualize(data=HB_df_detrended, file_name="HB预处理测试-01-2-HB_After_Detrend", output_path="output/figure",
             title="去漂移之后的血氧数据", mode='both', path_corrected=False)

# 测试01-2：TDDR
print("测试01-2：TDDR ========================================")
HB_df_tddr = HB_TDDR(HB_df_detrended, sfreq=sfreq)
print(HB_df_tddr)
HB_visualize(data=HB_df_tddr, file_name="HB预处理测试-01-3-HB_After_TDDR", output_path="output/figure",
             title="TDDR之后的血氧数据", mode='both', path_corrected=False)

# 测试01-3：滤波
print("测试01-3：滤波 ========================================")
HB_df_filtered = HB_filter(HB_df_detrended, sfreq=sfreq)
print(HB_df_filtered)
HB_visualize(data=HB_df_filtered, file_name="HB预处理测试-01-4-HB_After_Filter", output_path="output/figure",
             title="滤波之后的血氧数据", mode='both', path_corrected=False)



# 测试01：按照时间获取血氧信号均值
# TODO


# 测试02：按照脑区拟合通道
## 测试02-1：按照脑区拟合通道（Oxy信号）
print("测试02-1：按照脑区拟合通道（Oxy信号） ================================")
HB_brain_df = HB_brain_integration(HB_df_tddr, region_map, hb_type='oxy')
print(HB_brain_df)

## 测试02-2：按照脑区拟合通道（DeOxy信号）
print("测试02-2：按照脑区拟合通道（DeOxy信号） ================================")
HB_brain_df = HB_brain_integration(HB_df_tddr, region_map, hb_type='deOxy')
print(HB_brain_df)

