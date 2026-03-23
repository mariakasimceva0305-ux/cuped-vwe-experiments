from __future__ import annotations

import numpy as np


def diff_in_means(y: np.ndarray, treatment: np.ndarray) -> float:
    """Average treatment effect estimate via difference in means."""
    t = treatment.astype(bool)
    return float(y[t].mean() - y[~t].mean())



def cuped_adjustment_theta(y: np.ndarray, x: np.ndarray) -> float:
    """Return the CUPED coefficient theta = cov(Y, X) / var(X)."""
    x_centered = x - x.mean()
    y_centered = y - y.mean()
    var_x = np.mean(x_centered ** 2)
    if var_x == 0:
        return 0.0
    cov_xy = np.mean(x_centered * y_centered)
    return float(cov_xy / var_x)



def cuped_adjust(y: np.ndarray, x: np.ndarray) -> tuple[np.ndarray, float]:
    """Return CUPED-adjusted outcome and fitted theta."""
    theta = cuped_adjustment_theta(y, x)
    y_adj = y - theta * (x - x.mean())
    return y_adj, theta



def estimate_unit_variances(pre_matrix: np.ndarray, min_variance: float = 1e-6) -> np.ndarray:
    """Estimate per-unit variances from repeated pre-period observations."""
    if pre_matrix.ndim != 2:
        raise ValueError("pre_matrix must have shape (n_units, n_repeats)")
    variances = np.var(pre_matrix, axis=1, ddof=1)
    return np.maximum(variances, min_variance)



def inverse_variance_weights(variances: np.ndarray) -> np.ndarray:
    weights = 1.0 / variances
    return weights / weights.mean()



def weighted_mean(values: np.ndarray, weights: np.ndarray) -> float:
    return float(np.sum(values * weights) / np.sum(weights))



def weighted_diff_in_means(y: np.ndarray, treatment: np.ndarray, weights: np.ndarray) -> float:
    t = treatment.astype(bool)
    return weighted_mean(y[t], weights[t]) - weighted_mean(y[~t], weights[~t])



def effective_sample_size(weights: np.ndarray) -> float:
    s1 = np.sum(weights)
    s2 = np.sum(weights ** 2)
    if s2 == 0:
        return 0.0
    return float((s1 ** 2) / s2)
