import matplotlib.pyplot as plt
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import TensorDataset, DataLoader
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import matplotlib as mpl
from scipy.cluster.hierarchy import linkage, dendrogram, fcluster
import seaborn as sns
from matplotlib.colors import to_hex
from sklearn.decomposition import PCA
import os
import math
from adjustText import adjust_text
from collections import Counter
from typing import List, Any, Union, Dict, Tuple, Optional
from sklearn.model_selection import StratifiedShuffleSplit

mpl.rcParams.update({
    'font.family': ['Times New Roman','Simhei'],
    'font.size': 12,  # 基础字体大小
    'axes.titlesize': 14,  # 标题字体大小
    'axes.labelsize': 12,  # 坐标轴标签字体大小
    'legend.fontsize': 10,  # 图例字体大小
    'xtick.labelsize': 10,  # x轴刻度字体大小
    'ytick.labelsize': 10,  # y轴刻度字体大小
    'lines.linewidth': 1.5,  # 线条宽度
    'lines.markersize': 4,  # 标记点大小（如需添加标记）
    'axes.linewidth': 0.8,  # 坐标轴边框宽度
    'xtick.direction': 'in',
    'ytick.direction': 'in',
    'legend.framealpha': 0.8,  # 图例透明度
})
class Softmax(nn.Module):
    def __init__(self,input_size,output_size,regularization,lambda_reg):
        super().__init__()
        self.linear=nn.Linear(input_size,output_size)
        self.regularization=regularization
        self.lambda_reg=lambda_reg
    def forward(self,x):
        return self.linear(x)
    def compute_reg_loss(self):
        if self.regularization== 'l1':
            return self.lambda_reg*torch.norm(self.linear.weight,p=1)
        elif self.regularization== 'l2':
            return self.lambda_reg*torch.norm(self.linear.weight,p=2)
        return 0.0
def train_model(model:nn.modules,train_loader:DataLoader,x_test:np.ndarray,y_test:np.ndarray,loss_fn,
                optimizer:torch.optim,device,epochs=1000):
    train_loss=[]
    test_loss=[]
    x_test_tensor=torch.tensor(x_test,dtype=torch.float32).to(device)
    y_test_tensor=torch.tensor(y_test,dtype=torch.long).to(device)
    for epoch in range(epochs):
        model.train()
        total_loss=0
        for batch_x,batch_y in train_loader:
            batch_x,batch_y=batch_x.to(device),batch_y.to(device).squeeze().long()
            out_put=model(batch_x)
            ce_loss=loss_fn(out_put,batch_y)
            reg_loss=model.compute_reg_loss()
            loss=ce_loss+reg_loss

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            total_loss+=loss.item()
        cur_loss = total_loss / len(train_loader)
        train_loss.append(cur_loss)
        model.eval()
        with torch.no_grad():
            test_output=model(x_test_tensor)
            loss1=loss_fn(test_output,y_test_tensor)
            loss2=model.compute_reg_loss()
            loss=(loss1+loss2).item()
            test_loss.append(loss)
        if (epoch+1)%100==0:
            print(f'Epoch[{epoch+1}/{epochs}]：训练损失={cur_loss:.4f}  测试损失={loss}')
    plt.figure(figsize=(10,6))
    plt.plot(range(1,epochs+1),train_loss,label='训练损失')
    plt.plot(range(1,epochs+1),test_loss,label='测试损失',linestyle='--')
    plt.legend(frameon=False,fontsize=11)
    plt.grid(alpha=0.3)
    plt.title('训练集与测试集损失')
    plt.savefig('loss_cur.png',dpi=300, bbox_inches='tight')
    plt.show()
    return train_loss,test_loss
def evaluate_model(model:nn.modules,x_test:np.ndarray,y_test:np.ndarray,device):
    model.eval()
    with torch.no_grad():
        x_test_tensor=torch.tensor(x_test,dtype=torch.float32).to(device)
        _,y_pre=torch.max(model(x_test_tensor),dim=1)
        y_pre=y_pre.cpu().numpy()
    accuracy=accuracy_score(y_test,y_pre)
    print(f'准确率:{accuracy:.4f}')
    _confusion_matrix=confusion_matrix(y_test,y_pre)
    print(f'混淆矩阵{_confusion_matrix}')
    print('分类报告')
    _classification_report=classification_report(y_test,y_pre)
    print(_classification_report)
    return {
        '准确率':accuracy,
        '混淆矩阵':_confusion_matrix,
        '分类报告':_classification_report
    }
