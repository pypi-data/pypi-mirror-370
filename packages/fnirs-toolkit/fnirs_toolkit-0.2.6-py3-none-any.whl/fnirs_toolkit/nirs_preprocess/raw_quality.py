# 作者：@Boluo
# 日期：2025-06-19
# 描述：计算 fNIRS 原始光强数据中各个通道的变异系数（CV）和信噪比（SNR），支持多阈值测试，支持单一指标或双指标联合评估，输出每个通道在不同阈值下的保留与筛除结果


# import sys
# import os

# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import numpy as np
import pandas as pd
import re
import os 
from ..utils.helper import extract_channel_id, get_channel_columns, group_channels_by_id


def raw_CV(raw_df: pd.DataFrame, cv_threshold: float = 0.2, use_auto_threshold: bool = False, auto_threshold_quantile: float = 90, verbose: bool = True):
    """
    计算每个通道在各个波长下的变异系数（CV）。

    Parameters
    ----------
    raw_df : pd.DataFrame
        原始光强数据的DataFrame，每列为一个波长下的通道
    cv_threshold : float
        CV的手动阈值
    use_auto_threshold : bool
        True 表示使用自动阈值，False 表示使用手动阈值
    auto_threshold_quantile : float
        CV的自动阈值时使用的分位数（如0.90表示使用90%分位）
    verbose : bool
        是否打印详细信息

    Returns
    -------
    cv_df : pd.DataFrame
        含CV值及是否保留信息的DataFrame
    """
    cv_table = []
    bad_channels = {}

    # 使用 helper 函数获取通道列
    ch_cols = get_channel_columns(raw_df)
    
    # 使用 helper 函数按通道分组
    grouped = group_channels_by_id(raw_df)
    
    cv_dict = {}
    all_cv_values = []

    # 计算每个通道波长的 CV 值
    for ch_id, col_pair in grouped.items():
        for col in col_pair:
            signal = pd.to_numeric(raw_df[col], errors='coerce').dropna().values
            mean_signal = np.mean(signal) if len(signal) > 0 else 0

            if len(signal) == 0 or np.isclose(mean_signal, 0):
                cv = np.nan
            else:
                std_signal = np.std(signal)
                cv = std_signal / abs(mean_signal)

            cv_dict[col] = cv
            if not np.isnan(cv):
                all_cv_values.append(cv)

    # 自动或固定阈值
    if use_auto_threshold:
        cv_threshold_value = np.percentile(all_cv_values, auto_threshold_quantile)
        if verbose:
            print(f"自动选择CV阈值: {auto_threshold_quantile}th percentile = {cv_threshold_value:.4f}")
    else:
        cv_threshold_value = float(cv_threshold)
        if verbose:
            print(f"使用固定CV阈值: {cv_threshold_value:.4f}")

    # 正式判断每组通道是否保留
    bad_channels = {}
    for ch_id, col_pair in grouped.items():
        cv_values = []
        retain = True

        for col in sorted(col_pair):  # 保证顺序一致
            cv = cv_dict.get(col, np.nan)
            wl_match = re.search(r'\((\d+\.?\d*)\)', col)
            wl = wl_match.group(1) if wl_match else "UNK"
            cv_values.append((wl, cv))

            if np.isnan(cv):
                retain = False
                bad_channels[col] = "无效CV"
            elif cv > cv_threshold_value:
                retain = False
                bad_channels[col] = f"CV过大（CV={cv:.4f}）"

        # 如果波长数目不等于2，也标记异常
        if len(cv_values) != 2:
            retain = False
            bad_channels[ch_id] = "波长数目不足2"

        # 构造记录行
        if len(cv_values) == 2:
            row = {
                "Channel": ch_id,
                f"CV_{cv_values[0][0]}": cv_values[0][1],
                f"CV_{cv_values[1][0]}": cv_values[1][1],
                "Retained": retain
            }
        else:
            # 补 NaN 占位
            row = {"Channel": ch_id, "CV_1": np.nan, "CV_2": np.nan, "Retained": False}
        cv_table.append(row)

    # 输出异常信息
    if verbose:
        def ch_key(ch): return int(re.search(r'\d+', ch).group())
        bad_channels_summary = {}

        for ch_wl, reason in bad_channels.items():
            ch_id = extract_channel_id(ch_wl)
            wl_match = re.search(r'\((\d+\.?\d*)\)', ch_wl)
            wl = wl_match.group(1) if wl_match else "UNK"

            if "CV过大" in reason:
                cv_val_match = re.search(r'CV=([\d\.]+)', reason)
                cv_val = cv_val_match.group(1) if cv_val_match else "UNK"
                msg = f"CV过大（波长{wl}，CV={cv_val}）"
            else:
                msg = reason

            bad_channels_summary.setdefault(ch_id, []).append(msg)

        total_channels = len(grouped)
        bad_count = len(bad_channels_summary)
        bad_ratio = bad_count / total_channels if total_channels > 0 else 0

        if bad_channels_summary:
            print("⚠️ 发现异常通道：")
            for ch in sorted(bad_channels_summary.keys(), key=ch_key):
                print(f"  - {ch}: {', '.join(bad_channels_summary[ch])}")
            print(f"\n📊 异常通道数量: {bad_count} / {total_channels} ({bad_ratio:.2%})")
        else:
            print("✅ 所有通道数据正常。")

    # 转换为数据框并进行保存
    cv_df = pd.DataFrame(cv_table)

    return cv_df


