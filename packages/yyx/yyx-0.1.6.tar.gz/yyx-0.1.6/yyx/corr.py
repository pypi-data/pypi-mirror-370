import numpy as np
import pandas as pd
from scipy.stats import jarque_bera
import seaborn as sns
from matplotlib import pyplot as plt
from scipy import stats
def _calculate_stats(column):
    mean_val = column.mean()
    std_error = column.std() / np.sqrt(len(column))
    median_val = column.median()
    std_dev = column.std()
    var_val = column.var()
    kurtosis_val = column.kurt()
    skewness_val = column.skew()
    range_val = column.max() - column.min()
    min_val = column.min()
    max_val = column.max()
    sum_val = column.sum()
    # 按照顺序拼接结果
    stats_result = [
        mean_val,
        std_error,
        median_val,
        std_dev,
        var_val,
        kurtosis_val,
        skewness_val,
        range_val,
        min_val,
        max_val,
        sum_val
    ]
    return stats_result
def describe(df:pd.DataFrame)->pd.DataFrame:#描述性统计
    all_results = {}
    for col in df.columns:
        column_data = df[col]
        stats_result = _calculate_stats(column_data)
        all_results[col] = stats_result

    index_names = [
        '平均',
        '标准误差',
        '中位数',
        '标准差',
        '方差',
        '峰度',
        '偏度',
        '区域',
        '最小值',
        '最大值',
        '求和'
    ]
    return pd.DataFrame(all_results, index=index_names)
def jb_test(df, alpha=0.05):#JB检验
    jb_results = []
    numeric_cols = df.select_dtypes(include=['number']).columns
    for col in numeric_cols:
        data = df[col].dropna()  # 去除缺失值
        if len(data) >= 3:  # JB检验需要至少3个数据点
            jb_stat, p_value = jarque_bera(data)
            jb_results.append([col, round(jb_stat, 4), round(p_value, 4)])
        else:
            jb_results.append([col, None, None, "数据量不足"])  # 数据量不足时标记
    result_df = pd.DataFrame(
        jb_results,
        columns=['列名', 'JB统计量', 'p值']
    )
    result_df.transpose().to_excel('JB检验.xlsx', index=True,header=False)
def normalize(data_array:np.ndarray)->np.ndarray:#标准化
    normalized_array = np.zeros_like(data_array, dtype=np.float64)  # 初始化结果数组
    n_samples, n_features = data_array.shape  # 获取样本数和指标数

    for j in range(n_features):
        col_data = data_array[:, j]  # 取出第 j 列数据
        if (col_data < 0).any():  # 检查该列是否有负数
            # 情况 1：列中存在负数 → 用 (x_ij - max_j) / (max_j - min_j) 标准化
            max_val = np.max(col_data)
            min_val = np.min(col_data)
            denominator = max_val - min_val
            if denominator == 0:
                normalized_col = np.zeros_like(col_data)
            else:
                normalized_col = (col_data - max_val) / denominator
        else:
            # 情况 2：列中无负数 → 用 x_ij / sqrt(Σx_ij²) 标准化
            sum_sq = np.sum(col_data ** 2)
            if sum_sq == 0:
                normalized_col = np.zeros_like(col_data)
            else:
                normalized_col = col_data / np.sqrt(sum_sq)
        normalized_array[:, j] = normalized_col  # 将标准化后的列存入结果数组
    return normalized_array