def softmax_classifier(x:np.ndarray,y:np.ndarray,test_size:float=0.2,random_state:int=42,batch_size:int=32,
                       epochs:int=2000,lr:float=0.01,lambda_reg:float=0.001):
    '''
    softmax分类器，输入n*m的x和n*1的y，输出评估结果
    '''
    if x.ndim!=2:
        raise ValueError('x的维度必须为2')
    elif y.ndim!=1:
        raise ValueError('y的维度必须为1')
    elif len(x)!=len(y):
        raise ValueError('样本数不对应')
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    x_train,x_test,y_train,y_test=train_test_split(x,y,test_size=test_size,random_state=random_state)
    scaler=StandardScaler()
    x_train_scaled=scaler.fit_transform(x_train)
    x_test_scaled=scaler.transform(x_test)
    x_train_tensor=torch.tensor(x_train_scaled,dtype=torch.float32)
    y_train_tensor=torch.tensor(y_train,dtype=torch.float32)
    dataset=TensorDataset(x_train_tensor,y_train_tensor)
    dataloader=DataLoader(dataset,batch_size=batch_size,shuffle=True)
    input_size=x_train_tensor.shape[1]
    output_size= len(np.unique(y))
    model=Softmax(input_size,output_size,'l2',lambda_reg).to(device)
    optimizer=optim.Adam(model.parameters(),lr=lr)
    loss=nn.CrossEntropyLoss()
    train_model(model,dataloader,x_test_scaled,y_test,loss,optimizer,device,epochs)
    evaluate_model(model,x_test_scaled,y_test,device)
