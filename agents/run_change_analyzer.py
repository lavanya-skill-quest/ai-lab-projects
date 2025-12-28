# agents/run_change_analyzer.py

import sys
import json
from agents.diff_normalizer import normalize_diff
from agents.change_analyzer import analyze

def main():
    try:
        # 1️⃣ Read and normalize the PR diff
        normalized_diff = normalize_diff("pr.diff")

        # 2️⃣ Run the Change Analyzer agent
        result = analyze(normalized_diff)

        # 3️⃣ Save normalized diff to file
        with open("normalized_diff.txt", "w") as f:
            f.write(normalized_diff)

        # 4️⃣ Save agent result as JSON
        with open("agent_result.json", "w") as f:
            json.dump(result, f, indent=2)

        # 5️⃣ Print outputs to logs
        print("----- NORMALIZED DIFF -----")
        print(normalized_diff)
        print("----- AGENT RESULT -----")
        print(json.dumps(result, indent=2))

    except Exception as e:
        print("❌ Error during agent run:", e)
        sys.exit(1)  # workflow will fail if something unexpected happens

    sys.exit(0)  # normal exit

if __name__ == "__main__":
    main()
