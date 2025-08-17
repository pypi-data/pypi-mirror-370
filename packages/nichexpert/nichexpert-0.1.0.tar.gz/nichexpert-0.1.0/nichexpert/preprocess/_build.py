import copy
from ._utils import *
from dgl.dataloading import GraphDataLoader
from sklearn.neighbors import kneighbors_graph
import numpy as np
import torch 

def prepare_data(
        adata: AnnData,
        choose_views: Optional[list] = None,
        k_cutoff_graph: int = 20,
        mik_graph: int = 5,
        verbose: bool = True
):
    if verbose:
        print("-------Constructing graph for each view...")
    if choose_views is None:
        choose_views = ['X_cn_norm', 'X_data', 'X_data_nbr']
    else:
        missing_views = [view for view in choose_views if view not in adata.obsm.keys()]
        if missing_views:
            raise ValueError(f"The following views are missing in adata.obsm: {', '.join(missing_views)}")

    for view in choose_views:
        feat = adata.obsm[view]
        g = construct_graph(np.array(feat), k_cutoff_graph, mik_graph)
        graph_name = 'g_' + view
        adata.uns[graph_name] = g
    if verbose:
        print("Constructing done.")

    return adata


def prepare_data_batch(
        adata: AnnData,
        choose_views: Optional[list] = None,
        batch_num: int = 4,
        k_cutoff_graph: int = 20,
        mik_graph: int = 5,
        verbose: bool = True
):
    # create batch idx
    random.seed(123)
    batch_size = adata.shape[0] // batch_num
    left_cell_num = adata.shape[0] % batch_num
    add_cell_num = batch_num - left_cell_num
    add_cell = random.choices(range(adata.shape[0]), k=add_cell_num)

    # bug fixed
    if left_cell_num < batch_size:
        batch_idx = random_split(adata.shape[0], batch_size)
    else:
        batch_idx = random_split2(adata.shape[0], batch_num)

    if left_cell_num > 0:
        for i in range(left_cell_num):
            batch_idx[i].append(batch_idx[len(batch_idx) - 1][i])
        batch_idx = batch_idx[:-1]

        batch_idx_new = copy.deepcopy(batch_idx)
        for i in range(len(add_cell)):
            batch_idx_new[i + left_cell_num].append(add_cell[i])
    else:
        batch_idx_new = copy.deepcopy(batch_idx)

    adata.uns['batch_idx'] = batch_idx_new

    # check
    if choose_views is None:
        choose_views = ['X_cn_norm', 'X_data', 'X_data_nbr']
    else:
        missing_views = [view for view in choose_views if view not in adata.obsm.keys()]
        if missing_views:
            raise ValueError(f"The following views are missing in adata.obsm: {', '.join(missing_views)}")

    feat = [adata.obsm[view] for view in choose_views]
    g_list = [[] for _ in range(len(feat))]

    if verbose:
        print("-------Constructing batch-graph for each view...")

    for i in tqdm(range(batch_num)):
        for j in range(len(feat)):
            feat_tmp = feat[j][batch_idx_new[i]]
            g_tmp = construct_graph(np.array(feat_tmp), k_cutoff_graph, mik_graph)
            g_list[j].append(g_tmp)

    if verbose:
        print("Constructing done.")

    mydataset = myDataset(g_list)
    dataloader = GraphDataLoader(mydataset, batch_size=1, shuffle=False, pin_memory=True)
    adata.uns['dataloader'] = dataloader

    return adata


