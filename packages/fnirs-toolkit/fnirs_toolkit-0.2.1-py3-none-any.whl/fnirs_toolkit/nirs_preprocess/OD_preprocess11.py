import logging
import os
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from scipy.signal import butter, filtfilt, resample, welch
from scipy.ndimage import uniform_filter1d
from sklearn.decomposition import PCA
from nirs_io.raw_io import raw_intensity_import
from nirs_io.converters import od_beerlambert, raw_intensity_to_od
# from raw import raw_CV, raw_SNR
from nirs_plot.od_plot import od_plot
from typing import Optional
from ..utils.helper import extract_channel_id, get_channel_columns


from nirs_io.hb_io import hb_import

from nirs_analysis.integration import hb_time_average
from nirs_plot.od_plot import od_plot
from nirs_analysis.integration import hb_brain_integration
from nirs_plot.hb_plot import hb_plot, hb_heatmap, hb_region_plot
import pandas as pd


# ——————————————————————————————————————————————————
# —— 日志配置 —— 
# ——————————————————————————————————————————————————
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger(__name__)

def log_section(title: str):
    logger.info("="*10 + f" {title} " + "="*10)

def plot_cv_snr_distribution(raw_df, sfreq,
                             file_id="demo",
                             output_dir="qc_dist",
                             bins=40,
                             cv_thr=None,
                             snr_thr=None):
    """
    绘制 CV 与 SNR 的直方图 + 箱线图
    ──────────────────────────────────────────
      • 若 cv_thr / snr_thr 为空，则自动用
        CV 的 95% 分位、SNR 的 5% 分位作硬阈值。
      • 绿色底色 = 合格区；红虚线 = 软阈值 (same 被试分位)。
    """
    os.makedirs(output_dir, exist_ok=True)

    # ------------ 计算 -------------
    cv_df, _, _  = raw_CV(raw_df, use_auto_threshold=False)
    snr_df, _, _ = raw_SNR(raw_df, use_auto_threshold=False)

    cv_vals  = cv_df.iloc[:, 1:].astype(float).values.ravel()
    snr_vals = snr_df.iloc[:, 1:].astype(float).values.ravel()

    # 分位数
    cv_q   = np.percentile(cv_vals,  [5,25,50,75,95])
    snr_q  = np.percentile(snr_vals, [5,25,50,75,95])
    cv_soft, snr_soft = cv_q[4], snr_q[0]          # 软阈值
    cv_thr  = cv_thr  if cv_thr  is not None else cv_soft
    snr_thr = snr_thr if snr_thr is not None else snr_soft

    # ------------ 直方图 -------------
    fig_h, (ax_cv_h, ax_snr_h) = plt.subplots(1, 2, figsize=(11, 4))

    # CV-hist
    ax_cv_h.hist(cv_vals, bins=bins, color="#4C72B0")
    ax_cv_h.axvspan(0, cv_thr, color="#A5D6A7", alpha=0.25)          # 合格区
    ax_cv_h.axvline(cv_soft, ls='--', color='red',
                    label=f'软阈 95%={cv_soft*100:.1f}%')
    ax_cv_h.set_xlabel("CV (%)"); ax_cv_h.set_ylabel("通道数")
    ax_cv_h.set_title("CV 直方图"); ax_cv_h.legend(fontsize=8)

    # SNR-hist
    ax_snr_h.hist(snr_vals, bins=bins, color="#55A868")
    ax_snr_h.axvspan(snr_thr, snr_vals.max(), color="#A5D6A7", alpha=0.25)
    ax_snr_h.axvline(snr_soft, ls='--', color='red',
                     label=f'软阈 5%={snr_soft:.1f} dB')
    ax_snr_h.set_xlabel("SNR (dB)"); ax_snr_h.set_title("SNR 直方图")
    ax_snr_h.legend(fontsize=8)

    fig_h.suptitle(f"{file_id} | CV & SNR 直方图", fontsize=14)
    fig_h.tight_layout(rect=[0,0,1,0.95])
    fig_h.savefig(os.path.join(output_dir, f"{file_id}_cv_snr_hist.png"), dpi=300)
    plt.close(fig_h)

    # ------------ 箱线图 -------------
    fig_b, (ax_cv_b, ax_snr_b) = plt.subplots(1,2, figsize=(10,4), constrained_layout=True, gridspec_kw={'wspace':0.35})

    # CV-box
    ax_cv_b.boxplot(cv_vals, vert=True, showfliers=False)
    ax_cv_b.set_ylabel("CV (%)"); ax_cv_b.set_title("CV 箱线图")
    ax_cv_b.axhspan(0, cv_thr, facecolor="#A5D6A7", alpha=0.25)
    ax_cv_b.axhline(cv_soft, ls='--', color='red',
                    label=f'软阈 95%={cv_soft*100:.1f}%')
    ax_cv_b.legend(fontsize=8, loc='upper right')

    # SNR-box
    ax_snr_b.boxplot(snr_vals, vert=True, showfliers=False)
    ymax = max(snr_vals.max(), snr_thr)*1.05
    ax_snr_b.set_ylim(top=ymax)
    ax_snr_b.set_ylabel("SNR (dB)"); ax_snr_b.set_title("SNR 箱线图")
    ax_snr_b.axhspan(snr_thr, ymax, facecolor="#A5D6A7", alpha=0.25)
    ax_snr_b.axhline(snr_soft, ls='--', color='red',
                     label=f'软阈 5%={snr_soft:.1f} dB')
    ax_snr_b.legend(fontsize=8, loc='upper right')

    fig_b.suptitle(f"{file_id} | CV & SNR 箱线图", fontsize=14)
    
    fig_b.savefig(os.path.join(output_dir, f"{file_id}_cv_snr_box.png"), dpi=300)
    plt.close(fig_b)

    # ------------ 控制台反馈 -------------
    print("CV 分位 [5,25,50,75,95] =", np.round(cv_q,3))
    print("SNR 分位 [5,25,50,75,95] =", np.round(snr_q,1))
    print(f"图已保存至 {output_dir}\n")

    return dict(cv_thr=cv_thr, snr_thr=snr_thr,
                cv_percentiles=cv_q, snr_percentiles=snr_q)




