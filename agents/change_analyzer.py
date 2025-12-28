import json
from urllib import response
import vertexai
from vertexai.generative_models import GenerativeModel

PROJECT_ID = "warm-aegis-482602-j4"
LOCATION = "us-central1"
MODEL_NAME = "gemini-2.0-flash"  # ✅ universally available


def analyze(diff_text: str):
    """
    Sends normalized diff to Gemini (Vertex AI Generative API).
    Returns a dictionary with risk assessment and summary.
    """

    vertexai.init(
        project=PROJECT_ID,
        location=LOCATION,
    )

    model = GenerativeModel(MODEL_NAME)

    prompt = f"""
You are a Change Analyzer Agent for Quality Engineering automation.

Your task is to analyze a pull request diff and return a STRICTLY VALID JSON object.

RULES (must follow all):
- Output MUST be valid JSON
- Output MUST contain ONLY the keys defined below
- Do NOT add or remove keys
- Do NOT include explanations, markdown, or text outside JSON
- Use ONLY these risk levels: LOW, MEDIUM, HIGH
- If uncertain, choose the lowest reasonable risk_level
- confidence MUST be a number between 0 and 1

Output schema (EXACT keys and types):
{{
  "risk_level": "LOW | MEDIUM | HIGH",
  "change_type": [string],
  "affected_areas": [string],
  "breaking_change": boolean,
  "summary": string,
  "confidence": number
}}

Pull Request Diff:
<<<
{diff_text[:12000]}
>>>
"""
    print("DEBUG: diff_text length =", len(diff_text))
    response = model.generate_content(
        prompt,
    generation_config={
        "temperature": 0.2,
        "max_output_tokens": 512,
    },
)

    output_text = response.text if response else ""
    print("DEBUG: model raw output (first 500 chars):")
    print(output_text[:500])  # <-- see what the model really returned

    return parse_agent_output(output_text)



def parse_agent_output(text):
    """
    Converts LLM text to validated dict.
    Returns fallback JSON if parsing fails.
    """

    required_keys = {
        "risk_level",
        "change_type",
        "affected_areas",
        "breaking_change",
        "summary",
        "confidence",
    }

    def default_for_key(key: str):
        if key == "risk_level":
            return "LOW"
        elif key in ["change_type", "affected_areas"]:
            return []
        elif key == "breaking_change":
            return False
        elif key == "summary":
            return "Parsing failed"
        elif key == "confidence":
            return 0.0
        return None

    # Strip markdown code blocks if present
    import re
    match = re.search(r"\{.*\}", text, re.DOTALL)
    json_text = match.group(0) if match else text

    try:
        data = json.loads(json_text)

        # Fill missing keys with defaults
        for key in required_keys:
            if key not in data:
                data[key] = default_for_key(key)

        return data

    except Exception:
        # Fallback if JSON parsing fails completely
        return {key: default_for_key(key) for key in required_keys}
