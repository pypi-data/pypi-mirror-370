import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.nn import GCNConv, GATConv
from torch_geometric.utils import negative_sampling
import numpy as np
from sklearn.neighbors import kneighbors_graph
from torch_geometric.data import Data
from tqdm import tqdm

import scanpy as sc
import numpy as np
import torch
from sklearn.neighbors import kneighbors_graph
from torch_geometric.data import Data
from sklearn.metrics import pairwise_distances as pair
import pandas as pd
import copy
from dgl.dataloading import GraphDataLoader
import random
import numpy as np
import pandas as pd
import torch
import dgl
import scanpy as sc
from anndata import AnnData
from tqdm import tqdm
from sklearn.decomposition import PCA
from scipy.sparse import issparse
from torch.utils.data import Dataset, DataLoader
from sklearn.neighbors import NearestNeighbors
from typing import Optional, Union


device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
class Expert(nn.Module):
    """GCN/GAT专家模型"""
    def __init__(self, in_dim, out_dim, expert_type='gcn'):
        super().__init__()
        if expert_type == 'gcn':
            self.conv1 = GCNConv(in_dim, 2*out_dim)
            self.conv2 = GCNConv(2*out_dim, out_dim)
        elif expert_type == 'gat':
            self.conv1 = GATConv(in_dim, out_dim, heads=2, concat=True)
            self.conv2 = GATConv(2*out_dim, out_dim, heads=1, concat=False)
        elif expert_type == 'mlp':
            self.net = nn.Sequential(
                nn.Linear(in_dim, 2*out_dim),
                nn.ReLU(),
                nn.Dropout(0.5),
                nn.Linear(2*out_dim, out_dim)
            )
        self.expert_type = expert_type

    def forward(self, x, edge_index=None):
        if self.expert_type == 'mlp':
            return self.net(x)
        else:
            x = F.relu(self.conv1(x, edge_index))
            x = F.dropout(x, p=0.5, training=self.training)
            return self.conv2(x, edge_index)

class GatingNetwork(nn.Module):
    """门控网络"""
    def __init__(self, in_dim, num_experts):
        super().__init__()
        self.fc = nn.Sequential(
            nn.Linear(in_dim, 128),
            nn.ReLU(),
            nn.Linear(128, num_experts),
            nn.Softmax(dim=-1)
        )
    
    def forward(self, x):
        return self.fc(x)

class MoE_MVG(nn.Module):
    """多视图MoE统一模型"""
    def __init__(self, in_dims, out_dim, expert_types):
        super().__init__()
        self.num_views = len(in_dims)
        self.experts = nn.ModuleList([
            Expert(in_dim, out_dim, etype) 
            for in_dim, etype in zip(in_dims, expert_types)
        ])
        self.gating = GatingNetwork(sum(in_dims), self.num_views)
               
        self.mlp_adapters = nn.ModuleList([
            nn.Linear(in_dim, out_dim) if etype == 'mlp' else None
            for in_dim, etype in zip(in_dims, expert_types)
        ])
    def forward(self, features_list, edge_indices):
        features_list = [x.to(device) for x in features_list]
        edge_indices = [e.to(device) for e in edge_indices]
        # 专家嵌入
        expert_embs = [
            expert(x, edge_index) 
            for expert, x, edge_index in zip(
                self.experts, features_list, edge_indices)
        ]
    # def forward(self, features_list, edge_indices):
    #     features_list = [x.to(device) for x in features_list]
    #     # 修改：仅转换非None的edge_indices
    #     processed_edges = []
    #     for e in edge_indices:
    #         if e is not None:
    #             processed_edges.append(e.to(device))
    #         else:
    #             processed_edges.append(None)

    #     expert_embs = []
    #     for expert, x, edge_index in zip(self.experts, features_list, processed_edges):
    #         if expert.expert_type == 'mlp':
    #             emb = expert(x)  # MLP专家忽略edge_index
    #         else:
    #             emb = expert(x, edge_index)
    #         expert_embs.append(emb)
        # # 2. 基于专家输出计算视图地位嵌入
        # status_embs = torch.cat([emb.mean(dim=0) for emb in expert_embs])
        # gate_weights = self.gating(status_embs.mean(dim=0).unsqueeze(0))
        # 门控权重
        global_feature = torch.cat([
            x.mean(dim=0) for x in features_list
        ]).unsqueeze(0)  # 全局统计特征
        gate_weights = self.gating(global_feature)
        
        # 统一嵌入
        unified_emb = sum(w * emb for w, emb in zip(
            gate_weights.squeeze(), expert_embs))
        
        return unified_emb, gate_weights.squeeze()

    def reconstruction_loss(self, z, edge_index=None):
        if edge_index is None:
            # MLP专家的替代损失（如特征重构）
            return F.mse_loss(z, z.detach()) * 0.1  # 示例损失
        else:
            """视图重构损失"""
            pos_edge_index = edge_index
            neg_edge_index = negative_sampling(pos_edge_index, z.size(0))
            
            pos_score = (z[pos_edge_index[0]] * z[pos_edge_index[1]]).sum(dim=1)
            neg_score = (z[neg_edge_index[0]] * z[neg_edge_index[1]]).sum(dim=1)
            
            pos_loss = F.binary_cross_entropy_with_logits(
                pos_score, torch.ones_like(pos_score))
            neg_loss = F.binary_cross_entropy_with_logits(
                neg_score, torch.zeros_like(neg_score))
            return pos_loss + neg_loss

    def consistency_loss(self, expert_embs):
        """专家一致性损失"""
        loss = 0
        for i in range(len(expert_embs)):
            for j in range(i+1, len(expert_embs)):
                loss += F.mse_loss(expert_embs[i], expert_embs[j])
        return loss / (self.num_views * (self.num_views-1)/2)

    def total_loss(self, features_list, edge_indices):
       # 获取专家嵌入和统一嵌入
        expert_embs = [expert(x, edge_index) for expert, x, edge_index 
                      in zip(self.experts, features_list, edge_indices)]
        unified_emb, _ = self.forward(features_list, edge_indices)
        
        # 计算各视图重构损失
        recon_loss = sum(
            self.reconstruction_loss(unified_emb, edge_index) 
            for edge_index in edge_indices
        )
        
        # 专家一致性损失
        consist_loss = self.consistency_loss(expert_embs)
        
        return recon_loss + 0.5 * consist_loss
      
        # expert_embs = []
        # for expert, x, edge_index in zip(self.experts, features_list, edge_indices):
        #     if expert.expert_type == 'mlp':
        #         emb = expert(x)  # MLP忽略边信息
                              
        #         if adapter is not None:
        #             emb = adapter(emb)
        #     else:
        #         emb = expert(x, edge_index)
        #     expert_embs.append(emb)
        
        # unified_emb, _ = self.forward(features_list, edge_indices)
        
        # recon_loss = 0
        # for emb, edge_index in zip(expert_embs, edge_indices):
        #     if edge_index is not None:  # 仅图结构视图计算重构损失
        #         recon_loss += self.reconstruction_loss(emb, edge_index)
        #     else:  # MLP视图使用特征重构损失
        #         recon_loss += F.mse_loss(emb, x) * 0.1  # 可调整权重
        
        # consist_loss = self.consistency_loss(expert_embs)
        # return recon_loss + 0.5 * consist_loss

    