def hierarchical_clustering(df: pd.DataFrame, n_clusters: int = 2,
                             title1: str = '层次聚类谱系图',
                             title2: str = None,
                             title3: str = '层次聚类二维散点图(PCA降维)',
                             max_clusters: int = 10):
    '''
    层次聚类(平均组间连接)
    输入: 带 index 的 df，第一列为样本名，后续列为特征
    输出: 谱系图、肘部图、PCA图、聚类中心表格和用户命名聚类结果表格
    '''
    # -------- [1] 拆分样本名与指标 --------
    df = df.copy()
    sample_names = df.iloc[:, 0]
    df_features = df.iloc[:, 1:]

    # -------- [2] 标准化 --------
    scaler = StandardScaler()
    df_scaled = pd.DataFrame(
        scaler.fit_transform(df_features),
        index=sample_names,
        columns=df_features.columns
    )

    # -------- [3] 层次聚类 --------
    Z = linkage(df_scaled, method='ward', metric='euclidean')

    # -------- [4] 绘制谱系图 --------
    n_samples = len(sample_names)
    fig_height = max(6, n_samples * 0.3)
    plt.figure(figsize=(12, fig_height))
    color_palette = sns.color_palette("tab10", 10)
    link_color_func = lambda k: to_hex(color_palette[k % len(color_palette)])

    dendrogram(
        Z,
        labels=sample_names.tolist(),
        orientation='right',
        leaf_font_size=10,
        color_threshold=5,
        above_threshold_color='lightgray',
        link_color_func=link_color_func
    )
    if title1:
        plt.title(title1, fontsize=16, fontweight='bold')
    plt.xlabel('欧式距离', fontsize=13)
    plt.ylabel('样本名称', fontsize=13)
    plt.tight_layout()
    plt.savefig('dendrogram_vertical_adjusted.png', dpi=300, bbox_inches='tight')
    plt.show()

    # -------- [4.5] 肘部图 --------
    print("执行肘部原则分析（仅绘图，不强制修改聚类数）...")
    sse = []
    possible_clusters = range(1, min(max_clusters + 1, len(sample_names)))
    for k in possible_clusters:
        clusters_k = fcluster(Z, t=k, criterion='maxclust')
        cluster_centers = np.zeros((k, df_scaled.shape[1]))
        for i in range(1, k + 1):
            cluster_points = df_scaled[clusters_k == i]
            cluster_centers[i - 1] = cluster_points.mean(axis=0)
        sse_val = sum(np.sum((df_scaled[clusters_k == i + 1].values - cluster_centers[i]) ** 2)
                      for i in range(k))
        sse.append(sse_val)
    plt.figure(figsize=(10, 6))
    plt.plot(possible_clusters, sse, 'bo-')
    plt.xlabel('聚类数量 (k)')
    plt.ylabel('总误差平方和 (SSE)')
    plt.grid(alpha=0.3)
    if title2:
        plt.title(f'{title2}')
    plt.tight_layout()
    plt.savefig('肘部法.png', dpi=300)
    plt.show()

    # -------- [5] 获取簇标签 --------
    clusters = fcluster(Z, t=n_clusters, criterion='maxclust')
    df_result = df.copy()
    df_result['簇标签'] = clusters

    # -------- [5.5] 用户命名聚类标签（提前命名） --------
    unique_clusters = sorted(set(clusters))
    num_class = len(unique_clusters)
    print(f"共分为 {num_class} 类，请用空格隔开按顺序输入每一类的名称(1~{num_class})")
    user_input = input("请输入对应的聚类名称：")
    name_list = user_input.strip().split()

    while len(name_list) != len(unique_clusters):
        print(f"⚠️ 你输入了 {len(name_list)} 个类别名称，但需要 {len(unique_clusters)} 个。请重新输入：")
        user_input = input("请输入对应的聚类名称：")
        name_list = user_input.strip().split()

    cluster_names = {cluster_id: name for cluster_id, name in zip(unique_clusters, name_list)}

    # -------- [6] PCA 降维 --------
    pca = PCA(n_components=2)
    df_pca = pd.DataFrame(
        pca.fit_transform(df_scaled),
        columns=['PC1', 'PC2'],
        index=sample_names
    )
    df_pca['簇标签'] = clusters
    df_pca['聚类名称'] = [cluster_names[c] for c in clusters]

    # -------- [7] 聚类散点图 --------
    plt.figure(figsize=(10, 8))
    palette = sns.color_palette("tab10", len(set(clusters)))
    sns.scatterplot(
        data=df_pca,
        x='PC1', y='PC2',
        hue='聚类名称',
        palette=palette,
        s=50,
        edgecolor='black'
    )
    pca_centers = df_pca.groupby('聚类名称')[['PC1', 'PC2']].mean()
    plt.scatter(pca_centers['PC1'], pca_centers['PC2'],
                s=120, c='black', marker='X', label='聚类中心')

    texts = []
    for i in range(df_pca.shape[0]):
        if abs(df_pca['PC1'].iloc[i]) + abs(df_pca['PC2'].iloc[i]) > 2.5:
            texts.append(
                plt.text(
                    df_pca['PC1'].iloc[i],
                    df_pca['PC2'].iloc[i],
                    sample_names[i],
                    fontsize=8
                )
            )
    adjust_text(texts, arrowprops=dict(arrowstyle='-', color='gray'))

    if title3:
        plt.title(title3, fontsize=14)
    plt.xlabel('PC1', fontsize=12)
    plt.ylabel('PC2', fontsize=12)
    plt.legend(title='聚类名称', fontsize=10, loc='upper right')
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig("PCA降维聚类散点图.png", dpi=600)
    plt.show()

    # -------- [8] 导出聚类中心 --------
    cluster_centers = df_result.groupby('簇标签').mean(numeric_only=True).reset_index()
    center_file = '聚类中心.xlsx'
    cluster_centers.to_excel(center_file, index=False)
    print(f"聚类中心已保存为：{os.path.abspath(center_file)}")
    print(cluster_centers)

    # -------- [9] 输出三列表格 --------
    name_col = df.columns[0]  # 获取样本名列名
    final_df = pd.DataFrame({
        '个案号': range(1, len(sample_names) + 1),
        name_col: sample_names.values,
        '聚类': [cluster_names[c] for c in clusters]
    })
    table_file = '层次聚类结果.xlsx'
    final_df.to_excel(table_file, index=False)
    print(f"聚类结果已保存为：{os.path.abspath(table_file)}")

    return df_result, n_clusters


