# 功能：测试所有可视化相关函数

import sys
import os
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from nirs_io.raw_io import raw_intensity_import
from nirs_io.hb_io import hb_import
from nirs_io.converters import od_beerlambert, raw_intensity_to_od
from nirs_analysis.integration import hb_time_average
from nirs_plot.od_plot import od_plot
from nirs_analysis.integration import hb_brain_integration
from nirs_plot.hb_plot import hb_plot, hb_heatmap, hb_region_plot
import pandas as pd

### =========================== 数据的可视化 ================================

# 测试准备：读取原始光强数据
print("测试准备：读取原始光强数据 ================================")
raw_df = raw_intensity_import(r"fnirs_toolkit/data/raw/raw_sample01.measure")
od_df_base10 = raw_intensity_to_od(raw_df)
od_df_natural = raw_intensity_to_od(raw_df, base="natural")

raw_df2 = raw_intensity_import(r"fnirs_toolkit/data/raw/raw_sample04.csv")
od_df2 = raw_intensity_to_od(raw_df2)

HB_df_base10 = od_beerlambert(od_df_base10, [690, 830], base='base10')
HB_df_natural = od_beerlambert(od_df_natural, [690, 830], base='natural')
HB_df = hb_import(r"fnirs_toolkit/data/HB/HB_sample02.csv")
HB_df_time_avg_0_10 = hb_time_average(HB_df, freq=10, start_time=0, end_time=10)


# 测试01：光密度数据波形可视化
## 测试01-1：光密度数据波形可视化（Base 10）
print("测试01-1：光密度数据波形可视化（Base 10） ================================")
od_plot(od_df_base10, file_name="可视化测试-01-1-OD_Base10", output_path="output/figure")

## 测试01-2：光密度数据波形可视化（自然对数）
print("测试01-2：光密度数据波形可视化（自然对数） ================================")
od_plot(od_df_natural, file_name="可视化测试-01-2-OD_Natural", output_path="output/figure")

## 测试01-3：光密度数据波形可视化（89通道）
print("测试01-3：光密度数据波形可视化（89通道） ================================")
od_plot(od_df2, file_name="可视化测试-01-3-OD_89通道", output_path="output/figure")

# 测试02: 血氧数据可视化
## 测试02-1：血氧数据可视化（Base 10）
print("测试02-1：血氧数据可视化（Base 10） ================================")
hb_plot(hb_df=HB_df_base10, file_name="可视化测试-02-1-HB_Base10", output_path="output/figure",
             title="", mode='both', path_corrected=False)

## 测试02-2：血氧数据可视化（自然对数）
print("测试02-2：血氧数据可视化（自然对数） ================================")
hb_plot(hb_df=HB_df_natural, file_name="可视化测试-02-2-HB_Natural", output_path="output/figure",
             title="", mode='both', path_corrected=False)

## 测试02-3：血氧数据波形可视化（只可视化 oxy 信号）
print("测试02-3：血氧数据波形可视化（只可视化 oxy 信号） ================================")
hb_plot(hb_df=HB_df_base10, file_name="可视化测试-02-3-HB_Oxy", output_path="output/figure",
             title="", mode='oxy', path_corrected=False)

## 测试02-4：血氧数据波形可视化（只可视化 deOxy 信号）
print("测试02-4：血氧数据波形可视化（只可视化 deOxy 信号） ================================")
hb_plot(hb_df=HB_df_base10, file_name="可视化测试-02-4-HB_DeOxy", output_path="output/figure",
             title="", mode='deOxy', path_corrected=False)

## 测试02-5：血氧数据波形可视化（添加任务开始标注）
print("测试02-5：血氧数据波形可视化（添加任务开始标注） ================================")
hb_plot(hb_df=HB_df, file_name="可视化测试-02-5-HB_AddTask", output_path="output/figure",
             title="", mode='both', path_corrected=False, add_task=True)

## 测试02-6：血氧数据波形可视化（截取时间段）
print("测试02-6：血氧数据波形可视化（截取时间段） ================================")
hb_plot(hb_df=HB_df, file_name="可视化测试-02-6-HB_TimeRange", output_path="output/figure",
             title="", mode='both', path_corrected=True, add_task=True, time_range=[110, 340])

# 测试03：血氧数据热力图可视化
## 测试03-1：血氧数据热力图可视化（oxy）
print("测试03：血氧数据热力图可视化 ================================")
channel_df = pd.read_csv("fnirs_toolkit/data/channel_location_ZLHK_Plate.csv")
print(HB_df_time_avg_0_10)
hb_heatmap(channel_df, HB_df_time_avg_0_10, file_name="可视化测试-03-1-HB_Avg", signal_type="oxy", title="Test08-HB_Time_Avg_0_10",
           cmap="RdBu_r", figsize=(12, 6), output_path="output/figure")

## 测试03-2：血氧数据热力图可视化（deOxy）
print("测试03-2：血氧数据热力图可视化（deOxy） ================================")
hb_heatmap(channel_df, HB_df_time_avg_0_10, file_name="可视化测试-03-2-HB_Avg", signal_type="deOxy", title="Test08-HB_Time_Avg_0_10",
           cmap="RdBu_r", figsize=(12, 6), output_path="output/figure")

# 测试04：血氧数据脑区可视化
## 测试04-1：血氧数据脑区可视化（oxy）
print("测试04-1：血氧数据脑区可视化（oxy） ================================")
region_map = json.load(open(r"fnirs_toolkit/data/channel_region_map.json"))
hb_brain_df = hb_brain_integration(HB_df, region_map, hb_type='oxy')
hb_region_plot(hb_brain_df, file_name="可视化测试-04-1-HB_Region", output_path="output/figure",
                    title="", mode='oxy', path_corrected=False)

## 测试04-2：血氧数据脑区可视化（deOxy）
print("测试04-2：血氧数据脑区可视化（deOxy） ================================")
HB_brain_df = hb_brain_integration(HB_df, region_map, hb_type='deOxy')
hb_region_plot(HB_brain_df, file_name="可视化测试-04-2-HB_Region", output_path="output/figure",
                    title="", mode='deOxy', path_corrected=False)

## 测试04-3：血氧数据脑区可视化（中文标题）
hb_region_plot(
    HB_brain_df, file_name="可视化测试-04-3-HB_Region_CH", output_path="output/figure",
    title="脑区平均HbO2变化趋势", mode="oxy", path_corrected=True
)

