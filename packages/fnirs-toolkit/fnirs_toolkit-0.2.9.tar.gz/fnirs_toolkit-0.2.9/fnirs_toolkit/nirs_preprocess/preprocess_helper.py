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


