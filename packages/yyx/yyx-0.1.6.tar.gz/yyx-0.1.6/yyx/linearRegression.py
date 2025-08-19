import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.preprocessing import StandardScaler
import statsmodels.api as sm  # 用于显著性检验
from scipy.stats import chi2
import math
from scipy import stats

plt.rcParams['font.family'] = ['Times New Roman', 'Simhei']
plt.rcParams['axes.unicode_minus'] = False
class OLS:
    def __init__(self):
        """初始化线性回归模型"""
        self.model = LinearRegression()
        self.scaler = StandardScaler()
        self.X_train = None
        self.X_test = None
        self.y_train = None
        self.y_test = None
        self.y_pred = None
        self.features = None
        self.target = None
        self.data = None  # 存储原始数据

    def load_data(self, df: pd.DataFrame, target_column):
        """
        从DataFrame加载数据
        参数:
            df: 包含数据的DataFrame
            target_column: 目标变量列名
        """
        try:
            self.data = df.copy()
            print(f"成功读取数据，形状: {self.data.shape}")
            self.target = target_column
            self.features = [col for col in self.data.columns if col != self.target]
            print(f"\n特征变量: {self.features}")
            print(f"目标变量: {self.target}")
            return True
        except Exception as e:
            print(f"读取数据失败: {str(e)}")
            return False

    def preprocess_full_data(self, scale_features=False):
        """预处理全量数据（不划分训练集/测试集，仅处理缺失值）"""
        if self.data is None:
            print("请先加载数据")
            return False
        try:
            # 处理缺失值（与原逻辑一致）
            numeric_cols = self.data.select_dtypes(include=['number']).columns
            self.data[numeric_cols] = self.data[numeric_cols].fillna(self.data[numeric_cols].mean())
            categorical_cols = self.data.select_dtypes(exclude=['number']).columns
            for col in categorical_cols:
                self.data[col] = self.data[col].fillna(self.data[col].mode()[0])

            # 更新全量特征（预处理后）
            self.X = self.data[self.features]
            self.y = self.data[self.target]

            # 标准化（可选，默认关闭）
            if scale_features:
                self.X = self.scaler.fit_transform(self.X)
            return True
        except Exception as e:
            print(f"全量数据预处理失败: {str(e)}")
            return False

    def train_full(self, scale_features=False):
        """
        全量训练函数：使用所有数据训练OLS（不划分测试集，不评估）
        存储statsmodels结果用于后续残差提取
        """
        # 预处理全量数据
        if not self.preprocess_full_data(scale_features=scale_features):
            return False
        try:
            # 用statsmodels训练全量数据（带截距项）
            X_full_sm = sm.add_constant(self.X)
            model_sm = sm.OLS(self.y, X_full_sm)
            self.full_sm_results = model_sm.fit()
            print("全量数据OLS训练完成（用于残差提取）")
            return True
        except Exception as e:
            print(f"全量模型训练失败: {str(e)}")
            return False
    def preprocess_data(self, test_size=0.2, random_state=42, scale_features=True):
        """
        数据预处理：处理缺失值、划分训练集和测试集、特征缩放
        参数:
            test_size: 测试集比例
            random_state: 随机种子，保证结果可复现
            scale_features: 是否对特征进行标准化
        """
        if self.data is None:
            print("请先加载数据")
            return False
        try:
            print("\n缺失值使用每个指标的均值...")
            numeric_cols = self.data.select_dtypes(include=['number']).columns
            self.data[numeric_cols] = self.data[numeric_cols].fillna(self.data[numeric_cols].mean())
            categorical_cols = self.data.select_dtypes(exclude=['number']).columns
            for col in categorical_cols:
                self.data[col] = self.data[col].fillna(self.data[col].mode()[0])

            X = self.data[self.features]
            y = self.data[self.target]

            # 划分时保留索引，方便后续statsmodels使用
            self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
                X, y, test_size=test_size, random_state=random_state, stratify=None
            )

            if scale_features:
                print("标准化特征...")
                self.X_train_scaled = self.scaler.fit_transform(self.X_train)
                self.X_test_scaled = self.scaler.transform(self.X_test)
            else:
                self.X_train_scaled = self.X_train
                self.X_test_scaled = self.X_test

            print(f"训练集大小: {self.X_train.shape[0]} 样本")
            print(f"测试集大小: {self.X_test.shape[0]} 样本")
            return True
        except Exception as e:
            print(f"数据预处理失败: {str(e)}")
            return False

    def train(self):
        """训练线性回归模型（sklearn 版，用于预测）"""
        if self.X_train_scaled is None or self.y_train is None:
            print("请先预处理数据")
            return False

        try:
            self.model.fit(self.X_train_scaled, self.y_train)
            print("\n模型系数:")
            for i, feature in enumerate(self.features):
                print(f"{feature}: {self.model.coef_[i]:.4f}")
            print(f"截距: {self.model.intercept_:.4f}")
            return True
        except Exception as e:
            print(f"模型训练失败: {str(e)}")
            return False

    def train_statsmodels(self, cov_type='nonrobust',cov_kwds=None):
        """用 statsmodels 训练，用于显著性检验（使用未标准化的训练集）"""
        if self.X_train is None or self.y_train is None:
            print("请先预处理数据")
            return None  # 改为返回None，与后续判断一致
        try:
            X_train_sm = sm.add_constant(self.X_train.copy())
            y_train_sm = self.y_train.copy()
            model_sm = sm.OLS(y_train_sm, X_train_sm)
            results = model_sm.fit(cov_type=cov_type,cov_kwds=cov_kwds)
            return results  # 关键：返回训练结果对象
        except Exception as e:
            print(f"statsmodels 模型训练/检验失败: {str(e)}")
            return None

    def evaluate(self):
        """评估模型性能"""
        if self.X_test_scaled is None or self.y_test is None:
            print("请先预处理数据")
            return False

        try:
            self.y_pred = self.model.predict(self.X_test_scaled)

            mse = mean_squared_error(self.y_test, self.y_pred)
            rmse = np.sqrt(mse)
            mae = mean_absolute_error(self.y_test, self.y_pred)
            r2 = r2_score(self.y_test, self.y_pred)

            # 整理成 DataFrame
            eval_df = pd.DataFrame({
                "指标": ["均方误差 (MSE)", "均方根误差 (RMSE)", "平均绝对误差 (MAE)", "决定系数 (R²)"],
                "值": [mse, rmse, mae, r2],
            })
            eval_df=eval_df.transpose()
            eval_df.to_excel('模型评估指标.xlsx')
            return eval_df
        except Exception as e:
            print(f"模型评估失败: {str(e)}")
            return False

    def visualize(self, feature_index=0):
        """
        拆分可视化：分别绘制「预测值vs实际值」和「残差图」
        参数:
            feature_index: 单变量回归时指定特征索引（多变量无实际作用）
        """
        if self.y_pred is None:
            print("请先评估模型")
            return False
        try:
            # 1. 绘制「预测值 vs 实际值」图
            plt.figure(figsize=(8, 6))
            plt.scatter(self.y_test, self.y_pred, alpha=0.6)
            plt.plot([self.y_test.min(), self.y_test.max()],
                     [self.y_test.min(), self.y_test.max()], 'r--')
            plt.xlabel('实际值')
            plt.ylabel('预测值')
            plt.title('预测值 vs 实际值')
            plt.tight_layout()
            plt.show()

            # 2. 绘制「残差图」
            plt.figure(figsize=(8, 6))
            residuals = self.y_test - self.y_pred
            plt.scatter(self.y_pred, residuals, alpha=0.6)
            plt.axhline(y=0, color='r', linestyle='--')
            plt.xlabel('预测值')
            plt.ylabel('残差')
            plt.title('残差图')
            plt.tight_layout()
            plt.show()

            # 3. 若为单变量回归，额外绘制「特征-目标变量」散点图
            if len(self.features) == 1 and self.X_test_scaled.ndim == 2:
                plt.figure(figsize=(8, 6))
                plt.scatter(self.X_test_scaled[:, feature_index], self.y_test, alpha=0.6, label='实际值')
                plt.scatter(self.X_test_scaled[:, feature_index], self.y_pred, alpha=0.6, color='r', label='预测值')
                plt.xlabel(self.features[feature_index])
                plt.ylabel(self.target)
                plt.title(f'{self.features[feature_index]} vs {self.target}')
                plt.legend()
                plt.tight_layout()
                plt.show()

            return True
        except Exception as e:
            print(f"可视化失败: {str(e)}")
            return False

    def get_coef_table(self):
        """整理 sklearn 模型系数为 DataFrame（用 pd.concat 替代 append）"""
        if not hasattr(self.model, 'coef_'):
            print("模型未训练或无系数")
            return None

        # 构造特征系数的DataFrame
        coef_data = [{
            "特征": feature,
            "系数值": coef
        } for feature, coef in zip(self.features, self.model.coef_)]
        coef_df = pd.DataFrame(coef_data)

        # 构造截距的DataFrame（单独一行）
        intercept_df = pd.DataFrame([{
            "特征": "截距",
            "系数值": self.model.intercept_
        }])

        # 用pd.concat拼接（替代append）
        coef_df = pd.concat([coef_df, intercept_df], ignore_index=True)
        coef_df.to_excel('模型系数.xlsx')
        return coef_df

    def get_significance_table(self, sm_results):
        """从 statsmodels 结果中提取显著性（p 值）表格"""
        if sm_results is None:
            print("未获取 statsmodels 结果")
            return None
        # 提取系数、p 值等信息
        sm_summary = sm_results.summary2().tables[1]
        # 重命名列，方便理解
        sm_summary = sm_summary.rename(columns={
            'Coef.': '系数',
            'Std.Err.': '标准误',
            't': 't 值',
            'P>|t|': 'p 值',
            '[0.025': '95% CI 下限',
            '0.975]': '95% CI 上限'
        })
        sm_summary.to_excel('OLS显著性检验.xlsx')
        return sm_summary
