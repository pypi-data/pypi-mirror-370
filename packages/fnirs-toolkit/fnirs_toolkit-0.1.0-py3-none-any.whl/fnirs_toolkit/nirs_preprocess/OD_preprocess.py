import logging
import os
import re
import numpy as np
import pandas as pd
from scipy.signal import butter, filtfilt
from raw_import import raw_intensity_import, raw_intensity_to_od
from OD_visualize import OD_visualize
from OD_beerlambert import OD_beerlambert, load_absorption
from HB_visualize import HB_visualize, HB_heatmap, HB_region_visualize
from HB_integration import HB_brain_integration, HB_time_avg
from HB_preprocess import HB_detrend, HB_TDDR, HB_filter
from helper import get_task_index, extract_channel_id, get_sfreq
from typing import Optional
import json

def log_section(title: str):
    logger.info("="*10 + f" {title} " + "="*10)

# ===== 运动伪迹检测 =====
def OD_detect_motion_artifacts(
    od_df: pd.DataFrame,
    method_list=("derivative", "amplitude"),
    derivative_thresh=0.2,
    amplitude_thresh=0.2,
    tMotion=0.5,
    tMask=0.2,
    tIncMan: Optional[np.ndarray] = None,
    interpolate=True,
    visualize=True,
    output_dir=None,
    sfreq: Optional[float] = None,
    min_bad_len=20
):
    """
    运动伪迹检测与修复（差分法/振幅法，逐通道独立检测和插值）。
    返回: 插值后数据, 每通道伪迹占比, 坏通道列表。
    """

    log_section("运动伪迹检测与修复")

    # ---- 内部函数：查找连续缺失区间 ----
    def find_bad_segments(bad_mask, min_length=20):
        segments = []
        T = len(bad_mask)
        in_bad = False
        for i in range(T):
            if bad_mask[i] and not in_bad:
                start = i
                in_bad = True
            if not bad_mask[i] and in_bad:
                end = i - 1
                if end - start + 1 >= min_length:
                    segments.append((start, end, end - start + 1))
                in_bad = False
        if in_bad:
            end = T - 1
            if end - start + 1 >= min_length:
                segments.append((start, end, end - start + 1))
        return segments

    # 1. 提取通道列
    chs = [c for c in od_df.columns if re.match(r'^CH\d+\(\d+(\.\d+)?\)$', c)]
    data = od_df[chs].astype(float)
    T, C = data.shape

    # 2. 差分法与振幅法运动伪迹检测
    d = data.values
    diff_d = np.diff(d, axis=0)
    if sfreq is None:
       fs = get_sfreq(od_df)
    else:
       fs = sfreq
    max_delay = int(round(tMotion * fs))

    max_diff = np.zeros_like(diff_d)
    for w in range(1, max_delay+1):
        shifted = np.abs(d[w:,:] - d[:-w,:])
        pad = np.zeros_like(diff_d)
        pad[: T-w, :] = shifted
        max_diff = np.maximum(max_diff, pad)

    # 4. 两种检测
    masks = []
    if "derivative" in method_list:
        der_mask = np.abs(diff_d) > derivative_thresh
        masks.append(der_mask)
        bad_chs_der = [chs[i] for i in np.where(der_mask.any(axis=0))[0]]
        bad_physical_chs_der = sorted(set([c.split('(')[0] for c in bad_chs_der]))
        logger.info(f"差分法: 标记 {len(bad_physical_chs_der)} 个通道, 共 {len(bad_chs_der)} 条数据列: {bad_chs_der}")
    if "amplitude" in method_list:
        amp_mask = max_diff > amplitude_thresh
        masks.append(amp_mask)
        bad_chs_amp = [chs[i] for i in np.where(amp_mask.any(axis=0))[0]]
        bad_physical_chs_amp = sorted(set([c.split('(')[0] for c in bad_chs_amp]))
        logger.info(f"振幅法: 标记 {len(bad_physical_chs_amp)} 个通道, 共 {len(bad_chs_amp)} 条数据列: {bad_chs_amp}")

    # 5. 合并运动伪迹mask
    buffer_pts = int(round(tMask * fs))
    bad_mask = np.zeros((T, C), dtype=bool)
    for c in range(C):
        combined_c = np.zeros(T-1, dtype=bool)
        if "derivative" in method_list:
            combined_c |= der_mask[:,c]
        if "amplitude" in method_list:
            combined_c |= amp_mask[:,c]
        bad_idx = np.where(combined_c)[0]
        for idx in bad_idx:
            t0 = idx + 1
            start = max(0, t0 - buffer_pts)
            end   = min(T-1, t0 + buffer_pts)
            bad_mask[start:end+1, c] = True

        # 6. 手工保留掩码
    if tIncMan is not None:
        tIncMan = np.asarray(tIncMan, bool)
        bad_mask[~tIncMan, :] = False

    # 7. 根据伪迹占比标记坏通道（不赋全列 NaN、不插值）
    # 计算每个通道的伪迹比例
    artifact_ratios = {ch: bad_mask[:, j].mean() for j, ch in enumerate(chs)}
    max_artifact_ratio = 0.25
    bad_chs = [ch for ch, r in artifact_ratios.items() if r > max_artifact_ratio]
    good_chs = [ch for ch in chs if ch not in bad_chs]

    if bad_chs:
        logger.warning(
            f"伪迹占比超{max_artifact_ratio*100:.0f}%的通道，共 {len(bad_chs)} 个: {bad_chs}"
        )
        if len(bad_chs) > 0.5 * len(chs):
            logger.error(
                "超过一半通道伪迹占比超阈值，建议人工核查原始数据质量！"
            )

    # 8. 仅对好通道做坏点 NaN 标记，坏通道原样保留
    clean_df = od_df.copy()
    for j, ch in enumerate(chs):
        if ch in good_chs:
            clean_df.loc[bad_mask[:, j], ch] = np.nan

    # 对坏通道的日志提示
    for ch in bad_chs:
        logger.warning(
            f"{ch} 被标记为坏通道 (伪迹占比={artifact_ratios[ch]:.2%})，"
            "数据原样保留，不参与 NaN 标记和插值。"
        )

    # 9. 对好通道做插值
    if interpolate and good_chs:
        nan_before = {ch: np.isnan(clean_df[ch].values).copy() for ch in good_chs}
        try:
            clean_df[good_chs] = clean_df[good_chs].interpolate(
                method='spline', order=3, limit_direction="both"
            )
            interp_method = '三次样条'
        except Exception as e:
            logger.warning("spline 插值出错，降级为线性插值: %s", e)
            clean_df[good_chs] = clean_df[good_chs].interpolate(
                method='linear', limit_direction="both"
            )
            interp_method = '线性'

        # 统计插值修复点
        channels_with_repair = set()
        data_columns_with_repair = []
        for ch in good_chs:
            nan_b = nan_before[ch]
            nan_a = np.isnan(clean_df[ch].values)
            repaired_idx = np.where(nan_b & ~nan_a)[0]
            if repaired_idx.size:
                channels_with_repair.add(ch.split('(')[0])
                data_columns_with_repair.append(ch)
                logger.info(
                    # f"{ch} 用{interp_method}插值修复 {len(repaired_idx)} 个点，索引: {repaired_idx.tolist()}"
                    f"{ch} 用{interp_method}插值修复 {len(repaired_idx)} 个点"
                )
        logger.info(
            f"插值修复涉及 {len(channels_with_repair)} 个物理通道，"
            f"{len(data_columns_with_repair)} 条数据列。"
        )

    # 10. 只输出好通道的连续缺失片段
    for ch in good_chs:
        ch_nan_mask = np.isnan(clean_df[ch].values)
        segments = find_bad_segments(ch_nan_mask, min_length=min_bad_len)
        for start, end, length in segments:
            print(f"[{ch}] 连续缺失区间: {start} ~ {end} (共{length}点)")

    # 11. 返回结果
    return clean_df, artifact_ratios, bad_chs

