"""
fNIRS 血红蛋白浓度可视化模块

本模块专门用于血红蛋白浓度变化数据的可视化分析，提供：

核心功能：
- 多通道血氧波形图：同时显示HbO2和HbR的时间序列变化
- 空间激活热图：基于通道坐标的血氧浓度空间分布插值图
- 脑区平均信号图：按脑功能区域聚合的平均血氧信号
- 任务相关分析图：叠加任务标记的激活模式分析

技术特点：
- 双信号对比：HbO2（红色）与HbR（蓝色）的对比显示
- 径向基函数插值：使用RBF实现平滑的空间插值热图
- 自适应色阶：根据数据分布自动调整颜色映射范围
- 中文字体支持：完整的中文标题和标签显示支持

可视化类型：
- 通道级波形图：每个通道的详细时间序列
- 空间热图：基于通道位置的激活强度分布
- 脑区聚合图：功能区域的平均信号变化
- 统计分析图：激活显著性和效应量可视化

数据兼容性：
- 支持路径长度校正前后的数据（mM·mm 或 mM 单位）
- 兼容不同采样率的时间序列数据
- 支持任意数量通道的数据集

主要函数：
- HB_plot: 绘制血红蛋白浓度波形图
- HB_heatmap: 绘制空间激活热图
- HB_region_plot: 绘制脑区平均信号图

使用示例：
    >>> from fnirs_toolkit.nirs_plot.hb_plot import HB_plot, HB_heatmap
    >>> # 绘制双信号波形图
    >>> HB_plot(hb_data, "subject_01", "output/", mode='both', add_task=True)
    >>> # 绘制激活热图
    >>> HB_heatmap(channel_df, hb_data, "subject_01", signal_type="oxy")
"""

import matplotlib.pyplot as plt
import matplotlib
import seaborn as sns
import pandas as pd
import numpy as np
from scipy.interpolate import RBFInterpolator
import os
from ..utils.helper import get_sfreq


script_dir = os.path.dirname(os.path.abspath(__file__))


# 设置全局字体为中文可用字体（根据系统选择）
matplotlib.rcParams['font.family'] = 'SimHei'  # Windows：黑体
# matplotlib.rcParams['font.family'] = 'Microsoft YaHei'  # 或者微软雅黑
# matplotlib.rcParams['font.family'] = 'STHeiti'  # Mac 常用字体
# matplotlib.rcParams['font.family'] = 'Arial Unicode MS'  # 跨平台备用

# 避免负号无法显示
matplotlib.rcParams['axes.unicode_minus'] = False


