# Lamphron, Lamphrodyne, and Transform Passes

## Overview

Within RSVP field theory, lamphrons are stable, low-entropy attractor
configurations in the scalar-vector-entropy field. A lamphron is a
region of the plenum that has settled into a locally coherent, directionally
stable, and informationally dense state. The term is borrowed from the
broader RSVP theoretical apparatus where lamphron attractors describe
persistent structural features of evolving fields.

Lamphrodyne is the name given to the smoothing process by which high-entropy,
low-coherence regions of a field are brought toward lamphron configurations.
In text, lamphrodyne smoothing corresponds to editing operations that reduce
local disorder without destroying directional motion or scalar density.

---

## Lamphron Attractors in Text

A lamphron in a text is a passage that satisfies all three of:

    Φ is high or appropriately moderate for its register
    |v| is nonzero — the passage is directed, not static
    S is below threshold — the passage is internally coherent

Literary examples:

- A well-constructed dramatic scene in which character intention is clear,
  action advances, and vocabulary is controlled
- A mathematical proof section in which definitions precede usage,
  transitions are explicit, and notation is consistent
- A manifesto paragraph in which each sentence extends the preceding one
  in a coherent argumentative direction

The concept of a lamphron attractor is therefore not a stylistic ideal in
the usual sense. It is a structural configuration that any genre can exhibit
if its internal field dynamics are well-ordered.

---

## Entropy Pockets and Lamphrodyne Passes

An **EntropyPocket** is a localized region of high S surrounded by lower-
entropy context. It is the primary target of lamphrodyne passes.

Common causes of entropy pockets in writing:

1. **Vocabulary scatter**: the author has drawn on too many registers or
   synonym clusters simultaneously, producing incoherent surface texture

2. **Unresolved referents**: pronouns or nominal phrases whose antecedents
   are ambiguous or absent, fragmenting the referential structure

3. **Tonal drift**: a patch that begins in one register (ironic, formal,
   intimate) and drifts into another without a marked transition

4. **Syntactic overcompression**: too many embedded clauses or coordinate
   structures compressed into a single sentence, raising local entropy
   without raising Φ proportionally

5. **Hedging accumulation**: connective fragments ("I mean," "Well," "So,")
   that lower scalar density while scattering the token distribution

---

## The Named Transforms

Each transform pass in `rsvp/rewrite.py` corresponds to a specific
lamphrodyne operation.

### `redundancy_reduce`

Removes exact duplicate lines within a patch.

    Input:  He waited. He waited. The door did not open. He waited.
    Output: He waited. The door did not open.

This is the simplest lamphrodyne pass: it removes tautological repetition
that raises S (through token frequency non-uniformity) without contributing
directional information.

### `lamphrodyne_smooth`

Merges dangling short sentences — typically fragments of fewer than three
words — into their neighbouring sentences.

Short fragments contribute disproportionately to entropy by introducing
isolated, low-frequency tokens. Merging them smooths the local entropy
profile without altering semantic content.

    Input:  She crossed the room. Slowly. Her heels on the marble.
    Output: She crossed the room slowly, her heels on the marble.

### `torsion_sharpen`

Removes hedging connectives that dilute torsion points.

Narrative pivots and argumentative reversals require high κ (curvature).
Hedging phrases — "Well, I mean, anyway," "So, look, the thing is" —
insert low-density, high-entropy tokens at exactly the positions where
directional sharpness is most needed.

    Input:  MARCUS: Look, I know what you think. You're wrong.
    Output: MARCUS: I know what you think. You're wrong.

### `entropy_bleed_reduce`

Identifies hapax legomena — tokens appearing only once in a patch —
and surfaces them for human review. Single-occurrence rare tokens often
indicate vocabulary bleed from an adjacent register.

This pass does not automatically replace tokens; it annotates candidates
for the author's inspection. The decision to replace, retain, or expand
remains with the author.

### Applying Passes in Sequence

The default `rsvp-rewrite --pass all` pipeline applies passes in this
order:

    1. redundancy_reduce
    2. lamphrodyne_smooth
    3. torsion_sharpen
    4. entropy_bleed_reduce

This order is intentional. Removing duplicates first stabilises the token
distribution before smoothing is applied. Torsion sharpening operates on
clean sentence boundaries. Entropy bleed analysis runs last, after the
other passes have already reduced obvious disorder.

---

## Design Constraint: Inspectability

All transform passes in this suite are constrained, inspectable, and
diff-comparable. The suite does not perform opaque generative rewriting.
Every pass has a named operation, a documented mechanism, and outputs
either the transformed text or an explicit annotation of what changed.

This constraint is architectural, not incidental. It reflects the RSVP
principle that authorship is recursive field steering: the author must
be able to observe the field, apply a targeted transform, observe the
result, and decide whether the field has moved in the intended direction.
Any tool that hides this feedback loop undermines the authorial agency
the suite is designed to amplify.
