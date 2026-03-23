from __future__ import annotations

from pathlib import Path
import sys

import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.simulate import SimulationConfig, run_correlation_study, run_power_user_study


FIG_DIR = ROOT / "figures"
FIG_DIR.mkdir(exist_ok=True)


def main() -> None:
    config = SimulationConfig(n_units=4000, pre_repeats=10, n_sims=300, true_effect=0.0, seed=42)

    corr_df = run_correlation_study(config)
    power_df = run_power_user_study(config)

    corr_df.to_csv(FIG_DIR / "correlation_study.csv", index=False)
    power_df.to_csv(FIG_DIR / "power_user_study.csv", index=False)

    plt.figure(figsize=(8.5, 5.2))
    plt.plot(corr_df["rho_empirical"], corr_df["variance_reduction"] * 100, marker="o", linewidth=2)
    plt.xlabel("Корреляция между pre-period и experiment metric")
    plt.ylabel("Снижение дисперсии, %")
    plt.title("Где CUPED помогает: выигрыш растёт вместе с корреляцией")
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.savefig(FIG_DIR / "cuped_variance_reduction.png", dpi=220)
    plt.close()

    plt.figure(figsize=(8.5, 5.2))
    plt.plot(corr_df["rho_empirical"], corr_df["plain_sd"], marker="o", linewidth=2, label="Plain diff")
    plt.plot(corr_df["rho_empirical"], corr_df["cuped_sd"], marker="s", linewidth=2, label="CUPED")
    plt.xlabel("Корреляция между pre-period и experiment metric")
    plt.ylabel("Std оценки treatment effect")
    plt.title("Стандартное отклонение оценки эффекта")
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.legend()
    plt.tight_layout()
    plt.savefig(FIG_DIR / "cuped_sd_vs_correlation.png", dpi=220)
    plt.close()

    ordered = power_df.set_index("method").loc[["Plain diff", "CUPED", "VWE", "CUPED + VWE"]].reset_index()
    plt.figure(figsize=(8.5, 5.2))
    plt.bar(ordered["method"], ordered["rmse"])
    plt.ylabel("RMSE оценки treatment effect")
    plt.title("Когда одной CUPED мало: сценарий с power users")
    plt.grid(True, axis="y", linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.savefig(FIG_DIR / "power_users_rmse.png", dpi=220)
    plt.close()

    plt.figure(figsize=(8.5, 5.2))
    plt.bar(ordered["method"], ordered["sd"])
    plt.ylabel("Std оценки treatment effect")
    plt.title("Сравнение методов в гетерогенном сценарии")
    plt.grid(True, axis="y", linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.savefig(FIG_DIR / "power_users_sd.png", dpi=220)
    plt.close()

    print("Saved figures to", FIG_DIR)
    print("\nCorrelation study:\n", corr_df.round(4).to_string(index=False))
    print("\nPower-user study:\n", power_df.round(4).to_string(index=False))


if __name__ == "__main__":
    main()
