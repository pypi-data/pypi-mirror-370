
from .corr import describe,jb_test,normalize,positivation,pearson
from .linearRegression import ols,gls,hetero_test,vif,backward_stepwise_regression
from .classification import (softmax_classifier, hierarchical_clustering, svm, decisiontree_classify,
                             random_forest_classify, DecisionTree, RandomForest, _replace_cluster_numbers_with_strings)
from .evaluation import calculate_metrics,time_series_decomposition,grey_relation_analysis,entropy_weight_method,ACF
from matplotlib import pyplot as plt
import matplotlib as mpl
# plt.rcParams['font.family'] = ['Times New Roman','Simhei']
# plt.rcParams['axes.unicode_minus']= False
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
__all__=['describe','jb_test','normalize','positivation','pearson','gls','ols']