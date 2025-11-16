from bayes_opt import BayesianOptimization

"""定义优化参数"""
bayes_lgb = BayesianOptimization(
    rf_cv_lgb,
    {
        'num_leaves': (10, 200),
        'max_depth': (3, 20),
        'bagging_fraction': (0.5, 1.0),
        'feature_fraction': (0.5, 1.0),
        'bagging_freq': (0, 100),
        'min_data_in_leaf': (10, 100),
        'min_child_weight': (0, 10),
        'min_split_gain': (0.0, 1.0),
        'reg_alpha': (0.0, 10),
        'reg_lambda': (0.0, 10),
    }
)

"""开始优化"""
bayes_lgb.maximize(n_iter=10)

"""显示优化结果------根据这个进行更改参数"""
bayes_lgb.max
