
"""
fNIRS 信号质量评估可视化模块

本模块专门用于 fNIRS 数据质量指标的可视化分析，提供：

核心功能：
- 变异系数（CV）分布可视化：评估信号稳定性的关键指标
- 信噪比（SNR）分布可视化：评估信号强度与噪声水平
- 头皮耦合指数（SCI）分布图：评估光极与头皮的耦合质量
- 质量指标对比图：多种质量指标的综合对比分析

可视化类型：
- 直方图分布：展示质量指标在所有通道中的分布特征
- 箱线图统计：显示质量指标的统计特征（中位数、四分位数等）
- 散点图关联：分析不同质量指标之间的相关性
- 阈值标注图：标注质量控制的软硬阈值线

技术特点：
- 自动阈值计算：基于数据分布自动计算合理的质量阈值
- 多指标联合：支持CV、SNR、SCI等多种质量指标的联合分析
- 统计信息叠加：在图表中显示关键统计信息（均值、分位数等）
- 异常通道标注：自动标注质量不达标的异常通道

应用场景：
- 数据预处理质量控制
- 通道筛选决策支持
- 实验设计优化指导
- 质量报告生成

主要函数：
- plot_cv_snr: 绘制CV和SNR的分布图
- plot_sci: 绘制头皮耦合指数分布图
- plot_quality_comparison: 绘制多指标对比图
- plot_channel_quality_heatmap: 绘制通道质量热图

使用示例：
    >>> from fnirs_toolkit.nirs_plot.quality_plot import plot_cv_snr, plot_sci
    >>> # 绘制CV和SNR分布
    >>> plot_cv_snr(raw_data, "subject_01", "output/quality/")
    >>> # 绘制头皮耦合指数
    >>> plot_sci(od_data, "subject_01", "output/quality/", threshold=0.5)
"""

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
import os
from ..nirs_preprocess.raw_quality import raw_CV, raw_SNR
from ..utils.helper import get_sfreq
from ..nirs_preprocess.od_quality import od_sci


