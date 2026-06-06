import json
import os
import sys
from datetime import datetime

# When this file is executed as a script, Python's import path is set to the
# script's directory (evaluation/) which prevents sibling packages (like
# `prompts`) from being found. Add the project root to `sys.path` so
# `python evaluation/validator.py` works from the repository root.
if __package__ is None:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(current_dir, ".."))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

import ollama
from prompts import STANCES, PERSONALITIES, GUIDELINES
from evaluation.questions import STANCE_PROBES, PERSONALITY_PROBES

JUDGE_MODEL = "mistral"
AGENT_MODEL = "llama3.2"
VALIDATION_OUTPUT_DIR = "storage/validation"


def build_validation_system_prompt(stance: str, personality: str) -> str:
    return f"""{STANCES[stance]}

{PERSONALITIES[personality]}

{GUIDELINES}"""


def probe_agent(stance: str, personality: str, question: str, agent_model: str = AGENT_MODEL) -> str:
    """Send a single probe question to an agent and return its response."""
    system_prompt = build_validation_system_prompt(stance, personality)

    response = ollama.chat(
        model=agent_model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question}
        ]
    )

    return response["message"]["content"]


def parse_judge_response(raw: str, expected_keys: list) -> dict:
    """Robustly extract JSON from judge response even with surrounding text."""

    # Try to find JSON block
    try:
        start = raw.index("{")
        end = raw.rindex("}") + 1
        candidate = raw[start:end]
        result = json.loads(candidate)
        if all(k in result for k in expected_keys):
            return result
    except Exception:
        pass

    # Fallback: try line by line for inline JSON
    for line in raw.splitlines():
        line = line.strip()
        if line.startswith("{") and line.endswith("}"):
            try:
                result = json.loads(line)
                if all(k in result for k in expected_keys):
                    return result
            except Exception:
                continue

    # Final fallback — manually check for true/false in raw text
    fallback = {}
    for key in expected_keys:
        if f'"{key}": true' in raw or f'"{key}":true' in raw:
            fallback[key] = True
        elif f'"{key}": false' in raw or f'"{key}":false' in raw:
            fallback[key] = False
        else:
            fallback[key] = False
    fallback["confidence"] = "low"
    fallback["reasoning"] = "Parsed from raw text fallback"
    return fallback


def score_stance(response: str, expected_stance: str) -> dict:
    """
    Use Llama itself as a judge to score stance alignment.
    Returns a score and reasoning.
    """

    if expected_stance == "pro_immigration":
        stance_description = "supportive of open, humane, and expanded immigration policies"
    else:
        stance_description = "supportive of strict, controlled, and restrictive immigration policies"

    judge_prompt = f"""You are a strict evaluator. Read the following response and determine 
whether it is clearly {stance_description}.

Response to evaluate:
\"\"\"{response}\"\"\"

Answer with ONLY a JSON object in this exact format with no extra text:
{{
  "aligned": true or false,
  "confidence": "high", "medium", or "low",
  "reasoning": "one sentence explanation"
}}"""

    judge_response = ollama.chat(
    model=JUDGE_MODEL,
    messages=[
        {"role": "user", "content": judge_prompt}
    ]
)

    raw = judge_response["message"]["content"]
    result = parse_judge_response(raw, ["aligned", "confidence", "reasoning"])
    return result


def score_personality(response: str, personality: str) -> dict:
    """
    Use Llama as a judge to score personality trait visibility.
    """

    trait_descriptions = {
        "openness": "intellectually curious, imaginative, embraces complexity, uses creative analogies, explores multiple perspectives",
        "conscientiousness": "structured, methodical, disciplined, cites evidence, detail-oriented, logical sequences",
        "extraversion": "assertive, bold, confident, energetic, dominant, emphatic, never hedges",
        "agreeableness": "warm, cooperative, empathetic, acknowledges others, uses inclusive language, bridge-building",
        "neuroticism": "emotionally intense, anxious, reactive, defensive, expresses urgency and alarm"
    }

    judge_prompt = f"""You are a strict evaluator of personality expression in text.
Read the following response and determine whether it clearly exhibits 
the personality trait of HIGH {personality.upper()}.

A person high in {personality} is typically: {trait_descriptions[personality]}.

Response to evaluate:
\"\"\"{response}\"\"\"

Answer with ONLY a JSON object in this exact format with no extra text:
{{
  "trait_visible": true or false,
  "confidence": "high", "medium", or "low",
  "reasoning": "one sentence explanation"
}}"""

    judge_response = ollama.chat(
    model=JUDGE_MODEL,
    messages=[
        {"role": "user", "content": judge_prompt}
    ]
)

    raw = judge_response["message"]["content"]
    result = parse_judge_response(raw, ["trait_visible", "confidence", "reasoning"])
    return result