# ===== 1. 原始光强 QC ＆ 光密度转换 =====
logger = logging.getLogger(__name__)

def exclude_channels_raw(raw_df, sfreq,
                         cv_thresh=None,
                         snr_thresh=None,
                         use_auto=True,
                         visualize=True):
    """
    标记并输出坏通道的 CV/SNR 信息，不删除任何列。
    参数:
      raw_df      : 原始光强 DataFrame
      sfreq       : 采样率（本函数不实际用到，但保留签名）
      cv_thresh   : 硬阈值 CV 上限（例如 0.075），若 None 则取该被试 CV 的 95% 分位
      snr_thresh  : 硬阈值 SNR 下限（dB），若 None 则取该被试 SNR 的 5% 分位
      use_auto    : 是否让 raw_CV/raw_SNR 自适应阈值（此处固定 False，确保拿到所有数值）
      visualize   : 保留签名（本函数不画图）
    返回:
      raw_df         : 直接原样返回
      bad_cv         : List[(channel_id, wavelength_nm, cv_value)]
      bad_snr        : List[(channel_id, wavelength_nm, snr_value)]
      cv_used_thresh : 最终生效的 CV 阈值
      snr_used_thresh: 最终生效的 SNR 阈值
    """
    log_section("1. 原始光强 QC ＆ 光密度转换 ")
    
    # 使用 helper 函数获取通道列
    channel_cols = get_channel_columns(raw_df)
    meta_cols = [c for c in raw_df.columns if c not in channel_cols]
    
    # 1. 全量计算 CV / SNR
    cv_df, _, _  = raw_CV(raw_df, use_auto_threshold=False)
    snr_df, _, _ = raw_SNR(raw_df, use_auto_threshold=False)

    # 2. 提取所有数值，算“软阈值”
    cv_vals  = cv_df.iloc[:,1:].astype(float).values.ravel()
    snr_vals = snr_df.iloc[:,1:].astype(float).values.ravel()
    cv_soft95  = np.percentile(cv_vals, 95)
    snr_soft05 = np.percentile(snr_vals, 5)

    # 3. 硬阈值优先，否则用软阈值
    cv_used_thresh  = cv_thresh  if cv_thresh  is not None else cv_soft95
    snr_used_thresh = snr_thresh if snr_thresh is not None else snr_soft05

    # 4. 遍历所有通道×波长，标记超阈值条目
    bad_cv, bad_snr = [], []

    # 假定第一列是 'Channel'，后面列名形如 'CV_690','CV_830'
    wl_cv = []
    for col in cv_df.columns[1:]:
        m = re.search(r'_(\d+)', col)
        if not m:
            raise ValueError(f"Unexpected CV column name: {col}")
        wl_cv.append(int(m.group(1)))

    # 同理 SNR 列名形如 'SNR_690','SNR_830'
    wl_snr = []
    for col in snr_df.columns[1:]:
        m = re.search(r'_(\d+)', col)
        if not m:
            raise ValueError(f"Unexpected SNR column name: {col}")
        wl_snr.append(int(m.group(1)))

    # 根据阈值筛出坏通道
    for _, row in cv_df.iterrows():
        cid = row['Channel']
        for idx, wl in enumerate(wl_cv):
            val = float(row.iloc[idx+1])
            if val > cv_used_thresh:
                bad_cv.append((cid, wl, val))
    for _, row in snr_df.iterrows():
        cid = row['Channel']
        for idx, wl in enumerate(wl_snr):
            val = float(row.iloc[idx+1])
            if val < snr_used_thresh:
                bad_snr.append((cid, wl, val))


    # 5. 日志打印
    logger.info(f"生效阈值：CV ≤ {cv_used_thresh*100:.2f}%  (软阈95%={cv_soft95*100:.2f}%)")
    logger.info(f"生效阈值：SNR ≥ {snr_used_thresh:.1f} dB  (软阈5%={snr_soft05:.1f} dB)")
    logger.info(f"坏 CV 条目共 {len(bad_cv)} 条：")
    for cid, wl, cvv in bad_cv:
        logger.info(f"  - {cid}({wl}nm): CV={cvv:.4f}")
    logger.info(f"坏 SNR 条目共 {len(bad_snr)} 条：")
    for cid, wl, snrv in bad_snr:
        logger.info(f"  - {cid}({wl}nm): SNR={snrv:.1f} dB")

    # 6. 返回原始 DF + 标记列表 + 阈值
    return raw_df, bad_cv, bad_snr, cv_used_thresh, snr_used_thresh