def _replace_cluster_numbers_with_strings(
        cluster_result_df: pd.DataFrame,
        cluster_column: str = '聚类类别',
        export_path: str = '层次聚类结果.xlsx'
):
    """
    运行时提示用户输入字符串，将聚类结果中的数字类别替换为用户指定的字符串
    参数:
        cluster_result_df: 聚类结果DataFrame，包含序号、样本名和聚类类别列
        cluster_column: 聚类类别列的列名，默认为'聚类类别'
        export_path: 替换后的结果导出路径，为None则不导出
    返回:
        替换类别后的新DataFrame
    """
    # 复制原始DataFrame以避免修改原数据
    result_df = cluster_result_df.copy()

    # 获取唯一的聚类类别并排序
    unique_clusters = sorted(result_df[cluster_column].unique())
    cluster_count = len(unique_clusters)

    # 检查聚类是否从1开始的连续整数
    if unique_clusters != list(range(1, cluster_count + 1)):
        raise ValueError("聚类类别必须是从1开始的连续整数")

    # 提示用户输入对应数量的类别名称
    print(f"检测到共有 {cluster_count} 个聚类类别")
    print(f"请输入 {cluster_count} 个类别名称，以空格分隔（顺序对应 1, 2, ..., {cluster_count}）：")

    # 获取用户输入并处理
    while True:
        user_input = input("> ").strip()
        class_names = user_input.split()

        if len(class_names) == cluster_count:
            break
        else:
            print(f"输入的类别名称数量为 {len(class_names)}，与聚类数量 {cluster_count} 不匹配，请重新输入：")

    # 创建数字到字符串的映射字典
    cluster_mapping = {i + 1: class_names[i] for i in range(cluster_count)}

    # 替换聚类类别
    result_df[cluster_column] = result_df[cluster_column].map(cluster_mapping)

    # 如果指定了导出路径，则导出为Excel
    if export_path:
        # 创建目录（如果需要）
        export_dir = os.path.dirname(export_path)
        if export_dir and not os.path.exists(export_dir):
            os.makedirs(export_dir)
    return result_df

def svm(df: pd.DataFrame,target_column: str,  # 新增参数，指定标签列名
        n_components: int = 2,  # PCA降维维度
        kernel: str = 'rbf',  # SVM核函数，可选 'linear'、'poly'、'rbf' 等
        C: float = 1.0,  # SVM正则化参数
        gamma: float = 'scale'  # SVM核系数，'scale' 为默认缩放方式
        ):
    '''
    SVM支持向量机
    '''
    from sklearn.svm import SVC
    # -------- [1] 拆分样本名、特征与标签 --------
    df = df.copy()
    sample_names = df.iloc[:, 0]  # 假设第一列为样本名称
    feature_columns = [col for col in df.columns if col != target_column and col != df.columns[0]]
    df_features = df[feature_columns]
    df_target = df[target_column]

    # -------- [2] 标准化 --------
    scaler = StandardScaler()
    df_scaled = scaler.fit_transform(df_features)

    # -------- [3] PCA降维（可选，用于可视化） --------
    pca = PCA(n_components=n_components)
    df_pca = pca.fit_transform(df_scaled)
    df_pca = pd.DataFrame(df_pca, columns=[f'PC{i + 1}' for i in range(n_components)], index=sample_names)
    df_pca['标签'] = df_target.values

    # -------- [4] 训练SVM模型 --------
    svm_model = SVC(kernel=kernel, C=C, gamma=gamma)
    svm_model.fit(df_scaled, df_target)

    # -------- [5] 预测（这里用训练集自身预测演示，实际可按需划分测试集） --------
    predictions = svm_model.predict(df_scaled)

    # -------- [6] 可视化分类结果（仅当n_components=2时做二维可视化） --------
    if n_components == 2:
        plt.figure(figsize=(10, 8))
        unique_labels = df_target.unique()
        palette = plt.cm.get_cmap('tab10', len(unique_labels))
        for i, label in enumerate(unique_labels):
            indices = df_target == label
            plt.scatter(df_pca.loc[indices, 'PC1'], df_pca.loc[indices, 'PC2'],
                        color=palette(i), label=f'标签_{label}', s=50, edgecolor='black')

        # 添加部分样本名称标签（离群点或远离中心点等，类似之前逻辑）
        texts = []
        for name in sample_names:
            pc1 = df_pca.loc[name, 'PC1']
            pc2 = df_pca.loc[name, 'PC2']
            if abs(pc1) + abs(pc2) > 2.5:  # 设定阈值筛选要标注的点
                texts.append(plt.text(pc1, pc2, name, fontsize=8))
        adjust_text(texts, arrowprops=dict(arrowstyle='-', color='gray'))

        plt.title('SVM分类结果可视化(PCA降维)', fontsize=14)
        plt.xlabel('PC1', fontsize=12)
        plt.ylabel('PC2', fontsize=12)
        plt.legend(fontsize=10, loc='upper right')
        plt.grid(alpha=0.3)
        plt.tight_layout()
        plt.savefig("svm_classification_scatter.png", dpi=600)
        plt.show()
    # -------- [7] 输出分类结果 --------
    classification_result = df.copy()
    classification_result['SVM预测标签'] = predictions
    classification_result.to_excel('svm_classification_result.xlsx', index=False)
    print(f"分类结果已保存为：{os.path.abspath('svm_classification_result.xlsx')}")

    return classification_result, svm_model
