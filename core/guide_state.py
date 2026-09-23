"""Small, deterministic helpers shared by the V1.5 screens and tests."""

import re

SECTIONS = ("SUMMARY", "WHAT", "WHY", "WATCH", "NEXT")


def parse_guidance(value):
    """Fail closed if the existing model did not produce a complete summary."""
    matches = list(re.finditer(r"^\[(SUMMARY|WHAT|WHY|WATCH|NEXT)\]\s*$", value, re.M))
    if tuple(match.group(1) for match in matches) != SECTIONS:
        raise ValueError("Incomplete guidance")
    sections = {}
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(value)
        sections[match.group(1)] = value[match.end():end].strip()
    if not all(sections.values()):
        raise ValueError("Empty guidance section")
    # The three discussion suggestions are a product requirement, not a loose prompt.
    if len(re.findall(r"^\s*[1-3][.)]\s+", sections["NEXT"], re.M)) != 3:
        raise ValueError("Expected three discussion suggestions")
    return sections


def clear_result(state):
    for key in list(state):
        if (key.startswith(("guide_result", "product_feedback", "_product_feedback", "ship_", "_ship_"))
                or key in {"messages", "user_state", "user_zip", "conversation_finished", "guide_copy_text", "guide_error"}):
            state.pop(key, None)


def clear_person(state):
    """Changing beneficiary must clear all clinical/conversation state, not just profile."""
    for key in list(state):
        if key not in {"selected_language", "_widget_selected_language", "font_size", "_widget_font_size"}:
            state.pop(key, None)


def valid_zip(value):
    return not value or bool(re.fullmatch(r"[0-9]{5}", value))
