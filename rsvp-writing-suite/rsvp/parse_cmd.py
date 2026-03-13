"""
rsvp.parse_cmd
==============
Command-line interface for rsvp-parse.
Parses a document and emits the intermediate representation
as JSON, YAML, or normalized plain text.
"""

from __future__ import annotations
import sys
import json
import argparse
from typing import Optional

from .parser import parse


def format_json(doc) -> str:
    data = {
        "source": doc.source,
        "metadata": doc.metadata,
        "patches": [
            {
                "index": i,
                "kind": p.kind,
                "label": p.label,
                "speaker": p.speaker,
                "start": p.start,
                "end": p.end,
                "text": p.text,
            }
            for i, p in enumerate(doc.patches)
        ],
    }
    return json.dumps(data, indent=2)


def format_text(doc) -> str:
    lines = []
    for i, p in enumerate(doc.patches):
        tag = f"[{p.kind}]"
        if p.label:
            tag += f"[{p.label}]"
        if p.speaker:
            tag += f"[{p.speaker}]"
        lines.append(f"--- {tag} line {p.start + 1} ---")
        lines.append(p.text)
        lines.append("")
    return "\n".join(lines)


def main(argv: Optional[list] = None) -> None:
    p = argparse.ArgumentParser(
        prog="rsvp-parse",
        description="Parse a Fountain or prose document into typed patches.",
    )
    p.add_argument("file", nargs="?")
    p.add_argument("--fmt", choices=["json", "text"], default="json")
    p.add_argument("--format", choices=["fountain", "prose", "auto"],
                   default="auto", dest="docfmt")
    args = p.parse_args(argv)

    if args.file:
        with open(args.file) as fh:
            text = fh.read()
        source = args.file
    else:
        text = sys.stdin.read()
        source = "<stdin>"

    doc = parse(text, source=source, fmt=args.docfmt)

    if args.fmt == "json":
        print(format_json(doc))
    else:
        print(format_text(doc))


if __name__ == "__main__":
    main()
