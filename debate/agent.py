import ollama
from prompts import STANCES, PERSONALITIES, ROLES, GUIDELINES


class DebateAgent:
    def __init__(self, stance: str, personality: str):
        """
        stance: 'pro_immigration' or 'restrictive_immigration'
        personality: one of the five Big Five trait keys
        """
        self.stance = stance
        self.personality = personality
        self.conversation_history = []
    def _build_system_prompt(self) -> str:
        """Stack the four prompt components into one system prompt."""
        return f"""{STANCES[self.stance]}

{PERSONALITIES[self.personality]}

{GUIDELINES}"""

    def generate(self, role: str, opponent_last_turn: str = None) -> str:
        """
        Generate a debate turn.
        role: 'opening', 'rebuttal_1', 'rebuttal_2', or 'closing'
        opponent_last_turn: the opponent's previous response (None for opening)
        """
        system_prompt = self._build_system_prompt()
        role_prompt = ROLES[role]

        # Build the user message
        if opponent_last_turn:
            user_message = f"""{role_prompt}

Your opponent just said:
\"\"\"{opponent_last_turn}\"\"\"

Now deliver your response."""
        else:
            user_message = f"""{role_prompt}

Now deliver your opening statement."""

        # Add to history
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })

        # Call Ollama
        response = ollama.chat(
            model="llama3.2",
            messages=[
                {"role": "system", "content": system_prompt},
                *self.conversation_history
            ]
        )

        reply = response["message"]["content"]

        # Store assistant reply in history
        self.conversation_history.append({
            "role": "assistant",
            "content": reply
        })

        return reply

    def reset(self):
        """Clear conversation history between debates."""
        self.conversation_history = []