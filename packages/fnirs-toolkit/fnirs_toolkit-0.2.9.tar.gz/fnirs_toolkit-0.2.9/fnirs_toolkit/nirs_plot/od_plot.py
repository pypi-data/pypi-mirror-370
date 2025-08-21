"""
fNIRS 光密度信号可视化模块

本模块专门用于光密度（Optical Density, OD）数据的可视化分析，提供：

核心功能：
- 多通道双波长对比波形图：展示每个通道在不同波长下的OD信号变化
- 通道质量分布可视化：基于CV、SNR等指标评估通道质量
- 时间序列对比图：处理前后数据对比分析
- 任务标记叠加：在波形图上标注任务开始/结束时间点

技术特点：
- 自动通道配对：根据通道ID自动匹配不同波长的信号
- 灵活布局：支持多行多列的子图排列，适应不同通道数量
- 质量指标集成：结合信号质量评估结果进行可视化标注
- 高质量输出：支持300 DPI高分辨率图像保存

适用场景：
- 原始数据质量检查
- 预处理效果评估  
- 通道筛选决策支持
- 实验报告图表生成

主要函数：
- OD_plot: 绘制光密度信号的多通道波形图
- plot_od_quality: 绘制通道质量指标分布图
- plot_od_comparison: 绘制处理前后对比图

使用示例：
    >>> from fnirs_toolkit.nirs_plot.od_plot import OD_plot
    >>> OD_plot(od_data, "sample_01", "output/od_plots/", 
    ...               title="光密度信号波形图")
"""

import matplotlib.pyplot as plt
import seaborn as sns
import re
from ..utils.helper import extract_channel_id, get_channel_columns, group_channels_by_id


def od_plot(data, file_name, output_path, title=None, output_suffix=""):
    """
    可视化 OD 波形图（如 CH1(690) 与 CH1(830)）
    """
    # 使用 helper 函数按通道分组
    ch_dict = group_channels_by_id(data)

    # 检查提取的通道列是否成对
    paired_channels = [tuple(v) for v in ch_dict.values() if len(v) == 2]
    if not paired_channels:
        raise ValueError("No valid channel pairs found. 请检查列名格式是否为 'CHx(λ)'。")

    # 图像布局参数
    cols_per_row = 8
    rows = (len(paired_channels) + cols_per_row - 1) // cols_per_row
    fig, axes = plt.subplots(rows, cols_per_row, figsize=(4 * cols_per_row, 3 * rows))
    fig.suptitle(title or f'{file_name} OD Waveforms', fontsize=16)
    axes = axes.flatten()

    # 按照每个子图，可视化 OD 波形图
    for i, (col1, col2) in enumerate(paired_channels):
        ax = axes[i]
        label1 = f"{col1.split('(')[-1][:-1]} nm"
        label2 = f"{col2.split('(')[-1][:-1]} nm"
        sns.lineplot(x=data.index, y=data[col1], ax=ax, label=label1, color='darkred')
        sns.lineplot(x=data.index, y=data[col2], ax=ax, label=label2, color='darkblue')

        ax.set_title(col1.split('(')[0])
        ax.set_xlabel("Time Point")
        ax.set_ylabel("Optical Density (OD)")
        ax.legend()

    # 清理多余子图
    for j in range(i + 1, len(axes)):
        fig.delaxes(axes[j])

    plt.tight_layout(rect=[0, 0, 1, 0.97])

    # 给输出文件名加入自定义后缀（默认为空）
    if output_suffix == "":
        output_file_path = f"{output_path}/{file_name}_od.png"
    else:
        output_file_path = f"{output_path}/{file_name}_od_{output_suffix}.png"

    # 保存图像
    plt.savefig(output_file_path, dpi=300, bbox_inches='tight')
    plt.close(fig)