def validate_condition(stance: str, personality: str, agent_model: str = AGENT_MODEL) -> dict:
    """
    Run full validation for one agent condition.
    Returns a validation report.
    """

    print(f"\n{'='*60}")
    print(f"Validating: {stance} + {personality} [{agent_model}]")
    print(f"{'='*60}")

    stance_results = []
    personality_results = []

    # Stance probes
    print("\n-- Stance probes --")
    for i, question in enumerate(STANCE_PROBES):
        print(f"  Q{i+1}: {question}")
        response = probe_agent(stance, personality, question, agent_model)
        score = score_stance(response, stance)
        stance_results.append({
            "question": question,
            "response": response,
            "score": score
        })
        status = "✓" if score["aligned"] else "✗"
        print(f"  {status} Aligned: {score['aligned']} ({score['confidence']}) — {score['reasoning']}")

    # Personality probes
    print("\n-- Personality probes --")
    for i, question in enumerate(PERSONALITY_PROBES):
        print(f"  Q{i+1}: {question}")
        response = probe_agent(stance, personality, question, agent_model)
        score = score_personality(response, personality)
        personality_results.append({
            "question": question,
            "response": response,
            "score": score
        })
        status = "✓" if score["trait_visible"] else "✗"
        print(f"  {status} Trait visible: {score['trait_visible']} ({score['confidence']}) — {score['reasoning']}")

    # Summary
    stance_pass = sum(1 for r in stance_results if r["score"]["aligned"])
    personality_pass = sum(1 for r in personality_results if r["score"]["trait_visible"])
    total_stance = len(stance_results)
    total_personality = len(personality_results)

    passed = (
        stance_pass >= 4 and
        personality_pass >= 4
    )

    print(f"\n-- Summary --")
    print(f"  Stance:      {stance_pass}/{total_stance} passed")
    print(f"  Personality: {personality_pass}/{total_personality} passed")
    print(f"  Overall:     {'PASS ✓' if passed else 'FAIL ✗'}")

    report = {
        "model": agent_model,
        "stance": stance,
        "personality": personality,
        "timestamp": datetime.now().isoformat(),
        "stance_results": stance_results,
        "personality_results": personality_results,
        "summary": {
            "stance_pass": stance_pass,
            "stance_total": total_stance,
            "personality_pass": personality_pass,
            "personality_total": total_personality,
            "passed": passed
        }
    }

    return report


def run_all_validations(agent_model: str = AGENT_MODEL, stance_filter=None):
    """Validate all conditions for the given agent model.

    If `stance_filter` is provided, only that stance will be validated.
    """
    from debate.config import STANCES_LIST, PERSONALITIES_LIST

    model_tag = agent_model.replace(":", "_").replace(".", "_")
    output_dir = f"{VALIDATION_OUTPUT_DIR}/{model_tag}"
    os.makedirs(output_dir, exist_ok=True)

    all_reports = []
    failed_conditions = []

    if stance_filter:
        if stance_filter not in STANCES_LIST:
            print(f"Warning: stance '{stance_filter}' not found. Available: {STANCES_LIST}")
            return all_reports, [f"invalid stance: {stance_filter}"]
        stances_to_run = [stance_filter]
    else:
        stances_to_run = STANCES_LIST

    for stance in stances_to_run:
        for personality in PERSONALITIES_LIST:
            report = validate_condition(stance, personality, agent_model)
            all_reports.append(report)

            if not report["summary"]["passed"]:
                failed_conditions.append(f"{stance} + {personality}")

            filename = f"{output_dir}/{stance}_{personality}.json"
            with open(filename, "w") as f:
                json.dump(report, f, indent=2)

    print(f"\n{'='*60}")
    print(f"VALIDATION COMPLETE — {agent_model}")
    print(f"{'='*60}")
    print(f"Conditions passed: {len(all_reports) - len(failed_conditions)}/{len(all_reports)}")

    if failed_conditions:
        print(f"\nFailed conditions:")
        for c in failed_conditions:
            print(f"  ✗ {c}")
    else:
        print("\nAll conditions passed — safe to run debates.")

    combined_path = f"{output_dir}/all_validations.json"
    with open(combined_path, "w") as f:
        json.dump(all_reports, f, indent=2)

    return all_reports, failed_conditions


if __name__ == "__main__":
    import sys
    # CLI usage:
    #  - `python evaluation/validator.py`                         -> default model, all stances
    #  - `python evaluation/validator.py <model>`                 -> run all stances with given model
    #  - `python evaluation/validator.py <model> <stance>`        -> run only that stance with given model
    #  - `python evaluation/validator.py <stance>`                -> run only that stance with default model
    if len(sys.argv) > 2:
        model = sys.argv[1]
        stance = sys.argv[2]
    elif len(sys.argv) > 1:
        arg = sys.argv[1]
        from debate.config import STANCES_LIST
        if arg in STANCES_LIST:
            model = AGENT_MODEL
            stance = arg
        else:
            model = arg
            stance = None
    else:
        model = AGENT_MODEL
        stance = None

    run_all_validations(model, stance)