# ===== 2. OD 重采样 =====
def OD_resample(
    od_df: pd.DataFrame,
    sfreq: float,
    target_freq: float = 10,
    filter_cutoff: Optional[float] = None,
    filter_order: int = 4
) -> pd.DataFrame:
    """
    光密度数据滤波与重采样处理函数。

    - 若原始采样率 > 目标采样率：进行滤波 + 降采样。
    - 若原始采样率 == 目标采样率：仅滤波。
    - 若原始采样率 ∈ [5Hz, 10Hz)：仅滤波，不重采样。
    - 若原始采样率 < 5Hz：不建议处理，直接返回原始数据。
    """
    log_section("2. 光密度数据的滤波与重采样")

    # 1. 确定抗混叠滤波截止
    if filter_cutoff is None:
        filter_cutoff = target_freq / 2

    # 2. 判断是否需要降采样
    if sfreq > target_freq:
        do_resample = True
    elif sfreq >= 5:
        do_resample = False
    else:
        print(f"❌ 原始采样率 {sfreq:.2f}Hz 太低，直接返回原始数据")
        return od_df.copy()

    # 3. 设计 Butterworth 低通
    nyquist = sfreq / 2
    if filter_cutoff >= nyquist:
        filter_cutoff = 0.8 * nyquist
        print(f"⚠️ filter_cutoff 超过 Nyquist，已调整为 {filter_cutoff:.2f}Hz")
    norm_cutoff = filter_cutoff / nyquist
    b, a = butter(filter_order, norm_cutoff, btype='low')

    # 4. 分离通道／非通道列
    channel_cols = [c for c in od_df.columns if re.match(r'^CH\d+\(', c)]
    non_channel_cols = [c for c in od_df.columns if c not in channel_cols]

    # 5. 先对通道数据做双向滤波
    filtered_data = filtfilt(b, a, od_df[channel_cols].values, axis=0)

    if not do_resample:
        # 只滤波
        od_df[channel_cols] = filtered_data
        print(f"仅完成滤波，采样率保持 {sfreq:.2f}Hz")
        return od_df

    # 6. 降采样：先在通道上
    n_samples = int(len(od_df) * target_freq / sfreq)
    resampled_ch = resample(filtered_data, n_samples, axis=0)
    df_ch = pd.DataFrame(resampled_ch, columns=channel_cols)

    # 7. 生成新的 Time 列
    res_info = {}
    if "Time" in non_channel_cols:
        # 取原始第一行的时间字符串
        t0_str = str(od_df["Time"].iloc[0])
        # 尝试各种常见格式
        for fmt in ("%H:%M:%S.%f","%H:%M:%S","%M:%S.%f","%M:%S"):
            try:
                t0_dt = datetime.strptime(t0_str, fmt)
                break
            except ValueError:
                continue
        else:
            raise ValueError(f"无法解析时间格式：{t0_str}")
        dt = 1.0 / target_freq
        # 构造新的时间戳列表
        res_info["Time"] = [
            (t0_dt + timedelta(seconds=i*dt)).strftime("%H:%M:%S.%f")[:-3]
            for i in range(n_samples)
        ]

    # 8. 处理其它非通道列
    for col in non_channel_cols:
        if col == "Time":
            continue

        series = od_df[col]
        key = col.lower()

        if key.startswith("probe"):
            # —— Probe 列：插值后四舍五入为整数
            xi = np.linspace(0, 1, len(series))
            xo = np.linspace(0, 1, n_samples)
            vals = np.interp(xo, xi, series.astype(float))
            res_info[col] = np.round(vals).astype(int).tolist()

        elif key.startswith("mark"):
            # —— 打点列：保留所有非空事件，把它们贴到最近的新时间格点
            mark_new = [0] * n_samples
            events = od_df.loc[series.notnull() & (series != 0), ["Time", col]]
            # 预先把新时间戳解析为 datetime
            new_times = pd.to_datetime(res_info["Time"], format="%H:%M:%S.%f")
            for _, ev in events.iterrows():
                try:
                    orig_t = pd.to_datetime(ev["Time"], format="%H:%M:%S.%f")
                except:
                    orig_t = pd.to_datetime(ev["Time"], format="%H:%M:%S")
                j = np.argmin(np.abs(new_times - orig_t))
                mark_new[j] = ev[col]
            res_info[col] = mark_new

        elif pd.api.types.is_numeric_dtype(series):
            # —— 其它数值列：线性插值
            xi = np.linspace(0, 1, len(series))
            xo = np.linspace(0, 1, n_samples)
            res_info[col] = np.interp(xo, xi, series.astype(float)).tolist()

        else:
            # —— 其它文本列：全部填第一个值
            res_info[col] = [series.iloc[0]] * n_samples

    # 9. 拼回完整表格并保持原列顺序
    df_info = pd.DataFrame(res_info)
    full = pd.concat([df_info, df_ch], axis=1)[od_df.columns]

    print(f"滤波+降采样完成：{sfreq:.2f}Hz → {target_freq}Hz，共 {n_samples} 行")
    return full