def ols(df:pd.DataFrame,target_column:str,cov_type='nonrobust',cov_kwds=None):#给定df和目标列的名称进行ols，输出参数、显著性检验和评估指标
    lr_model = OLS()
    lr_model.load_data(df, target_column)
    # 2. 数据预处理
    lr_model.preprocess_data(test_size=0.2, random_state=42)
    # 3. 训练 sklearn 模型（用于预测、系数展示）
    lr_model.train()
    # 4. 训练 statsmodels 模型（用于显著性检验）
    sm_results = lr_model.train_statsmodels(cov_type=cov_type,cov_kwds=None)
    # 5. 评估模型
    eval_df = lr_model.evaluate()
    # 6. 整理并输出表格
    coef_table = lr_model.get_coef_table()
    significance_table = lr_model.get_significance_table(sm_results)
    print("\n模型系数")
    print(coef_table)
    if significance_table is not None:
        print("\n显著性检验")
        print(significance_table)
        significance_table.to_excel('显著性检验.xlsx')
    print("\n评估指标表格")
    print(eval_df)
    lr_model.visualize()
def backward_stepwise_regression(df: pd.DataFrame, target_col: str, alpha=0.05, file_name="逐步回归结果.xlsx"):
    """
    向后逐步回归函数，输出最终特征的参数估计值并保存为Excel
    """
    # 1. 初始化OLS模型并加载数据
    ols_model = OLS()
    if not ols_model.load_data(df, target_col):
        raise ValueError("数据加载失败，无法执行逐步回归")

    # 2. 预处理数据（关闭标准化，保留原始尺度便于解读系数）
    if not ols_model.preprocess_data(scale_features=False, test_size=0.2, random_state=42):
        raise ValueError("数据预处理失败，无法执行逐步回归")

    # 3. 初始特征集
    current_features = ols_model.features.copy()
    print(f"初始特征集: {current_features}")
    print(f"训练集大小: {ols_model.X_train.shape[0]} 样本")
    print(f"测试集大小: {ols_model.X_test.shape[0]} 样本")

    # 4. 逐步移除不显著特征
    while True:
        prev_feature_count = len(current_features)
        if not current_features:
            break

        # 更新模型特征和数据
        ols_model.features = current_features
        ols_model.X_train = ols_model.X_train[current_features]
        ols_model.X_test = ols_model.X_test[current_features]

        # 训练模型
        sm_results = ols_model.train_statsmodels()
        if sm_results is None:
            break

        # 提取p值（排除截距）
        p_values = sm_results.pvalues.drop('const', errors='ignore')
        valid_features = [feat for feat in current_features if feat in p_values.index]
        if not valid_features:
            break

        # 找到最不显著的特征
        max_p_feature = max(valid_features, key=lambda x: p_values[x])
        max_p_value = p_values[max_p_feature]

        # 判断是否移除
        if max_p_value > alpha:
            current_features.remove(max_p_feature)
            print(f"移除特征: {max_p_feature} (p值: {max_p_value:.4f})")
        else:
            break

        # 防止无限循环
        if len(current_features) == prev_feature_count:
            break

    # 5. 训练最终模型并提取参数
    final_params = None
    if current_features:
        # 更新模型为最终特征集
        ols_model.features = current_features
        ols_model.X_train = ols_model.X_train[current_features]
        final_sm_results = ols_model.train_statsmodels()

        if final_sm_results is not None:
            # 提取参数（包含截距）
            final_params = final_sm_results.summary2().tables[1].reset_index()
            final_params = final_params.rename(columns={
                'index': '特征',
                'Coef.': '系数估计值',
                'Std.Err.': '标准误',
                't': 't值',
                'P>|t|': 'p值',
                '[0.025': '95%CI下限',
                '0.975]': '95%CI上限'
            })
            # 将截距项的特征名改为中文
            final_params['特征'] = final_params['特征'].replace('const', '截距')

    # 6. 输出结果
    print("\n===== 最终模型参数估计 =====")
    if final_params is not None:
        print(final_params.to_string(index=False))  # 打印参数表
        # 保存为Excel
        final_params.to_excel(file_name, index=False)
        print(f"\n结果已保存至: {file_name}")
    else:
        print("未保留有效特征，无法生成参数表")

    return current_features, final_params