def prepare_knn_graphs(
        adata: AnnData,
        choose_views: list,
        k: int = 6,
        verbose: bool = True
):
    """
    Preprocess and construct KNN graphs for specified views, storing results in adata.uns
    
    Parameters
    ----------
    adata : AnnData
        AnnData object containing view data in obsm
    choose_views : list
        List of keys in adata.obsm specifying the views to process
    k : int, optional
        Number of nearest neighbors (default: 6)
    verbose : bool, optional
        Whether to print progress messages (default: True)
    """
    if verbose:
        print("-------Constructing KNN graphs for all views-------")
    
    for view in choose_views:
        if view not in adata.obsm:
            raise ValueError(f"View '{view}' not found in adata.obsm")
        
        if verbose:
            print(f"Processing view: {view}")
        
        # Data preparation
        X = adata.obsm[view]
        if issparse(X):
            X = X.toarray()
        X = X.astype(np.float32)
        
        # KNN graph construction
        if X.shape[0] > 50000:
            if verbose:
                print(f"Large dataset ({X.shape[0]} cells), using batch processing...")
            
            rows, cols = [], []
            batch_size = 5000
            for i in range(0, X.shape[0], batch_size):
                batch_X = X[i:i+batch_size]
                knn_batch = kneighbors_graph(
                    batch_X, n_neighbors=k, 
                    mode='connectivity', 
                    include_self=False
                )
                coo = knn_batch.tocoo()
                rows.extend(coo.row + i)
                cols.extend(coo.col + i)
            edge_index = np.vstack([rows, cols])
        else:
            knn = kneighbors_graph(
                X, n_neighbors=k, 
                mode='connectivity', 
                include_self=False
            )
            edge_index = np.array(knn.nonzero())

        edge_index = torch.tensor(np.array(knn.nonzero()), dtype=torch.long)
        # # Create DGL graph
        # g = dgl.graph((edge_index[0], edge_index[1]))
        # g.ndata['feat'] = torch.tensor(X, dtype=torch.float32)
        
        # Store in adata.uns
        graph_name = f'g_{view}'
        adata.uns[graph_name] = edge_index


        # features = torch.tensor(X, dtype=torch.float32)
        # feature_name = f'{view}'
        # adata.uns[feature_name] = features

        if verbose:
            print(f"  Graph '{graph_name}' constructed: {X.shape[0]} nodes, {edge_index.shape[1]} edges")
    
    if verbose:
        print("All graphs constructed and stored in adata.uns")
# def prepare_knn_graph(adata, view_key, k=6):
#     """为指定视图构建KNN图"""
#     X = adata.obsm[view_key]
    
#     # 构建KNN邻接矩阵
#     knn = kneighbors_graph(X, n_neighbors=k, mode='connectivity', include_self=False)
    
#     # 转换为edge_index格式
#     edge_index = torch.tensor(np.array(knn.nonzero()), dtype=torch.long)
    
#     # 节点特征
#     features = torch.tensor(X, dtype=torch.float32)
    
#     return features, edge_index

# def prepare_knn_graph(
#         adata: AnnData,
#         view_key: str,
#         k: int = 6,
#         verbose: bool = True
# ) :
#     """
#     Construct KNN graph for specified view with memory-efficient processing
    
#     Parameters
#     ----------
#     adata : AnnData
#         AnnData object containing view data in obsm
#     view_key : str
#         Key in adata.obsm for the target view matrix
#     k : int, optional
#         Number of nearest neighbors (default: 6)
#     verbose : bool, optional
#         Whether to print progress messages (default: True)
        
#     Returns
#     -------
#     Tuple[torch.Tensor, torch.Tensor]
#         Node feature matrix and edge index in PyTorch format
#     """
    
#     # Input validation
#     if verbose:
#         print(f"-------Constructing KNN graph for view '{view_key}'...")
    
#     if view_key not in adata.obsm:
#         raise ValueError(f"View '{view_key}' not found in adata.obsm")
    
#     # Data preparation
#     X = adata.obsm[view_key]
#     if issparse(X):
#         X = X.toarray()  # Convert sparse to dense if needed
#     X = X.astype(np.float32)  # Standardize precision
    
#     # Memory-efficient KNN construction
#     if X.shape[0] > 50000:  # Batch processing for large datasets
#         if verbose:
#             print(f"Large dataset detected ({X.shape[0]} cells), using batch processing...")
        
#         # Initialize COO format storage
#         rows, cols = [], []
        
#         # Process in batches
#         batch_size = 5000
#         for i in range(0, X.shape[0], batch_size):
#             batch_X = X[i:i+batch_size]
#             knn_batch = kneighbors_graph(
#                 batch_X, 
#                 n_neighbors=k, 
#                 mode='connectivity', 
#                 include_self=False
#             )
#             coo = knn_batch.tocoo()
            
#             # Adjust indices to global scope
#             rows.extend(coo.row + i)
#             cols.extend(coo.col + i)
            
#         edge_index = np.vstack([rows, cols])
#     else:
#         # Direct computation for small datasets
#         knn = kneighbors_graph(
#             X, 
#             n_neighbors=k, 
#             mode='connectivity', 
#             include_self=False
#         )
#         edge_index = np.array(knn.nonzero())
    
#     # Convert to PyTorch tensors
#     features = torch.tensor(X, dtype=torch.float32)
#     edge_index = torch.tensor(edge_index, dtype=torch.long)
    
#     if verbose:
#         print(f"Graph constructed: {features.shape[0]} nodes, {edge_index.shape[1]} edges")
    
#     return features, edge_index