def hb_plot(
        hb_df, file_name, output_path, 
        title=None, 
        mode='both', 
        path_corrected=False,
        add_task=False, 
        time_range=None):
    """
    可视化 HbO2 / HbR 波形图

    参数
    ----------
    hb_df : pd.DataFrame
        包含 CH 通道数据的 DataFrame，列名应包含 '(oxy)' 或 '(deOxy)'
    file_name : str
        文件或样本标识符，用于输出文件命名
    output_path : str
        图像保存路径
    title : str, optional
        图像主标题，默认使用 file_name
    mode : str, optional
        可选 'oxy', 'deoxy', 'both'，控制绘制内容。默认 'both'
    path_corrected : bool, optional
        如果为 True，y 轴单位为 'mM'，否则为 'mM·mm'
    add_task : bool, optional
        是否在图中添加任务开始标注（Mark != 0 的点）
    time_range : list or None, optional
        [start_time, end_time]，仅绘制该范围的数据
    """
    unit = "mM" if path_corrected else "mM·mm"
    ylabel = f"ΔConcentration ({unit})"

    # 获取采样率
    sfreq = get_sfreq(hb_df)

    # 如果 time_range 有值，做时间过滤
    if time_range is not None:
        start_time, end_time = time_range
        start_probe = int(start_time * sfreq) + 1
        end_probe = int(end_time * sfreq) + 1

        if 'Probe1' not in hb_df.columns:
            raise ValueError("数据中必须包含 'Probe1' 列以进行时间区间筛选")

        hb_df = hb_df.loc[(hb_df["Probe1"] >= start_probe) & (hb_df["Probe1"] <= end_probe)].copy()

    if mode == 'both':
        # 配对通道
        oxy_cols = [col for col in hb_df.columns if '(oxy)' in col]
        paired_channels = []
        for oxy_col in oxy_cols:
            base = oxy_col.replace("(oxy)", "")
            deoxy_col = f"{base}(deOxy)"
            if deoxy_col in hb_df.columns:
                paired_channels.append((oxy_col, deoxy_col))
    else:
        # 单独通道
        if mode == 'oxy':
            plot_columns = [col for col in hb_df.columns if '(oxy)' in col]
        elif mode == 'deOxy':
            plot_columns = [col for col in hb_df.columns if '(deOxy)' in col]
        else:
            raise ValueError("mode 必须为 'oxy'、'deOxy' 或 'both'")
        paired_channels = [(col,) for col in plot_columns]

    if add_task:
        # 任务时间点 (只计算一次)
        task_points = []
        if 'Mark' in hb_df.columns:
            task_points = (
                hb_df.loc[hb_df['Mark'] != "0", 'Probe1']
                .drop_duplicates()
                .sort_values()
                .values
            )
            # 限制数量
            max_marks = 50
            if len(task_points) > max_marks:
                print(f"⚠️ 任务标注点太多（{len(task_points)}），仅绘制前{max_marks}个")
                task_points = task_points[:max_marks]

    # 图像排列
    cols_per_row = 8
    rows = (len(paired_channels) + cols_per_row - 1) // cols_per_row
    fig, axes = plt.subplots(rows, cols_per_row, figsize=(4 * cols_per_row, 3 * rows))
    fig.suptitle(title or f'{file_name} Channel Waveforms', fontsize=16)
    axes = axes.flatten()

    for i, ch_pair in enumerate(paired_channels):
        ax = axes[i]
        for col in ch_pair:
            color = 'crimson' if '(oxy)' in col else 'blue'
            label = 'HbO2' if '(oxy)' in col else 'HbR'
            sns.lineplot(data=hb_df, x="Probe1", y=col, ax=ax, label=label, color=color)

        # 如果需要任务标注
        if add_task:
            for tp in task_points:
                ax.axvline(
                    tp,
                    color='green',
                    linestyle='--',
                    alpha=0.5,
                    linewidth=1
                )

        ax.set_title(ch_pair[0].split('(')[0])
        ax.set_xlabel("Time Point")
        ax.set_ylabel(ylabel)
        ax.legend()

    # 删除多余子图
    for j in range(i + 1, len(axes)):
        fig.delaxes(axes[j])

    plt.tight_layout(rect=[0, 0, 1, 0.97])
    os.makedirs(output_path, exist_ok=True)
    output_file_path = os.path.join(output_path, f"{file_name}_{mode}.png")
    plt.savefig(output_file_path, dpi=300, bbox_inches='tight')
    plt.close(fig)


def scale_to_range(data, min_val, max_val):
    """将数据缩放到指定范围"""
    data_min, data_max = np.min(data), np.max(data)
    if data_max == data_min:
        return np.full_like(data, (min_val + max_val) / 2)
    return min_val + (data - data_min) * (max_val - min_val) / (data_max - data_min)


