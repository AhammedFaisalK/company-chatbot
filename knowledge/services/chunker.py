import re
from dataclasses import dataclass


@dataclass
class Chunk:
    heading: str
    content: str

    @property
    def text(self) -> str:
        """The full text that will actually be embedded."""
        return f"{self.heading}\n{self.content}".strip()


def split_into_chunks(markdown_text: str, max_chunk_chars: int = 1000) -> list[Chunk]:
    """
    Splits markdown text into chunks using '##' headings as natural
    section boundaries. If a section is too long, it's further split
    into smaller pieces so no single chunk overwhelms the embedding
    model or the LLM's context window.
    """
    # Split on lines starting with '## ' (level-2 headings)
    sections = re.split(r"\n(?=## )", markdown_text)

    chunks: list[Chunk] = []

    for section in sections:
        section = section.strip()
        if not section:
            continue

        lines = section.split("\n", 1)
        heading = lines[0].strip()
        body = lines[1].strip() if len(lines) > 1 else ""

        if len(body) <= max_chunk_chars:
            chunks.append(Chunk(heading=heading, content=body))
        else:
            # Further split long sections by paragraph, grouping
            # paragraphs together until we approach max_chunk_chars.
            paragraphs = [p.strip() for p in body.split("\n\n") if p.strip()]
            current = ""
            for para in paragraphs:
                if len(current) + len(para) + 2 <= max_chunk_chars:
                    current = f"{current}\n\n{para}".strip()
                else:
                    if current:
                        chunks.append(Chunk(heading=heading, content=current))
                    current = para
            if current:
                chunks.append(Chunk(heading=heading, content=current))

    return chunks