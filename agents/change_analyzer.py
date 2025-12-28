# agents/change_analyzer.py

def analyze(diff_text: str):
    """
    Stub for Change Analyzer Agent.

    Input:
        diff_text: normalized diff string from diff_normalizer

    Output:
        A dictionary with risk assessment (example)
    """
    # For debugging: print length of diff received
    print("Received diff of length:", len(diff_text))

    # TODO: replace this with actual Gemini model logic
    return {
        "risk_level": "UNKNOWN",
        "summary": "This is a placeholder result. Replace with Gemini analysis.",
        "files_analyzed": diff_text.count("FILE:")  # simple metric
    }
