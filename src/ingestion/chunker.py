
import re


def chunk_by_heading(body: str) -> list[dict]:
    sections = re.split(r"\n(?=## )", body.strip())
    chunks = []
    leading_title = ""
    for section in sections:
        section = section.strip()
        if not section:
            continue
        heading_match = re.match(r"^## (.+)$", section, re.MULTILINE)
        if heading_match is None:
            # Leading '# Title' line before any '##' section - fold it into
            # the next real chunk instead of indexing a near-empty fragment.
            leading_title = section
            continue
        heading = heading_match.group(1).strip()
        text = (leading_title + "\n\n" + section).strip() if leading_title else section
        leading_title = ""
        chunks.append({"heading": heading, "text": text})
    return chunks