# 描述：从不同设备的原始文件读取原始的光密度数据

import numpy as np
import pandas as pd
import re


def od_import(file_path, device_type="ZLHK", convert_to_base10=True):
    """
    从不同设备的原始文件读取原始的光密度数据

    Parameters
    ----------
    file_path: str
        OD 文件路径
    device_type: str
        OD 设备类型
    convert_to_base10: bool
        是否将光密度转换为 base10 对数

    Returns
    -------
    pd.DataFrame
        光密度（OD）DataFrame，其他列保持不变
    """
    if device_type == "ZLHK":
        od_df = pd.read_csv(file_path, encoding='ISO-8859-1',skiprows=40)
        print(f"读取文件: {file_path}")
    else:
        raise ValueError("设备类型错误")
    
    # 对光密度数据进行基线校正
    ch_cols = [col for col in od_df.columns if re.match(r'^CH\d+\(\d+\.?\d*\)$', col)]
    od_df_copy = od_df.copy()

    for col in ch_cols:
        # 如果原始为自然对数，转换为 base10 对数
        if convert_to_base10:
            od_df_copy[col] = od_df_copy[col] / np.log(10)

        # 使用第一行作为 reference 参考值
        signal = od_df_copy[col].values
        ref = signal[0] 

        # 减去第一行的参考值，进行基线校正
        od_df_copy[col] = signal - ref   

    return od_df_copy
