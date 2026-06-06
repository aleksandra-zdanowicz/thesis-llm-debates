import json
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import os

SCORES_PATH = "storage/scores/all_scores.json"
FIGURES_DIR = "storage/figures"

def load_scores():
    with open(SCORES_PATH, "r") as f:
        return json.load(f)

def build_dataframe(scores):
    rows = []
    for debate in scores:
        personality = debate["agent_a"]["personality"]
        motion = debate["motion"]

        rows.append({
            "debate_id": debate["debate_id"][:8],
            "motion": motion[:40],
            "personality": personality,
            "stance": "pro_immigration",
            "avg_stance": debate["summary"]["avg_stance_a"],
            "avg_personality": debate["summary"]["avg_personality_a"],
            "stance_drift": debate["summary"]["stance_drift_a"],
            "personality_drift": debate["summary"]["personality_drift_a"],
            "argument_quality": debate["summary"]["argument_quality"],
            "rebuttal_directness": debate["summary"]["rebuttal_directness"],
            "coherence": debate["summary"]["coherence"],
            "civility": debate["summary"]["civility"],
        })

        rows.append({
            "debate_id": debate["debate_id"][:8],
            "motion": motion[:40],
            "personality": personality,
            "stance": "restrictive_immigration",
            "avg_stance": debate["summary"]["avg_stance_b"],
            "avg_personality": debate["summary"]["avg_personality_b"],
            "stance_drift": debate["summary"]["stance_drift_b"],
            "personality_drift": debate["summary"]["personality_drift_b"],
            "argument_quality": debate["summary"]["argument_quality"],
            "rebuttal_directness": debate["summary"]["rebuttal_directness"],
            "coherence": debate["summary"]["coherence"],
            "civility": debate["summary"]["civility"],
        })

    return pd.DataFrame(rows)


PERSONALITY_ORDER = [
    "agreeableness",
    "conscientiousness",
    "extraversion",
    "neuroticism",
    "openness"
]

COLORS = {
    "pro_immigration": "#2196F3",
    "restrictive_immigration": "#F44336"
}

STANCE_LABELS = {
    "pro_immigration": "Pro-Immigration",
    "restrictive_immigration": "Restrictive"
}


def plot_avg_stance_by_personality(df):
    """Bar chart: average stance score by personality and stance."""
    fig, ax = plt.subplots(figsize=(10, 6))

    x = np.arange(len(PERSONALITY_ORDER))
    width = 0.35

    pro = df[df["stance"] == "pro_immigration"].groupby("personality")["avg_stance"].mean()
    res = df[df["stance"] == "restrictive_immigration"].groupby("personality")["avg_stance"].mean()

    pro_vals = [pro.get(p, 0) for p in PERSONALITY_ORDER]
    res_vals = [res.get(p, 0) for p in PERSONALITY_ORDER]

    bars1 = ax.bar(x - width/2, pro_vals, width, label="Pro-Immigration",
                   color=COLORS["pro_immigration"], alpha=0.85)
    bars2 = ax.bar(x + width/2, res_vals, width, label="Restrictive",
                   color=COLORS["restrictive_immigration"], alpha=0.85)

    ax.set_xlabel("Personality Trait", fontsize=12)
    ax.set_ylabel("Average Stance Score (0-3)", fontsize=12)
    ax.set_title("Average Stance Consistency by Personality Trait and Stance", fontsize=13)
    ax.set_xticks(x)
    ax.set_xticklabels([p.capitalize() for p in PERSONALITY_ORDER])
    ax.set_ylim(0, 3.5)
    ax.axhline(y=3, color="gray", linestyle="--", linewidth=0.8, alpha=0.5)
    ax.legend()
    ax.grid(axis="y", alpha=0.3)

    for bar in bars1:
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05,
                f"{bar.get_height():.2f}", ha="center", va="bottom", fontsize=9)
    for bar in bars2:
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05,
                f"{bar.get_height():.2f}", ha="center", va="bottom", fontsize=9)

    plt.tight_layout()
    path = f"{FIGURES_DIR}/1_avg_stance_by_personality.png"
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"Saved: {path}")


