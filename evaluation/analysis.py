import json
import pandas as pd
from collections import defaultdict

SCORES_PATH = "storage/scores/all_scores.json"

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

def print_separator(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def analyze(df):

    # 1. Overall consistency
    print_separator("OVERALL STANCE CONSISTENCY")
    print(df.groupby("stance")["avg_stance"].describe().round(2))

    print_separator("OVERALL PERSONALITY ADHERENCE")
    print(df.groupby("stance")["avg_personality"].describe().round(2))

    # 2. Drift by personality trait
    print_separator("STANCE DRIFT BY PERSONALITY TRAIT")
    drift_stance = df.groupby(["personality", "stance"])["stance_drift"].mean().round(2)
    print(drift_stance.to_string())

    print_separator("PERSONALITY DRIFT BY PERSONALITY TRAIT")
    drift_personality = df.groupby(["personality", "stance"])["personality_drift"].mean().round(2)
    print(drift_personality.to_string())

    # 3. Which personality shows most drift
    print_separator("AVERAGE STANCE DRIFT PER PERSONALITY (both stances combined)")
    print(df.groupby("personality")["stance_drift"].mean().round(2).sort_values())

    print_separator("AVERAGE PERSONALITY DRIFT PER PERSONALITY (both stances combined)")
    print(df.groupby("personality")["personality_drift"].mean().round(2).sort_values())

    # 4. Pro vs restrictive comparison
    print_separator("PRO vs RESTRICTIVE — AVERAGE STANCE SCORE")
    print(df.groupby("stance")["avg_stance"].mean().round(2))

    print_separator("PRO vs RESTRICTIVE — AVERAGE DRIFT")
    print(df.groupby("stance")["stance_drift"].mean().round(2))

    # 5. Debate quality by personality
    print_separator("DEBATE QUALITY BY PERSONALITY TRAIT")
    quality_cols = ["argument_quality", "rebuttal_directness", "coherence", "civility"]
    print(df.groupby("personality")[quality_cols].mean().round(2))

    # 6. Most and least consistent conditions
    print_separator("TOP 5 MOST CONSISTENT CONDITIONS (avg stance score)")
    top = df.groupby(["personality", "stance"])["avg_stance"].mean().round(2).sort_values(ascending=False).head(5)
    print(top.to_string())

    print_separator("TOP 5 LEAST CONSISTENT CONDITIONS (avg stance score)")
    bottom = df.groupby(["personality", "stance"])["avg_stance"].mean().round(2).sort_values().head(5)
    print(bottom.to_string())

    # 7. Drift direction counts
    print_separator("DRIFT DIRECTION COUNTS (stance)")
    df["drift_direction"] = df["stance_drift"].apply(
        lambda x: "improved" if x > 0 else ("degraded" if x < 0 else "stable")
    )
    print(df.groupby(["personality", "stance", "drift_direction"]).size().to_string())

    return df

if __name__ == "__main__":
    scores = load_scores()
    df = build_dataframe(scores)
    df = analyze(df)

    # Save dataframe for further analysis
    df.to_csv("storage/scores/analysis.csv", index=False)
    print("\nAnalysis saved to storage/scores/analysis.csv")