# 导入模块
from fnirs_toolkit.nirs_analysis.connectivity import functional_connectivity, plot_connectivity_matrix

# 计算功能连接矩阵
fc_matrix, info = functional_connectivity(
    hb_df,                # 血氧数据
    hb_type='oxy',        # 使用氧合血红蛋白
    method='pearson',     # 使用皮尔逊相关
    filter_threshold=0.3  # 过滤低于0.3的连接
)

# 可视化连接矩阵
plot_connectivity_matrix(
    fc_matrix,
    title="静息态功能连接矩阵 (HbO2)",
    output_path="output/connectivity",
    file_name="resting_fc_matrix.png"
)

# 计算图论指标
metrics = graph_metrics(fc_matrix, threshold=0.3)
print(f"网络密度: {metrics['density']:.3f}")
print(f"平均聚类系数: {metrics['average_clustering']:.3f}")