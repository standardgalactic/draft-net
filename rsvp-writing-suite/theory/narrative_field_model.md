# Narrative Field Model

## Overview

A screenplay or narrative document can be modeled as a field manifold
in which each scene occupies a local patch of the plenum and the overall
dramatic arc corresponds to the global structure of the field. This
document describes how the RSVP field model extends to narrative-specific
quantities: character intention vectors, scene topology, beat curvature,
and dramatic continuity.

---

## Scenes as Field Patches

In the RSVP field model, a scene is a contiguous region of the document
manifold bounded by scene headings. Within a scene, the field quantities
(Φ, v, S) are computed over the constituent action blocks and dialogue
clusters.

The scene-level RSVP profile is the mean of its constituent patch values:

    Φ_scene = (1/|scene|) Σ_{pᵢ ∈ scene} Φᵢ
    S_scene  = (1/|scene|) Σ_{pᵢ ∈ scene} Sᵢ
    |v|_scene = (1/|scene|) Σ_{pᵢ ∈ scene} |vᵢ|
    κ_scene  = (1/|scene|) Σ_{pᵢ ∈ scene} κᵢ

These four quantities define the beat classification used by `rsvp-beats`.

---

## Beat Classification

The topological type of a scene is determined by thresholding the
scene-level RSVP profile:

    pivot       κ_scene > 0.35         — turning point, reversal, revelation
    sink        |v|_scene < 0.15
                AND S_scene < 2.5      — tension absorbed without release
    stagnation  |v|_scene < 0.12       — no directional motion
    drive       |v|_scene > 0.40       — strong forward momentum
    normal      otherwise

A well-structured screenplay will exhibit a sequence of drive → sink →
pivot → drive patterns corresponding to the classic escalation-release-
reversal arc. Consecutive stagnation beats indicate sections that need
restructuring. Consecutive pivots without intervening drive beats may
indicate overloaded structure.

---

## Character Intention Vectors

Each character c can be modeled as a partially persistent vector source
whose intention field perturbs the local field of scenes in which they
appear.

The intention vector of character c at time i is approximated by the
mean embedding of their most recent n dialogue patches:

    intentionᵢ(c) = mean{ E(p) : p ∈ recent_dialogue(c, i, n=5) }

The projection of this vector onto the scene's directional field gives
the character's contribution to local flow:

    contribution(c, scene) = intention(c) · v_scene / ‖v_scene‖

Characters with high positive contribution are driving the scene forward.
Characters with near-zero contribution are present but not advancing
the dramatic field.

---

## Dramatic Continuity

The continuity of a scene transition is measured by cosine similarity
between the field vectors of adjacent scenes:

    continuity(sceneᵢ, sceneᵢ₊₁) = vᵢ · vᵢ₊₁ / (‖vᵢ‖ · ‖vᵢ₊₁‖)

High continuity: the two scenes share thematic or directional coherence.
Low continuity: a sharp tonal or conceptual break — acceptable at act
transitions, potentially disorienting elsewhere.

Entropy gradient at scene boundaries:

    ∇S_transition = S_scene(i+1) − S_scene(i)

Large ∇S at a transition may indicate that scene order should be revisited,
or that a bridging beat is needed.

---

## Motif Fields and ScalarNodes

A motif is a recurring semantic cluster — an image, phrase, object, or
concept that appears multiple times across the document. Each motif
occurrence contributes to a ScalarNode: a local concentration of Φ
associated with that motif's semantic content.

Motif recurrence across scenes produces a scalar field modulation:
scenes containing the motif have elevated Φ relative to their baseline.
This modulation can be tracked to ensure that motif recurrences are
structurally distributed rather than clustered or absent in critical
regions.

The simplest operationalisation is to compute the TF-IDF weight of a
given term across all scenes and plot its distribution across the scene
sequence.

---

## Document Graph

Beyond the linear sequence, a screenplay can be represented as a graph
G = (V, E) where:

    V = {scene patches, character nodes, motif nodes}
    E = {adjacency, character presence, motif recurrence, causal dependency}

RSVP metrics can then run relationally over this graph rather than only
linearly along the document ribbon. A scene that appears structurally
sound in isolation may look weak once the graph reveals that it
redundantly echoes an earlier scene without adding new directional
information.

This graph layer is planned for a future module (`rsvp/graph.py`) and
is not yet implemented in the current prototype.

---

## The Ribbon

The document is sometimes referred to as a Ribbon: the ordered sequence
of patches from first to last. The Ribbon is the primary axis of analysis
for entropy, flow, and beat topology. The document graph adds relational
structure above the Ribbon but does not replace it. Most diagnostic tools
operate on the Ribbon; relational diagnostics require the graph.
