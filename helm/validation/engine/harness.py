"""
The walk-forward-CV harness (ADR-0001 §6.2). evaluate_loo and
evaluate_multiseed_kfold are the proven template from the 4 completed
equity studies, reused verbatim (short-interest-study/run_analysis.py:31-97)
for Leg A's feature-vs-forward-return regression. Leg B's paired
strategy-comparison (leg_b.py) reuses this harness's SHAPE but adapts the
comparison itself -- see that module's docstring for exactly how and why.
"""
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import KFold, LeaveOneOut


def evaluate_loo(X, y):
    """
    X: (n, 1) feature array. y: (n,) target array. Fits a linear model on
    all-but-one, predicts the held-out point, repeats for every point;
    compares RMSE against a naive baseline (predict the training fold's
    mean) computed the same way.
    """
    X = np.asarray(X, dtype=float)
    y = np.asarray(y, dtype=float)
    n = len(y)
    loo = LeaveOneOut()
    preds_model = np.zeros(n)
    preds_naive = np.zeros(n)
    for train_idx, test_idx in loo.split(X):
        m = LinearRegression().fit(X[train_idx], y[train_idx])
        preds_model[test_idx] = m.predict(X[test_idx])
        preds_naive[test_idx] = y[train_idx].mean()

    rmse_model = float(np.sqrt(np.mean((y - preds_model) ** 2)))
    rmse_naive = float(np.sqrt(np.mean((y - preds_naive) ** 2)))
    return {
        "n": n,
        "rmse_model_loo": round(rmse_model, 6),
        "rmse_naive_loo": round(rmse_naive, 6),
        "beats_naive_baseline": bool(rmse_model < rmse_naive),
        "pct_improvement_vs_naive": round(100 * (rmse_naive - rmse_model) / rmse_naive, 2) if rmse_naive else None,
    }


def evaluate_multiseed_kfold(X, y, n_splits=5, n_seeds=30):
    """
    5-fold CV averaged over n_seeds independent shuffles -- a single seed
    is not a reliable verdict (the catalyst study's fragile result showed
    this directly). Returns pct_seeds_beating_naive, the D-TRADE-021
    seed-agreement statistic.
    """
    X = np.asarray(X, dtype=float)
    y = np.asarray(y, dtype=float)

    beats = []
    pct_improvements = []
    for seed in range(n_seeds):
        kf = KFold(n_splits=n_splits, shuffle=True, random_state=seed)
        rmse_model_folds, rmse_naive_folds = [], []
        for train_idx, test_idx in kf.split(X):
            m = LinearRegression().fit(X[train_idx], y[train_idx])
            pred_model = m.predict(X[test_idx])
            pred_naive = np.full(len(test_idx), y[train_idx].mean())
            rmse_model_folds.append(np.sqrt(np.mean((y[test_idx] - pred_model) ** 2)))
            rmse_naive_folds.append(np.sqrt(np.mean((y[test_idx] - pred_naive) ** 2)))
        rm, rn = float(np.mean(rmse_model_folds)), float(np.mean(rmse_naive_folds))
        beats.append(rm < rn)
        pct_improvements.append(100 * (rn - rm) / rn if rn else 0.0)

    return {
        "n_seeds": n_seeds,
        "n_splits": n_splits,
        "pct_seeds_beating_naive": round(100 * float(np.mean(beats)), 1),
        "mean_pct_improvement_vs_naive": round(float(np.mean(pct_improvements)), 3),
    }