def raw_SNR(df_data: pd.DataFrame, snr_thresholds: list[float] = None, auto_threshold_quantile: float = 0.95, use_auto_threshold: bool = True,
            verbose: bool = True):
    """
    计算每个通道在各个波长下的信噪比（SNR）。

    参数:
        df_data: 原始光强数据的DataFrame
        snr_thresholds: SNR的手动阈值列表
        auto_threshold_quantile: 自动阈值时使用的分位数
        use_auto_threshold: 是否启用自动阈值
        verbose: 是否打印详细信息

    返回:
        merged_df: 含SNR值及是否保留信息的DataFrame
        bad_channels_all: 每个阈值对应的异常通道信息（dict）
        auto_thresholds: 自动计算得到的SNR阈值（dict）
    """
    channel_cols = [col for col in df_data.columns if re.match(r'^CH\d+\(\d+\.?\d*\)$', col)]
    
    # 分组：同一通道不同波长
    grouped = {}
    for col in channel_cols:
        ch_id = extract_channel_id(col)
        grouped.setdefault(ch_id, []).append(col)
    
    raw_snr_data = []
    for ch_id, col_pair in grouped.items():
        ch_snr_info = {"Channel": ch_id}
        for col in col_pair:
            wl_match = re.search(r'\((\d+\.?\d*)\)', col)
            wl = wl_match.group(1) if wl_match else "UNK"
            signal = pd.to_numeric(df_data[col], errors='coerce').dropna().values
            if len(signal) == 0:
                snr = np.nan
            else:
                mean_signal = np.mean(signal)
                std_signal = np.std(signal)
                

                if std_signal != 0:
                    snr = 20 * np.log10(mean_signal / std_signal)
                else:
                    snr = np.nan

            ch_snr_info[f"SNR_{wl}"] = snr
        raw_snr_data.append(ch_snr_info)
    
    base_df = pd.DataFrame(raw_snr_data)
    
    auto_thresholds = {}
    
    if use_auto_threshold and (snr_thresholds is None or len(snr_thresholds) == 0) and auto_threshold_quantile is not None:
        all_snr_values = base_df.filter(like='SNR_').values.flatten()
        all_snr_values = all_snr_values[~np.isnan(all_snr_values)]
        if len(all_snr_values) > 0:
            auto_thresh = np.quantile(all_snr_values, auto_threshold_quantile)
            auto_thresholds[f"AutoQ{int(auto_threshold_quantile*100)}"] = round(float(auto_thresh), 5)
            if verbose:
                print(f"\n⚙️ 自动SNR阈值（{auto_threshold_quantile:.0%}分位） = {auto_thresh:.5f}")
            thresholds = [auto_thresh]
        else:
            thresholds = []
    else:
        thresholds = snr_thresholds if snr_thresholds else []
    
    merged_df = base_df.copy()
    bad_channels_all = {}
    
    for thresh in thresholds:
        retained_list = []
        bad_channels = {}
        
        for idx, row in base_df.iterrows():
            ch_id = row["Channel"]
            channel_retained = True
            for col in [c for c in row.index if c.startswith("SNR_")]:
                snr = row[col]
                wl = col.split("_")[1]
                if pd.isna(snr):
                    channel_retained = False
                    bad_channels.setdefault(ch_id, []).append(f"{wl}：NaN")
                elif snr < thresh:
                    channel_retained = False
                    bad_channels.setdefault(ch_id, []).append(f"{wl}：SNR={snr:.4f}")
            retained_list.append(channel_retained)
        
        colname = f"Retained({thresh})"
        merged_df[colname] = retained_list
        bad_channels_all[f"Thresh={thresh}"] = bad_channels
        
        if verbose:
            bad_count = sum(~pd.Series(retained_list))
            total = len(base_df)
            print("\n" + "-"*50)
            print(f"⚠️ 阈值 = {thresh} ：异常通道数量 {bad_count} / {total} ({bad_count/total:.2%})")
            print("-"*50)
            for ch_id in sorted(bad_channels, key=lambda c: int(re.search(r'\d+', c).group())):
                print(f"  - {ch_id}:")
                for reason in bad_channels[ch_id]:
                    reason_fmt = reason.replace("：", " nm: SNR = ")
                    print(f"     • {reason_fmt}")
            print()
    
    return merged_df, bad_channels_all, auto_thresholds




