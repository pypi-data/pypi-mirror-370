# 作者：@Jamie
# 日期：2025-07-08
# 描述：测试光密度数据预处理步骤


import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from functions.raw_import import raw_intensity_import, raw_intensity_to_od
from functions.OD_preprocess import OD_resample, OD_cut, OD_detect_motion_artifacts
from functions.helper import get_sfreq, get_task_index
from functions.OD_visualize import OD_visualize

# 读取原始数据并转换为 OD
raw_df = raw_intensity_import(r"data/raw/raw_sample02.measure")
od_df = raw_intensity_to_od(raw_df)



## 测试01: OD 数据的重采样
print("测试01：OD 数据的重采样 ================================")
sfreq = get_sfreq(od_df)
print("原始的采样率: ", sfreq)
od_resampled = OD_resample(od_df, sfreq=sfreq, target_freq = 10)
print(od_resampled)
sfreq = get_sfreq(od_resampled)
print("重采样之后的采样率： ", od_resampled)



## 测试02：OD 数据的截取
print("测试02：OD 数据的任务截取 ================================")
VFT_start = get_task_index(od_resampled, task="VFT1", type="start")
VFT_end = get_task_index(od_resampled, task="VFT1", type="end", task_duration=60)
od_VFT = OD_cut(od_resampled, index_range=[VFT_start - 10*sfreq, VFT_end])
print(od_VFT.shape)
print(od_VFT.head())
OD_visualize(od_VFT, file_name="伪迹测试-03-1-原始波形", output_path="output/figure")



## 测试03：OD 数据的滤波
print("测试03：OD 数据的滤波 ================================")
sfreq = get_sfreq(od_resampled)
od_VFT_FIL = OD_detect_motion_artifacts(od_VFT)
OD_visualize(od_VFT_FIL, file_name="伪迹测试-03-2-滤波后波形", output_path="output/figure")



## 测试04：OD 数据的伪迹处理
print("测试04：OD 数据的伪迹处理 ================================")
OD_VFT_Clean = OD_detect_motion_artifacts(od_VFT_FIL)
OD_visualize(OD_VFT_Clean, file_name="伪迹测试-03-2-处理后波形", output_path="output/figure")