def positivation(data_array: np.ndarray) -> np.ndarray:
    transformed = data_array.copy().astype(np.float64)
    n_cols = transformed.shape[1]
    print(f"检测到数据包含 {n_cols} 列指标（1-{n_cols}）")
    while True:
        cols_input = input("请输入需要正向化的列索引（用逗号分隔，如'1,3'，没有请输入0）：")
        if cols_input == '0':
            return data_array
        try:
            cols_to_process = [int(c.strip()) - 1 for c in cols_input.split(',')]
            if all(0 <= c < n_cols for c in cols_to_process):
                break
            else:
                print(f"错误：列索引必须在 1-{n_cols} 范围内，请重新输入")
        except ValueError:
            print("输入格式错误，请使用逗号分隔的整数（如'1,3'）")
    def min_to_max(col_data):
        """极小型→极大型：x' = max - x"""
        max_val = np.max(col_data)
        return max_val - col_data
    def near_best_value(col_data, best_val):
        """越接近最佳值越好：x' = 1 - |x - best_val| / (max(|x - best_val|))"""
        diff = np.abs(col_data - best_val)
        max_diff = np.max(diff)
        return 1 - diff / max_diff if max_diff != 0 else np.ones_like(col_data)
    def best_interval(col_data, a, b):
        max_val = np.max(col_data)
        min_val = np.min(col_data)
        below = (col_data - min_val) / (a - min_val) if (a - min_val) != 0 else 0
        above = (max_val - col_data) / (max_val - b) if (max_val - b) != 0 else 0
        return np.where(
            col_data < a, below,
            np.where(col_data > b, above, 1)
        )
    for col in cols_to_process:
        # 显示时转回1开始的索引，方便用户理解
        print(f"\n处理第 {col + 1} 列：")
        print(f"当前列数据预览：{transformed[:5, col]}...")
        # 选择正向化方法
        while True:
            print("\n请选择正向化方法：")
            print("1. 极小型→极大型（值越小越好→值越大越好）")
            print("2. 指定最佳值（越接近该值越好）")
            print("3. 指定最佳区间（在区间内最佳）")
            print("4. 极大型保持不变（已为正向指标，仅确认）")

            method = input("输入方法编号（1-4）：").strip()
            if method in ['1', '2', '3', '4']:
                break
            print("无效输入，请输入1-4之间的数字")

        # 应用选择的方法
        col_data = transformed[:, col]
        if method == '1':
            transformed[:, col] = min_to_max(col_data)
            print("已应用：极小型→极大型转换")

        elif method == '2':
            while True:
                try:
                    best_val = float(input("请输入最佳值："))
                    break
                except ValueError:
                    print("请输入有效的数字")
            transformed[:, col] = near_best_value(col_data, best_val)
            print(f"已应用：接近 {best_val} 越好")

        elif method == '3':
            while True:
                try:
                    a = float(input("请输入区间下限a："))
                    b = float(input("请输入区间上限b（b > a）："))
                    if b > a:
                        break
                    print("错误：上限b必须大于下限a")
                except ValueError:
                    print("请输入有效的数字")
            transformed[:, col] = best_interval(col_data, a, b)
            print(f"已应用：在区间 [{a}, {b}] 内最佳")

        elif method == '4':
            print("确认：该列已是极大型指标，不做转换")

    return transformed
def pearson(df,jb_alpha=0.05):
    '''
    df没有索引
    '''
    # 描述性统计
    df = df.fillna(0)
    describe_res = describe(df)
    describe_res.to_excel('描述性统计结果.xlsx')
    # 绘制散点图
    sns.pairplot(df)
    # sns.pairplot(df1, hue="花叶类")
    plt.show()
    # 绘制相关性系数热力图
    plt.figure(figsize=(9, 6), dpi=100)
    sns.heatmap(df.corr().round(2), annot=True, cmap='Reds')
    plt.show()
    # JB检验
    jb_test(df,alpha=jb_alpha)
    # 假设检验p值法
    correlation_matrix = df.corr(method='pearson')
    print("皮尔逊相关系数矩阵：")
    print(correlation_matrix.round(4))  # 保留4位小数
    # 创建一个空的DataFrame来存储p值
    p_value_matrix = pd.DataFrame(index=df.columns, columns=df.columns)
    for i in df.columns:
        for j in df.columns:
            if i != j:  # 避免计算自身与自身的相关性
                corr, p_value = stats.pearsonr(df[i], df[j])
                # 根据p值大小添加星号标记
                if p_value < 0.01:
                    p_value_str = f"{p_value:.3f}***"  # p<0.01高度显著
                elif p_value < 0.05:
                    p_value_str = f"{p_value:.3f}**"  # p<0.05显著
                elif p_value < 0.1:
                    p_value_str = f"{p_value:.3f}"
                else:
                    p_value_str = f"{p_value:.3f}"  # 不显著
                p_value_matrix.loc[i, j] = p_value_str
            else:
                p_value_matrix.loc[i, j] = "0.0"  # 自身与自身的p值为0
    p_value_matrix.to_excel('假设检验p值.xlsx')
    print('表注复制这句话\n注：***、**分别表示1%，5%的显著水平')

