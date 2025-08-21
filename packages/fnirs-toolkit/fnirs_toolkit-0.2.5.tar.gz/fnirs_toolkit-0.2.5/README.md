# 近红外数据预处理流程

本项目包括整个近红外数据预处理流程，和相关算法。整体流程图如下所示：

![整体处理流程图](flowchart.png)

## 一、光强数据读取和处理

所有以 raw 开头的函数文件名，均应用于光密度数据。

### 1.1 原始数据读取

```Python
# 读取原始光强数据
raw_df = raw_intensity_import(r"data/raw/raw_sample01.csv")
```
### 1.2 光强数据转换为光密度数据

提供以10为底和以自然对数为底两种方法，默认和推荐以10为底。

```Python
# 将原始光强数据转换为光密度数据 (默认 base10 对数)
od_df_base10 = raw_intensity_to_od(raw_df)

# 将原始光强数据转换为光密度数据 (以自然对数为底)
od_df_natural = raw_intensity_to_od(raw_df, base="natural")
```
### 1.3 光强数据的变异系数 CV

TODO

### 1.4 光强数据的信噪比 SNR

TODO

## 二、光密度数据读取和处理

### 2.1 光密度数据的读取

```Python
# 读取光密度数据并完成基线校正
od_df = OD_import(r"data/OD/OD_sample.csv")
```

### 2.2 光密度数据可视化

对光密度数据以通道进行子图可视化，示例图：

![40288781841d31b601841d4a54030114_od.png](https://s2.loli.net/2025/06/17/h8bxRVqNelYOgBf.png)

```Python
OD_visualize(od_df, "保存文件名", "output/figure")
```

### 2.3 计算各个通道头皮耦合指数（SCI）

可以自定义采样率和阈值。

```Python
sci_df = OD_scalp_coupling_index(od_df, sfreq=10, threshold=0.75)
```

### 2.4 光密度数据转换为血氧数据

```Python
HB_df_base10 = OD_beerlambert(od_df_base10, [690, 830], base='base10')
```

## 三、血氧数据处理

### 3.1 血氧数据的读取

```Python
HB_df = HB_import(r"data/HB/HB_sample02.csv")
```

### 3.2 血氧数据通道可视化

示例图：

![40288781841d31b601841d4a54030114_both.png](https://s2.loli.net/2025/06/17/fIaS8Et4A1CkQGh.png)

```Python
HB_visualize(data=hb_df, file_id=file_id, output_path="output/zlhk_figures/oxy",
             title="S01 Hemoglobin Waveforms", mode='both', path_corrected=True)
```

### 3.3 血氧数据热图可视化

示例图：

![Oxy_heatmap.png](https://s2.loli.net/2025/06/17/YwMN7Z8ECsbWAdj.png)

```Python
channel_df = pd.read_csv("./data/channel_location_ZLHK_Plate.csv")
HB_heatmap(channel_df, data_df,
               signal_type="Oxy",
               title="ZLHK - HbO2 Change Heatmap",
               output_path = "output")
```

### 3.4 血氧数据通道 -> 脑区映射

```Python
region_map = json.load(open(r"data/channel_region_map.json"))
HB_brain_df = HB_brain_integration(HB_df, region_map, hb_type='oxy')
```

### 3.5 血氧脑区通道可视化

可视化示例图：

![Test04-HB_Region_region_oxy.png](https://s2.loli.net/2025/06/23/baCt9LnyDfF1iBV.png)

```Python
HB_brain_df = HB_brain_integration(HB_df, region_map, hb_type='oxy')
HB_region_visualize(HB_brain_df, file_name="Test04-HB_Region", output_path="output/figure",
                    title="", mode='oxy', path_corrected=False)
```