#Stock and Watson (2011)推荐，在大多数情况下应该使用“OLS+稳健标准误”
class GLS:
    def __init__(self):
        """初始化广义最小二乘模型（GLS）"""
        self.scaler = StandardScaler()
        self.X_train = None  # 未标准化训练特征（用于statsmodels GLS）
        self.X_test = None   # 未标准化测试特征
        self.X_train_scaled = None  # 标准化训练特征（用于预测）
        self.X_test_scaled = None   # 标准化测试特征
        self.y_train = None
        self.y_test = None
        self.y_pred = None
        self.features = None
        self.target = None
        self.data = None
        self.gls_results = None  # 存储statsmodels GLS的训练结果
        self.weights = None  # 权重矩阵（用于GLS）

    def load_data(self, df: pd.DataFrame, target_column):
        """加载数据并指定目标变量"""
        try:
            self.data = df.copy()
            print(f"成功读取数据，形状: {self.data.shape}")
            self.target = target_column
            self.features = [col for col in self.data.columns if col != self.target]
            print(f"\n特征变量: {self.features}")
            print(f"目标变量: {self.target}")
            return True
        except Exception as e:
            print(f"读取数据失败: {str(e)}")
            return False

    def preprocess_data(self, test_size=0.2, random_state=42, scale_features=False):  # 关闭标准化
        """数据预处理：不标准化，统一用原始特征"""
        if self.data is None:
            print("请先加载数据")
            return False
        try:
            print("\n缺失值使用均值填充...")
            numeric_cols = self.data.select_dtypes(include=['number']).columns
            self.data[numeric_cols] = self.data[numeric_cols].fillna(self.data[numeric_cols].mean())
            categorical_cols = self.data.select_dtypes(exclude=['number']).columns
            for col in categorical_cols:
                self.data[col] = self.data[col].fillna(self.data[col].mode()[0])

            X = self.data[self.features]
            y = self.data[self.target]

            # 划分数据集
            self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
                X, y, test_size=test_size, random_state=random_state, stratify=None
            )

            # 不标准化，直接使用原始特征值
            self.X_train_scaled = self.X_train.values  # 仅作为预测时的别名，实际是原始值
            self.X_test_scaled = self.X_test.values

            print(f"训练集大小: {self.X_train.shape[0]} 样本")
            print(f"测试集大小: {self.X_test.shape[0]} 样本")
            return True
        except Exception as e:
            print(f"数据预处理失败: {str(e)}")
            return False

    def estimate_weights(self, method='ols_residuals'):
        """
        估计GLS权重矩阵（用于处理异方差）
        method: 权重估计方法
            - 'ols_residuals': 用OLS残差的方差倒数作为权重（常用）
            - 'identity': 恒等矩阵（退化为OLS）
        """
        if self.X_train is None or self.y_train is None:
            print("请先预处理数据")
            return False

        try:
            if method == 'ols_residuals':
                # 先用OLS估计残差，再用残差方差的倒数作为权重（处理异方差）
                X_ols = sm.add_constant(self.X_train)
                ols_model = sm.OLS(self.y_train, X_ols).fit()
                residuals = ols_model.resid
                residual_var = np.square(residuals)
                # 避免除以0，加极小值
                self.weights = np.diag(1.0 / (residual_var + 1e-10))
                print("使用OLS残差方差的倒数作为GLS权重（处理异方差）")
            elif method == 'identity':
                # 恒等矩阵，等价于OLS
                self.weights = np.eye(len(self.y_train))
                print("使用恒等矩阵作为权重（等价于OLS）")
            return True
        except Exception as e:
            print(f"权重矩阵估计失败: {str(e)}")
            return False

    def train(self, weight_method='ols_residuals'):
        """训练GLS模型（基于statsmodels，同时支持预测）"""
        if self.X_train is None or self.y_train is None:
            print("请先预处理数据")
            return False

        try:
            # 估计权重矩阵
            if not self.estimate_weights(method=weight_method):
                return False

            # 构造GLS模型（加截距项）
            X_gls = sm.add_constant(self.X_train)
            model_gls = sm.GLS(self.y_train, X_gls, sigma=self.weights)
            self.gls_results = model_gls.fit()

            # 输出GLS系数（原始特征尺度）
            print("\nGLS模型系数（原始特征尺度）:")
            for feature, coef in zip(['截距'] + self.features, self.gls_results.params):
                print(f"{feature}: {coef:.4f}")
            return True
        except Exception as e:
            print(f"GLS模型训练失败: {str(e)}")
            return False

    def evaluate(self):
        """预测时使用原始特征（与训练尺度一致）"""
        if self.gls_results is None or self.X_test is None:
            print("请先训练模型或预处理数据")
            return False

        try:
            # 直接用原始测试特征预测（加截距项）
            X_test_gls = sm.add_constant(self.X_test)  # 使用未标准化的原始特征
            self.y_pred = self.gls_results.predict(X_test_gls)

            # 计算评估指标（后续不变）
            mse = mean_squared_error(self.y_test, self.y_pred)
            rmse = np.sqrt(mse)
            mae = mean_absolute_error(self.y_test, self.y_pred)
            r2 = r2_score(self.y_test, self.y_pred)

            eval_df = pd.DataFrame({
                "指标": ["均方误差 (MSE)", "均方根误差 (RMSE)", "平均绝对误差 (MAE)", "决定系数 (R²)"],
                "值": [mse, rmse, mae, r2],
            }).transpose()
            eval_df.to_excel('GLS模型评估指标.xlsx')
            return eval_df
        except Exception as e:
            print(f"模型评估失败: {str(e)}")
            return False

    def visualize(self, feature_index=0):
        """可视化预测结果（与OLS版本保持一致）"""
        if self.y_pred is None:
            print("请先评估模型")
            return False

        try:
            # 1. 预测值 vs 实际值
            plt.figure(figsize=(8, 6))
            plt.scatter(self.y_test, self.y_pred, alpha=0.6, label='GLS预测')
            plt.plot([self.y_test.min(), self.y_test.max()],
                     [self.y_test.min(), self.y_test.max()], 'r--', label='理想线')
            plt.xlabel('实际值')
            plt.ylabel('预测值')
            plt.title('GLS: 预测值 vs 实际值')
            plt.legend()
            plt.tight_layout()
            plt.show()

            # 2. 残差图
            residuals = self.y_test - self.y_pred
            plt.figure(figsize=(8, 6))
            plt.scatter(self.y_pred, residuals, alpha=0.6)
            plt.axhline(y=0, color='r', linestyle='--')
            plt.xlabel('预测值')
            plt.ylabel('残差')
            plt.title('GLS: 残差图')
            plt.tight_layout()
            plt.show()

            # 3. 单变量特征散点图（若适用）
            if len(self.features) == 1 and self.X_test_scaled.ndim == 2:
                plt.figure(figsize=(8, 6))
                plt.scatter(self.X_test_scaled[:, feature_index], self.y_test, alpha=0.6, label='实际值')
                plt.scatter(self.X_test_scaled[:, feature_index], self.y_pred, alpha=0.6, color='r', label='GLS预测值')
                plt.xlabel(self.features[feature_index])
                plt.ylabel(self.target)
                plt.title(f'GLS: {self.features[feature_index]} vs {self.target}')
                plt.legend()
                plt.tight_layout()
                plt.show()
            return True
        except Exception as e:
            print(f"可视化失败: {str(e)}")
            return False

    def get_coef_table(self):
        """提取GLS模型系数表格（含截距）"""
        if self.gls_results is None:
            print("请先训练GLS模型")
            return None

        coef_data = [
            {"特征": '截距', "系数值": self.gls_results.params['const']}
        ] + [
            {"特征": feature, "系数值": coef}
            for feature, coef in zip(self.features, self.gls_results.params[self.features])
        ]
        coef_df = pd.DataFrame(coef_data)
        coef_df.to_excel('GLS模型系数.xlsx')
        return coef_df

    def get_significance_table(self):
        """提取GLS显著性检验表格（p值、置信区间等）"""
        if self.gls_results is None:
            print("请先训练GLS模型")
            return None

        # 提取statsmodels结果并整理
        sm_summary = self.gls_results.summary2().tables[1]
        sm_summary = sm_summary.rename(columns={
            'Coef.': '系数',
            'Std.Err.': '标准误',
            't': 't 值',
            'P>|t|': 'p 值',
            '[0.025': '95% CI 下限',
            '0.975]': '95% CI 上限'
        })
        sm_summary.to_excel('GLS显著性检验.xlsx')
        return sm_summary
