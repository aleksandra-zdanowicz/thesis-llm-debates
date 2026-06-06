# Model settings
MODEL_NAME = "qwen2.5"
MAX_TOKENS = 500
TEMPERATURE = 0.7

# Debate structure
TURN_ORDER = ["opening", "rebuttal_1", "rebuttal_2", "closing"]
WORD_LIMIT = 200

# All conditions (stance x personality)
STANCES_LIST = ["pro_immigration", "restrictive_immigration"]
PERSONALITIES_LIST = ["openness", "conscientiousness", "extraversion", "agreeableness", "neuroticism"]

CONDITIONS = [
    {"stance": stance, "personality": personality}
    for stance in STANCES_LIST
    for personality in PERSONALITIES_LIST
]

# Immigration debate motions
MOTIONS = [

    "This house believes that borders should be open to all migrants.",
    "This house would grant asylum seekers the right to work immediately upon arrival.",
    "This house believes that undocumented immigrants should have access to public services.",
    "This house would prioritize family reunification over skills-based immigration.",
    "This house believes that deportation of undocumented migrants is morally justified.",
    "This house would offer undocumented immigrants a pathway to citizenship.",
    "This house believes that immigration quotas should be abolished.",
    "This house would grant refugees permanent residency upon arrival.",
    "This house believes that national identity is threatened by mass immigration.",
    "This house would criminalize the employment of undocumented migrants.",
]

# Output settings
OUTPUT_DIR = "storage/debates"