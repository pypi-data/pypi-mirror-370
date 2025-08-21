import fnirs_toolkit as fnirs

# 数据加载
raw_data = fnirs.load_raw_intensity("data/raw_sample.csv")

# 预处理流水线
od_data = fnirs.raw_to_od(raw_data)
od_resampled = fnirs.nirs_preprocess.resample_data(od_data, target_freq=10)
hb_data = fnirs.od_to_hb(od_resampled, wavelengths=[690, 830])
hb_filtered = fnirs.nirs_preprocess.filter_hb(hb_data, sfreq=10)

# 可视化
fnirs.plot_od(od_data, "sample_od")
fnirs.plot_hb(hb_data, "sample_hb", mode='both')

# 分析
brain_regions = fnirs.nirs_analysis.brain_region_integration(
    hb_data, region_map, hb_type='oxy'
)