def gls(df: pd.DataFrame, target_column: str, weight_method='ols_residuals'):
    """
    执行GLS回归并输出结果
    参数:
        weight_method: 权重计算方法（'ols_residuals'处理异方差，'identity'等价于OLS）
    """
    gls_model = GLS()
    gls_model.load_data(df, target_column)
    gls_model.preprocess_data(test_size=0.2, random_state=42)
    gls_model.train(weight_method=weight_method)  # 训练GLS模型
    eval_df = gls_model.evaluate()  # 评估指标
    coef_table = gls_model.get_coef_table()  # 系数表格
    significance_table = gls_model.get_significance_table()  # 显著性检验

    # 打印结果
    print("\n===== GLS模型系数 =====")
    print(coef_table)
    if significance_table is not None:
        print("\n===== GLS显著性检验 =====")
        print(significance_table)
    print("\n===== GLS评估指标 =====")
    print(eval_df)
    gls_model.visualize()
def _plot_residuals_vs_features(X_full, residuals):
    n_vars = X_full.shape[1]
    var_names = X_full.columns
    residual_squared = np.square(residuals)

    # 决定图像排列方式
    if int(math.sqrt(n_vars))**2 == n_vars:
        # 完全平方数，正方形排列
        n_rows = n_cols = int(math.sqrt(n_vars))
    elif n_vars <= 5:
        # 少于5个变量，单行排列
        n_rows = 1
        n_cols = n_vars
    else:
        # 不是完全平方数，尽量排成接近正方形，每行最多 5 个
        n_cols = min(5, math.ceil(math.sqrt(n_vars)))
        n_rows = math.ceil(n_vars / n_cols)

    # 创建图像和子图
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(4 * n_cols, 4 * n_rows))
    axes = np.array(axes).reshape(-1)  # 展平以统一处理

    for i, col in enumerate(var_names):
        ax = axes[i]
        ax.scatter(X_full[col], residual_squared, alpha=0.5)
        ax.set_xlabel(col)
        ax.set_ylabel("残差平方")
        ax.set_title(f"{col} vs 残差²")

    # 删除多余的子图（如果变量数量不足）
    for j in range(n_vars, len(axes)):
        fig.delaxes(axes[j])

    plt.tight_layout()
    plt.show()
