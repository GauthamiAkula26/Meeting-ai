import re
from typing import List


ACTION_PATTERNS = [
    r"(?i)\baction item[:\-]\s*(.+)",
    r"(?i)\bnext step[:\-]\s*(.+)",
    r"(?i)\bowner[:\-]\s*(.+)",
    r"(?i)\bwill\s+(.+)",
    r"(?i)\bneeds to\s+(.+)",
]

DECISION_PATTERNS = [
    r"(?i)\bdecision[:\-]\s*(.+)",
    r"(?i)\bdecided to\s+(.+)",
    r"(?i)\bagreed to\s+(.+)",
    r"(?i)\bwe will\s+(.+)",
]

RISK_PATTERNS = [
    r"(?i)\brisk[:\-]\s*(.+)",
    r"(?i)\bblocker[:\-]\s*(.+)",
    r"(?i)\bissue[:\-]\s*(.+)",
    r"(?i)\bconcern[:\-]\s*(.+)",
    r"(?i)\bdependency[:\-]\s*(.+)",
]


def _extract_by_patterns(text: str, patterns: List[str], limit: int = 8) -> List[str]:
    findings = []
    lines = [line.strip(" -•\t") for line in text.splitlines() if line.strip()]

    for line in lines:
        for pattern in patterns:
            m = re.search(pattern, line)
            if m:
                item = m.group(1).strip(" .:-")
                if len(item) > 3:
                    findings.append(item)
                break

    deduped = []
    seen = set()
    for item in findings:
        key = item.lower()
        if key not in seen:
            seen.add(key)
            deduped.append(item)

    return deduped[:limit]


def extract_action_items(text: str) -> List[str]:
    return _extract_by_patterns(text, ACTION_PATTERNS, limit=10)


def extract_decisions(text: str) -> List[str]:
    return _extract_by_patterns(text, DECISION_PATTERNS, limit=10)


def extract_risks(text: str) -> List[str]:
    return _extract_by_patterns(text, RISK_PATTERNS, limit=10)


def build_overview_summary(text: str, decisions: List[str], actions: List[str], risks: List[str]) -> str:
    lines = []
    lines.append(
        f"This meeting transcript contains {len(text.split())} words and focuses on planning, updates, and follow-up actions."
    )

    if decisions:
        lines.append(f"Key decisions identified: {len(decisions)}.")
    if actions:
        lines.append(f"Action items identified: {len(actions)}.")
    if risks:
        lines.append(f"Risks or blockers identified: {len(risks)}.")

    if decisions:
        lines.append(f"Example decision: {decisions[0]}")
    if actions:
        lines.append(f"Example action item: {actions[0]}")
    if risks:
        lines.append(f"Example risk/blocker: {risks[0]}")

    return " ".join(lines)
