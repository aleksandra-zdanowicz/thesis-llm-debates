import json
import os
import uuid
from datetime import datetime
from debate.agent import DebateAgent
from debate.config import TURN_ORDER, OUTPUT_DIR


def run_debate(stance_a: str, personality_a: str,
               stance_b: str, personality_b: str,
               motion: str) -> dict:
    """
    Run a full Oxford-style debate between two agents.
    Returns a structured debate record.
    """

    # Create agents
    agent_a = DebateAgent(stance_a, personality_a)
    agent_b = DebateAgent(stance_b, personality_b)

    transcript = []
    last_a = None
    last_b = None

    print(f"\n{'='*60}")
    print(f"MOTION: {motion}")
    print(f"Agent A: {stance_a} + {personality_a}")
    print(f"Agent B: {stance_b} + {personality_b}")
    print(f"{'='*60}\n")

    for turn in TURN_ORDER:
        # Agent A goes first
        print(f"[Agent A | {turn}]")
        response_a = agent_a.generate(
            role=turn,
            opponent_last_turn=last_b
        )
        last_a = response_a
        print(response_a)
        print()

        transcript.append({
            "turn": turn,
            "agent": "A",
            "stance": stance_a,
            "personality": personality_a,
            "response": response_a
        })

        # Agent B responds
        print(f"[Agent B | {turn}]")
        response_b = agent_b.generate(
            role=turn,
            opponent_last_turn=last_a
        )
        last_b = response_b
        print(response_b)
        print()

        transcript.append({
            "turn": turn,
            "agent": "B",
            "stance": stance_b,
            "personality": personality_b,
            "response": response_b
        })

    # Build debate record
    debate_record = {
        "id": str(uuid.uuid4()),
        "timestamp": datetime.now().isoformat(),
        "motion": motion,
        "agent_a": {"stance": stance_a, "personality": personality_a},
        "agent_b": {"stance": stance_b, "personality": personality_b},
        "transcript": transcript
    }

    # Save to JSON
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    filename = f"{OUTPUT_DIR}/{debate_record['id']}.json"
    with open(filename, "w") as f:
        json.dump(debate_record, f, indent=2)

    print(f"\nDebate saved to {filename}")
    return debate_record