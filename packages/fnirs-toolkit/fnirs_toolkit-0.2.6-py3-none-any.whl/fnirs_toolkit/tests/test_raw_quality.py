# 作者：@Jamie
# 日期：2025-06-23
# 功能：测试所有光强数据质量控制相关函数


import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from nirs_io.raw_io import raw_intensity_import
from nirs_preprocess.raw_quality import raw_CV


# 测试准备：读取原始光强数据
print("测试准备：读取原始光强数据 ================================")
raw_df = raw_intensity_import(r"data/raw/raw_sample01.measure")

# 测试01：光强数据变异系数情况
## 测试01-1：光强数据变异性情况（手动阈值，默认值 0.2）
print("测试01-1：光强数据变异性情况（手动阈值，默认值 0.2） ================================")
raw_cv_df = raw_CV(raw_df, verbose=False)
print(raw_cv_df)

## 测试01-2：光强数据变异性情况（手动阈值，自定义阈值 0.1）
print("测试01-2：光强数据变异性情况（手动阈值，自定义阈值 0.1） ================================")
raw_cv_df = raw_CV(raw_df, cv_threshold=0.1, verbose=False)
print(raw_cv_df)

## 测试01-3：光强数据变异性情况（自动阈值，默认值 90）
print("测试01-3：光强数据变异性情况（自动阈值，默认值 90） ================================")
raw_cv_df = raw_CV(raw_df, use_auto_threshold=True, verbose=False)
print(raw_cv_df)

## 测试01-4：光强数据变异性情况（自动阈值，自定义阈值 90）
print("测试01-4：光强数据变异性情况（自动阈值，自定义阈值 90） ================================")
raw_cv_df = raw_CV(raw_df, use_auto_threshold=True, auto_threshold_quantile=90, verbose=False)
print(raw_cv_df)


## 测试01-5：光强数据变异性情况（自动阈值，自定义阈值 90，verbose=True）
print("测试01-5：光强数据变异性情况（自动阈值，自定义阈值 90，verbose=True） ================================")
raw_cv_df = raw_CV(raw_df, use_auto_threshold=True, auto_threshold_quantile=90, verbose=True)
print(raw_cv_df)


    # file_id = "翁羽_自定义方案1_20241104142325"
    # input_path = f"{file_id}.csv"
    # raw_df = raw_intensity_import(input_path)

    # # 只保留通道列，转换为数值
    # channel_cols = [col for col in raw_df.columns if re.match(r'^CH\d+\(\d+\.?\d*\)$', col)]
    # raw_df = raw_df[channel_cols].apply(pd.to_numeric, errors='coerce')



    # print("=== 单独计算 CV ===")
    # cv_df, bad_info_cv, auto_thresh_cv = raw_CV(
    #     raw_df,
    #     cv_thresholds=[0.15],
    #     auto_threshold_quantile=0.95,
    #     use_auto_threshold=False,  # 手动阈值
    #     verbose=True
    # )
    # print(cv_df.head())

    # print("\n=== 单独计算 SNR ===")
    # snr_df, bad_info_snr, auto_thresh_snr = raw_SNR(
    #     raw_df,
    #     snr_thresholds=[13],
    #     auto_threshold_quantile=0.95,
    #     use_auto_threshold=False,  # 手动阈值
    #     verbose=True
    # )
    # print(snr_df.head())

    # print("\n=== 综合 CV + SNR 分析 ===")
    # # 综合分析，use_auto_threshold 可按需求设置
    # result = analyze_channel_quality(
    #     raw_df,
    #     cv_threshold=0.15,
    #     snr_threshold=13,
    #     use_auto_threshold=False,
    #     return_type="dict",
    #     verbose=True,
    #     save_csv=True,
    #     file_prefix=file_id
    # )

    # # result 是 dict，里面包含各项结果
    # cv_df = result["CV_Data"]
    # bad_info_cv = result["CV_Bad_Info"]
    # snr_df = result["SNR_Data"]
    # bad_info_snr = result["SNR_Bad_Info"]

    # print(cv_df.head())
    # print(snr_df.head())

    # cv_thresh_key = f"Thresh={result['Final_CV_Threshold']}"  # e.g. Thresh=0.15
    # bad_channels_cv = set(bad_info_cv.get(cv_thresh_key, {}).keys())


    # # 提取所有SNR坏通道名
    # bad_channels_snr = set()
    # for thresh_key, bad_ch_dict in bad_info_snr.items():
    #     bad_channels_snr.update(bad_ch_dict.keys())

    # # 合并所有坏通道
    # all_bad_channels = bad_channels_cv.union(bad_channels_snr)

    
    # # 确认 bad_channels_cv 和 bad_channels_snr 来自的是哪个 thresh key
    # print(bad_info_cv.keys())   # 确保是 'Thresh=0.15'
    # print(bad_info_snr.keys())  # 确保是 'Thresh=13'

    # # 严格提取特定阈值下的通道集合
    # cv_bad_set = set(bad_info_cv.get("Thresh=0.15", {}).keys())
    # snr_bad_set = set(bad_info_snr.get("Thresh=13", {}).keys())

    # only_cv = cv_bad_set - snr_bad_set
    # only_snr = snr_bad_set - cv_bad_set
    # both = cv_bad_set & snr_bad_set
    # either = cv_bad_set | snr_bad_set

    # print(f"仅CV异常通道数: {len(only_cv)}")
    # print(f"仅SNR异常通道数: {len(only_snr)}")
    # print(f"CV和SNR均异常通道数: {len(both)}")
    # print(f"坏通道总数（CV或SNR异常）: {len(either)}")


    # print("\n坏通道详细信息：")
    # for ch in sorted(all_bad_channels):
    #     print(f"\n通道 {ch}:")
    #     if ch in bad_channels_cv:
    #         cv_info = bad_info_cv.get("Thresh=0.15", {}).get(ch, "无详细信息")
    #         print(f"  - CV异常，详情：{cv_info}")
    #     else:
    #         print("  - CV正常")

    #     if ch in bad_channels_snr:
    #         snr_info = bad_info_snr.get("Thresh=13", {}).get(ch, "无详细信息")
    #         print(f"  - SNR异常，详情：{snr_info}")
    #     else:
    #         print("  - SNR正常")
