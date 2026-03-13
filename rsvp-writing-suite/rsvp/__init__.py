"""
rsvp — RSVP Writing Suite
=========================
A constraint-first authorship environment treating documents as evolving
scalar-vector-entropy fields.

Submodules:
  document   — Patch and Document data model
  metrics    — RSVP field approximations (Φ, v, S)
  parser     — Fountain and prose document parser
  entropy    — Entropy analysis and quickfix output
  flow       — Vector flow and curvature analysis
  persona    — Character field modeling
  beats      — Beat and scene topology mapper
  rewrite    — Constrained transform passes
"""

from .document import Patch, Document
from .metrics import Metrics
from .parser import parse, parse_fountain, parse_prose

__all__ = [
    "Patch", "Document", "Metrics",
    "parse", "parse_fountain", "parse_prose",
]
