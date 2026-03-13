# Screenplay Editing Agent Guide

## Purpose

This file provides operational rules for agents assisting with screenplay
analysis and revision within the RSVP writing suite. It defines how to
interpret tool output, when to suggest transforms, and what constraints
govern editorial interventions.

---

## Fundamental Rule

The author is the field-theoretic agent. The suite provides diagnostics
and constrained transforms. Agents assist by surfacing structured
information and suggesting targeted operations. Agents do not rewrite
freely; they propose named transforms and wait for author confirmation.

---

## Reading Tool Output

### rsvp-entropy output

Lines marked with `*` are flagged patches. The flag means one of:

- `high entropy (N.NN)` — the patch has S > threshold; vocabulary is
  scattered or structure is fragmented
- `entropy gradient +N.NN` — the following patch has significantly
  higher entropy; a coherence break is occurring at this boundary

**What to do**: jump to flagged lines in Vim (`:cn` / `:cp`). Read the
passage. Determine whether the high entropy is intentional (e.g. a
character in genuine confusion, an intentionally fragmented monologue)
or structural noise. If the latter, suggest a specific transform.

### rsvp-flow output

Symbols:

    →  strong drive  (|v| > 0.40)
    ·  normal flow
    ↻  torsion point (κ > 0.40) — narrative pivot
    ─  stagnation    (|v| < 0.15)
    ⬇  sink          (|v| < 0.15 and S < 2.5)

Stagnation patches are revision priorities. Torsion points are structurally
important and should be protected.

### rsvp-beats output

Beat types:

    drive      — scenes with strong forward momentum; protect these
    normal     — unremarkable; may need minor tuning
    pivot      — turning points; verify they have earned dramatic weight
    sink       — tension absorbed without release; often need restructuring
    stagnation — no motion at all; high revision priority

A healthy dramatic arc shows: drive → sink → pivot → drive, possibly
with normal beats in between. Consecutive sinks or stagnation beats
indicate structural problems in that region.

### rsvp-persona output

Voice similarity flags mean two characters' dialogue embeddings have
become too similar (cosine > 0.90). Suggest: read the two characters'
recent dialogue side by side. Identify which character has drifted.
Propose targeted dialogue revision for the drifted character.

Dominance flags mean a character's influence field is more than 2.5×
the mean. This is not automatically bad: protagonists should dominate.
But in ensemble scenes or secondary acts, unexpected dominance may
indicate imbalance.

---

## Transform Selection Guide

| Diagnostic              | Suggested Transform         |
|-------------------------|-----------------------------|
| High S in action block  | `lamphrodyne_smooth`        |
| Exact line repetition   | `redundancy_reduce`         |
| Hedging before pivot    | `torsion_sharpen`           |
| Vocabulary scatter      | `entropy_bleed_reduce`      |
| Voice convergence       | Manual dialogue revision    |
| Stagnation basin        | Manual scene restructuring  |
| Sink region             | Manual beat addition        |
| Pivot without drive     | Manual preceding beat check |

Transforms can be applied to visual selections in Vim:

    select lines → :RSVPRewrite transform_name

Always apply to a selection, not the whole file, unless a global pass
is explicitly requested.

---

## Conventions for Scene Analysis

When analysing a specific scene:

1. Extract the scene: `scene-current FILE LINE | rsvp-entropy`
2. Check beat type: look up scene in `rsvp-beats` output
3. Check character presence: `char-report CHARACTER FILE`
4. Identify the dominant field issue (entropy, stagnation, voice)
5. Propose one named transform or a structural question

Do not propose more than one transform per analysis turn. The author
needs to see the effect of one change before the next is applied.

---

## What Agents Must Not Do

- Do not apply transforms without showing the annotation first
- Do not suggest changes to torsion points without explicit author
  confirmation that the pivot is unintentional
- Do not suggest removing a character's dialogue on the basis of
  dominance alone; dominance may be structurally correct
- Do not interpret entropy as uniformly bad; some high-S passages are
  intentional (fragmented interior monologue, overlapping dialogue,
  disorienting exposition)
- Do not suggest generative rewrites; suggest named transforms only
