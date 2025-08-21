# 描述：从不同设备的原始文件读取原始的血氧数据


import pandas as pd

def hb_import(file_path, device_type="ZLHK"):
    """
    从不同设备的原始文件读取原始的血氧数据

    Parameters
    ----------
    file_path: str
        血氧文件路径
    device_type: str

    Returns
    -------
    HB_df: pd.DataFrame
        血氧数据
    """
    if device_type == "ZLHK":
        HB_df = pd.read_csv(file_path, encoding='ISO-8859-1', skiprows=40)
        print(f"读取文件: {file_path}")
    else:
        raise ValueError("设备类型错误")
    
    return HB_df