def hetero_test(df: pd.DataFrame, target_col: str):
    """
    异方差检验函数（基于全量OLS训练结果）
    参数:
        df: 输入数据集（DataFrame）
        target_col: 目标变量列名
    返回:
        dict: 包含怀特检验和布罗施-帕甘检验的p值 {'white_p': ..., 'bp_p': ...}
    """
    # 1. 初始化OLS模型并全量训练
    ols_model = OLS()
    if not ols_model.load_data(df, target_col):
        raise ValueError("数据加载失败，无法进行检验")
    # 全量训练（不标准化，保留原始特征尺度）
    if not ols_model.train_full(scale_features=False):
        raise ValueError("全量OLS训练失败，无法进行检验")

    # 2. 提取全量训练的残差和特征
    residuals = ols_model.full_sm_results.resid  # 全量残差
    X_full = ols_model.X  # 全量特征（预处理后）
    # 3. bp检验
    def breusch_pagan():
        X_aux = sm.add_constant(X_full)  # 辅助回归自变量（含截距）
        y_aux = np.square(residuals)  # 残差平方作为因变量
        bp_model = sm.OLS(y_aux, X_aux).fit()
        n = len(y_aux)
        r2 = bp_model.rsquared
        stat = n * r2  # 检验统计量
        df = X_aux.shape[1] - 1  # 自由度
        p_value = 1 - chi2.cdf(stat, df)
        return round(p_value, 4)
    # 4. 怀特检验
    def white():
        X = X_full.copy() if isinstance(X_full, pd.DataFrame) else pd.DataFrame(X_full)
        features = []
        # 原始特征
        features.extend([X[col] for col in X.columns])
        # 平方项
        features.extend([X[col] ** 2 for col in X.columns])
        # 交互项（i < j）
        for i, col1 in enumerate(X.columns):
            for j, col2 in enumerate(X.columns[i + 1:], i + 1):
                features.append(X[col1] * X[col2])
        # 辅助回归自变量（含截距）
        X_aux = pd.concat(features, axis=1)
        X_aux = sm.add_constant(X_aux)
        y_aux = np.square(residuals)
        # 拟合辅助回归
        white_model = sm.OLS(y_aux, X_aux).fit()
        n = len(y_aux)
        r2 = white_model.rsquared
        stat = n * r2  # 检验统计量
        df = X_aux.shape[1] - 1  # 自由度
        p_value = 1 - chi2.cdf(stat, df)
        return round(p_value, 4)
    print(f"BP检验p值：{breusch_pagan()}\nwhite检验p值：{white()}")
    _plot_residuals_vs_features(X_full, residuals)