def hb_heatmap(data_df, file_name, signal_type="oxy", channel_df=None,
               title="Channel Heatmap", cmap="RdBu_r",
               figsize=(12, 6), output_path=None):
    """
    可视化 fNIRS 通道的空间插值热图（基于坐标 + 值 + 插值）

    参数
    ----------
    channel_df : pd.DataFrame
        通道空间位置数据，需包含列 ["channel", "x", "y"]
    data_df : pd.DataFrame  
        血氧数据，包含各通道的浓度值
    file_name : str
        文件名标识符
    signal_type : str, optional
        信号类型，'oxy' 或 'deOxy'，默认 'oxy'
    title : str, optional
        图表标题
    cmap : str, optional
        颜色映射，默认 'RdBu_r'
    figsize : tuple, optional
        图像尺寸
    output_path : str, optional
        输出路径，如果为None则不保存
    """
    if channel_df is None:
        channel_df = pd.read_csv(os.path.join(script_dir, "channel_location_ZLHK_Plate.csv"))

    # 提取目标类型信号
    value_df = data_df.loc[data_df.Type == signal_type, ["CH", "Value"]]
    channel_df["CH"] = channel_df["channel"].apply(lambda x: f"CH{x}")

    # 合并坐标和值
    merged = pd.merge(channel_df, value_df, left_on='CH', right_on='CH', how='inner')
    
    if merged.empty:
        raise ValueError("通道坐标数据与血氧数据无法匹配")
    
    # 标准化坐标到合适范围
    merged["x_std"] = scale_to_range(merged["x"], 0, 70)
    merged["y_std"] = scale_to_range(merged["y"], 0, 40)

    # 构建插值器（更平滑）
    coords = merged[["x_std", "y_std"]].values
    values = merged["Value"].values
    rbf = RBFInterpolator(coords, values, smoothing=0.005)  # 可调 smoothing

    # 构建网格（全填充背景）
    xi = np.linspace(-5, 75, 400)
    yi = np.linspace(-5, 45, 400)
    grid_x, grid_y = np.meshgrid(xi, yi)
    grid_coords = np.column_stack([grid_x.ravel(), grid_y.ravel()])
    grid_values = rbf(grid_coords).reshape(grid_x.shape)

    # 自动确定色阶上下限
    # TODO: 需要优化，让最后出来的图中的 contour 的中心值是 0.0，两边对称
    vmin, vmax = np.nanmin(grid_values), np.nanmax(grid_values)
    if abs(vmin) > abs(vmax):
        vmax = abs(vmin)
    else:
        vmin = -abs(vmax)

    # 计算四分位数用于文字颜色判断
    q1 = np.percentile(grid_values, 5)
    q3 = np.percentile(grid_values, 95)

    # 绘图
    plt.figure(figsize=figsize)
    contour = plt.contourf(grid_x, grid_y, grid_values, levels=100, cmap=cmap, vmin=vmin, vmax=vmax)

    # 标记通道编号（颜色根据插值值自动调整）
    for _, row in merged.iterrows():
        x, y = row["x_std"], row["y_std"]
        val = rbf([[x, y]])[0]
        if val <= q1 or val >= q3:
            color = "white"
        else:
            color = "black"
        plt.text(x, y, str(row["channel"]),
                 ha='center', va='center',
                 color=color, fontsize=12, fontweight='bold')

    plt.colorbar(contour, label="ΔValue")
    plt.xticks([]); plt.yticks([])
    plt.title(title)
    plt.grid(False)
    plt.tight_layout()

    # 保存图像
    if output_path:
        os.makedirs(output_path, exist_ok=True)
        filepath = os.path.join(output_path, f"{file_name}_{signal_type}_heatmap.png")
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        print(f"Saved to: {filepath}")


def hb_region_plot(region_df, file_name, output_path, title=None, mode='oxy', path_corrected=False):
    """
    可视化脑区的 HbO2 / HbR 波形均值

    Parameters
    ----------
    region_df : pd.DataFrame
        宽格式脑区数据（列为脑区名，行为时间点，需包含 'Probe1'）
    file_name : str
        文件名或样本标识符
    output_path : str
        图片保存目录
    title : str, optional
        图像主标题。若不指定，则使用 file_name
    mode : str, optional
        'oxy', 'deOxy', or 'both'，控制绘制的类型
    path_corrected : bool, optional
        决定 y 轴单位是 'mM' 还是 'mM·mm'
    """
    if mode not in ['oxy', 'deOxy', 'both']:
        raise ValueError("mode 必须为 'oxy'、'deOxy' 或 'both'")

    os.makedirs(output_path, exist_ok=True)
    unit = "mM" if path_corrected else "mM·mm"
    ylabel = f"ΔConcentration ({unit})"

    # 准备数据
    time_col = 'Probe1'
    value_cols = [col for col in region_df.columns if col != time_col]

    # 转换为长格式
    df_long = region_df.melt(id_vars=time_col, var_name="Region", value_name="Value")

    # 绘图
    plt.figure(figsize=(12, 6))
    sns.lineplot(data=df_long, x=time_col, y="Value", hue="Region", linewidth=1.5)

    plt.title(title or f"{file_name} Region-level Hb {mode}", fontsize=16)
    plt.xlabel("Time Point")
    plt.ylabel(ylabel)
    plt.legend(title="Region", bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()

    # 保存图像
    output_file_path = os.path.join(output_path, f"{file_name}_region_{mode}.png")
    plt.savefig(output_file_path, dpi=300, bbox_inches='tight')
    plt.close()

