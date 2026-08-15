from pathlib import Path


def load_markdown_file(file_path: Path) -> str:
    """
    Reads a markdown file from disk and returns its raw text content.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def clean_text(text: str) -> str:
    """
    Basic cleanup: normalize line endings and collapse excessive blank lines.
    We deliberately keep markdown headings (##) intact — they're used
    as chunk boundaries in the next step.
    """
    text = text.replace("\r\n", "\n")

    lines = text.split("\n")
    cleaned_lines = []
    blank_streak = 0

    for line in lines:
        stripped = line.rstrip()
        if stripped == "":
            blank_streak += 1
            if blank_streak <= 1:
                cleaned_lines.append("")
        else:
            blank_streak = 0
            cleaned_lines.append(stripped)

    return "\n".join(cleaned_lines).strip()