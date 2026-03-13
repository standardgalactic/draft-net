# Coding Agent Guide

## Purpose

This file provides operational rules for coding agents (automated or
AI-assisted) working within the RSVP writing suite repository. Read
this file before modifying any Python modules, adding new tools, or
extending the Vim integration.

---

## Conceptual Model

This repository implements a constraint-first authorship environment.
The central model is:

    Document = sequence of Patches
    Patch    = (text, start, end, kind, scalar_density, vector_flow, entropy)
    RSVP fields: Φ (scalar density), v (vector flow), S (entropy)

All analysis tools compute, display, or transform one or more of these
three quantities. No tool should perform opaque or non-inspectable
transformations.

Read `theory/rsvp_foundations.md` and `theory/scalar_vector_entropy.md`
before modifying `rsvp/metrics.py` or `rsvp/document.py`.

---

## Architecture Rules

### One module per concern

Each file in `rsvp/` has a single responsibility:

    document.py    — data model only, no computation
    metrics.py     — field approximations only, no I/O
    parser.py      — parsing only, no analysis
    entropy.py     — entropy analysis + CLI
    flow.py        — flow analysis + CLI
    persona.py     — character analysis + CLI
    beats.py       — scene topology + CLI
    rewrite.py     — transform passes + CLI
    parse_cmd.py   — parse CLI only

Do not add cross-module dependencies beyond what already exists.
In particular, do not import from `entropy.py` into `flow.py` or vice
versa. Both should import from `metrics.py` and `document.py` only.

### Three output formats

Every analysis module must support at least these three output formats:

    terminal  — human-readable columnar output with flag markers
    quickfix  — Vim quickfix format: file:line:col:message
    json      — structured JSON for piping and downstream processing

The `--fmt` argument controls the output format. All three formats
must produce output that is parseable by downstream Unix tools.

### All transforms must be named and annotated

Every function in `rsvp/rewrite.py` must:

1. Have a name that appears in the `TRANSFORMS` registry
2. Return `(result_text, annotation_string)`
3. Include a docstring that names the RSVP-theoretic operation it performs

Do not add transforms that produce output without annotation.

### No generative rewriting

The rewrite module must not call any external language model or generative
API. All transforms must be deterministic, text-level operations. If
semantic rewriting is desired in future, it must be implemented as a
separate module (`rsvp/generate.py`) with explicit opt-in invocation.

---

## Adding a New Tool

To add a new analysis tool (e.g. `rsvp-motif`):

1. Create `rsvp/motif.py` with analysis logic and a `main()` function
2. Create `bin/rsvp-motif` as a shell wrapper calling `python -m rsvp.motif`
3. `chmod +x bin/rsvp-motif`
4. Add a Vim command `:RSVPMotif` in `vim/plugin/rsvp.vim`
5. Add a key mapping in `vim/ftplugin/fountain.vim`
6. Write a theory document in `theory/` explaining the new field quantity
7. Add tests in `tests/test_motif.py`

Do not add tools that lack theory documentation.

---

## Metrics Module Guidelines

When modifying `rsvp/metrics.py`:

- Do not change the function signatures of `entropy()`, `scalar_density()`,
  `embed()`, `displacement()`, or `cosine_similarity()`
- The `Metrics` class must always expose these five methods
- If you improve the embedding quality (e.g. by integrating a proper
  sentence transformer), do so by replacing the body of `embed()` only
- Document the mathematical change in a comment in `metrics.py` and
  update `theory/scalar_vector_entropy.md`

---

## Parser Guidelines

The parser must produce correct Patch kinds for all Fountain elements:

    scene_heading, action, character, dialogue, parenthetical,
    transition, note, section, synopsis, page_break

If you add support for a new format (e.g. Final Draft XML, Celtx JSON),
add a new `parse_X()` function and register it in `parse()` under a new
`fmt` value. Do not modify the existing `parse_fountain()` function
except to fix bugs.

---

## Git Conventions

Commit messages should name the Spherepop operation performed:

    "add rsvp/motif.py: ScalarNode detection for recurring terms"
    "entropy_bleed_reduce: extend hapax threshold parameter"
    "vim: add :RSVPMotif command and fountain.vim key mapping"
    "theory: add motif_fields.md to theory/"

This keeps the event history of the repository readable as a sequence
of RSVP-theoretic operations, consistent with the Spherepop model
described in `spherepop/events.md`.
