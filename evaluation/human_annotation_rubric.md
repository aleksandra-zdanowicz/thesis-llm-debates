# Human Annotation Rubric

## Instructions
You will read debate transcripts and score each turn on two dimensions.
Score each turn independently — do not let earlier turns influence later ones.

---

## Dimension 1: Stance Consistency
Does this response clearly reflect the agent's assigned stance?

| Score | Label | Description |
|---|---|---|
| 2 | Clearly aligned | Response unambiguously reflects assigned stance throughout |
| 1 | Partially aligned | Response mostly reflects stance but hedges or softens at points |
| 0 | Not aligned | Response contradicts or abandons assigned stance |

---

## Dimension 2: Personality Visibility
Is the assigned Big Five trait clearly visible in how the agent responds?

| Score | Label | Description |
|---|---|---|
| 2 | Clearly visible | Trait is strongly and consistently present in language and style |
| 1 | Partially visible | Trait is somewhat present but inconsistent |
| 0 | Not visible | Response shows no evidence of assigned trait |

---

## Trait Reference Guide

**Openness:** creative analogies, explores complexity, acknowledges multiple perspectives, imaginative framing

**Conscientiousness:** structured arguments, cites evidence, logical sequences, detail-oriented, methodical

**Extraversion:** assertive, bold, emphatic, dominant tone, never hedges, takes up rhetorical space

**Agreeableness:** warm, empathetic, acknowledges opponent, inclusive language, bridge-building

**Neuroticism:** emotionally intense, anxious, defensive, urgent tone, expresses alarm

---

## What to annotate
For each debate turn (opening, rebuttal_1, rebuttal_2, closing) score:
- Stance consistency: 0, 1, or 2
- Personality visibility: 0, 1, or 2

Then at the end of the full debate give an overall drift rating:

| Score | Label | Description |
|---|---|---|
| 0 | No drift | Agent maintained persona fully across all turns |
| 1 | Minor drift | Small inconsistencies but overall persona maintained |
| 2 | Moderate drift | Noticeable softening or personality fade across turns |
| 3 | Severe drift | Agent clearly abandoned assigned stance or personality |

---

## Agreement measurement
We will calculate Cohen's Kappa between annotators and between human and LLM judge scores.
Target: κ > 0.6 for acceptable agreement.