def analyze_channel_quality(
    raw_df: pd.DataFrame, 
    cv_threshold: float = None,         # === 修改点 === 默认为 None
    snr_threshold: float = None,        # === 修改点 === 默认为 None
    use_auto_threshold: bool = True,    # === 新增参数 ===
    return_type: str = "all",  # "all", "list", "dict"
    verbose: bool = False, 
    save_csv: bool = False, 
    file_prefix: str = None, 
    output_dir: str = "output/cv_snr"
):
    """
    综合分析原始光强数据的通道质量，基于CV和SNR判断异常通道。

    参数:
        raw_df: 原始DataFrame数据，仅包含通道列
        cv_threshold: 手动设置的CV阈值
        snr_threshold: 手动设置的SNR阈值
        use_auto_threshold: 是否启用自动计算阈值
        return_type: 返回格式，可选 "dict", "list", "all"
        verbose: 是否输出详细日志
        save_csv: 是否保存中间结果为CSV文件
        file_prefix: 输出文件名前缀
        output_dir: 输出CSV的文件夹路径

    返回:
        结果（字典/列表/多返回值），包括CV/SNR数据、坏通道信息、使用的阈值等
    """

    if save_csv:
        os.makedirs(output_dir, exist_ok=True)

    # CV阈值准备
    cv_thresholds = []
    if use_auto_threshold:
        if cv_threshold is not None:
            cv_thresholds = [cv_threshold]
        else:
            cv_thresholds = []  # 让 raw_CV 计算自动阈值
    else:
        # 不用自动阈值，必须有手动阈值
        if cv_threshold is not None:
            cv_thresholds = [cv_threshold]
        else:
            cv_thresholds = []

    # SNR阈值准备
    snr_thresholds = []
    if use_auto_threshold:
        if snr_threshold is not None:
            snr_thresholds = [snr_threshold]
        else:
            snr_thresholds = []  # 让 raw_SNR 计算自动阈值
    else:
        if snr_threshold is not None:
            snr_thresholds = [snr_threshold]
        else:
            snr_thresholds = []

    # 计算CV
    cv_df, bad_info_cv, auto_thresh_cv = raw_CV(
        raw_df,
        cv_thresholds=cv_thresholds,
        auto_threshold_quantile=0.95,
        use_auto_threshold=use_auto_threshold,
        verbose=verbose
    )
    if save_csv and file_prefix:
        cv_df.to_csv(os.path.join(output_dir, f"{file_prefix}_CV.csv"), index=False, encoding='utf-8-sig')
        if verbose:
            print(f"\n📌 自动计算CV阈值: {auto_thresh_cv}")

    # 计算SNR
    snr_df, bad_info_snr, auto_thresh_snr = raw_SNR(
        raw_df,
        snr_thresholds=snr_thresholds,
        auto_threshold_quantile=0.95,
        use_auto_threshold=use_auto_threshold,
        verbose=verbose
    )
    if save_csv and file_prefix:
        snr_df.to_csv(os.path.join(output_dir, f"{file_prefix}_SNR.csv"), index=False, encoding='utf-8-sig')
        if verbose:
            print(f"\n📌 自动计算SNR阈值: {auto_thresh_snr}")

    # 选用实际阈值：优先使用手动阈值，否则用自动阈值
    final_cv_thresh = cv_threshold if (cv_threshold is not None and not use_auto_threshold) else auto_thresh_cv
    final_snr_thresh = snr_threshold if (snr_threshold is not None and not use_auto_threshold) else auto_thresh_snr

    # 输出结构整理
    result = {
        "CV_Data": cv_df,
        "CV_Bad_Info": bad_info_cv,
        "Auto_CV_Threshold": auto_thresh_cv,
        "SNR_Data": snr_df,
        "SNR_Bad_Info": bad_info_snr,
        "Auto_SNR_Threshold": auto_thresh_snr,
        "Final_CV_Threshold": final_cv_thresh,
        "Final_SNR_Threshold": final_snr_thresh,
    }

    if return_type == "list":
        return [cv_df, bad_info_cv, auto_thresh_cv, snr_df, bad_info_snr, auto_thresh_snr]
    elif return_type == "dict":
        return result
    else:
        # all
        return cv_df, bad_info_cv, auto_thresh_cv, snr_df, bad_info_snr, auto_thresh_snr

