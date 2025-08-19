import numpy as np
import pandas as pd
from collections import Counter
from typing import List, Any, Union, Dict, Tuple, Optional
class DecisionTree:
    def __init__(self) -> None:
        self.tree: Optional[Union[Dict[str, Any], str]] = None  # 树结构（字典或叶节点类别）
    def _entropy(self, y: np.ndarray) -> float:
        """计算信息熵"""
        # 计算每个类别的概率
        probabilities = [count / len(y) for count in Counter(y).values()]
        # 计算信息熵
        entropy = -sum(p * np.log2(p) for p in probabilities if p > 0)
        return entropy

    def _information_gain(self, X: np.ndarray, y: np.ndarray, feature_idx: int) -> float:
        """计算信息增益"""
        # 原始数据集的熵
        original_entropy = self._entropy(y)

        # 根据特征值划分数据集
        feature_values = X[:, feature_idx]
        unique_values = np.unique(feature_values)

        # 计算划分后的加权熵
        weighted_entropy = 0.0
        for value in unique_values:
            # 找出该特征值对应的样本索引
            indices = np.where(feature_values == value)
            # 子集的标签
            y_subset = y[indices]
            # 计算权重和子集的熵
            weighted_entropy += (len(y_subset) / len(y)) * self._entropy(y_subset)

        # 信息增益 = 原始熵 - 划分后的加权熵
        return original_entropy - weighted_entropy

    def _best_feature(self, X: np.ndarray, y: np.ndarray) -> int:
        """选择信息增益最大的特征（返回特征索引）"""
        num_features = X.shape[1]
        best_gain = -1.0
        best_feature_idx = -1

        # 计算每个特征的信息增益
        for i in range(num_features):
            gain = self._information_gain(X, y, i)
            if gain > best_gain:
                best_gain = gain
                best_feature_idx = i

        return best_feature_idx
    def _majority_vote(self, y: np.ndarray) -> Any:
        """多数投票决定叶节点的类别（返回出现次数最多的类别）"""
        return Counter(y).most_common(1)[0][0]#返回y中最多的前1个数的列表的第0个元组的第0个元素
    def _build_tree(self,X: np.ndarray,y: np.ndarray,feature_names: List[str],depth: int = 0,
        max_depth: int = 5):
        if len(y)==1:
            return y[0]
        if depth>=max_depth or not feature_names:
            return self._majority_vote(y)
        best_feature_idx=self._best_feature(X,y)
        best_feature_name=feature_names[best_feature_idx]
        remain_feature=[name for name in feature_names if name != best_feature_name]
        tree={best_feature_name:{}}
        feature_values=X[:,best_feature_idx]
        unique_values=np.unique(feature_values)
        for value in unique_values:
            indice=np.where(feature_values==value)
            x_sub=X[indice]
            y_sub=y[indice]
            x_sub=np.delete(x_sub,best_feature_idx,axis=1)
            tree[best_feature_name][value]=self._build_tree(x_sub,y_sub,remain_feature,depth+1,max_depth)
        return tree


    def fit(
        self,
        X: Union[np.ndarray, pd.DataFrame, List[List[Any]]],
        y: Union[np.ndarray, pd.Series, List[Any]],
        feature_names: List[str],
        max_depth: int = 5
    ):
        """训练决策树模型（无返回值，更新self.tree）"""
        # 确保输入是numpy数组
        X = np.array(X)
        y = np.array(y)
        self.tree = self._build_tree(X, y, feature_names, max_depth=max_depth)

    def _predict_sample(self,sample: pd.Series,tree: Union[Dict[str, Any], Any]):
        if not isinstance(tree,dict):
            return tree
        feature_name=next(iter(tree))
        feature_value=sample[feature_name]
        if feature_value in tree[feature_name]:
            return self._predict_sample(sample,tree[feature_name][feature_value])
        else:
            return next(iter(tree[feature_name].values()))

    def predict(self,X):
        if self.tree is None:
            raise ValueError('模型还未训练，请先调用fit方法')
        if not isinstance(X,pd.DataFrame):
            X=pd.DataFrame(X)
        res=[self._predict_sample(X.iloc[i],self.tree) for i in range(len(X))]
        return np.array(res)

# 示例用法
if __name__ == "__main__":
    # 创建一个简单的数据集：是否去打球
    data: Dict[str, List[str]] = {
        '天气': ['晴', '晴', '阴', '雨', '雨', '雨', '阴', '晴', '晴', '雨', '晴', '阴', '阴', '雨'],
        '温度': ['高', '高', '高', '中', '低', '低', '低', '中', '低', '中', '中', '中', '高', '中'],
        '湿度': ['高', '高', '高', '高', '正常', '正常', '正常', '高', '正常', '正常', '正常', '高', '正常', '高'],
        '风速': ['弱', '强', '弱', '弱', '弱', '强', '强', '弱', '弱', '弱', '强', '强', '弱', '强'],
        '是否打球': ['否', '否', '是', '是', '是', '否', '是', '否', '是', '是', '是', '是', '是', '否']
    }

    df = pd.DataFrame(data)
    X: pd.DataFrame = df.drop('是否打球', axis=1)
    y: pd.Series = df['是否打球']

    # 训练决策树
    dt: DecisionTree = DecisionTree()
    dt.fit(X, y, feature_names=X.columns.tolist(), max_depth=3)

    # 打印决策树结构
    print("决策树结构:")
    import pprint
    pprint.pprint(dt.tree)

    # 测试预测
    test_samples: pd.DataFrame = pd.DataFrame([
        {'天气': '晴', '温度': '低', '湿度': '正常', '风速': '弱'},
        {'天气': '雨', '温度': '中', '湿度': '高', '风速': '强'}
    ])

    predictions: np.ndarray = dt.predict(test_samples)
    print("\n预测结果:")
    for i, pred in enumerate(predictions):
        print(f"样本 {i + 1}: {pred}")