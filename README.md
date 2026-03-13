# Draft-Net

Draft-Net is a research scaffold for trajectory learning over evolving artifacts such as LaTeX drafts, code revisions, and painting progress shots. Instead of modeling only final outputs, it models the path between early and late states.

The repository is organized around a single canonical abstraction: a draft trajectory made of ordered states, each with raw content, optional latent encodings, and derived diagnostics such as RSVP field features or spectral summaries.

## Quick start

Create a virtual environment, install the package in editable mode, then run one of the CLI entry points.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

A typical workflow is extraction, training, evaluation, then replay.

```bash
draftnet-extract --config configs/tex_revision.yaml
draftnet-train --config configs/text_bridge.yaml
draftnet-eval --config configs/text_bridge.yaml --checkpoint experiments/bridge.pt
draftnet-replay --config configs/text_bridge.yaml --checkpoint experiments/bridge.pt --trajectory tex_paper_001
```

## Current scope

This scaffold includes Git-based extraction, trajectory manifests, baseline text encoders, RSVP feature extraction, a bridge model, a velocity model, curriculum subdivision utilities, loss functions, and evaluation metrics. The image branch is represented structurally in the schema and configuration layer, but the first implementation is text-first so the core path-learning architecture is immediately usable.
