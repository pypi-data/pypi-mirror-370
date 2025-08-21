# 描述：从不同设备的原始文件读取原始的光强数据

import numpy as np
import pandas as pd


def raw_intensity_import(file_path, device_type="ZLHK"):
    """
    从不同设备的原始文件读取原始的光密度数据

    Parameters
    ---------- 
      file_path: 文件路径
      device_type: 设备类型，默认是 ZLHK，也可以是 ZLHK_1000

    Returns
    -------
      raw_od: 原始的光密度数据
    """
    if device_type == "ZLHK":
        raw_od = pd.read_csv(file_path, encoding='ISO-8859-1', skiprows=40)
        print(f"读取文件: {file_path}")
    else:
        raise ValueError("设备类型错误")
    
    return raw_od
