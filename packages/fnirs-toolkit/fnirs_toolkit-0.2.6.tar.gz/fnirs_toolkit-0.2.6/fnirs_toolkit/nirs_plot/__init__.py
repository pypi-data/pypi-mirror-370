"""
fNIRS 数据可视化模块

本模块提供 fNIRS 数据的全面可视化功能，包括：

数据类型可视化：
- 原始光强信号波形图
- 光密度（OD）信号波形图  
- 血红蛋白浓度变化波形图
- 脑区平均信号波形图

质量评估可视化：
- 信号质量指标分布图（CV、SNR）
- 头皮耦合指数（SCI）分布图
- 通道质量热图

空间分析可视化：
- 血氧浓度激活热图
- 通道空间分布图
- 脑区激活模式图

主要模块：
- od_plot: 光密度信号可视化
- hb_plot: 血红蛋白浓度可视化  
- quality_plot: 信号质量可视化

使用示例：
    >>> import fnirs_toolkit as fnirs
    >>> # 绘制血氧波形图
    >>> fnirs.plot_hb_channels(hb_data, "sample", "output/", mode='both')
    >>> # 绘制激活热图
    >>> fnirs.plot_hb_heatmap(channel_df, hb_data, "sample", signal_type="oxy")
"""

from .od_plot import od_plot
from .hb_plot import hb_plot, hb_heatmap, hb_region_plot
# from .quality_plot import plot_sci, plot_cv_snr

__all__ = [
    "od_plot", "hb_plot", "hb_heatmap", "hb_region_plot"
    # 'plot_sci', 'plot_cv_snr'
]
