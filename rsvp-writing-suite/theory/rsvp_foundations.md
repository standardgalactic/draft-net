# RSVP Foundations

## Overview

RSVP — Relativistic Scalar-Vector Plenum — is a field-theoretic framework
in which any structured medium can be described by the simultaneous
evolution of three coupled field quantities: a scalar density field Φ, a
directional vector field v, and an entropy field S. The framework was
developed to model semantic, cognitive, and computational substrates as
genuine physical-style fields rather than as sequences of discrete symbols.

In the context of text and authorship, the central claim is that a document
is not merely a linear sequence of tokens. It is a structured plenum whose
local density, directional tendency, and disorder can be measured, tracked,
and deliberately shaped. Writing becomes constrained field steering.

---

## The Three Fields

### Scalar Field Φ

The scalar field represents the local density of meaningful content:
thematic weight, semantic concentration, symbolic load, or philosophical
intensity.

    High Φ: philosophical definitions, dramatic revelations, dense exposition
    Low  Φ: transitional narration, connective tissue, conventional dialogue

Φ is a real-valued function over the document domain. For a discrete
document partitioned into patches {p₁, p₂, ..., pₙ}, the scalar density
of each patch is:

    Φᵢ = (1/|pᵢ|) Σ_{w ∈ pᵢ} I(w)

where I(w) = −log P(w) is the information content of token w under a
reference corpus distribution P. Rare, conceptually loaded tokens carry
high information content and therefore elevate Φ.

### Vector Field v

The vector field represents directional tendency: the way meaning moves
across the document. In an essay this corresponds to argumentative
progression. In a screenplay it corresponds to character intention,
narrative motion, conflict escalation, or revelation.

The vector field is approximated by embedding displacements between
adjacent patches:

    vᵢ = E(pᵢ)
    |vᵢ| = ‖E(pᵢ₊₁) − E(pᵢ)‖

where E(p) is a semantic embedding of the patch. Large |vᵢ| indicates
meaningful progression; small |vᵢ| indicates stasis.

The curvature of the vector trajectory — the rate of directional change —
is:

    κᵢ = ‖vᵢ − vᵢ₋₁‖

High curvature corresponds to pivots, reversals, and revelations.

### Entropy Field S

The entropy field represents structural disorder within a patch:
heterogeneous vocabulary, unresolved references, tonal instability,
fragmented syntax, or conceptual scatter.

    Sᵢ = −Σ_{w ∈ V} p(w) log₂ p(w)

where p(w) is the empirical token frequency within the patch.

The entropy gradient detects abrupt coherence transitions:

    ∇Sᵢ = Sᵢ₊₁ − Sᵢ

A large positive ∇S indicates a sudden collapse of coherence. A large
negative ∇S indicates a sudden sharpening of focus — which may signal
either clarity or compression.

---

## The Patch Representation

A document D is modeled as an ordered sequence of discrete patches:

    D = {p₁, p₂, ..., pₙ}

Each patch pᵢ carries:

    pᵢ ↦ (Φᵢ, vᵢ, Sᵢ, κᵢ)

This defines the RSVP field profile of the document. The tools in this
suite compute, display, and transform these profiles.

---

## The Document as a Manifold

At a higher level of abstraction, the document can be treated as a
one-dimensional manifold M parameterized by position x ∈ [0, L], where
the three RSVP fields are continuous functions:

    Φ(x),   v(x),   S(x)

The discrete patch values are samples of these continuous fields. In this
framing:

- **Stagnation basins** are regions where |v(x)| ≈ 0 and ∇Φ(x) ≈ 0:
  the field is static and undirected.

- **Sink regions** are regions where v(x) converges but S(x) is low:
  tension is absorbed without release.

- **Torsion points** are positions where κ(x) is large: the directional
  field changes rapidly, marking pivots and reversals.

- **Entropy pockets** are localized regions of high S(x) surrounded by
  lower-entropy context: candidates for revision.

---

## RSVP and Writing

The operative claim for the writing suite is that authorship is recursive
field steering. A draft is not a finished object but a traversable field
manifold with detectable imbalances. The task of revision is to bring the
field into a desired configuration: appropriate scalar density for each
region, directional vectors that build coherently toward intended reversals,
entropy levels that match the intended tonal register of each patch.

The tools in this suite surface field diagnostics. They do not generate
text. All transforms are constrained, inspectable, and reversible. The
author remains the field-theoretic agent.

---

## Implementation Notes

The Python modules in `rsvp/` approximate the continuous RSVP fields
using discrete patch-level statistics:

- `metrics.py` — implements Φ, S, embedding, displacement, curvature
- `document.py` — implements the Patch and Document data model
- `entropy.py`  — threshold-based entropy diagnostics
- `flow.py`     — stagnation and torsion detection
- `beats.py`    — scene-level field aggregation and topology classification

The embeddings used in the current prototype are deterministic TF-IDF-style
vectors. Production deployments should replace `metrics.embed()` with a
proper sentence transformer. All other field quantities remain valid
regardless of embedding quality, as they depend only on relative
displacement and token frequency statistics.