# ===== 低通滤波  =====
def OD_filter(od_df, sfreq, cutoff=0.1, order=3):
    """
    对fNIRS光密度(OD)数据进行低通滤波。

    Parameters
    ----------
    od_df : pandas.DataFrame
        包含通道光密度数据的DataFrame，每列一个通道。
    sfreq : float
        采样率（Hz）。
    cutoff : float, 默认0.1
        低通滤波截止频率（Hz），即保留此频率以下的信号。
    order : int, 默认3
        Butterworth滤波器的阶数。

    Returns
    ----------
    od_df : pandas.DataFrame
        完成低通滤波的数据框。
    """
    log_section(f"低通滤波：cutoff={cutoff}Hz, order={order}")
    # 正则表达式选择通道列名
    CH_cols = [col for col in od_df.columns if extract_channel_id(col) is not None]

    # 创建低通Butterworth滤波器
    nyq = sfreq / 2
    b, a = butter(order, cutoff / nyq, btype='low')

    # 提取数据并进行滤波
    data = od_df[CH_cols].values
    filt = filtfilt(b, a, data, axis=0)
    od_df[CH_cols] = filt

    return od_df

# ===== 根据时间戳截取光密度数据  =====
def OD_cut(od_df, index_range):
    """
    根据时间戳截取光密度数据

    Parameters
    ----------
    od_df: pd.DataFrame
        原始光密度数据，包含通道和非通道列。
    start_time: float
        开始时间（秒）
    end_time: float
        结束时间（秒）

    Returns
    ----------
    pd.DataFrame
        截取后的光密度数据
    """
    if index_range is None:
        raise ValueError("index_range 不能为 None")
    if 'Probe1' not in od_df.columns:
        raise ValueError("数据中必须包含 'Probe1' 列以进行时间区间筛选")
    
    # 获取需要开始和结束的 index 位置
    start_probe, end_probe = index_range

    od_df = od_df.loc[(od_df["Probe1"] >= start_probe) & (od_df["Probe1"] <= end_probe)].copy()

    return od_df



