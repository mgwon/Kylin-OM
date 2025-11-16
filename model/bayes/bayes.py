

from bayes_opt import BayesianOptimization
"""
1、贪心调参
2、网格搜索
3、贝叶斯调参     使用前要安装 pip install bayesian-optimization
"""
from sklearn.model_selection import cross_val_score
from sklearn.metrics import make_scorer
from UI.APP.workspace.getdata import get_mysql_data
"""定义优化函数"""

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
            'swappiness': (0, 100),
            "net.core.netdev_max_backlog": (0, 65535),
            "ipv4.tcp_max_syn_backlog": (0, 65535),
            "net.core.somaxconn": (0, 65535),
            "net.ipv4.tcp_keepalive_time": (0, 30),
            "net.ipv4.tcp_keepalive_intvl": (0, 10),
            "net.ipv4.tcp_keepalive_probes": (0, 10),
            "net.ipv4.tcp_fin_timeout": (0, 10),
            "net.ipv4.tcp_tw_reuse": (1, 50),
            "net.ipv4.tcp_tw_recycle": (1, 50),
            "soft nofile": (0, 65535),
            "hard nofile": (0, 65535),
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


        #score = np.sqrt(mean_squared_erroe(vale_pred, val_y))

    return oof, test_predict


def rf_cv_sys(text,swappiness,netdev_max_backlog,tcp_max_syn_backlog,somaxconn,tcp_keepalive_time,tcp_keepalive_intvl,tcp_keepalive_probes,tcp_fin_timeout,tcp_tw_reuse,tcp_tw_recycle,softnofile,hardnofile):
    # 建立模型
    outls,errls,result,IO_w,IO_r,tps,qps=get_mysql_data(text)
    f1 = make_scorer(qps, average='micro')
    # 使用的是5折交叉认证+f1的评定方法
    val = cross_val_score(get_mysql_data(text), X_train, y_train, cv=5, scoring=f1).mean()

    return val

def bayes_sys():
    """定义优化参数"""
    bayes_lgb = BayesianOptimization(
        rf_cv_sys,
        {
            'swappiness': (0, 100),
            "net.core.netdev_max_backlog" :(0,65535),
            "ipv4.tcp_max_syn_backlog": (0, 65535),
            "net.core.somaxconn": (0, 65535),
            "net.ipv4.tcp_keepalive_time": (0, 30),
            "net.ipv4.tcp_keepalive_intvl": (0, 10),
            "net.ipv4.tcp_keepalive_probes": (0, 10),
            "net.ipv4.tcp_fin_timeout": (0, 10),
            "net.ipv4.tcp_tw_reuse":(1,50),
            "net.ipv4.tcp_tw_recycle":(1,50),
            "soft nofile":(0,65535),
            "hard nofile":(0,65535),
        }
    )

    """开始优化"""
    bayes_sys.maximize(n_iter=10)

    """显示优化结果------根据这个进行更改参数"""
    (bayes_sys.max)
