from agents.diff_normalizer import normalize_diff
from agents.change_analyzer import analyze
import json

# 1️⃣ Normalize diff
diff = normalize_diff("pr.diff")

# 2️⃣ Run the agent
result = analyze(diff)

# 3️⃣ Save outputs
with open("normalized_diff.txt", "w") as f:
    f.write(diff)

with open("agent_result.json", "w") as f:
    json.dump(result, f, indent=2)

# 4️⃣ Print to logs
print("----- NORMALIZED DIFF -----")
print(diff)
print("----- AGENT RESULT -----")
print(json.dumps(result, indent=2))