def vif(df: pd.DataFrame, target_col: str,file_name='VIF.xlsx') -> pd.DataFrame:
    """
    计算所有特征的方差膨胀因子（VIF），检测多重共线性
    参数:
        df: 输入数据集（包含特征和目标变量）
        target_col: 目标变量列名（用于排除目标变量，只计算特征的VIF）
    返回:
        DataFrame: 包含特征名称和对应VIF值的表格，按VIF降序排列
    """
    # 1. 提取特征（排除目标变量）
    features = [col for col in df.columns if col != target_col]
    X = df[features].copy()

    # 2. 检查数据类型，确保均为数值型
    non_numeric = X.select_dtypes(exclude=['number']).columns.tolist()
    if non_numeric:
        raise ValueError(f"特征包含非数值类型，无法计算VIF：{non_numeric}")

    # 3. 处理缺失值（用均值填充，避免VIF计算失败）
    X = X.fillna(X.mean())

    # 4. 计算每个特征的VIF
    vif_data = []
    for feature in features:
        # 以当前特征为因变量，其他特征为自变量构建回归模型
        X_others = X.drop(columns=[feature])
        X_others = sm.add_constant(X_others)  # 添加截距项
        model = sm.OLS(X[feature], X_others).fit()

        # VIF = 1 / (1 - R²)，其中R²是当前特征对其他特征的回归决定系数
        r_squared = model.rsquared
        vif = 1 / (1 - r_squared) if (1 - r_squared) != 0 else float('inf')
        vif_data.append({"特征": feature, "VIF值": round(vif, 2)})

    # 5. 整理结果并按VIF降序排列
    vif_df = pd.DataFrame(vif_data).sort_values(by="VIF值", ascending=False)
    print(f'总体VIF:{max(vif_df['VIF值'])}')
    vif_df=vif_df.set_index('特征').T
    vif_df.to_excel(file_name)