class DecisionTree:
    def __init__(self):
        self.tree=None
        self.node_count = 0
    def _entropy(self,y):
        p=[cnt/len(y) for cnt in Counter(y).values()]
        p=np.array(p)
        res=-np.sum(p*np.log2(p,where=(p>0)))
        return res
    def _infor_gain(self,X,y,feature_idx):
        original_entropy=self._entropy(y)
        feature_values=X[:,feature_idx]
        unique_values=np.unique(feature_values)
        weighted_entropy=0
        for value in unique_values:
            indice=np.where(feature_values==value)
            y_sub=y[indice]
            weighted_entropy=weighted_entropy+len(y_sub)/len(y)*self._entropy(y_sub)
        return original_entropy-weighted_entropy
    def _best_feature_idx(self,X:np.ndarray,y:np.ndarray):
        best_idx=-1
        best_val=-1.0
        cnt=X.shape[1]
        for i in range(cnt):
            cur_gain=self._infor_gain(X,y,i)
            if cur_gain>best_val:
                best_idx=i
                best_val=cur_gain
        return best_idx
    def decide_y_res(self,y):
        return Counter(y).most_common(1)[0][0]
    def build_tree(self,X,y,cur_feature,dep=0,max_dep=10):
        if len(np.unique(y))==1:
            return y[0]
        if dep>=max_dep or not cur_feature:
            return self.decide_y_res(y)
        feature_idx=self._best_feature_idx(X,y)
        feature_name=cur_feature[feature_idx]
        remain_feature=[name for i,name in enumerate(cur_feature) if i!=feature_idx]
        tree={feature_name:{}}
        feature_value=X[:,feature_idx]
        unique_feature=np.unique(feature_value)
        for value in unique_feature:
            indice=np.where(feature_value==value)
            cur_x=X[indice]
            cur_x=np.delete(cur_x,feature_idx,axis=1)
            cur_y=y[indice]
            tree[feature_name][value]=self.build_tree(cur_x,cur_y,remain_feature,dep+1,max_dep)
        return tree
    def fit(self, X, y, feature_names,max_dep=10):
        if self.tree!=None:
            self.tree=None
        X=np.array(X)
        y=np.array(y)
        self.tree=self.build_tree(X, y, feature_names, dep=0, max_dep=max_dep)

    def pre_simgle(self, sample: pd.Series, tree, default_class=None):
        # 首次调用时，计算训练集的多数类作为默认值
        if default_class is None:
            from collections import Counter
            # 收集树中所有叶节点的分类结果
            leaves = []

            def collect_leaves(t):
                if isinstance(t, dict):
                    for child in t.values():
                        collect_leaves(child)
                else:
                    leaves.append(t)

            collect_leaves(self.tree)
            # 取出现次数最多的类作为默认值
            default_class = Counter(leaves).most_common(1)[0][0]

        if not isinstance(tree, dict):
            return tree

        feature_name = next(iter(tree))
        feature_value = sample[feature_name]

        if feature_value in tree[feature_name]:
            # 存在对应分支，继续递归
            return self.pre_simgle(sample, tree[feature_name][feature_value], default_class)
        else:
            # 未见过的特征值，返回默认类
            return default_class

    def predict(self, X: pd.DataFrame):
        if self.tree is None:
            raise ValueError('模型还没训练，请先调用fit')
        if not isinstance(X, pd.DataFrame):
            X = pd.DataFrame(X)
        # 调用pre_simgle时不传递default_class，让其自动计算
        res=[self.pre_simgle(X.iloc[i], self.tree) for i in range(len(X))]
        return res

    def _tree_to_dot(self, tree, dot_str):
        if not isinstance(tree, dict):
            return dot_str, self.node_count
        self.node_count += 1
        current_node = self.node_count
        feature = next(iter(tree))
        dot_str += f'{current_node} [label="{feature}"];\n'
        for value, child in tree[feature].items():
            child_node = self.node_count + 1
            if isinstance(child, dict):
                dot_str, _ = self._tree_to_dot(child, dot_str)
                dot_str += f'{current_node} -> {child_node} [label="{value}"];\n'
            else:
                self.node_count += 1
                child_node = self.node_count
                dot_str += f'{child_node} [label="{child}", shape=box];\n'
                dot_str += f'{current_node} -> {child_node} [label="{value}"];\n'
        return dot_str, self.node_count

    def export_dot(self):
        if self.tree is None:
            raise ValueError('模型尚未训练，请先调用fit方法')
        self.node_count = 0
        dot_str = 'digraph DecisionTree {\n'
        dot_str, _ = self._tree_to_dot(self.tree, dot_str)
        dot_str += '}'
        return dot_str
