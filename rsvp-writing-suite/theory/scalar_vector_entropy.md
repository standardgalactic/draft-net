# Scalar, Vector, and Entropy Fields in Text

## Purpose

This document defines the operational mathematics of the three RSVP field
quantities as implemented in the `rsvp/metrics.py` module. It serves as
the bridge between the theoretical RSVP framework and the concrete
computational approximations used by the analysis tools.

---

## 1. Scalar Density Φ

### Conceptual definition

Scalar density measures how much semantic information is concentrated
within a span of text. A passage dense with rare, conceptually loaded
terms has high Φ. A passage of connective narration has low Φ.

### Mathematical definition

Let V be a token vocabulary and P(w) the probability of token w under
a reference corpus distribution. The information content of a token is:

    I(w) = −log₂ P(w)

The scalar density of patch pᵢ containing tokens w₁, ..., w_N is:

    Φᵢ = (1/N) Σₙ I(wₙ)

### Properties

- Φ ≥ 0 always
- Common tokens (the, and, is) contribute low I(w), lowering Φ
- Domain-specific or rare tokens contribute high I(w), raising Φ
- A patch consisting entirely of function words has Φ ≈ log₂(1000) ≈ 10
  under the current heuristic; a patch of rare technical vocabulary
  approaches log₂(1,000,000) ≈ 20

### Implementation note

`metrics.scalar_density()` uses a heuristic IDF weighting: tokens in a
hardcoded common-word set receive I(w) = log₂(1000); all others receive
I(w) = log₂(1,000,000). Production implementations should load a proper
corpus IDF table or use embedding norm as a proxy.

---

## 2. Vector Flow v and Displacement |v|

### Conceptual definition

The vector field represents directional semantic motion across the
document. It is defined at each patch as the embedding vector of that
patch's content, and its magnitude is the displacement to the next patch.

### Mathematical definition

Let E: text → ℝᵈ be a semantic embedding function. The flow vector at
patch pᵢ is:

    vᵢ = E(pᵢ)

The flow magnitude — the primary diagnostic quantity — is:

    |vᵢ| = ‖E(pᵢ₊₁) − E(pᵢ)‖₂

The curvature of the directional trajectory is:

    κᵢ = ‖vᵢ − vᵢ₋₁‖₂ = ‖E(pᵢ) − E(pᵢ₋₁)‖₂

### Derived diagnostic quantities

Cosine similarity between adjacent patches:

    sim(pᵢ, pᵢ₊₁) = (vᵢ · vᵢ₊₁) / (‖vᵢ‖ · ‖vᵢ₊₁‖)

High cosine similarity = thematic continuity.
Low cosine similarity = conceptual discontinuity.

Stagnation condition (for rsvp-flow):

    |vᵢ| < θ_stagnation

where θ_stagnation = 0.15 (default). Stagnant patches have low directional
motion and may require revision to advance the narrative or argument.

Torsion condition:

    κᵢ > θ_torsion

where θ_torsion = 0.40 (default). High-curvature positions are dramatic
pivots, revelations, or argumentative reversals.

### Implementation note

`metrics.embed()` currently uses a 16-dimensional TF-IDF-style vector
with hash-bucket projection and L2 normalisation. Replace with a proper
sentence transformer (e.g. sentence-transformers library) for production
use. The displacement and curvature computations are embedding-agnostic.

---

## 3. Entropy S

### Conceptual definition

Entropy measures structural disorder within a patch. High entropy patches
contain heterogeneous vocabulary, unresolved referents, abrupt tonal shifts,
or fragmented syntax. Low entropy patches are either focused and coherent
or repetitive and monotonous — context determines which.

### Mathematical definition

Let p(w) be the empirical frequency of token w within patch pᵢ. The
Shannon entropy of the patch is:

    Sᵢ = −Σ_{w ∈ V} p(w) log₂ p(w)

with the convention 0 log 0 = 0.

### Entropy gradient

The gradient detects abrupt changes in coherence between adjacent patches:

    ∇Sᵢ = Sᵢ₊₁ − Sᵢ

    ∇Sᵢ > θ_gradient  →  coherence collapse: patch i+1 is more disordered
    ∇Sᵢ < −θ_gradient →  coherence spike: patch i+1 is sharply narrower

Default threshold θ_gradient = 1.5 (in bits).

### Entropy range reference

    S ≈ 0.0 – 1.5   single repeated word or minimal vocabulary
    S ≈ 1.5 – 3.0   focused paragraph with limited vocabulary
    S ≈ 3.0 – 4.5   typical prose paragraph
    S ≈ 4.5 – 6.0   high vocabulary diversity (academic prose, dense exposition)
    S > 6.0          very high scatter; often indicates fragmented or mixed content

Default flagging threshold: S > 4.0.

---

## 4. Combined Diagnostics

The three fields interact to produce a richer topology. Key combined
patterns that the tools surface:

| Φ    | |v|  | S    | Interpretation                               |
|------|------|------|----------------------------------------------|
| high | low  | low  | Dense, static: possible over-compression      |
| high | low  | high | Dense, disordered: revision priority           |
| low  | high | low  | Light, directed: transitional narration        |
| low  | low  | low  | Inert: stagnation basin                        |
| any  | high | any  | Strong momentum: dramatic drive                |
| any  | any  | high | Entropy pocket: structural disorder            |

---

## 5. Character Influence Fields

For screenplay analysis, each character c with appearances at patch
indices P_c = {j₁, j₂, ...} generates an influence field over the
document:

    I_c(i) = Σ_{j ∈ P_c} exp(−λ|i − j|)

where λ is the decay constant (default λ = 0.1). This creates a
spatially decaying field centred on each character appearance.

Peak regions of I_c(i) mark scenes dominated by character c's narrative
presence. The total influence of a character is:

    I_c^total = Σᵢ I_c(i)

Characters with I_c^total > 2.5 × mean influence are flagged as
potentially dominant — their field may be overwhelming the dramatic
balance.

---

## 6. Voice Similarity

The voice signature of character c is the mean embedding of their
dialogue patches:

    μ_c = mean{ E(p) : p ∈ dialogue(c) }

Voice similarity between characters A and B is measured by cosine
similarity:

    sim(A, B) = (μ_A · μ_B) / (‖μ_A‖ · ‖μ_B‖)

Characters with sim(A, B) > 0.90 are flagged as voice-converging:
their dialogue has become difficult to distinguish.
