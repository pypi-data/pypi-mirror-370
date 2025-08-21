# 作者：@Jamie
# 日期：2025-06-23
# 功能：测试所有OD质量控制相关函数


import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from functions.raw_import import raw_intensity_import, raw_intensity_to_od
from functions.OD_quality import OD_CV, OD_scalp_coupling_index, OD_psp


# 测试准备：读取原始光强数据
print("测试准备：读取原始光强数据 ================================")
raw_df = raw_intensity_import(r"data/raw/raw_sample01.measure")
OD_df_base10 = raw_intensity_to_od(raw_df)


# 测试01：光强数据变异性情况
## 测试01-1：光强数据变异性情况（手动阈值，默认值 0.2）
print("测试01-1：光强数据变异性情况（手动阈值，默认值 0.2） ================================")
OD_cv_df = OD_CV(OD_df_base10, verbose=False)
print(OD_cv_df)

## 测试01-2：光强数据变异性情况（手动阈值，自定义阈值 0.1）
print("测试01-2：光强数据变异性情况（手动阈值，自定义阈值 0.1） ================================")
OD_cv_df = OD_CV(OD_df_base10, cv_threshold=0.1, verbose=False)
print(OD_cv_df)

## 测试01-3：光强数据变异性情况（自动阈值，默认值 90）
print("测试01-3：光强数据变异性情况（自动阈值，默认值 90） ================================")
OD_cv_df = OD_CV(OD_df_base10, use_auto_threshold=True, verbose=False)
print(OD_cv_df)

## 测试01-4：光强数据变异性情况（自动阈值，自定义阈值 90）
print("测试01-4：光强数据变异性情况（自动阈值，自定义阈值 90） ================================")
OD_cv_df = OD_CV(OD_df_base10, use_auto_threshold=True, auto_threshold_quantile=90, verbose=False)
print(OD_cv_df)


## 测试01-5：光强数据变异性情况（自动阈值，自定义阈值 90，verbose=True）
print("测试01-5：光强数据变异性情况（自动阈值，自定义阈值 90，verbose=True） ================================")
OD_cv_df = OD_CV(OD_df_base10, use_auto_threshold=True, auto_threshold_quantile=90, verbose=True)
print(OD_cv_df)


# 测试2：光强数据头皮耦合指数情况
## 测试2-1：光强数据头皮耦合指数情况（默认值）
OD_SCI_df = OD_scalp_coupling_index(OD_df_base10)
print(OD_SCI_df)

## 测试2-2：光强数据头皮耦合指数情况（自定义阈值）
OD_SCI_df = OD_scalp_coupling_index(OD_df_base10, threshold=0.6)
print(OD_SCI_df)

# 测试3：光强数据Peak Spectral Power (PSP)指标情况
## 测试3-1：光强数据Peak Spectral Power (PSP)指标情况（默认值）
print("测试3-1：光强数据Peak Spectral Power (PSP)指标情况（默认值） ================================")
OD_psp_df = OD_psp(OD_df_base10)
print(OD_psp_df)

## 测试3-2：光强数据Peak Spectral Power (PSP)指标情况（自定义阈值）
print("测试3-2：光强数据Peak Spectral Power (PSP)指标情况（自定义阈值） ================================")
OD_psp_df = OD_psp(OD_df_base10, threshold=0.05)
print(OD_psp_df)
