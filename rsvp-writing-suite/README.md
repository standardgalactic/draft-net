# RSVP Writing Suite

A constraint-first authorship environment in which documents are treated
as evolving scalar-vector-entropy fields. Text is not merely a sequence
of words. It is a structured plenum whose local density, directional flow,
and disorder can be measured, transformed, and steered.

Built for Bash and Vim on Linux/WSL. Python provides the semantic and
field-theoretic computation. Bash and Vim provide the interaction layer.

---

## Theoretical Basis

The suite is grounded in two theoretical frameworks:

**RSVP** (Relativistic Scalar-Vector Plenum) models a text as a field
manifold carrying three coupled quantities at each patch:

    Φ  — scalar density   (semantic weight, information concentration)
    v  — vector flow      (directional narrative or argumentative motion)
    S  — entropy          (structural disorder, vocabulary scatter)

**Spherepop** treats every editorial action as an irreversible event in
the document's history. The Git repository is the event record. Identity
is constituted by history, not by static state.

See `theory/` and `spherepop/` for full documentation including mathematics.

---

## Repository Layout

```
rsvp-writing-suite/
├── bin/                    Shell entry points (one per tool)
├── rsvp/                   Python package — core analysis and transforms
│   ├── document.py         Patch and Document data model
│   ├── metrics.py          RSVP field approximations (Φ, v, S)
│   ├── parser.py           Fountain screenplay and prose parser
│   ├── entropy.py          Entropy analysis + CLI
│   ├── flow.py             Vector flow and curvature analysis + CLI
│   ├── persona.py          Character field modeling + CLI
│   ├── beats.py            Beat and scene topology mapper + CLI
│   ├── rewrite.py          Constrained transform passes + CLI
│   └── parse_cmd.py        Parse CLI
├── vim/
│   ├── plugin/rsvp.vim     Vim commands and quickfix integration
│   └── ftplugin/           Filetype plugins for fountain and markdown
├── scripts/                Bash helpers (scene-current, script-audit, etc.)
├── examples/               Sample screenplay and essay
├── tests/                  pytest test suite
├── theory/                 RSVP theoretical substrate (Markdown)
├── spherepop/              Spherepop event model documentation
├── agents/                 Operational guides for coding and editing agents
└── pyproject.toml
```

---

## Installation

```bash
git clone https://github.com/yourname/rsvp-writing-suite
cd rsvp-writing-suite
pip install -e .                     # installs CLI entry points
# or use bin/ directly without installing:
export PATH="$PWD/bin:$PATH"
```

For production-quality embeddings (recommended for `rsvp-flow` and
`rsvp-persona`):

```bash
pip install -e ".[embeddings]"
# Then replace metrics.embed() with a sentence-transformers call
```

---

## Quick Start

```bash
# Parse a screenplay and inspect its structure
rsvp-parse examples/sample_screenplay.fountain --fmt text | less

# Scan for high-entropy regions (outputs quickfix-compatible list)
rsvp-entropy examples/sample_screenplay.fountain

# Measure narrative flow and find stagnation basins
rsvp-flow examples/sample_screenplay.fountain

# Beat topology map
rsvp-beats examples/sample_screenplay.fountain

# Character field report
rsvp-persona examples/sample_screenplay.fountain

# Full audit
scripts/script-audit examples/sample_screenplay.fountain

# Apply a named transform to a passage (pipe)
echo "He waited. He waited. The door did not open." | rsvp-rewrite --pass redundancy_reduce
```

---

## Vim Integration

Add the `vim/` directory to your Vim runtime path:

```vim
" In your .vimrc:
set runtimepath+=/path/to/rsvp-writing-suite/vim
let g:rsvp_bin_dir = '/path/to/rsvp-writing-suite/bin'
```

Available commands (in any buffer):

| Command              | Effect                                    |
|----------------------|-------------------------------------------|
| `:RSVPEntropy`       | Entropy scan → quickfix list              |
| `:RSVPFlow`          | Flow scan → location list                 |
| `:RSVPBeats`         | Beat topology → preview window            |
| `:RSVPPersona`       | Character field report → preview          |
| `:RSVPPersona NAME`  | Focus on named character                  |
| `:RSVPRewrite PASS`  | Apply transform to visual selection       |
| `:RSVPParse`         | Parse tree → preview window               |
| `:RSVPStatus`        | One-line field summary                    |

Fountain filetype key mappings (`<LocalLeader>` prefix):

    e  RSVPEntropy     f  RSVPFlow     b  RSVPBeats
    p  RSVPPersona     r  RSVPParse    s  RSVPStatus
    m  :make (entropy quickfix)

Scene navigation:  `]]` next scene,  `[[` previous scene

---

## Transform Passes

All rewrite transforms are constrained, named, and annotated.

| Pass                   | Operation                                        |
|------------------------|--------------------------------------------------|
| `redundancy_reduce`    | Remove exact duplicate lines                     |
| `lamphrodyne_smooth`   | Merge short dangling sentence fragments          |
| `torsion_sharpen`      | Remove hedging connectives before pivots         |
| `entropy_bleed_reduce` | Surface hapax tokens for review                  |

```bash
# Apply to file
rsvp-rewrite --pass lamphrodyne_smooth scene.txt

# Show annotation only (diff mode)
rsvp-rewrite --pass torsion_sharpen --diff scene.txt

# Apply all passes in sequence
rsvp-rewrite --pass all scene.txt
```

---

## RSVP Field Diagnostics Reference

```
Φᵢ = (1/N) Σ −log P(w)      scalar density (mean token information)
|vᵢ| = ‖E(pᵢ₊₁) − E(pᵢ)‖   flow magnitude (semantic displacement)
Sᵢ = −Σ p(w) log₂ p(w)      entropy (token distribution disorder)
κᵢ = ‖vᵢ − vᵢ₋₁‖            curvature (rate of directional change)
```

Beat types:

```
→ drive       |v| > 0.40               strong narrative momentum
· normal      default                  unremarkable
↻ pivot       κ > 0.35                 turning point or reversal
⬇ sink        |v| < 0.15, S < 2.5     tension absorbed without release
─ stagnation  |v| < 0.12              no directional motion
```

---

## Running Tests

```bash
pip install pytest
python -m pytest tests/ -v
```

---

## Theoretical Reading Order

1. `theory/rsvp_foundations.md`          — core RSVP field model
2. `theory/scalar_vector_entropy.md`     — field mathematics
3. `theory/lamphron_lamphrodyne.md`      — transform theory
4. `theory/narrative_field_model.md`     — screenplay application
5. `spherepop/events.md`                 — irreversibility and identity
6. `spherepop/spherepop_operations.md`  — operator vocabulary
7. `agents/coding_agent_guide.md`        — rules for code contributions
8. `agents/screenplay_agent_guide.md`   — rules for editorial assistance

---

## Design Philosophy

The tools in this suite are not generic AI writing assistants. Their
distinctiveness comes from treating writing as constrained field dynamics
rather than token prediction. Every transform is named. Every diagnostic
is interpretable. Every metric has a mathematical definition. The author
remains the field-theoretic agent. The software makes the field visible.