class ridge(OLS):
    def __init__(self, alpha=1.0, n_bootstrap=1000):
        super().__init__()
        self.model = Ridge(alpha=alpha)
        self.alpha = alpha
        self.n_bootstrap = n_bootstrap  # Bootstrap抽样次数

    def train_statsmodels(self, cov_type='nonrobust', cov_kwds=None):
        """重写为返回训练数据，用于Bootstrap"""
        if self.X_train_scaled is None or self.y_train is None:
            print("请先预处理数据")
            return None
        # 返回训练数据，用于后续Bootstrap计算
        return (self.X_train_scaled, self.y_train)

    def get_significance_table(self, train_data):
        """使用Bootstrap方法计算显著性检验结果"""
        if train_data is None:
            print("请先训练模型")
            return None
        try:
            X_train, y_train = train_data
            n_samples = X_train.shape[0]
            n_features = X_train.shape[1]

            # 存储每次Bootstrap的系数
            bootstrap_coefs = []

            # 添加截距项对应的列（全为1）
            X_with_intercept = np.hstack([np.ones((n_samples, 1)), X_train])

            # 进行Bootstrap抽样
            for _ in range(self.n_bootstrap):
                # 有放回抽样
                indices = np.random.choice(n_samples, size=n_samples, replace=True)
                X_boot = X_with_intercept[indices]
                y_boot = y_train.iloc[indices]  # 处理Series类型

                # 训练岭回归模型（带截距项）
                boot_model = Ridge(alpha=self.alpha, fit_intercept=False)
                boot_model.fit(X_boot, y_boot)
                bootstrap_coefs.append(boot_model.coef_)

            # 计算系数的统计量
            coefs = np.array(bootstrap_coefs)
            mean_coef = np.mean(coefs, axis=0)  # 平均系数（估计值）
            std_err = np.std(coefs, axis=0)  # 标准误（系数标准差）
            t_stats = mean_coef / std_err  # t统计量
            p_values = 2 * (1 - stats.norm.cdf(np.abs(t_stats)))  # p值（双侧检验）

            # 计算95%置信区间
            ci_lower = mean_coef - 1.96 * std_err
            ci_upper = mean_coef + 1.96 * std_err

            # 构造结果表格
            sig_table = pd.DataFrame({
                "特征": ["截距"] + self.features,
                "系数": mean_coef.round(4),
                "标准误": std_err.round(4),
                "t 值": t_stats.round(4),
                "p 值": p_values.round(4),
                "95% CI 下限": ci_lower.round(4),
                "95% CI 上限": ci_upper.round(4)
            })
            sig_table.to_excel('岭回归显著性检验.xlsx', index=False)
            return sig_table
        except Exception as e:
            print(f"提取岭回归显著性结果失败: {e}")
            return None
def run_regression(df: pd.DataFrame, target_column: str,model_class=OLS, model_kwargs={},
                   cov_type='nonrobust', cov_kwds=None):
    """通用回归函数，支持OLS和岭回归的显著性检验"""
    # 初始化模型
    model = model_class(**model_kwargs)

    # 执行流程
    model.load_data(df, target_column)
    model.preprocess_data()
    model.train()
    train_results = model.train_statsmodels(cov_type=cov_type, cov_kwds=cov_kwds)
    eval_df = model.evaluate()
    model.visualize()
    coef_table = model.get_coef_table()
    sig_table = model.get_significance_table(train_results)

    # 输出结果
    print("\n模型系数:")
    print(coef_table)

    if sig_table is not None:
        print("\n显著性检验:")
        print(sig_table)

    print("\n评估指标:")
    print(eval_df)

    return model
if __name__ == '__main__':
    df=pd.read_excel('DATA6.xls').iloc[:,1:12]
    run_regression(df,'y', model_class=ridge, model_kwargs={'alpha':0.5})
    # ols(df,'y')


