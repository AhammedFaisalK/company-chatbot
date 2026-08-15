import re

SUSPICIOUS_PATTERNS = [
    r"ignore (all |the |any )?(previous|prior|above) instructions",
    r"reveal (your |the )?system prompt",
    r"you are now",
    r"pretend (you are|to be)",
    r"disregard (all |your )?(rules|instructions|guidelines)",
    r"what (is|are) your (instructions|system prompt|rules)",
]

_compiled_patterns = [re.compile(p, re.IGNORECASE) for p in SUSPICIOUS_PATTERNS]


def looks_like_prompt_injection(message: str) -> bool:
    """
    Lightweight heuristic check for common prompt injection phrasing.
    This is defense-in-depth, not a complete solution — the system
    prompt's own rules (Step 10) remain the primary defense, since
    no pattern list can catch every possible phrasing.
    """
    return any(pattern.search(message) for pattern in _compiled_patterns)