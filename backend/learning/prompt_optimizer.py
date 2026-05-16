# learning/prompt_optimizer.py

import os

PROMPT_FILE = "prompts/generator_prompt.txt"


def analyze_feedback(feedback: str):
    """
    Simple rule-based analysis (extend later with ML)
    """
    feedback = feedback.lower()

    improvements = []

    if "missing" in feedback or "incomplete" in feedback:
        improvements.append("Ensure answers are complete and cover all key aspects.")

    if "unclear" in feedback or "not clear" in feedback:
        improvements.append("Improve clarity with step-by-step explanation.")

    if "no example" in feedback:
        improvements.append("Always include at least one example.")

    if "incorrect" in feedback:
        improvements.append("Ensure factual correctness and alignment with context.")

    return improvements


def update_prompt(feedback):
    """
    Append improvements to generator prompt
    """
    improvements = analyze_feedback(feedback)

    if not improvements:
        return

    if not os.path.exists(PROMPT_FILE):
        return

    with open(PROMPT_FILE, "a") as f:
        f.write("\n\n# Auto-Improvement Rules:\n")

        for rule in improvements:
            f.write(f"- {rule}\n")