import time
import json
import os
import uuid
from datetime import datetime
from collections import Counter
import ollama
from debate.config import PERSONALITIES_LIST, MOTIONS
from prompts import STANCES, PERSONALITIES, ROLES, GUIDELINES

OUTPUT_DIR = "storage/debates_llama"
MODEL = "llama3.2"
TARGET_REPEATS = 5


def build_system_prompt(stance, personality):
    return f"{STANCES[stance]}\n\n{PERSONALITIES[personality]}\n\n{GUIDELINES}"


def generate_turn(stance, personality, history, role, opponent_last):
    system_prompt = build_system_prompt(stance, personality)
    role_prompt = ROLES[role]

    if opponent_last:
        user_message = f"{role_prompt}\n\nYour opponent just said:\n\"\"\"{opponent_last}\"\"\"\n\nNow deliver your response."
    else:
        user_message = f"{role_prompt}\n\nNow deliver your opening statement."

    history.append({"role": "user", "content": user_message})
    response = ollama.chat(
        model=MODEL,
        messages=[{"role": "system", "content": system_prompt}, *history]
    )
    reply = response["message"]["content"]
    history.append({"role": "assistant", "content": reply})
    return reply


def run_debate(personality, motion):
    print(f"\n{'='*60}")
    print(f"MOTION: {motion}")
    print(f"Personality: {personality} (both agents)")
    print(f"{'='*60}\n")

    history_a, history_b = [], []
    transcript = []
    last_a = last_b = None
    turn_order = ["opening", "rebuttal_1", "rebuttal_2", "closing"]

    for turn in turn_order:
        print(f"[Agent A | {turn}]")
        resp_a = generate_turn("pro_immigration", personality, history_a, turn, last_b)
        last_a = resp_a
        print(resp_a[:100] + "...\n")
        transcript.append({"turn": turn, "agent": "A", "stance": "pro_immigration",
                            "personality": personality, "response": resp_a})

        print(f"[Agent B | {turn}]")
        resp_b = generate_turn("restrictive_immigration", personality, history_b, turn, last_a)
        last_b = resp_b
        print(resp_b[:100] + "...\n")
        transcript.append({"turn": turn, "agent": "B", "stance": "restrictive_immigration",
                            "personality": personality, "response": resp_b})

    record = {
        "id": str(uuid.uuid4()),
        "timestamp": datetime.now().isoformat(),
        "motion": motion,
        "agent_a": {"stance": "pro_immigration", "personality": personality},
        "agent_b": {"stance": "restrictive_immigration", "personality": personality},
        "transcript": transcript
    }

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    path = f"{OUTPUT_DIR}/{record['id']}.json"
    with open(path, "w") as f:
        json.dump(record, f, indent=2)
    print(f"Saved: {path}")
    return record


def get_missing():
    counts = Counter()
    for f in os.listdir(OUTPUT_DIR):
        if not f.endswith('.json'):
            continue
        with open(f"{OUTPUT_DIR}/{f}") as fp:
            d = json.load(fp)
        pa, pb = d['agent_a']['personality'], d['agent_b']['personality']
        if pa == pb:
            counts[(pa, d['motion'])] += 1

    needed = []
    for p in PERSONALITIES_LIST:
        for m in MOTIONS:
            gap = TARGET_REPEATS - counts.get((p, m), 0)
            for _ in range(gap):
                needed.append((p, m))
    return needed


if __name__ == "__main__":
    needed = get_missing()
    total = len(needed)
    print(f"Generating {total} missing llama debates (same-personality pairs)...\n")

    for i, (personality, motion) in enumerate(needed):
        print(f"\n[{i+1}/{total}] {personality}")
        try:
            run_debate(personality, motion)
            time.sleep(2)
        except Exception as e:
            print(f"ERROR: {e} — skipping")
            continue

    final = len(os.listdir(OUTPUT_DIR))
    print(f"\nDone. debates_llama now has {final} debates.")
