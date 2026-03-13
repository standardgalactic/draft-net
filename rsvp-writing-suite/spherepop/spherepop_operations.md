# Spherepop Operations in the Writing Suite

## Overview

This document maps the abstract Spherepop operator vocabulary onto the
concrete operations available in the RSVP writing suite. It serves as a
reference for understanding what the tools are doing at the theoretical
level, and as a guide for extending the suite with new operations that
remain consistent with the Spherepop model.

---

## Operator Reference

### pop(context, event)

**Abstract**: evaluate and consume the top event in a context, returning
the modified context and any side-channel result.

**In the suite**: applying a single transform pass to a text span.

    rsvp-rewrite --pass redundancy_reduce scene.fountain

The scene text is the context. The pass is the event being popped. The
output is the modified context (rewritten text) plus the annotation
(side-channel result).

---

### bind(patch, diagnostic)

**Abstract**: attach a computation or label to a pending event without
yet evaluating it.

**In the suite**: loading a quickfix list.

    :RSVPEntropy

The entropy diagnostics are bound to line numbers in the quickfix list.
The binding does not yet modify the text; it prepares a set of pending
edit events for the author to evaluate or dismiss.

---

### collapse(event_sequence) → event

**Abstract**: reduce a sequence of events to a single composite event
that represents their net effect.

**In the suite**: committing a revision to Git.

    git commit -m "lamphrodyne_smooth: act 1 action blocks"

The individual edits made during the revision session are collapsed into
a single named event in the document's event history. The commit message
names the Spherepop operation that the collapse represents.

---

## VectorTrace

A VectorTrace is the trajectory of a character's intention vector across
the document. It is the sequence:

    trace(c) = (intention₁(c), intention₂(c), ..., intentionₖ(c))

where each intentionᵢ(c) is the mean embedding of the character's most
recent dialogue at scene i.

The VectorTrace makes character arc visible as a geometric object: a
curve in embedding space. Characters whose traces are straight lines have
consistent, perhaps monotonous, arcs. Characters whose traces exhibit
sharp turns have undergone genuine internal change. Characters whose
traces converge with another character's trace are becoming
indistinguishable.

`rsvp-persona` approximates VectorTraces through its voice similarity
and coherence diagnostics.

---

## EntropyPocket

An EntropyPocket is a Patch (or contiguous sequence of Patches) with:

    Sᵢ > θ_entropy  AND  Sᵢ₋₁ < θ_entropy  AND  Sᵢ₊₁ < θ_entropy

That is, a local entropy maximum surrounded by lower-entropy context.
EntropyPockets are the primary targets of lamphrodyne passes.

`rsvp-entropy` identifies and reports EntropyPockets. The quickfix
integration allows direct navigation to them from within Vim.

---

## ScalarNode

A ScalarNode is a local concentration of Φ associated with a recurring
motif, symbolic cluster, or thematic anchor. ScalarNodes are high-density
regions of the scalar field that have structural significance beyond their
local context.

ScalarNodes are not yet computed explicitly by the current tools, but they
can be approximated by tracking TF-IDF weight profiles of specific terms
across scene sequences.

---

## LamphrodynePass

A LamphrodynePass is any named, constrained transform that moves a text
patch toward a lower-entropy, more directionally coherent configuration.
The available passes are documented in `theory/lamphron_lamphrodyne.md`
and implemented in `rsvp/rewrite.py`.

A LamphrodynePass is always:

1. **Named**: it has a specific identifier (e.g. `torsion_sharpen`)
2. **Constrained**: it modifies only the targeted field quantity
3. **Inspectable**: it produces an annotation describing what changed
4. **Composable**: it can be piped with other passes through the shell

---

## Stagnation Basin

A stagnation basin is a contiguous sequence of Patches for which:

    |vᵢ| < θ_stagnation  for all i in the sequence

The field is static: no meaningful semantic motion is occurring. In a
screenplay, a stagnation basin often indicates a scene that has good
surface texture (dialogue, action) but no dramatic purpose.

`rsvp-flow` identifies stagnation basins and reports them in the
location list.

---

## Torsion Point

A torsion point is a Patch at which:

    κᵢ > θ_torsion

The directional field changes sharply: a narrative pivot, dramatic
reversal, or argumentative surprise. Torsion points are structurally
important and should be protected from inadvertent smoothing.

`rsvp-flow` reports torsion points with the symbol ↻ in terminal output.