def plot_stance_drift_by_personality(df):
    """Bar chart: average stance drift by personality and stance."""
    fig, ax = plt.subplots(figsize=(10, 6))

    x = np.arange(len(PERSONALITY_ORDER))
    width = 0.35

    pro = df[df["stance"] == "pro_immigration"].groupby("personality")["stance_drift"].mean()
    res = df[df["stance"] == "restrictive_immigration"].groupby("personality")["stance_drift"].mean()

    pro_vals = [pro.get(p, 0) for p in PERSONALITY_ORDER]
    res_vals = [res.get(p, 0) for p in PERSONALITY_ORDER]

    bars1 = ax.bar(x - width/2, pro_vals, width, label="Pro-Immigration",
                   color=COLORS["pro_immigration"], alpha=0.85)
    bars2 = ax.bar(x + width/2, res_vals, width, label="Restrictive",
                   color=COLORS["restrictive_immigration"], alpha=0.85)

    ax.set_xlabel("Personality Trait", fontsize=12)
    ax.set_ylabel("Average Stance Drift (closing - opening)", fontsize=12)
    ax.set_title("Stance Drift by Personality Trait and Stance", fontsize=13)
    ax.set_xticks(x)
    ax.set_xticklabels([p.capitalize() for p in PERSONALITY_ORDER])
    ax.axhline(y=0, color="black", linewidth=1)
    ax.legend()
    ax.grid(axis="y", alpha=0.3)

    for bar in bars1:
        height = bar.get_height()
        offset = 0.05 if height >= 0 else -0.15
        ax.text(bar.get_x() + bar.get_width()/2, height + offset,
                f"{height:.2f}", ha="center", va="bottom", fontsize=9)
    for bar in bars2:
        height = bar.get_height()
        offset = 0.05 if height >= 0 else -0.15
        ax.text(bar.get_x() + bar.get_width()/2, height + offset,
                f"{height:.2f}", ha="center", va="bottom", fontsize=9)

    plt.tight_layout()
    path = f"{FIGURES_DIR}/2_stance_drift_by_personality.png"
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"Saved: {path}")


def plot_personality_drift_by_trait(df):
    """Bar chart: average personality drift by trait and stance."""
    fig, ax = plt.subplots(figsize=(10, 6))

    x = np.arange(len(PERSONALITY_ORDER))
    width = 0.35

    pro = df[df["stance"] == "pro_immigration"].groupby("personality")["personality_drift"].mean()
    res = df[df["stance"] == "restrictive_immigration"].groupby("personality")["personality_drift"].mean()

    pro_vals = [pro.get(p, 0) for p in PERSONALITY_ORDER]
    res_vals = [res.get(p, 0) for p in PERSONALITY_ORDER]

    bars1 = ax.bar(x - width/2, pro_vals, width, label="Pro-Immigration",
                   color=COLORS["pro_immigration"], alpha=0.85)
    bars2 = ax.bar(x + width/2, res_vals, width, label="Restrictive",
                   color=COLORS["restrictive_immigration"], alpha=0.85)

    ax.set_xlabel("Personality Trait", fontsize=12)
    ax.set_ylabel("Average Personality Drift (closing - opening)", fontsize=12)
    ax.set_title("Personality Adherence Drift by Trait and Stance", fontsize=13)
    ax.set_xticks(x)
    ax.set_xticklabels([p.capitalize() for p in PERSONALITY_ORDER])
    ax.axhline(y=0, color="black", linewidth=1)
    ax.legend()
    ax.grid(axis="y", alpha=0.3)

    for bar in bars1:
        height = bar.get_height()
        offset = 0.05 if height >= 0 else -0.15
        ax.text(bar.get_x() + bar.get_width()/2, height + offset,
                f"{height:.2f}", ha="center", va="bottom", fontsize=9)
    for bar in bars2:
        height = bar.get_height()
        offset = 0.05 if height >= 0 else -0.15
        ax.text(bar.get_x() + bar.get_width()/2, height + offset,
                f"{height:.2f}", ha="center", va="bottom", fontsize=9)

    plt.tight_layout()
    path = f"{FIGURES_DIR}/3_personality_drift_by_trait.png"
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"Saved: {path}")


