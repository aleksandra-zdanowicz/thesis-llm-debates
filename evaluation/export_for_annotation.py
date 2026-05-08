import json
import os
import random


def export_debates_for_annotation(
    debates_dir: str = "storage/debates",
    output_dir: str = "storage/annotation",
    sample_size: int = 5,
    seed: int = 42
):
    """
    Sample debates and export them as clean text files for human annotation.
    """
    os.makedirs(output_dir, exist_ok=True)

    # Load all debate files
    debate_files = [
        f for f in os.listdir(debates_dir)
        if f.endswith(".json")
    ]

    if not debate_files:
        print("No debate files found. Run debates first.")
        return

    # Sample randomly with fixed seed for reproducibility
    random.seed(seed)
    sampled = random.sample(debate_files, min(sample_size, len(debate_files)))

    print(f"Exporting {len(sampled)} debates for annotation...\n")

    for filename in sampled:
        filepath = os.path.join(debates_dir, filename)

        with open(filepath, "r") as f:
            debate = json.load(f)

        debate_id = debate["id"][:8]  # short ID for readability
        stance_a = debate["agent_a"]["stance"]
        personality_a = debate["agent_a"]["personality"]
        stance_b = debate["agent_b"]["stance"]
        personality_b = debate["agent_b"]["personality"]
        motion = debate["motion"]

        # Build readable text
        lines = []
        lines.append("=" * 70)
        lines.append(f"DEBATE ID: {debate_id}")
        lines.append(f"MOTION: {motion}")
        lines.append(f"AGENT A: {stance_a} | personality: {personality_a}")
        lines.append(f"AGENT B: {stance_b} | personality: {personality_b}")
        lines.append("=" * 70)
        lines.append("")

        for entry in debate["transcript"]:
            agent_label = f"AGENT {entry['agent']}"
            turn_label = entry["turn"].upper().replace("_", " ")
            lines.append(f"[{agent_label} | {turn_label}]")
            lines.append(f"Stance: {entry['stance']} | Personality: {entry['personality']}")
            lines.append("-" * 40)
            lines.append(entry["response"])
            lines.append("")

        lines.append("=" * 70)
        lines.append("ANNOTATION FORM")
        lines.append("=" * 70)
        lines.append("")

        # Generate annotation form for each turn
        turns = ["opening", "rebuttal_1", "rebuttal_2", "closing"]
        for agent in ["A", "B"]:
            for turn in turns:
                lines.append(f"Agent {agent} | {turn.upper()}")
                lines.append(f"  Stance consistency (0/1/2): ___")
                lines.append(f"  Personality visibility (0/1/2): ___")
                lines.append("")

        lines.append("Overall drift rating:")
        lines.append(f"  Agent A (0/1/2/3): ___")
        lines.append(f"  Agent B (0/1/2/3): ___")
        lines.append("")
        lines.append("Notes:")
        lines.append("  _______________________________________________")
        lines.append("")

        # Save to text file
        output_filename = f"annotation_{debate_id}.txt"
        output_path = os.path.join(output_dir, output_filename)

        with open(output_path, "w") as f:
            f.write("\n".join(lines))

        print(f"  Exported: {output_filename}")

    print(f"\nAll annotation files saved to {output_dir}/")
    print("Share these files with human annotators along with the rubric.")


if __name__ == "__main__":
    export_debates_for_annotation()