# —— 日志配置 —— 
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(levelname)-8s %(message)s")
logger = logging.getLogger(__name__)

# —— 配置参数 —— 
file_id        = "王敬枝_左患侧下肢运动临床测查方案_20250207145917"
input_dir      = "raw_data"
output_dir     = "output/resample"
sfreq          = 10.0
detect_artifact= True

artifact_params = {
    "method_list": ("derivative","amplitude"),
    "derivative_thresh": 0.2,
    "amplitude_thresh": 0.2,
    "tMotion": 0.5,
    "tMask": 0.2,
    "interpolate": True,
    "visualize": True
}

od_filter_cutoff = 0.1
od_filter_order  = 3

wavelengths     = [690,830]
bl_base         = 'base10'
path_corrected  = True
dist            = 0.03
dpf_corrected   = True
dpf             = 6.0


# —— 载入脑区映射 —— 
with open("data/channel_region_map.json", "r", encoding="utf-8") as f:
    brain_region_map = json.load(f)

# —— 1. 原始强度导入 & OD 转换 —— 
raw_df, _ = raw_intensity_import(os.path.join(input_dir, f"{file_id}.csv"))
chs = [c for c in raw_df.columns if re.match(r'^CH\d+\(\d+(\.\d+)?\)$', c)]
meta  = raw_df.drop(columns=chs)
od_vals = raw_intensity_to_od(raw_df[chs])
od_df   = pd.concat([meta, od_vals], axis=1)

# —— 2. 原始 OD 可视化 （可选） —— 
OD_visualize(od_df, file_id, output_dir, "Raw OD")

# —— 3. 运动伪迹检测 —— 
if detect_artifact:
    od_df, art_ratios, bad_chs = OD_detect_motion_artifacts(
        od_df, sfreq=sfreq, **artifact_params
    )

# —— 4. 低通滤波 —— 
od_df = OD_filter(od_df, sfreq, cutoff=od_filter_cutoff, order=od_filter_order)
OD_visualize(od_df, file_id, output_dir, "Filtered OD")

# —— 5. 按 Probe1 截取 Task 段 —— 
# task2_df = OD_cut(od_df, index_range=(1000, 4600))        #  假设 Task2 的 Probe1 范围是 [1000, 4600]

# —— 6. OD → HbO/HbR —— 
hb_df  = OD_beerlambert(
    od_df, wavelengths, bl_base,
    path_corrected, dist,
    dpf_corrected, dpf
)


logger.info("处理完成！")