# ===== 3. 运动伪迹检测 =====
def OD_detect_motion_artifacts(od_df,
                               method_list=("derivative","std","amplitude"),
                               derivative_thresh=0.5,
                               std_window=10, std_thresh=0.2,
                               amplitude_thresh=1.0,
                               interpolate=True, visualize=True,
                               output_dir=None):
    log_section("3. 运动伪迹检测与修复")

    # 先找出所有通道列（CHx(λ)）
    chs = [c for c in od_df.columns if re.match(r'^CH\d+\(', c)]
    data = od_df[chs]  # 仅通道数据

    masks = []
    # 差分法                                
    # 通过计算相邻采样点的一阶差分，当信号突变幅度超过阈值时，认为发生了快速运动伪迹。
    if "derivative" in method_list:
    # HOMER2 软件包中的 hmrMotionArtifact 就采用了类似的“slope‐based”检测，推荐的阈值约 0.1 OD 单位／样本（在 10 Hz 采样下相当于 0.01 OD/ms）
        diff_mask = data.diff().abs() > derivative_thresh
        masks.append(diff_mask)
        bad_count = (diff_mask.mean(axis=0) > 0.1).sum()
        logger.info(f"差分法: 剔除通道数≈{bad_count}")
    # 滑动标准差法（Sliding‐window STD）        
    # 先计算窗口内（如 10 个点≈1 s）信号的平滑一阶差分的标准差，再与整个通道的全局标准差做比例比较。当局部波动远大于背景抖动时，判定为运动伪迹。
    if "std" in method_list:
        dif = np.abs(np.diff(data.values, axis=0, prepend=data.values[0:1]))
        smooth = uniform_filter1d(dif, size=std_window, axis=0)
        std_mask = smooth > std_thresh * np.std(data.values, axis=0)
        std_mask = pd.DataFrame(std_mask, columns=chs)
        masks.append(std_mask)
        bad_count = (std_mask.mean(axis=0) > 0.05).sum()
        logger.info(f"滑动std法: 剔除通道数≈{bad_count}")
    # 振幅阈值法（Amplitude threshold）     
    # 直接标记相邻两点振幅差超过某一绝对值（如 0.3 OD），快速筛出大动作导致的剧烈振幅跳变
    if "amplitude" in method_list:
        amp_mask = data.diff().abs() > amplitude_thresh
        masks.append(amp_mask)
        bad_count = (amp_mask.mean(axis=0) > 0.05).sum()
        logger.info(f"振幅法: 剔除通道数≈{bad_count}")
    # 合并
    combined_mask = np.logical_or.reduce([m.values for m in masks])

    # 3. 只把通道列置为 NaN
    clean = od_df.copy()
    clean_ch = clean[chs].copy()
    clean_ch.values[combined_mask] = np.nan
    clean[chs] = clean_ch

    # 4. 插值
    if interpolate:
        clean[chs] = clean[chs].interpolate(limit_direction="both")
    return clean, combined_mask