class RandomForest:
    def __init__(self, n_estimators: int = 10, max_depth: int = 10, max_features: Union[str, int] = 'sqrt'):
        """
        初始化随机森林
        :param n_estimators: 决策树数量
        :param max_depth: 每棵树的最大深度
        :param max_features: 每棵树使用的最大特征数（'sqrt'表示开平方，int表示固定数量）
        """
        self.n_estimators = n_estimators  # 树的数量
        self.max_dep = max_depth        # 树的最大深度
        self.max_features = max_features  # 每棵树使用的最大特征数
        self.trees = []                   # 存储所有决策树
        self.feature_names = None         # 特征名称

    def _bootstrap_sample(self, X: np.ndarray, y: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        #随机选取样本
        n=X.shape[0]
        sample_idx=np.random.choice(n,size=n,replace=True)
        oob_idx=np.setdiff1d(np.arange(n),sample_idx)
        return X[sample_idx],y[sample_idx],oob_idx

    def _random_feature_idx(self,n_total:int):#随机选取特征
        if self.max_features=='sqrt':
            n_feature=int(np.sqrt(n_total))
        elif isinstance(self.max_features,int):
            n_feature=self.max_features
        else:
            n_feature=n_total
        return np.random.choice(n_total,size=n_feature,replace=False)
    def fit(self, X: Union[pd.DataFrame, np.ndarray], y: Union[pd.Series, np.ndarray], feature_names: List[str]):
        X=np.array(X)
        y=np.array(y)
        self.feature_names=feature_names
        feature_num=X.shape[1]
        for _ in range(self.n_estimators):
            X_sub,y_sub,_=self._bootstrap_sample(X,y)
            feature_idx=self._random_feature_idx(feature_num)
            X_sub_=X_sub[:,feature_idx]
            sub_feature_name=[feature_names[i] for i in feature_idx]
            tree=DecisionTree()
            tree.fit(X_sub_, y_sub, sub_feature_name, max_dep=self.max_dep)
            self.trees.append({
                'tree':tree,
                'feature_idx':feature_idx
            })
    def predict(self,X):
        if not self.trees:
            raise ValueError('模型还没训练，请先调用fit方法')
        if not isinstance(X,pd.DataFrame):
            X=pd.DataFrame(X)
        X_np=np.array(X)
        all_pre=[]
        for tree_info in self.trees:
            tree:DecisionTree=tree_info['tree']
            feature_idx=tree_info['feature_idx']
            X_sub=X_np[:,feature_idx]
            X_sub_df=pd.DataFrame(data=X_sub,columns=[self.feature_names[i] for i in feature_idx])
            res=tree.predict(X_sub_df)
            all_pre.append(res)
        all_pre=np.array(all_pre).T
        res=[Counter(pre).most_common(1)[0][0] for pre in all_pre]
        return np.array(res)
def random_forest_classify(df: pd.DataFrame, target_col: str = None,
                           num_trees: int = 20, max_dep: int = 10):
    """
    随机森林分类函数，包含划分训练集和测试集、训练、预测、评估等流程
    :param df: 包含特征列和目标标签列的数据框
    :param target_col: 目标标签列的列名
    :param num_trees: 随机森林中树的数量，默认20
    :param max_dep: 树的最大深度，默认10
    """
    if target_col is None:
        raise ValueError("请指定目标标签列名 target_col")

    X = df.drop(target_col, axis=1)
    y = df[target_col]

    # 2. 分层随机划分训练集和测试集，测试集占比可根据需求调整，这里设为 0.2（即 20% 作为测试集）
    #    StratifiedShuffleSplit 能保证训练集和测试集中各类别分布与原始数据一致
    split = StratifiedShuffleSplit(n_splits=1, test_size=0.2, random_state=42)
    for train_index, test_index in split.split(X, y):
        train_df = df.iloc[train_index]
        test_df = df.iloc[test_index]

    print("训练集大小:", len(train_df))
    print("测试集大小:", len(test_df))

    # 3. 从训练集和测试集中拆分特征和标签
    X_train = train_df.drop(target_col, axis=1)
    y_train = train_df[target_col]
    X_test = test_df.drop(target_col, axis=1)
    y_true = test_df[target_col]

    # 4. 训练随机森林
    rf = RandomForest(n_estimators=num_trees, max_depth=max_dep)
    rf.fit(X_train, y_train, feature_names=X_train.columns.tolist())

    # 5. 展示每棵树的预测结果（投票过程，这里仅示例，实际可完善）
    print("===== 每棵树的预测结果（投票过程） =====")
    all_tree_preds = []
    for tree_idx, tree_info in enumerate(rf.trees):
        tree = tree_info['tree']
        # 这里假设 tree_info['feature_idx'] 是特征索引相关，实际按真实逻辑处理
        feature_idx = tree_info['feature_idx']
        X_sub_df = X_test.iloc[:, feature_idx].copy()
        X_sub_df.columns = [X_test.columns[i] for i in feature_idx]
        # 修复预测时可能出现的"无法分类"错误
        try:
            tree_pred = tree.predict(X_sub_df)
        except ValueError:
            # 若出现未见过的特征值，用训练集多数类填充
            tree_pred = [pd.Series(y_train).value_counts().index[0]] * len(X_test)
        all_tree_preds.append(tree_pred)
        print(f"树 {tree_idx + 1} 的预测：{tree_pred}")

    # 6. 最终预测结果
    final_pred = rf.predict(X_test)
    print("\n===== 最终预测结果（多数投票） =====")
    result_df = pd.DataFrame({
        '样本索引': [f"样本 {i + 1}" for i in range(len(X_test))],
        '特征': [str(X_test.iloc[i].to_dict()) for i in range(len(X_test))],
        '真实标签': y_true,
        '预测标签': final_pred
    })
    print(result_df.to_string(index=False))

    # 7. 混淆矩阵可视化（修正版）
    print("\n===== 混淆矩阵（评估模型性能） =====")
    # 定义标签顺序（确保后续所有操作按此顺序）
    labels = pd.Series(y_true).unique().tolist()
    # 生成混淆矩阵（严格按labels顺序）
    from sklearn.metrics import confusion_matrix
    import seaborn as sns
    import matplotlib.pyplot as plt

    cm = confusion_matrix(y_true, final_pred, labels=labels)

    plt.figure(figsize=(6, 4))
    sns.heatmap(
        cm,
        annot=True,
        fmt='d',
        cmap='Blues',
        # 确保坐标轴标签与labels顺序严格一致
        xticklabels=[f'预测“{label}”' for label in labels],
        yticklabels=[f'真实“{label}”' for label in labels]
    )
    plt.xlabel('预测标签')
    plt.ylabel('真实标签')
    plt.title('随机森林分类混淆矩阵')
    plt.show()
    # 8. 计算并打印查准率和查全率等指标
    from sklearn.metrics import precision_score, recall_score
    precision = precision_score(y_true, final_pred, average='weighted',zero_division=0)
    recall = recall_score(y_true, final_pred, average='weighted',zero_division=0)
    print("\n===== 模型评估指标（查准率、查全率） =====")
    print(f"查准率（Precision）：{precision:.2%}")
    print(f"查全率（Recall）：{recall:.2%}")
def decisiontree_classify(train_df:pd.DataFrame,test_df:pd.DataFrame,taget_col:str,max_dep:int=20):
    '''
    决策树
    做决定任务
    输入：train_df:训练df，包含决策列和影响列 test_df：实际预测df，只有影响列，target.col:决策列名
    '''
    X= train_df.drop(taget_col, axis=1)
    y = train_df[taget_col]
    dt = DecisionTree()
    dt.fit(X, y, feature_names=X.columns.tolist(),max_dep=max_dep)
    print("决策树结构:")
    import pprint
    pprint.pprint(dt.tree)
    predictions: np.ndarray = dt.predict(test_df)
    print("\n预测结果:")
    for i, pred in enumerate(predictions):
        print(f"样本 {i + 1}: {pred}")

if __name__ == '__main__':
    df=pd.read_excel('分析指标.xlsx')
    hierarchical_clustering(df)
