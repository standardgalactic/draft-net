"""
rsvp.parser
===========
Converts Fountain screenplay files and plain prose into Document objects
composed of typed Patches.

Fountain format reference:
  https://fountain.io/syntax

Recognized element types:
  scene_heading   — INT./EXT. lines (also I/E, INT, EXT alone)
  action          — unformatted action/description paragraphs
  character       — all-caps lines preceding dialogue
  dialogue        — lines following a character cue
  parenthetical   — lines in parentheses within dialogue
  transition      — lines ending in TO: or FADE IN/OUT
  note            — [[double bracket notes]]
  section         — # Markdown-style section headers
  synopsis        — = synopsis lines
  page_break      — === explicit page breaks
  paragraph       — fallback for plain prose documents
"""

from __future__ import annotations
import re
from typing import List
from .document import Document, Patch


# ── Fountain patterns ─────────────────────────────────────────────────────────

_SCENE_RE = re.compile(
    r'^(INT|EXT|INT\./EXT|EXT\./INT|I/E)[\.\s]', re.IGNORECASE
)
_FORCED_SCENE_RE = re.compile(r'^\.')
_CHARACTER_RE = re.compile(r'^[A-Z][A-Z0-9 \-\']+(\s*\(.*\))?\s*$')
_PAREN_RE = re.compile(r'^\s*\(.*\)\s*$')
_TRANSITION_RE = re.compile(r'^(FADE\s+(IN|OUT|TO)|CUT\s+TO|SMASH\s+CUT).*:?\s*$', re.IGNORECASE)
_NOTE_RE = re.compile(r'^\[\[.*\]\]$')
_SECTION_RE = re.compile(r'^(#{1,3})\s+(.+)')
_SYNOPSIS_RE = re.compile(r'^=\s+(.+)')
_PAGE_BREAK_RE = re.compile(r'^={3,}\s*$')


def _is_blank(line: str) -> bool:
    return line.strip() == ""


def parse_fountain(text: str, source: str = "") -> Document:
    """
    Parse a Fountain-format screenplay into a Document of typed Patches.
    """
    lines = text.splitlines()
    patches: List[Patch] = []

    i = 0
    prev_was_blank = True
    in_dialogue = False
    current_speaker: str | None = None

    def flush_buffer(buf: List[str], start: int, kind: str,
                     label: str = "", speaker: str | None = None) -> None:
        content = "\n".join(buf).strip()
        if content:
            patches.append(Patch(
                text=content,
                start=start,
                end=i,
                kind=kind,
                label=label,
                speaker=speaker,
            ))

    buf: List[str] = []
    buf_start = 0
    buf_kind = "action"

    def commit() -> None:
        flush_buffer(buf, buf_start, buf_kind,
                     speaker=current_speaker if buf_kind == "dialogue" else None)
        buf.clear()

    while i < len(lines):
        line = lines[i]
        raw = line.rstrip()

        if _PAGE_BREAK_RE.match(raw):
            commit()
            patches.append(Patch(raw, i, i + 1, kind="page_break"))
            prev_was_blank = False
            in_dialogue = False
            i += 1
            continue

        if _is_blank(raw):
            commit()
            prev_was_blank = True
            in_dialogue = False
            current_speaker = None
            i += 1
            continue

        if _NOTE_RE.match(raw):
            commit()
            patches.append(Patch(raw, i, i + 1, kind="note"))
            prev_was_blank = False
            i += 1
            continue

        if _SECTION_RE.match(raw):
            commit()
            patches.append(Patch(raw, i, i + 1, kind="section"))
            prev_was_blank = False
            i += 1
            continue

        if _SYNOPSIS_RE.match(raw):
            commit()
            patches.append(Patch(raw, i, i + 1, kind="synopsis"))
            prev_was_blank = False
            i += 1
            continue

        if _SCENE_RE.match(raw) or _FORCED_SCENE_RE.match(raw):
            commit()
            slug = raw.lstrip(".")
            patches.append(Patch(slug, i, i + 1, kind="scene_heading", label=slug))
            prev_was_blank = False
            in_dialogue = False
            i += 1
            continue

        if _TRANSITION_RE.match(raw) and prev_was_blank:
            commit()
            patches.append(Patch(raw, i, i + 1, kind="transition"))
            prev_was_blank = False
            i += 1
            continue

        if prev_was_blank and _CHARACTER_RE.match(raw) and not in_dialogue:
            commit()
            current_speaker = raw.strip()
            in_dialogue = True
            buf_kind = "character"
            buf[:] = [raw]
            buf_start = i
            prev_was_blank = False
            i += 1
            # peek: next non-blank line should be dialogue or parenthetical
            commit()
            continue

        if in_dialogue and _PAREN_RE.match(raw):
            commit()
            patches.append(Patch(
                raw, i, i + 1, kind="parenthetical", speaker=current_speaker
            ))
            prev_was_blank = False
            i += 1
            continue

        if in_dialogue:
            if buf_kind != "dialogue":
                commit()
                buf_kind = "dialogue"
                buf_start = i
            buf.append(raw)
            prev_was_blank = False
            i += 1
            continue

        # Default: action
        if buf_kind != "action":
            commit()
            buf_kind = "action"
            buf_start = i
        buf.append(raw)
        prev_was_blank = False
        i += 1

    commit()
    return Document(patches=patches, source=source)


# ── Plain prose parser ────────────────────────────────────────────────────────

_HEADING_RE = re.compile(r'^(#{1,6})\s+(.+)')
_BLANK_LINE_SEP = re.compile(r'\n{2,}')


def parse_prose(text: str, source: str = "") -> Document:
    """
    Parse plain prose or Markdown into a Document of paragraph Patches.
    Headings become section patches; blank-line-separated blocks become
    paragraph patches.
    """
    patches: List[Patch] = []
    lines = text.splitlines()

    buffer: List[str] = []
    buf_start = 0

    def flush(end: int) -> None:
        content = "\n".join(buffer).strip()
        if not content:
            return
        m = _HEADING_RE.match(content.splitlines()[0])
        kind = "section" if m else "paragraph"
        label = m.group(2) if m else ""
        patches.append(Patch(content, buf_start, end, kind=kind, label=label))
        buffer.clear()

    for i, line in enumerate(lines):
        if _is_blank(line):
            flush(i)
            buf_start = i + 1
        else:
            if not buffer:
                buf_start = i
            buffer.append(line)

    flush(len(lines))
    return Document(patches=patches, source=source)


# ── Unified entry point ───────────────────────────────────────────────────────

def parse(text: str, source: str = "", fmt: str = "auto") -> Document:
    """
    Auto-detect or explicitly parse a document.

    fmt: "fountain" | "prose" | "auto"
    """
    if fmt == "fountain":
        return parse_fountain(text, source)
    if fmt == "prose":
        return parse_prose(text, source)

    # Auto-detect by file extension first, then content
    if source.endswith(".fountain"):
        return parse_fountain(text, source)
    if _SCENE_RE.search(text):
        return parse_fountain(text, source)
    return parse_prose(text, source)