# ===== 4. 带通滤波 (0.01–0.2Hz) =====
def OD_hemo_bandpass(od_df, sfreq, low=0.01, high=0.2, order=3):
    log_section("4. Hemodynamic 带通滤波")
    logger.info(f"频段: {low}-{high}Hz, 阶数={order}")
    chs = [c for c in od_df.columns if re.match(r'^CH\d+\(', c)]
    nyq = sfreq/2
    b1,a1 = butter(order, high/nyq, btype='low')
    b2,a2 = butter(order, low/nyq, btype='high')
    data = od_df[chs].values
    filt = filtfilt(b1,a1, data, axis=0)
    filt = filtfilt(b2,a2, filt, axis=0)
    od_df[chs] = filt
    logger.info("带通完成\n")
    return od_df

# ===== 5. LF 去噪：PCA & 全局平均 =====
def lf_denoise_pca(od_df, n_comp=1):
    """
    低频 PCA 去噪，先对 NaN 做插值，然后再做 PCA。
    """
    log_section("5. LF De-Noising: PCA")
    # 1. 找到所有通道列
    chs = [c for c in od_df.columns if re.match(r'^CH\d+\(', c)]
    df_ch = od_df[chs].copy()

    # 2. 对 NaN 做插值，然后如果两端还有 NaN 再做前后填充
    df_ch = df_ch.interpolate(limit_direction='both', axis=0) \
                   .fillna(method='bfill', axis=0) \
                   .fillna(method='ffill', axis=0)

    # 3. 再次检查是否还有 NaN，如果有就报错
    if df_ch.isna().any().any():
        raise ValueError("lf_denoise_pca: 插值和填充后仍存在 NaN，请检查数据。")

    # 4. PCA 去噪
    X = df_ch.values
    mu = X.mean(0)
    Xc = X - mu
    pca = PCA(n_components=n_comp).fit(Xc)
    logger.info(f"PCA 删除前{n_comp}主成分, 贡献率={pca.explained_variance_ratio_}")

    recon = pca.transform(Xc).dot(pca.components_)
    clean = Xc - recon + mu

    od_df.loc[:, chs] = clean
    logger.info("PCA去噪完成\n")
    return od_df




def lf_denoise_global_avg(od_df, sfreq, corr_thresh=0.37, max_delay=5):
    log_section("5. LF De-Noising: Global Avg")
    chs = [c for c in od_df.columns if re.match(r'^CH\d+\(', c)]
    X = od_df[chs].values; gm = X.mean(1)
    lags = np.arange(-int(max_delay*sfreq), int(max_delay*sfreq)+1)
    removed = []
    for j, c in enumerate(chs):
        sig = X[:,j]
        corrs = [np.corrcoef(sig, np.roll(gm,lag))[0,1] for lag in lags]
        i = np.argmax(np.abs(corrs))
        if abs(corrs[i])>corr_thresh:
            beta = sig.dot(np.roll(gm,lags[i])) / gm.dot(np.roll(gm,lags[i]))
            X[:,j] = sig - beta*np.roll(gm,lags[i])
            removed.append((c, corrs[i], lags[i]))
    od_df[chs] = X
    logger.info(f"全局平均去噪, 处理通道数={len(removed)}")
    for c, corr, lag in removed:
        logger.info(f"  • {c}: corr={corr:.2f}, lag={lag}")
    logger.info("")
    return od_df

