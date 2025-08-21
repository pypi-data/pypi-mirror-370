"""
fNIRS Toolkit - A comprehensive Python package for fNIRS data analysis
"""

__version__ = "0.2.4"
__author__ = "Youguo"

# 导入主要模块
from . import nirs_io
from . import utils
from . import nirs_preprocess

# from . import nirs_plot  
# from . import quality
# from . import nirs_analysis


# 导入常用函数到顶层命名空间
# from .nirs_io import load_raw_intensity, load_od_data, load_hb_data
# from .nirs_preprocess import raw_to_od, od_to_hb, resample_data
# from .nirs_plot import plot_od, plot_hb, plot_brain_regions