def plot_pro_vs_restrictive_overview(df):
    """Side by side: pro vs restrictive on stance and personality scores."""
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    for ax, metric, label, ylim in zip(
        axes,
        ["avg_stance", "avg_personality"],
        ["Average Stance Score (0-3)", "Average Personality Score (0-3)"],
        [(0, 3.5), (0, 3.5)]
    ):
        pro_vals = [
            df[(df["stance"] == "pro_immigration") &
               (df["personality"] == p)]["" + metric].mean()
            for p in PERSONALITY_ORDER
        ]
        res_vals = [
            df[(df["stance"] == "restrictive_immigration") &
               (df["personality"] == p)][metric].mean()
            for p in PERSONALITY_ORDER
        ]

        x = np.arange(len(PERSONALITY_ORDER))
        width = 0.35

        ax.bar(x - width/2, pro_vals, width, label="Pro-Immigration",
               color=COLORS["pro_immigration"], alpha=0.85)
        ax.bar(x + width/2, res_vals, width, label="Restrictive",
               color=COLORS["restrictive_immigration"], alpha=0.85)

        ax.set_ylabel(label, fontsize=11)
        ax.set_xticks(x)
        ax.set_xticklabels([p.capitalize() for p in PERSONALITY_ORDER], rotation=15)
        ax.set_ylim(ylim)
        ax.legend(fontsize=9)
        ax.grid(axis="y", alpha=0.3)

    axes[0].set_title("Stance Consistency", fontsize=12)
    axes[1].set_title("Personality Adherence", fontsize=12)
    fig.suptitle("Pro-Immigration vs Restrictive: Consistency Comparison", fontsize=13)

    plt.tight_layout()
    path = f"{FIGURES_DIR}/4_pro_vs_restrictive_overview.png"
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"Saved: {path}")


def plot_debate_quality(df):
    """Heatmap-style bar chart of debate quality by personality."""
    fig, ax = plt.subplots(figsize=(11, 6))

    quality_cols = ["argument_quality", "rebuttal_directness", "coherence", "civility"]
    quality_labels = ["Argument Quality", "Rebuttal Directness", "Coherence", "Civility"]

    x = np.arange(len(PERSONALITY_ORDER))
    width = 0.18
    offsets = [-1.5, -0.5, 0.5, 1.5]

    palette = ["#4CAF50", "#2196F3", "#FF9800", "#9C27B0"]

    for i, (col, label, color) in enumerate(zip(quality_cols, quality_labels, palette)):
        vals = [
            df[df["personality"] == p][col].mean()
            for p in PERSONALITY_ORDER
        ]
        ax.bar(x + offsets[i] * width, vals, width,
               label=label, color=color, alpha=0.85)

    ax.set_xlabel("Personality Trait", fontsize=12)
    ax.set_ylabel("Average Score (0-2)", fontsize=12)
    ax.set_title("Debate Quality Dimensions by Personality Trait", fontsize=13)
    ax.set_xticks(x)
    ax.set_xticklabels([p.capitalize() for p in PERSONALITY_ORDER])
    ax.set_ylim(0, 2.5)
    ax.legend(loc="upper right")
    ax.grid(axis="y", alpha=0.3)

    plt.tight_layout()
    path = f"{FIGURES_DIR}/5_debate_quality_by_personality.png"
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"Saved: {path}")