# ===== 主流程 =====
def OD_process_and_preprocess(
    file_id, input_dir=".", output_dir="output/",
    target_freq=10, cv_thresh=0.075, snr_thresh=6,
    use_auto=True, detect_artifact=False, artifact_params=None,
    hemo_band=(0.01,0.2), hemo_order=3,
    output_csv=True, visualize=True
):
    os.makedirs(output_dir, exist_ok=True)
    log_section("开始 OD 预处理主流程")
    raw_path = os.path.join(input_dir, f"{file_id}.csv")
    raw_df, sfreq = raw_intensity_import(raw_path)

    raw_df, bad_cv, bad_snr, cv_thr, snr_thr = exclude_channels_raw(
                                                                    raw_df, sfreq,
                                                                    cv_thresh=0.075,    # 或传 None 使用软分位
                                                                    snr_thresh=6,      # 或 None 使用软分位
                                                                    use_auto=False,
                                                                    visualize=False
                                                                )
    # 只保留通道列，丢掉其它非通道数据
    channel_cols = [c for c in raw_df.columns if re.match(r'^CH\d+\(\d+(\.\d+)?\)$', c)]
    meta_cols = [c for c in raw_df.columns if c not in channel_cols]
    
    # ——— 1. QC 分布图（只用通道光强） ———
    plot_cv_snr_distribution(
        raw_df[channel_cols], sfreq,
        file_id=file_id,
        output_dir=os.path.join(output_dir, "qc_dist"),
        cv_thr=cv_thresh,
        snr_thr=snr_thresh
    )

    # ——— 2. OD 转换（只用通道光强） ———
    od_chan = raw_intensity_to_od(raw_df[channel_cols])
    logger.info(f"   转换到光密度后 shape={od_chan.shape}\n")

    # ——— 3. 拼接 meta + OD，供重采样使用 ———
    od_full = pd.concat(
        [raw_df[meta_cols].reset_index(drop=True),
         od_chan.reset_index(drop=True)],
        axis=1
    )[ meta_cols + channel_cols ]

    # 重采样
    od_rs = OD_resample(od_full, sfreq, target_freq)

    if output_csv:
        rs_path = os.path.join(output_dir, f"{file_id}_resampled.csv")
        od_rs.to_csv(rs_path, index=False)
        logger.info(f"重采样结果已保存至 {rs_path}")
    
    if visualize:
        OD_visualize(od_full, file_id, output_dir, "OD Raw", "od_raw")
        OD_visualize(od_rs, file_id, output_dir, f"OD RS {target_freq}Hz", "od_rs")
    if detect_artifact:
        od_mc, _ = OD_detect_motion_artifacts(od_rs, **(artifact_params or {}))
    else:
        od_mc = od_rs.copy()
    
    od_hemo = OD_hemo_bandpass(od_mc, target_freq, *hemo_band, order=hemo_order)


    od_pca = lf_denoise_pca(od_hemo, n_comp=1)
    od_glb = lf_denoise_global_avg(od_hemo, sfreq=target_freq,
                                   corr_thresh=0.37, max_delay=5)
    
    if visualize:
        log_section("6. Hemodynamic Visualization")
        OD_visualize(od_hemo, file_id, output_dir, "Hemodynamic", "hemo")
        logger.info(f"Hemo 图像已保存至 {os.path.join(output_dir, f'{file_id}_hemo.png')}\n")

    if output_csv:
        od_hemo.to_csv(os.path.join(output_dir, f"{file_id}_hemo.csv"), index=False)
        logger.info(f"Hemo CSV 已保存至 {output_dir}\n")
    return {
        "od_resampled": od_rs,
        "od_hemo": od_hemo,
        "od_pca": od_pca,
        "od_global": od_glb
    }

# ===== 示例调用 =====
if __name__=="__main__":
    result = OD_process_and_preprocess(
        # file_id="翁羽_自定义方案1_20241104142325",
        # file_id = "王晓文_自定义方案1_20241031091304",
        # file_id = "40288781841d31b601841d4a54030114",
        file_id = "刘0001",
        # file_id = "0704",
        # file_id = "刘0002",
        input_dir="raw_data",
        output_dir="output/resample",
        target_freq=10,
        detect_artifact=True,
        artifact_params={"derivative_thresh":0.5, "std_thresh":0.2,
                         "amplitude_thresh":1.0, "interpolate":True,
                         "visualize":True}
    )