def plot_cv_snr(raw_df, file_name, output_path, sfreq=None, 
                cv_threshold=None, snr_threshold=None, bins=40):
    """
    绘制变异系数（CV）和信噪比（SNR）的分布图
    
    Parameters
    ----------
    raw_df : pd.DataFrame
        原始光强数据
    file_name : str
        输出文件名标识符
    output_path : str
        图像保存路径
    sfreq : float, optional
        采样率，如果为None则从数据中估计
    cv_threshold : float, optional
        CV阈值线，默认为None
    snr_threshold : float, optional  
        SNR阈值线，默认为None
    bins : int, optional
        直方图分箱数，默认40
    """
    # 获取采样率
    if sfreq is None:
        sfreq = get_sfreq(raw_df)
    
    # 计算CV和SNR
    cv_df, _, _ = raw_CV(raw_df, use_auto_threshold=False)
    snr_df, _, _ = raw_SNR(raw_df, use_auto_threshold=False)
    
    # 提取数值
    cv_vals = cv_df.iloc[:, 1:].astype(float).values.ravel()
    snr_vals = snr_df.iloc[:, 1:].astype(float).values.ravel()
    
    # 移除NaN值
    cv_vals = cv_vals[~np.isnan(cv_vals)]
    snr_vals = snr_vals[~np.isnan(snr_vals)]
    
    # 创建子图
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    fig.suptitle(f'{file_name} - 信号质量分析', fontsize=16)
    
    # CV直方图
    axes[0, 0].hist(cv_vals, bins=bins, alpha=0.7, color='skyblue', edgecolor='black')
    axes[0, 0].set_title('变异系数 (CV) 分布')
    axes[0, 0].set_xlabel('CV值')
    axes[0, 0].set_ylabel('通道数量')
    axes[0, 0].axvline(np.mean(cv_vals), color='red', linestyle='--', label=f'均值: {np.mean(cv_vals):.3f}')
    if cv_threshold is not None:
        axes[0, 0].axvline(cv_threshold, color='orange', linestyle='-', linewidth=2, 
                          label=f'阈值: {cv_threshold}')
    axes[0, 0].legend()
    
    # SNR直方图
    axes[0, 1].hist(snr_vals, bins=bins, alpha=0.7, color='lightgreen', edgecolor='black')
    axes[0, 1].set_title('信噪比 (SNR) 分布')
    axes[0, 1].set_xlabel('SNR值 (dB)')
    axes[0, 1].set_ylabel('通道数量')
    axes[0, 1].axvline(np.mean(snr_vals), color='red', linestyle='--', label=f'均值: {np.mean(snr_vals):.1f}')
    if snr_threshold is not None:
        axes[0, 1].axvline(snr_threshold, color='orange', linestyle='-', linewidth=2,
                          label=f'阈值: {snr_threshold}')
    axes[0, 1].legend()
    
    # CV箱线图
    axes[1, 0].boxplot(cv_vals, vert=True, patch_artist=True,
                       boxprops=dict(facecolor='skyblue', alpha=0.7))
    axes[1, 0].set_title('CV 箱线图')
    axes[1, 0].set_ylabel('CV值')
    axes[1, 0].grid(True, alpha=0.3)
    
    # SNR箱线图
    axes[1, 1].boxplot(snr_vals, vert=True, patch_artist=True,
                       boxprops=dict(facecolor='lightgreen', alpha=0.7))
    axes[1, 1].set_title('SNR 箱线图')
    axes[1, 1].set_ylabel('SNR值 (dB)')
    axes[1, 1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # 保存图像
    os.makedirs(output_path, exist_ok=True)
    output_file = os.path.join(output_path, f"{file_name}_cv_snr_analysis.png")
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    
    # 打印统计信息
    print(f"CV统计: 均值={np.mean(cv_vals):.3f}, 中位数={np.median(cv_vals):.3f}, 标准差={np.std(cv_vals):.3f}")
    print(f"SNR统计: 均值={np.mean(snr_vals):.1f}, 中位数={np.median(snr_vals):.1f}, 标准差={np.std(snr_vals):.1f}")


def plot_sci(od_df, file_name, output_path, threshold=0.5, bins=30):
    """
    绘制头皮耦合指数（SCI）分布图
    
    Parameters
    ----------
    od_df : pd.DataFrame
        光密度数据
    file_name : str
        输出文件名标识符
    output_path : str
        图像保存路径
    threshold : float, optional
        SCI阈值线，默认0.5
    bins : int, optional
        直方图分箱数，默认30
    """
    # 计算SCI
    sci_df = od_sci(od_df)
    sci_vals = sci_df.iloc[:, 1:].astype(float).values.ravel()
    sci_vals = sci_vals[~np.isnan(sci_vals)]
    
    # 创建图表
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    fig.suptitle(f'{file_name} - 头皮耦合指数 (SCI) 分析', fontsize=16)
    
    # SCI直方图
    axes[0].hist(sci_vals, bins=bins, alpha=0.7, color='coral', edgecolor='black')
    axes[0].set_title('SCI 分布')
    axes[0].set_xlabel('SCI值')
    axes[0].set_ylabel('通道数量')
    axes[0].axvline(np.mean(sci_vals), color='red', linestyle='--', 
                   label=f'均值: {np.mean(sci_vals):.3f}')
    axes[0].axvline(threshold, color='orange', linestyle='-', linewidth=2,
                   label=f'阈值: {threshold}')
    axes[0].legend()
    
    # SCI箱线图
    axes[1].boxplot(sci_vals, vert=True, patch_artist=True,
                   boxprops=dict(facecolor='coral', alpha=0.7))
    axes[1].set_title('SCI 箱线图')
    axes[1].set_ylabel('SCI值')
    axes[1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # 保存图像
    os.makedirs(output_path, exist_ok=True)
    output_file = os.path.join(output_path, f"{file_name}_sci_analysis.png")
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    
    # 统计信息
    good_channels = np.sum(sci_vals >= threshold)
    total_channels = len(sci_vals)
    print(f"SCI统计: 均值={np.mean(sci_vals):.3f}, 中位数={np.median(sci_vals):.3f}")
    print(f"良好通道: {good_channels}/{total_channels} ({good_channels/total_channels*100:.1f}%)")


def plot_quality_comparison(raw_df, file_name, output_path, 
                           cv_threshold=0.2, snr_threshold=15):
    """
    绘制多指标对比图
    
    Parameters
    ----------
    raw_df : pd.DataFrame
        原始光强数据
    file_name : str
        输出文件名标识符
    output_path : str
        图像保存路径
    cv_threshold : float, optional
        CV阈值，默认0.2
    snr_threshold : float, optional
        SNR阈值，默认15
    """
    from ..nirs_preprocess.raw_quality import raw_CV, raw_SNR
    from ..utils.helper import extract_channel_id
    
    # 计算质量指标
    cv_df, _, _ = raw_CV(raw_df, use_auto_threshold=False)
    snr_df, _, _ = raw_SNR(raw_df, use_auto_threshold=False)
    
    # 准备数据
    quality_data = []
    cv_cols = [col for col in cv_df.columns if col != 'Probe1']
    snr_cols = [col for col in snr_df.columns if col != 'Probe1']
    
    for cv_col, snr_col in zip(cv_cols, snr_cols):
        ch_id = extract_channel_id(cv_col)
        cv_val = cv_df[cv_col].iloc[0] if len(cv_df) > 0 else np.nan
        snr_val = snr_df[snr_col].iloc[0] if len(snr_df) > 0 else np.nan
        
        # 判断通道质量
        cv_good = cv_val <= cv_threshold if not np.isnan(cv_val) else False
        snr_good = snr_val >= snr_threshold if not np.isnan(snr_val) else False
        
        if cv_good and snr_good:
            quality = 'Good'
        elif cv_good or snr_good:
            quality = 'Moderate'
        else:
            quality = 'Poor'
            
        quality_data.append({
            'Channel': ch_id,
            'CV': cv_val,
            'SNR': snr_val,
            'Quality': quality
        })
    
    quality_df = pd.DataFrame(quality_data)
    
    # 创建图表
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle(f'{file_name} - 通道质量综合分析', fontsize=16)
    
    # CV vs SNR散点图
    colors = {'Good': 'green', 'Moderate': 'orange', 'Poor': 'red'}
    for quality in colors:
        subset = quality_df[quality_df['Quality'] == quality]
        axes[0, 0].scatter(subset['CV'], subset['SNR'], 
                          c=colors[quality], label=quality, alpha=0.7, s=50)
    
    axes[0, 0].axvline(cv_threshold, color='gray', linestyle='--', alpha=0.7)
    axes[0, 0].axhline(snr_threshold, color='gray', linestyle='--', alpha=0.7)
    axes[0, 0].set_xlabel('CV值')
    axes[0, 0].set_ylabel('SNR值 (dB)')
    axes[0, 0].set_title('CV vs SNR 散点图')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)
    
    # 质量分布饼图
    quality_counts = quality_df['Quality'].value_counts()
    axes[0, 1].pie(quality_counts.values, labels=quality_counts.index, 
                   colors=[colors[q] for q in quality_counts.index],
                   autopct='%1.1f%%', startangle=90)
    axes[0, 1].set_title('通道质量分布')
    
    # 通道质量条形图
    quality_df_sorted = quality_df.sort_values('Channel')
    x_pos = range(len(quality_df_sorted))
    bar_colors = [colors[q] for q in quality_df_sorted['Quality']]
    
    axes[1, 0].bar(x_pos, quality_df_sorted['CV'], color=bar_colors, alpha=0.7)
    axes[1, 0].axhline(cv_threshold, color='red', linestyle='--', linewidth=2)
    axes[1, 0].set_xlabel('通道')
    axes[1, 0].set_ylabel('CV值')
    axes[1, 0].set_title('各通道CV值')
    axes[1, 0].set_xticks(x_pos[::2])  # 每隔一个显示标签
    axes[1, 0].set_xticklabels(quality_df_sorted['Channel'].iloc[::2], rotation=45)
    
    axes[1, 1].bar(x_pos, quality_df_sorted['SNR'], color=bar_colors, alpha=0.7)
    axes[1, 1].axhline(snr_threshold, color='red', linestyle='--', linewidth=2)
    axes[1, 1].set_xlabel('通道')
    axes[1, 1].set_ylabel('SNR值 (dB)')
    axes[1, 1].set_title('各通道SNR值')
    axes[1, 1].set_xticks(x_pos[::2])
    axes[1, 1].set_xticklabels(quality_df_sorted['Channel'].iloc[::2], rotation=45)
    
    plt.tight_layout()
    
    # 保存图像
    os.makedirs(output_path, exist_ok=True)
    output_file = os.path.join(output_path, f"{file_name}_quality_comparison.png")
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    
    # 保存质量数据
    csv_file = os.path.join(output_path, f"{file_name}_channel_quality.csv")
    quality_df.to_csv(csv_file, index=False)
    
    # 统计信息
    print(f"通道质量统计:")
    for quality in ['Good', 'Moderate', 'Poor']:
        count = len(quality_df[quality_df['Quality'] == quality])
        percentage = count / len(quality_df) * 100
        print(f"  {quality}: {count} ({percentage:.1f}%)")


def plot_channel_quality_heatmap(channel_df, quality_df, file_name, output_path,
                                 metric='CV', title=None):
    """
    绘制通道质量热图
    
    Parameters
    ----------
    channel_df : pd.DataFrame
        通道位置信息，包含['channel', 'x', 'y']列
    quality_df : pd.DataFrame
        质量指标数据
    file_name : str
        输出文件名标识符
    output_path : str
        图像保存路径
    metric : str, optional
        质量指标类型，'CV'或'SNR'，默认'CV'
    title : str, optional
        图表标题
    """
    from scipy.interpolate import RBFInterpolator
    
    # 提取质量数据
    quality_cols = [col for col in quality_df.columns if col != 'Probe1']
    quality_values = []
    
    for col in quality_cols:
        ch_id = extract_channel_id(col)
        value = quality_df[col].iloc[0] if len(quality_df) > 0 else np.nan
        quality_values.append({'channel': ch_id, 'value': value})
    
    value_df = pd.DataFrame(quality_values)
    
    # 合并位置和质量数据
    merged = pd.merge(channel_df, value_df, on='channel', how='inner')
    
    if merged.empty:
        raise ValueError("通道位置数据与质量数据无法匹配")
    
    # 标准化坐标
    merged["x_std"] = (merged["x"] - merged["x"].min()) / (merged["x"].max() - merged["x"].min()) * 70
    merged["y_std"] = (merged["y"] - merged["y"].min()) / (merged["y"].max() - merged["y"].min()) * 40
    
    # 插值
    coords = merged[["x_std", "y_std"]].values
    values = merged["value"].values
    rbf = RBFInterpolator(coords, values, smoothing=0.01)
    
    # 创建网格
    xi = np.linspace(-5, 75, 300)
    yi = np.linspace(-5, 45, 300)
    grid_x, grid_y = np.meshgrid(xi, yi)
    grid_coords = np.column_stack([grid_x.ravel(), grid_y.ravel()])
    grid_values = rbf(grid_coords).reshape(grid_x.shape)
    
    # 绘图
    plt.figure(figsize=(12, 8))
    
    # 选择颜色映射
    if metric == 'CV':
        cmap = 'Reds'  # CV越高越差，用红色
        vmin, vmax = 0, np.nanmax(grid_values)
    else:  # SNR
        cmap = 'Greens'  # SNR越高越好，用绿色
        vmin, vmax = np.nanmin(grid_values), None
    
    contour = plt.contourf(grid_x, grid_y, grid_values, levels=50, 
                          cmap=cmap, vmin=vmin, vmax=vmax)
    
    # 标记通道位置和数值
    for _, row in merged.iterrows():
        x, y = row["x_std"], row["y_std"]
        plt.scatter(x, y, c='white', s=100, edgecolors='black', linewidth=2)
        plt.text(x, y, f"{row['channel']}\n{row['value']:.2f}", 
                ha='center', va='center', fontsize=8, fontweight='bold')
    
    plt.colorbar(contour, label=f'{metric} 值')
    plt.title(title or f'{file_name} - {metric} 空间分布')
    plt.xticks([])
    plt.yticks([])
    plt.tight_layout()
    
    # 保存图像
    os.makedirs(output_path, exist_ok=True)
    output_file = os.path.join(output_path, f"{file_name}_{metric.lower()}_heatmap.png")
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()


def plot_quality_violin(raw_df, file_name, output_path, group_by_wavelength=True):
    """
    绘制质量指标的小提琴图
    
    Parameters
    ----------
    raw_df : pd.DataFrame
        原始光强数据
    file_name : str
        输出文件名标识符
    output_path : str
        图像保存路径
    group_by_wavelength : bool, optional
        是否按波长分组，默认True
    """
    from ..nirs_preprocess.raw_quality import raw_CV, raw_SNR
    from ..utils.helper import extract_channel_id
    
    # 计算质量指标
    cv_df, _, _ = raw_CV(raw_df, use_auto_threshold=False)
    snr_df, _, _ = raw_SNR(raw_df, use_auto_threshold=False)
    
    # 准备数据
    plot_data = []
    cv_cols = [col for col in cv_df.columns if col != 'Probe1']
    snr_cols = [col for col in snr_df.columns if col != 'Probe1']
    
    for cv_col, snr_col in zip(cv_cols, snr_cols):
        ch_info = cv_col.split('(')
        ch_id = ch_info[0]
        wavelength = ch_info[1].rstrip(')') if len(ch_info) > 1 else 'Unknown'
        
        cv_val = cv_df[cv_col].iloc[0] if len(cv_df) > 0 else np.nan
        snr_val = snr_df[snr_col].iloc[0] if len(snr_df) > 0 else np.nan
        
        plot_data.extend([
            {'Channel': ch_id, 'Wavelength': wavelength, 'Metric': 'CV', 'Value': cv_val},
            {'Channel': ch_id, 'Wavelength': wavelength, 'Metric': 'SNR', 'Value': snr_val}
        ])
    
    plot_df = pd.DataFrame(plot_data)
    plot_df = plot_df.dropna(subset=['Value'])
    
    # 创建图表
    if group_by_wavelength:
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))
        fig.suptitle(f'{file_name} - 质量指标分布（按波长分组）', fontsize=16)
        
        # CV小提琴图
        cv_data = plot_df[plot_df['Metric'] == 'CV']
        sns.violinplot(data=cv_data, x='Wavelength', y='Value', ax=axes[0])
        axes[0].set_title('CV 分布')
        axes[0].set_ylabel('CV值')
        
        # SNR小提琴图
        snr_data = plot_df[plot_df['Metric'] == 'SNR']
        sns.violinplot(data=snr_data, x='Wavelength', y='Value', ax=axes[1])
        axes[1].set_title('SNR 分布')
        axes[1].set_ylabel('SNR值 (dB)')
        
    else:
        fig, ax = plt.subplots(1, 1, figsize=(10, 6))
        fig.suptitle(f'{file_name} - 质量指标分布', fontsize=16)
        
        sns.violinplot(data=plot_df, x='Metric', y='Value', ax=ax)
        ax.set_title('质量指标分布')
        ax.set_ylabel('指标值')
    
    plt.tight_layout()
    
    # 保存图像
    os.makedirs(output_path, exist_ok=True)
    suffix = 'by_wavelength' if group_by_wavelength else 'combined'
    output_file = os.path.join(output_path, f"{file_name}_quality_violin_{suffix}.png")
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()