def plot_drift_direction_counts(df):
    """Stacked bar chart: drift direction per personality and stance."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    df["drift_direction"] = df["stance_drift"].apply(
        lambda x: "Improved" if x > 0 else ("Degraded" if x < 0 else "Stable")
    )

    direction_colors = {
        "Improved": "#4CAF50",
        "Stable": "#9E9E9E",
        "Degraded": "#F44336"
    }

    for ax, stance, title in zip(
        axes,
        ["pro_immigration", "restrictive_immigration"],
        ["Pro-Immigration Agents", "Restrictive Agents"]
    ):
        subset = df[df["stance"] == stance]
        counts = subset.groupby(["personality", "drift_direction"]).size().unstack(fill_value=0)

        for direction in ["Improved", "Stable", "Degraded"]:
            if direction not in counts.columns:
                counts[direction] = 0

        counts = counts[["Improved", "Stable", "Degraded"]]
        counts = counts.reindex(PERSONALITY_ORDER)

        bottom = np.zeros(len(PERSONALITY_ORDER))
        for direction in ["Improved", "Stable", "Degraded"]:
            vals = counts[direction].values
            ax.bar(range(len(PERSONALITY_ORDER)), vals, bottom=bottom,
                   label=direction, color=direction_colors[direction], alpha=0.85)
            bottom += vals

        ax.set_title(title, fontsize=12)
        ax.set_xticks(range(len(PERSONALITY_ORDER)))
        ax.set_xticklabels([p.capitalize() for p in PERSONALITY_ORDER], rotation=15)
        ax.set_ylabel("Number of Debates", fontsize=11)
        ax.set_ylim(0, 6)
        ax.legend()
        ax.grid(axis="y", alpha=0.3)

    fig.suptitle("Stance Drift Direction by Personality Trait", fontsize=13)
    plt.tight_layout()
    path = f"{FIGURES_DIR}/6_drift_direction_counts.png"
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"Saved: {path}")


def plot_scatter_stance_vs_personality(df):
    """Scatter plot: stance consistency vs personality adherence, colored by personality trait."""
    fig, ax = plt.subplots(figsize=(11, 8))

    PERSONALITY_COLORS = {
        "agreeableness": "#4CAF50",
        "conscientiousness": "#2196F3",
        "extraversion": "#FF9800",
        "neuroticism": "#E91E63",
        "openness": "#9C27B0"
    }

    PERSONALITY_MARKERS = {
        "pro_immigration": "o",
        "restrictive_immigration": "s"
    }

    for _, row in df.iterrows():
        color = PERSONALITY_COLORS[row["personality"]]
        marker = PERSONALITY_MARKERS[row["stance"]]
        ax.scatter(
            row["avg_stance"],
            row["avg_personality"],
            color=color,
            marker=marker,
            alpha=0.75,
            s=100,
            edgecolors="white",
            linewidths=0.5
        )

    # Legend for personality traits
    personality_handles = [
        mpatches.Patch(color=color, label=p.capitalize())
        for p, color in PERSONALITY_COLORS.items()
    ]

    # Legend for stance (marker shape)
    stance_handles = [
        plt.scatter([], [], marker="o", color="gray", alpha=0.75, s=80, label="Pro-Immigration"),
        plt.scatter([], [], marker="s", color="gray", alpha=0.75, s=80, label="Restrictive"),
    ]

    first_legend = ax.legend(
        handles=personality_handles,
        title="Personality Trait",
        loc="upper left",
        fontsize=9,
        title_fontsize=10
    )
    ax.add_artist(first_legend)
    ax.legend(
        handles=stance_handles,
        title="Stance",
        loc="lower right",
        fontsize=9,
        title_fontsize=10
    )

    ax.set_xlabel("Average Stance Score (0-3)", fontsize=12)
    ax.set_ylabel("Average Personality Score (0-3)", fontsize=12)
    ax.set_title("Stance Consistency vs Personality Adherence\n(color = personality trait, shape = stance)", fontsize=13)
    ax.set_xlim(0, 3.5)
    ax.set_ylim(0, 3.5)
    ax.grid(alpha=0.3)

    plt.tight_layout()
    path = f"{FIGURES_DIR}/7_stance_vs_personality_scatter.png"
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"Saved: {path}")


def run_all_visualizations():
    os.makedirs(FIGURES_DIR, exist_ok=True)

    scores = load_scores()
    df = build_dataframe(scores)

    print("Generating visualizations...\n")

    plot_avg_stance_by_personality(df)
    plot_stance_drift_by_personality(df)
    plot_personality_drift_by_trait(df)
    plot_pro_vs_restrictive_overview(df)
    plot_debate_quality(df)
    plot_drift_direction_counts(df)
    plot_scatter_stance_vs_personality(df)

    print(f"\nAll figures saved to {FIGURES_DIR}/")


if __name__ == "__main__":
    run_all_visualizations()