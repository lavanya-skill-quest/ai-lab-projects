"""
Diff Normalization Utility

Purpose:
- Convert raw git diff (pr.diff) into an LLM-friendly, deterministic format
- Control token usage
- Preserve semantic meaning of code changes

This module MUST remain:
- Model-agnostic
- LangGraph-agnostic
- Deterministic
"""

import re
from typing import List


# -------------------------------------------------
# Step 1A: Read raw diff safely
# -------------------------------------------------

def read_diff(path: str) -> str:
    """
    Reads raw git diff from file.
    Handles non-UTF8 characters safely.
    """
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


# -------------------------------------------------
# Step 1B: Split diff by file
# -------------------------------------------------

def split_diff_by_file(diff_text: str) -> List[str]:
    """
    Splits a raw git diff into per-file diff blocks.

    Git guarantees each file starts with:
    'diff --git a/... b/...'
    """
    blocks = diff_text.split("diff --git ")
    return [b for b in blocks if b.strip()]


# -------------------------------------------------
# Step 1C: Extract file metadata
# -------------------------------------------------

def extract_filename(file_block: str) -> str:
    """
    Extracts the file path from a diff block.
    """
    first_line = file_block.splitlines()[0]
    match = re.search(r"a/(.*?) b/(.*)", first_line)
    if match:
        return match.group(2)
    return "unknown"


def extract_change_type(file_block: str) -> str:
    """
    Determines if a file was added, deleted, or modified.
    """
    for line in file_block.splitlines():
        if line.startswith("new file mode"):
            return "added"
        if line.startswith("deleted file mode"):
            return "deleted"
    return "modified"


# -------------------------------------------------
# Step 1D: Remove git noise
# -------------------------------------------------

def remove_git_noise(file_block: str) -> str:
    """
    Removes git metadata that is not useful for change analysis.
    """
    cleaned_lines = []

    for line in file_block.splitlines():
        if line.startswith("index "):
            continue
        if line.startswith("--- "):
            continue
        if line.startswith("+++ "):
            continue
        if line.startswith("new file mode"):
            continue
        if line.startswith("deleted file mode"):
            continue

        cleaned_lines.append(line)

    return "\n".join(cleaned_lines)


# -------------------------------------------------
# Step 1E: Keep only meaningful lines
# -------------------------------------------------

def extract_meaningful_lines(
    cleaned_diff: str,
    max_lines: int = 200
) -> str:
    """
    Keeps only meaningful diff lines:
    - Hunk headers (@@)
    - Added lines (+)
    - Removed lines (-)

    Applies a hard per-file line limit.
    """
    meaningful = []

    for line in cleaned_diff.splitlines():
        if line.startswith("@@") or line.startswith("+") or line.startswith("-"):
            meaningful.append(line)

        if len(meaningful) >= max_lines:
            break

    return "\n".join(meaningful)


# -------------------------------------------------
# Step 1F: Assemble final normalized diff
# -------------------------------------------------

def normalize_diff(
    path: str = "pr.diff",
    max_chars: int = 12000,
    max_lines_per_file: int = 200
) -> str:
    """
    Full normalization pipeline.

    Output:
    - Human-readable
    - LLM-friendly
    - Token-safe
    """
    raw_diff = read_diff(path)
    file_blocks = split_diff_by_file(raw_diff)

    assembled_sections = []

    for block in file_blocks:
        filename = extract_filename(block)
        change_type = extract_change_type(block)

        cleaned = remove_git_noise(block)
        meaningful = extract_meaningful_lines(
            cleaned,
            max_lines=max_lines_per_file
        )

        if not meaningful.strip():
            continue

        section = (
            f"FILE: {filename}\n"
            f"CHANGE_TYPE: {change_type}\n"
            f"{meaningful}"
        )

        assembled_sections.append(section)

    final_diff = "\n\n".join(assembled_sections)

    # Global safety cap
    if len(final_diff) > max_chars:
        final_diff = final_diff[:max_chars] + "\n...TRUNCATED..."

    return final_diff
