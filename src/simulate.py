from __future__ import annotations

from dataclasses import dataclass
import numpy as np
import pandas as pd

from .estimators import (
    cuped_adjust,
    diff_in_means,
    estimate_unit_variances,
    effective_sample_size,
    inverse_variance_weights,
    weighted_diff_in_means,
)


@dataclass
class SimulationConfig:
    n_units: int = 4000
    pre_repeats: int = 10
    n_sims: int = 300
    base_mean: float = 10.0
    true_effect: float = 0.0
    seed: int = 42



def simulate_correlated_metric(
    n_units: int,
    rho: float,
    true_effect: float,
    rng: np.random.Generator,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return pre metric x, experiment metric y, treatment assignment.

    The construction gives approximately corr(x, y) = rho.
    """
    treatment = rng.integers(0, 2, size=n_units)
    x = rng.normal(size=n_units)
    independent_noise = rng.normal(size=n_units)
    y0 = rho * x + np.sqrt(max(1e-8, 1 - rho**2)) * independent_noise
    y = y0 + treatment * true_effect
    return x, y, treatment



def run_correlation_study(config: SimulationConfig, rho_grid: list[float] | None = None) -> pd.DataFrame:
    if rho_grid is None:
        rho_grid = [0.0, 0.2, 0.4, 0.6, 0.8, 0.95]

    rng = np.random.default_rng(config.seed)
    rows: list[dict[str, float]] = []

    for rho in rho_grid:
        plain_estimates = []
        cuped_estimates = []
        empirical_corrs = []
        thetas = []

        for _ in range(config.n_sims):
            x, y, treatment = simulate_correlated_metric(
                n_units=config.n_units,
                rho=rho,
                true_effect=config.true_effect,
                rng=rng,
            )
            empirical_corrs.append(float(np.corrcoef(x, y)[0, 1]))
            plain_estimates.append(diff_in_means(y, treatment))
            y_adj, theta = cuped_adjust(y, x)
            cuped_estimates.append(diff_in_means(y_adj, treatment))
            thetas.append(theta)

        plain_sd = float(np.std(plain_estimates, ddof=1))
        cuped_sd = float(np.std(cuped_estimates, ddof=1))
        variance_reduction = 1 - (cuped_sd**2 / plain_sd**2)
        rows.append(
            {
                "rho_target": rho,
                "rho_empirical": float(np.mean(empirical_corrs)),
                "plain_sd": plain_sd,
                "cuped_sd": cuped_sd,
                "variance_reduction": variance_reduction,
                "theta_mean": float(np.mean(thetas)),
            }
        )

    return pd.DataFrame(rows)



def simulate_power_user_dataset(
    n_units: int,
    pre_repeats: int,
    true_effect: float,
    rng: np.random.Generator,
    power_share: float = 0.12,
    stable_sd: float = 1.0,
    power_sd: float = 5.0,
    base_sd: float = 1.2,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    treatment = rng.integers(0, 2, size=n_units)
    is_power = rng.random(size=n_units) < power_share

    baseline = rng.normal(loc=10.0, scale=base_sd, size=n_units)
    unit_sd = np.where(is_power, power_sd, stable_sd)

    pre_matrix = baseline[:, None] + rng.normal(scale=unit_sd[:, None], size=(n_units, pre_repeats))
    x = pre_matrix.mean(axis=1)

    experiment_noise = rng.normal(scale=unit_sd)
    y = baseline + experiment_noise + treatment * true_effect

    return pre_matrix, x, y, treatment



def run_power_user_study(config: SimulationConfig) -> pd.DataFrame:
    rng = np.random.default_rng(config.seed + 1)
    rows: list[dict[str, float]] = []

    plain_estimates = []
    cuped_estimates = []
    vwe_estimates = []
    cuped_vwe_estimates = []
    ess_values = []

    for _ in range(config.n_sims):
        pre_matrix, x, y, treatment = simulate_power_user_dataset(
            n_units=config.n_units,
            pre_repeats=config.pre_repeats,
            true_effect=config.true_effect,
            rng=rng,
        )
        variances = estimate_unit_variances(pre_matrix)
        weights = inverse_variance_weights(variances)
        ess_values.append(effective_sample_size(weights))

        plain_estimates.append(diff_in_means(y, treatment))

        y_cuped, _ = cuped_adjust(y, x)
        cuped_estimates.append(diff_in_means(y_cuped, treatment))

        vwe_estimates.append(weighted_diff_in_means(y, treatment, weights))
        cuped_vwe_estimates.append(weighted_diff_in_means(y_cuped, treatment, weights))

    methods = {
        "Plain diff": plain_estimates,
        "CUPED": cuped_estimates,
        "VWE": vwe_estimates,
        "CUPED + VWE": cuped_vwe_estimates,
    }

    for method, estimates in methods.items():
        est_arr = np.array(estimates)
        rows.append(
            {
                "method": method,
                "mean_estimate": float(est_arr.mean()),
                "sd": float(est_arr.std(ddof=1)),
                "rmse": float(np.sqrt(np.mean((est_arr - config.true_effect) ** 2))),
                "median_abs_error": float(np.median(np.abs(est_arr - config.true_effect))),
                "mean_effective_sample_size": float(np.mean(ess_values)) if "VWE" in method else float(config.n_units),
            }
        )

    return pd.DataFrame(rows)
