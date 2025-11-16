
import os
import gc
import math

import pandas as pd
import numpy as np

from sklearn.linear_model import SGDRegressor, LinearRegression, Ridge
from sklearn.preprocessing import MinMaxScaler

from sklearn.model_selection import StratifiedKFold, KFold
from sklearn.metrics import log_loss
from sklearn.model_selection import train_test_split

from tqdm import tqdm
import matplotlib.pyplot as plt
import time
import warnings
from sklearn.model_selection import train_test_split
from UI.APP.workspace import getdata

warnings.filterwarnings('ignore')

df = pd.read_csv("random_data.csv")
#  提取特征和目标变量
X = df.drop(columns="Default")
Y = df["Default"]

# 划分训练集和测试集数据


X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.2, random_state=42)


def cv_model(clf, train_x, train_y, test_x, seed=2024):
    # 使用K折交叉验证训练和验证模型
    folds = 5
    kf = KFold(n_splits=folds, shuffle=True, random_state=seed)

    # 初始化oof预测和测试集预测
    oof = np.zeros(train_x.shape[0])
    test_predict = np.zeros(test_x.shape[0])
    cv_scores = []

    # KFold交叉验证
    for i, (train_index, valid_index) in enumerate(kf.split(train_x, train_y)):
        print('************************************ {} ************************************'.format(str(i + 1)))
        trn_x, trn_y, val_x, val_y = train_x.iloc[train_index], train_y[train_index], train_x.iloc[valid_index], \
        train_y[valid_index]

        # 转换数据为lightgbm数据格式
        train_matrix = clf.Dataset(trn_x, label=trn_y)
        valid_matrix = clf.Dataset(val_x, label=val_y)

        # 定义参数
        params = {
            'boosting_type': 'gbdt',  # GBDT算法为基础
            'objective': 'multiclass',  # 多分类任务
            'num_class': 4,  # 设置多分类问题的类别个数
            'num_leaves': 2 ** 5,  # 指定叶子的个数，默认值为31，大会更准,但可能过拟合。最大不能超过2^max_depth
            # 构建弱学习器，对特征随机采样的比例，默认值为1，可以防止过拟合，每次迭代中随机选择80％的参数来建树
            'feature_fraction': 0.8,
            'bagging_fraction': 0.8,  # 每次迭代时用的数据比例，用于加快训练速度和减小过拟合
            'bagging_freq': 4,  # 表示bagging（采样）的频率，0意味着没有使用bagging ，k意味着每k轮迭代进行一次bagging
            'learning_rate': 0.025,
            'seed': seed,
            # 使用线程数，一般设置成-1,使用所有线程。这个参数用来控制最大并行的线程数，如果你希望取得所有CPU的核，那么你就不用管它。
            'nthread': 28,
            'n_jobs': 24,  # 使用多少个线性并构造模型
            'verbose': -1,
            'lambda_l1': 0.4,  # L1正则化权重项，增加此值将使模型更加保守。
            'lambda_l2': 0.5,  # L2正则化权重项，增加此值将使模型更加保守
            # 'device' : 'gpu'
        }

        # 使用训练集数据进行模型训练
        model = clf.train(params,
                          train_set=train_matrix,
                          valid_sets=valid_matrix,
                          num_boost_round=2000,
                          verbose_eval=100,
                          early_stopping_rounds=200)

        # 对验证集进行预测
        val_pred = model.predict(val_x, num_iteration=model.best_iteration)
        test_pred = model.predict(test_x, num_iteration=model.best_iteration)

        oof[valid_index] = val_pred
        test_predict += test_pred / kf.n_splits

        # 计算打印当前折的分数
        score = np.sqrt(mean_squared_erroe(vale_pred, val_y))
        cv_scores.apped(score)
        print(cv_scores)

    return oof, test_predict

