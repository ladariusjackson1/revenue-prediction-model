#!/usr/bin/env python3
"""Write the chart images used in the portfolio README.

Each chart is drawn from that project's training code. The headline number
printed on the chart is checked against models/metrics.json before the file
is saved. Run from the repository root:

    python scripts/export_figures.py
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

ROOT = Path(__file__).resolve().parents[1]
IMAGE_DIR = ROOT / "docs" / "images"

PLOTS = (
    "plot_daily_sales",
    "plot_churn",
    "plot_lead_score",
    "plot_segments",
    "plot_expenses",
    "plot_mrr",
    "plot_noshow",
)


def _style():
    import matplotlib.pyplot as plt

    plt.rcParams.update(
        {
            "figure.facecolor": "#f4f7f8",
            "axes.facecolor": "#ffffff",
            "axes.edgecolor": "#d5dee3",
            "axes.labelcolor": "#0b1f2a",
            "axes.titlecolor": "#0b1f2a",
            "xtick.color": "#3a5563",
            "ytick.color": "#3a5563",
            "text.color": "#0b1f2a",
            "font.size": 11,
            "axes.grid": True,
            "grid.color": "#e6eef2",
            "grid.linewidth": 0.8,
            "axes.axisbelow": True,
        }
    )
    return plt


def _save(fig, name: str) -> None:
    IMAGE_DIR.mkdir(parents=True, exist_ok=True)
    path = IMAGE_DIR / name
    fig.savefig(path, dpi=140, bbox_inches="tight")
    print(path)


def _use_project(project: str) -> None:
    sys.path.insert(0, str(ROOT / "projects" / project))


def _use_src(project: str) -> None:
    sys.path.insert(0, str(ROOT / "projects" / project / "src"))


def plot_daily_sales() -> None:
    plt = _style()
    _use_project("01-daily-sales-forecast")
    from src.forecast import (
        METRICS_PATH,
        add_features,
        holdout_predictions,
        load_daily_revenue,
        run_evaluation,
    )

    saved = json.loads(METRICS_PATH.read_text())
    result = run_evaluation(add_features(load_daily_revenue()))
    if result["test"] != saved["test"]:
        raise SystemExit("Daily sales test scores did not match metrics.json")
    table = holdout_predictions(result)
    forest_mae = saved["test"]["random_forest"]["mae"]
    naive_mae = saved["test"]["seasonal_naive"]["mae"]

    fig, ax = plt.subplots(figsize=(10.2, 5.2))
    ax.plot(table["date"], table["actual"], color="#0b1f2a", lw=1.6, label="Actual")
    ax.plot(
        table["date"],
        table["random_forest"],
        color="#0d8a6a",
        lw=1.6,
        label="Random forest",
    )
    ax.plot(
        table["date"],
        table["seasonal_naive"],
        color="#1f6f8b",
        lw=1.2,
        ls="--",
        label="Seasonal naive",
    )
    ax.set_title(
        f"Daily net sales, held-out window  {saved['periods']['test']['start']}"
        f" to {saved['periods']['test']['end']}\n"
        f"Random forest MAE £{forest_mae:,.2f}   ·   "
        f"seasonal naive MAE £{naive_mae:,.2f}"
    )
    ax.set_ylabel("Net sales (GBP)")
    ax.legend(frameon=False, ncol=3, loc="upper left")
    fig.autofmt_xdate()
    fig.tight_layout()
    _save(fig, "01-daily-sales-holdout.png")


def plot_churn() -> None:
    plt = _style()
    import numpy as np

    _use_src("02-customer-churn")
    from train import METRICS, train

    payload = train()
    saved = json.loads(METRICS.read_text())
    if payload["test_metrics"] != saved["test_metrics"]:
        raise SystemExit("Churn metrics did not match metrics.json")

    labels = ["ROC-AUC", "Average precision", "F1 at 0.5"]
    keys = ["roc_auc", "avg_precision", "f1"]
    colors = {"logreg": "#0d8a6a", "rf": "#1f6f8b", "gbm": "#d97706"}
    x = np.arange(len(labels))
    width = 0.24
    fig, ax = plt.subplots(figsize=(10.2, 5.2))
    for i, row in enumerate(payload["test_metrics"]):
        offset = (i - 1) * width
        bars = ax.bar(
            x + offset,
            [row[key] for key in keys],
            width,
            color=colors[row["model"]],
            label=row["model"],
        )
        for bar in bars:
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                height + 0.015,
                f"{height:.3f}",
                ha="center",
                va="bottom",
                fontsize=8,
                color="#3a5563",
            )
    selected = payload["selected_model"]
    selected_auc = next(row["roc_auc"] for row in payload["test_metrics"] if row["model"] == selected)
    ax.set_xticks(x, labels)
    ax.set_ylim(0, 1.08)
    ax.set_ylabel("Score")
    ax.set_title(
        f"Customer churn, 25% stratified holdout  ·  n={payload['n_rows']:,}"
        f"  ·  churn rate {payload['churn_rate']:.2%}\n"
        f"Selected by ROC-AUC: {selected} ({selected_auc:.4f})"
    )
    ax.legend(frameon=False, ncol=3)
    fig.tight_layout()
    _save(fig, "02-churn-model-scores.png")


def plot_lead_score() -> None:
    plt = _style()
    _use_src("03-lead-scoring")
    import joblib
    import pandas as pd
    from sklearn.metrics import average_precision_score, roc_auc_score, roc_curve
    from sklearn.model_selection import train_test_split

    from train import CAT, DATA, METRICS, MODEL, NUM, train

    payload = train()
    saved = json.loads(METRICS.read_text())
    if payload != saved:
        raise SystemExit("Lead-score metrics did not match metrics.json")
    df = pd.read_csv(DATA)
    x, y = df[NUM + CAT], df["won"]
    _, x_test, _, y_test = train_test_split(x, y, test_size=0.25, random_state=0, stratify=y)
    pipe = joblib.load(MODEL)["model"]
    proba = pipe.predict_proba(x_test)[:, 1]
    auc = round(float(roc_auc_score(y_test, proba)), 4)
    ap = round(float(average_precision_score(y_test, proba)), 4)
    if auc != payload["roc_auc"] or ap != payload["avg_precision"]:
        raise SystemExit(f"Lead-score redraw {auc}, {ap} != saved metrics")
    fpr, tpr, _ = roc_curve(y_test, proba)
    fig, ax = plt.subplots(figsize=(7.4, 5.6))
    ax.plot(fpr, tpr, color="#0d8a6a", lw=2, label=f"Gradient boosting (AUC {auc:.4f})")
    ax.plot([0, 1], [0, 1], color="#9aafb8", lw=1, ls="--", label="Chance")
    ax.set_xlabel("False positive rate")
    ax.set_ylabel("True positive rate")
    ax.set_title(
        f"Lead scoring ROC  ·  n={payload['n_rows']:,}"
        f"  ·  win rate {payload['win_rate']:.2%}\n"
        f"Average precision {ap:.4f}"
    )
    ax.legend(frameon=False, loc="lower right")
    fig.tight_layout()
    _save(fig, "03-lead-score-roc.png")


def plot_segments() -> None:
    plt = _style()
    _use_src("04-customer-segmentation")
    import pandas as pd
    from sklearn.cluster import KMeans
    from sklearn.metrics import silhouette_score
    from sklearn.preprocessing import StandardScaler

    from train import DATA, FEATURES, METRICS, train

    payload = train()
    saved = json.loads(METRICS.read_text())
    if payload["silhouette"] != saved["silhouette"] or payload["cluster_sizes"] != saved["cluster_sizes"]:
        raise SystemExit("Segmentation metrics did not match metrics.json")
    df = pd.read_csv(DATA)
    scaled = StandardScaler().fit_transform(df[FEATURES])
    labels = KMeans(n_clusters=payload["k"], n_init=20, random_state=0).fit_predict(scaled)
    silhouette = round(float(silhouette_score(scaled, labels)), 4)
    if silhouette != payload["silhouette"]:
        raise SystemExit(f"Silhouette redraw {silhouette} != {payload['silhouette']}")
    colors = ["#0d8a6a", "#1f6f8b", "#d97706"]
    counted = {str(cluster): int((labels == cluster).sum()) for cluster in range(payload["k"])}
    expected = {key: int(value) for key, value in payload["cluster_sizes"].items()}
    if counted != expected:
        raise SystemExit(f"Cluster sizes {counted} != {expected}")
    fig, ax = plt.subplots(figsize=(10.2, 5.6))
    for cluster in range(payload["k"]):
        mask = labels == cluster
        size = counted[str(cluster)]
        ax.scatter(
            df.loc[mask, "recency_days"],
            df.loc[mask, "monetary_12m"],
            s=16,
            alpha=0.75,
            color=colors[cluster],
            label=f"Cluster {cluster} (n={size})",
        )
    ax.set_xlabel("Recency (days)")
    ax.set_ylabel("Monetary, last 12 months")
    ax.set_title(
        f"RFM KMeans (k={payload['k']})  ·  n={payload['n_rows']:,}\n"
        f"Silhouette {payload['silhouette']:.4f}   ·   "
        f"ARI vs latent segment {payload['ari_vs_latent']:.4f}"
    )
    ax.legend(frameon=False)
    fig.tight_layout()
    _save(fig, "04-customer-segments.png")


def plot_expenses() -> None:
    plt = _style()
    _use_src("05-expense-classifier")
    import joblib
    import pandas as pd
    from sklearn.metrics import ConfusionMatrixDisplay, f1_score
    from sklearn.model_selection import train_test_split

    from train import DATA, METRICS, MODEL, train

    payload = train()
    saved = json.loads(METRICS.read_text())
    if payload != saved:
        raise SystemExit("Expense metrics did not match metrics.json")
    df = pd.read_csv(DATA)
    _, x_test, _, y_test = train_test_split(
        df["memo"], df["category"], test_size=0.25, random_state=0, stratify=df["category"]
    )
    pred = joblib.load(MODEL).predict(x_test)
    macro = round(float(f1_score(y_test, pred, average="macro")), 4)
    if macro != payload["macro_f1"]:
        raise SystemExit(f"Expense macro F1 redraw {macro} != {payload['macro_f1']}")
    fig, ax = plt.subplots(figsize=(8.4, 6.4))
    ConfusionMatrixDisplay.from_predictions(y_test, pred, ax=ax, colorbar=False, cmap="Greens")
    ax.tick_params(axis="x", labelrotation=30)
    ax.set_title(
        f"Expense memo classifier, 25% holdout  ·  n={payload['n_rows']:,}"
        f"  ·  {payload['n_classes']} classes\n"
        f"Macro F1 {payload['macro_f1']:.4f}"
    )
    fig.tight_layout()
    _save(fig, "05-expense-confusion.png")


def plot_mrr() -> None:
    plt = _style()
    _use_src("06-mrr-forecast")
    import joblib
    import pandas as pd
    from sklearn.metrics import mean_absolute_error, r2_score

    from train import DATA, METRICS, MODEL, make_features, train

    payload = train()
    saved = json.loads(METRICS.read_text())
    if payload["test_scores"] != saved["test_scores"]:
        raise SystemExit("MRR scores did not match metrics.json")
    featured = make_features(pd.read_csv(DATA))
    cols = ["lag_1", "lag_3", "lag_12", "roll_3", "month_num"]
    test = featured.iloc[-8:]
    bundle = joblib.load(MODEL)
    if bundle["name"] != payload["selected_model"]:
        raise SystemExit("Saved MRR model name does not match metrics.json")
    pred = bundle["model"].predict(test[cols])
    mae = round(float(mean_absolute_error(test["mrr"], pred)), 2)
    r2 = round(float(r2_score(test["mrr"], pred)), 4)
    ridge = next(row for row in payload["test_scores"] if row["model"] == "ridge")
    naive = next(row for row in payload["test_scores"] if row["model"] == "seasonal_naive_lag12")
    if mae != ridge["mae"] or r2 != ridge["r2"]:
        raise SystemExit(f"MRR redraw MAE {mae} R2 {r2} != saved ridge scores")

    fig, ax = plt.subplots(figsize=(10.2, 5.2))
    months = pd.to_datetime(featured["month_dt"])
    ax.plot(months, featured["mrr"], color="#0b1f2a", lw=1.6, label="Actual")
    ax.plot(pd.to_datetime(test["month_dt"]), pred, color="#0d8a6a", lw=1.8, marker="o", label="Ridge")
    ax.plot(
        pd.to_datetime(test["month_dt"]),
        test["lag_12"],
        color="#1f6f8b",
        lw=1.2,
        ls="--",
        marker="o",
        label="Seasonal naive",
    )
    ax.axvspan(
        pd.to_datetime(test["month_dt"]).iloc[0],
        pd.to_datetime(test["month_dt"]).iloc[-1],
        color="#0d8a6a",
        alpha=0.08,
        label="Holdout",
    )
    ax.set_ylabel("MRR")
    ax.set_title(
        f"Monthly MRR, last 8 months held out  ·  {payload['n_rows']} modeled months\n"
        f"Ridge MAE {ridge['mae']:.2f} (R² {ridge['r2']:.4f})   ·   "
        f"lag-12 naive MAE {naive['mae']:.2f}"
    )
    ax.legend(frameon=False, ncol=4, loc="upper left")
    fig.autofmt_xdate()
    fig.tight_layout()
    _save(fig, "06-mrr-forecast.png")


def plot_noshow() -> None:
    plt = _style()
    _use_src("07-appointment-noshow")
    import joblib
    import pandas as pd
    from sklearn.metrics import roc_auc_score, roc_curve
    from sklearn.model_selection import train_test_split

    from train import DATA, METRICS, MODEL, train

    payload = train()
    saved = json.loads(METRICS.read_text())
    if payload != saved:
        raise SystemExit("No-show metrics did not match metrics.json")
    df = pd.read_csv(DATA)
    num, cat = ["lead_time_hours", "weekday", "prior_noshows", "reminder_sent"], ["channel"]
    x, y = df[num + cat], df["noshow"]
    _, x_test, _, y_test = train_test_split(x, y, test_size=0.25, random_state=1, stratify=y)
    proba = joblib.load(MODEL).predict_proba(x_test)[:, 1]
    auc = round(float(roc_auc_score(y_test, proba)), 4)
    if auc != payload["roc_auc"]:
        raise SystemExit(f"No-show AUC redraw {auc} != {payload['roc_auc']}")
    fpr, tpr, _ = roc_curve(y_test, proba)
    fig, ax = plt.subplots(figsize=(7.4, 5.6))
    ax.plot(fpr, tpr, color="#0d8a6a", lw=2, label=f"Random forest (AUC {auc:.4f})")
    ax.plot([0, 1], [0, 1], color="#9aafb8", lw=1, ls="--", label="Chance")
    ax.set_xlabel("False positive rate")
    ax.set_ylabel("True positive rate")
    ax.set_title(
        f"Appointment no-show ROC  ·  n={payload['n_rows']:,}"
        f"  ·  no-show rate {payload['noshow_rate']:.2%}\n"
        f"ROC-AUC {payload['roc_auc']:.4f}"
    )
    ax.legend(frameon=False, loc="lower right")
    fig.tight_layout()
    _save(fig, "07-noshow-roc.png")


def main() -> None:
    if len(sys.argv) == 3 and sys.argv[1] == "--only":
        globals()[sys.argv[2]]()
        return
    script = str(Path(__file__).resolve())
    for name in PLOTS:
        subprocess.check_call([sys.executable, script, "--only", name])


if __name__ == "__main__":
    main()
