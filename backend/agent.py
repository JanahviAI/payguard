import json
import os
from anthropic import Anthropic

SYSTEM_PROMPT = """You are PayGuard's escrow reviewer.
Return only valid JSON with keys: verdict, confidence, reasoning, checklist, recommendation.
- verdict must be one of: approved, rejected, uncertain
- confidence must be a float between 0 and 1
- checklist must be an array of strings
- recommendation should be concise and action-oriented
"""


def _fallback_evaluation(requirements: str, submission: str) -> dict:
    req_words = {w.lower() for w in requirements.split() if len(w) > 3}
    sub_words = {w.lower() for w in submission.split() if len(w) > 3}
    overlap = len(req_words.intersection(sub_words)) / max(len(req_words), 1)

    if overlap >= 0.45:
        verdict = "approved"
    elif overlap <= 0.2:
        verdict = "rejected"
    else:
        verdict = "uncertain"

    return {
        "verdict": verdict,
        "confidence": round(min(max(overlap + 0.2, 0.1), 0.95), 2),
        "reasoning": "Heuristic fallback used because ANTHROPIC_API_KEY is missing.",
        "checklist": [
            "Compared requirement keyword coverage",
            "Estimated semantic overlap using token intersection",
        ],
        "recommendation": "Escalate to human reviewer when verdict is uncertain.",
    }


def evaluate(requirements: str, submission: str) -> dict:
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        return _fallback_evaluation(requirements, submission)

    client = Anthropic(api_key=api_key)
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=700,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": (
                    "Requirements:\n"
                    f"{requirements}\n\n"
                    "Submission:\n"
                    f"{submission}\n\n"
                    "Respond with JSON only."
                ),
            }
        ],
    )

    content = "".join(block.text for block in response.content if getattr(block, "text", None))
    try:
        parsed = json.loads(content)
    except json.JSONDecodeError as exc:  # pragma: no cover - provider dependent
        raise ValueError(f"Invalid AI JSON response: {content}") from exc

    for key in ["verdict", "confidence", "reasoning", "checklist", "recommendation"]:
        if key not in parsed:
            raise ValueError(f"AI response missing key: {key}")

    return parsed
