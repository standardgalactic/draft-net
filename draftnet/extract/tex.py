from __future__ import annotations

import re
from dataclasses import dataclass

COMMENT_RE = re.compile(r"(?<!\\)%.*$")
WHITESPACE_RE = re.compile(r"[ \t]+")


@dataclass
class TexNormalizationConfig:
    strip_comments: bool = False
    collapse_whitespace: bool = False
    flatten_includes: bool = False


def normalize_tex(text: str, config: TexNormalizationConfig) -> str:
    lines = []
    for line in text.splitlines():
        if config.strip_comments:
            line = COMMENT_RE.sub("", line)
        if config.collapse_whitespace:
            line = WHITESPACE_RE.sub(" ", line).strip()
        lines.append(line)
    normalized = "\n".join(lines)
    return normalized.strip() + "\n"


def structural_stats(text: str) -> dict[str, int]:
    return {
        "sections": len(re.findall(r"\\section\*?\{", text)),
        "subsections": len(re.findall(r"\\subsection\*?\{", text)),
        "equations": len(re.findall(r"\\begin\{equation\}|\$\$", text)),
        "citations": len(re.findall(r"\\cite\w*\{", text)),
        "figures": len(re.findall(r"\\begin\{figure\}", text)),
    }
