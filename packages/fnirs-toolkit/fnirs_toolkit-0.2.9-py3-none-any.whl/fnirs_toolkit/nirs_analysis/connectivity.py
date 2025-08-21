"""
fNIRS 功能连接分析模块

本模块提供静息态和任务态下的功能连接分析功能，包括：
1. 皮尔逊相关系数计算
2. 相干性分析
3. 偏相关分析
4. 图论指标计算

主要功能：
- functional_connectivity: 计算通道间的功能连接矩阵
- coherence_analysis: 计算通道间的相干性
- graph_metrics: 计算连接矩阵的图论指标
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from scipy import signal
import networkx as nx
import os

from ..utils.helper import get_channel_columns, extract_channel_id


def functional_connectivity(hb_df, hb_type='oxy', method='pearson', 
                           filter_threshold=None, absolute=False):
    """
    计算静息态功能连接矩阵
    
    Parameters
    ----------
    hb_df : pd.DataFrame
        血氧数据，包含CHx(oxy)和CHx(deOxy)列
    hb_type : str, optional
        'oxy' - 使用氧合血红蛋白数据
        'deOxy' - 使用脱氧血红蛋白数据
        默认为'oxy'
    method : str, optional
        'pearson' - 皮尔逊相关系数
        'spearman' - 斯皮尔曼等级相关
        'kendall' - 肯德尔等级相关
        'partial' - 偏相关（控制其他通道的影响）
        默认为'pearson'
    filter_threshold : float, optional
        相关系数阈值，低于此值的连接将被设为0
        默认为None（不过滤）
    absolute : bool, optional
        是否取绝对值，默认为False
        
    Returns
    -------
    pd.DataFrame
        通道间功能连接矩阵，行列索引为通道名称
    dict
        包含额外信息的字典，如平均连接强度等
    """
    # 获取指定类型的通道列
    target_cols = [col for col in hb_df.columns if f'({hb_type})' in col]
    
    if not target_cols:
        raise ValueError(f"未找到{hb_type}类型的通道数据")
    
    # 提取通道ID作为标签
    channel_ids = [extract_channel_id(col) for col in target_cols]
    
    # 准备数据矩阵
    data_matrix = hb_df[target_cols].values
    
    # 计算相关矩阵
    if method == 'pearson':
        corr_matrix = np.corrcoef(data_matrix.T)
    elif method == 'spearman':
        corr_matrix, _ = stats.spearmanr(data_matrix, axis=0)
    elif method == 'kendall':
        # 肯德尔相关需要两两计算
        n_channels = len(target_cols)
        corr_matrix = np.zeros((n_channels, n_channels))
        for i in range(n_channels):
            for j in range(n_channels):
                corr, _ = stats.kendalltau(data_matrix[:, i], data_matrix[:, j])
                corr_matrix[i, j] = corr
    elif method == 'partial':
        # 偏相关计算
        from sklearn.covariance import GraphicalLassoCV
        model = GraphicalLassoCV(alphas=4)
        model.fit(data_matrix)
        # 偏精度矩阵的负值即为偏相关
        precision = model.precision_
        d = np.sqrt(np.diag(precision))
        corr_matrix = -precision / np.outer(d, d)
        np.fill_diagonal(corr_matrix, 1)
    else:
        raise ValueError(f"不支持的方法: {method}")
    
    # 处理NaN值
    corr_matrix = np.nan_to_num(corr_matrix)
    
    # 应用绝对值（如果需要）
    if absolute:
        corr_matrix = np.abs(corr_matrix)
    
    # 应用阈值过滤
    if filter_threshold is not None:
        if absolute:
            corr_matrix[np.abs(corr_matrix) < filter_threshold] = 0
        else:
            corr_matrix[corr_matrix < filter_threshold] = 0
    
    # 创建DataFrame
    fc_df = pd.DataFrame(corr_matrix, index=channel_ids, columns=channel_ids)
    
    # 计算额外指标
    info = {
        'mean_connectivity': np.mean(np.abs(corr_matrix[~np.eye(corr_matrix.shape[0], dtype=bool)])),
        'density': np.sum(np.abs(corr_matrix) > 0.3) / (corr_matrix.shape[0]**2 - corr_matrix.shape[0]),
        'max_connectivity': np.max(np.abs(corr_matrix[~np.eye(corr_matrix.shape[0], dtype=bool)])),
        'method': method,
        'hb_type': hb_type
    }
    
    return fc_df, info


def coherence_analysis(hb_df, hb_type='oxy', freq_range=(0.01, 0.1), fs=None):
    """
    计算通道间的频域相干性
    
    Parameters
    ----------
    hb_df : pd.DataFrame
        血氧数据，包含CHx(oxy)和CHx(deOxy)列
    hb_type : str, optional
        'oxy' - 使用氧合血红蛋白数据
        'deOxy' - 使用脱氧血红蛋白数据
        默认为'oxy'
    freq_range : tuple, optional
        感兴趣的频率范围 (min_freq, max_freq)，单位为Hz
        默认为(0.01, 0.1)，对应静息态低频振荡
    fs : float, optional
        采样率，如果为None则从数据中估计
        
    Returns
    -------
    pd.DataFrame
        通道间相干性矩阵，行列索引为通道名称
    dict
        包含频率信息的字典
    """
    from ..utils.helper import get_sfreq
    
    # 获取采样率
    if fs is None:
        fs = get_sfreq(hb_df)
    
    # 获取指定类型的通道列
    target_cols = [col for col in hb_df.columns if f'({hb_type})' in col]
    
    if not target_cols:
        raise ValueError(f"未找到{hb_type}类型的通道数据")
    
    # 提取通道ID作为标签
    channel_ids = [extract_channel_id(col) for col in target_cols]
    n_channels = len(channel_ids)
    
    # 准备数据矩阵
    data_matrix = hb_df[target_cols].values
    
    # 计算相干性矩阵
    coh_matrix = np.zeros((n_channels, n_channels))
    freq_info = {}
    
    for i in range(n_channels):
        for j in range(i, n_channels):
            # 计算相干性
            f, Cxy = signal.coherence(data_matrix[:, i], data_matrix[:, j], fs=fs)
            
            # 提取感兴趣频率范围内的平均相干性
            mask = (f >= freq_range[0]) & (f <= freq_range[1])
            mean_coh = np.mean(Cxy[mask])
            
            coh_matrix[i, j] = mean_coh
            coh_matrix[j, i] = mean_coh
            
            # 存储第一对通道的频率信息作为参考
            if i == 0 and j == 1:
                freq_info = {
                    'frequencies': f[mask],
                    'coherence': Cxy[mask],
                    'freq_range': freq_range
                }
    
    # 创建DataFrame
    coh_df = pd.DataFrame(coh_matrix, index=channel_ids, columns=channel_ids)
    
    return coh_df, freq_info


def plot_connectivity_matrix(conn_matrix, title=None, cmap='coolwarm', 
                            output_path=None, file_name=None):
    """
    可视化连接矩阵
    
    Parameters
    ----------
    conn_matrix : pd.DataFrame
        连接矩阵，行列索引为通道名称
    title : str, optional
        图表标题
    cmap : str, optional
        颜色映射，默认为'coolwarm'
    output_path : str, optional
        输出路径，如果为None则不保存
    file_name : str, optional
        文件名，如果为None则使用默认名称
        
    Returns
    -------
    matplotlib.figure.Figure
        图表对象
    """
    plt.figure(figsize=(10, 8))
    mask = np.zeros_like(conn_matrix, dtype=bool)
    np.fill_diagonal(mask, True)  # 隐藏对角线
    
    sns.heatmap(conn_matrix, annot=True, cmap=cmap, mask=mask,
                vmin=-1, vmax=1, center=0, square=True, linewidths=.5)
    
    if title:
        plt.title(title, fontsize=16)
    plt.tight_layout()
    
    # 保存图表
    if output_path and file_name:
        os.makedirs(output_path, exist_ok=True)
        plt.savefig(os.path.join(output_path, file_name), dpi=300, bbox_inches='tight')
    
    return plt.gcf()


def graph_metrics(conn_matrix, threshold=0.3, weighted=True):
    """
    计算连接矩阵的图论指标
    
    Parameters
    ----------
    conn_matrix : pd.DataFrame
        连接矩阵，行列索引为通道名称
    threshold : float, optional
        连接阈值，低于此值的连接将被忽略
        默认为0.3
    weighted : bool, optional
        是否使用加权图，默认为True
        
    Returns
    -------
    dict
        包含各种图论指标的字典
    """
    # 创建图
    G = nx.from_pandas_adjacency(conn_matrix)
    
    # 应用阈值
    for u, v, d in list(G.edges(data=True)):
        if abs(d['weight']) < threshold:
            G.remove_edge(u, v)
        elif not weighted:
            G[u][v]['weight'] = 1
    
    # 计算图论指标
    metrics = {}
    
    # 基本指标
    metrics['node_count'] = G.number_of_nodes()
    metrics['edge_count'] = G.number_of_edges()
    metrics['density'] = nx.density(G)
    
    # 节点级指标
    try:
        metrics['degree_centrality'] = nx.degree_centrality(G)
        metrics['betweenness_centrality'] = nx.betweenness_centrality(G, weight='weight' if weighted else None)
        metrics['closeness_centrality'] = nx.closeness_centrality(G, distance='weight' if weighted else None)
    except:
        # 如果图不连通，某些指标可能计算失败
        pass
    
    # 网络级指标
    try:
        metrics['average_clustering'] = nx.average_clustering(G, weight='weight' if weighted else None)
        metrics['transitivity'] = nx.transitivity(G)
        
        # 最大连通子图的指标
        largest_cc = max(nx.connected_components(G), key=len)
        largest_sg = G.subgraph(largest_cc)
        
        metrics['largest_component_size'] = len(largest_cc)
        metrics['average_shortest_path'] = nx.average_shortest_path_length(largest_sg, weight='weight' if weighted else None)
        metrics['diameter'] = nx.diameter(largest_sg, e=None, weight='weight' if weighted else None)
    except:
        # 如果图不连通，某些指标可能计算失败
        pass
    
    # 小世界性指标
    try:
        # 生成随机图进行比较
        random_G = nx.gnm_random_graph(G.number_of_nodes(), G.number_of_edges())
        
        # 计算小世界系数
        C = nx.average_clustering(G)
        C_rand = nx.average_clustering(random_G)
        
        L = nx.average_shortest_path_length(largest_sg)
        L_rand = nx.average_shortest_path_length(random_G)
        
        metrics['small_worldness'] = (C/C_rand) / (L/L_rand)
    except:
        # 如果图不连通，某些指标可能计算失败
        pass
    
    return metrics

