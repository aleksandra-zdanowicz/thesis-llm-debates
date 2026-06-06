import time
import random
import json
import os
import uuid
from datetime import datetime
import ollama
from debate.config import PERSONALITIES_LIST, MOTIONS
from prompts import STANCES, PERSONALITIES, ROLES, GUIDELINES

OUTPUT_DIR = "storage/debates_llama"
MODEL = "llama3.2"
TOTAL = 70


def build_system_prompt(stance, personality):
    return f"{STANCES[stance]}\n\n{PERSONALITIES[personality]}\n\n{GUIDELINES}"


def generate_turn(model, stance, personality, history, role, opponent_last):
    system_prompt = build_system_prompt(stance, personality)
    role_prompt = ROLES[role]

    if opponent_last:
        user_message = f"{role_prompt}\n\nYour opponent just said:\n\"\"\"{opponent_last}\"\"\"\n\nNow deliver your response."
    else:
        user_message = f"{role_prompt}\n\nNow deliver your opening statement."

    history.append({"role": "user", "content": user_message})

    response = ollama.chat(
        model=model,
        messages=[{"role": "system", "content": system_prompt}, *history]
    )
    reply = response["message"]["content"]
    history.append({"role": "assistant", "content": reply})
    return reply


def run_debate(personality_a, personality_b, motion):
    print(f"\n{'='*60}")
    print(f"MOTION: {motion}")
    print(f"Agent A: pro_immigration + {personality_a}")
    print(f"Agent B: restrictive_immigration + {personality_b}")
    print(f"{'='*60}\n")

    history_a, history_b = [], []
    transcript = []
    last_a = last_b = None
    turn_order = ["opening", "rebuttal_1", "rebuttal_2", "closing"]

    for turn in turn_order:
        print(f"[Agent A | {turn}]")
        resp_a = generate_turn(MODEL, "pro_immigration", personality_a, history_a, turn, last_b)
        last_a = resp_a
        print(resp_a[:100] + "...\n")
        transcript.append({"turn": turn, "agent": "A", "stance": "pro_immigration",
                            "personality": personality_a, "response": resp_a})

        print(f"[Agent B | {turn}]")
        resp_b = generate_turn(MODEL, "restrictive_immigration", personality_b, history_b, turn, last_a)
        last_b = resp_b
        print(resp_b[:100] + "...\n")
        transcript.append({"turn": turn, "agent": "B", "stance": "restrictive_immigration",
                            "personality": personality_b, "response": resp_b})

    record = {
        "id": str(uuid.uuid4()),
        "timestamp": datetime.now().isoformat(),
        "motion": motion,
        "agent_a": {"stance": "pro_immigration", "personality": personality_a},
        "agent_b": {"stance": "restrictive_immigration", "personality": personality_b},
        "transcript": transcript
    }

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    path = f"{OUTPUT_DIR}/{record['id']}.json"
    with open(path, "w") as f:
        json.dump(record, f, indent=2)
    print(f"Saved: {path}")
    return record


if __name__ == "__main__":
    print(f"Generating {TOTAL} random llama debates...\n")
    for i in range(TOTAL):
        personality_a = random.choice(PERSONALITIES_LIST)
        personality_b = random.choice(PERSONALITIES_LIST)
        motion = random.choice(MOTIONS)
        print(f"\n[{i+1}/{TOTAL}]")
        try:
            run_debate(personality_a, personality_b, motion)
            time.sleep(2)
        except Exception as e:
            print(f"ERROR: {e} — skipping")
            continue

    final = len(os.listdir(OUTPUT_DIR))
    print(f"\nDone. debates_llama now has {final} debates.")
