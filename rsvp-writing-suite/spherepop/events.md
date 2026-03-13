# Events in Spherepop

## Core Principle

Spherepop treats computation as a sequence of irreversible events.
Unlike systems in which state is mutable and history is discarded,
Spherepop formalises the event sequence as the primary ontological
object. The current state is derived from the history, not the other
way around.

Formally, an event e is any action that modifies the possible future
of a system. The event history of a system after k steps is:

    H = (e₁, e₂, ..., eₖ)

The system's current state is fully determined by H. There is no
independent state object; state is a function of history.

---

## Application to Writing and Editing

In a writing environment, every editorial action is an event. The events
that constitute document authorship include:

- inserting a sentence or paragraph
- deleting dialogue or action
- restructuring a scene (reordering patches)
- renaming a character
- applying a lamphrodyne transform pass
- committing a revision

Each event changes the future editing possibilities: the document after
event eₖ is a different object than the document before it, not merely
because its content has changed, but because its event history has grown.

This framing aligns naturally with version control systems. A Git commit
is a Spherepop event. The commit graph is the event history tree. Two
documents are equivalent if they were produced by the same sequence of
events from the same initial state.

---

## Identity Through History

Spherepop defines document identity through event history:

    Identity(D) = H(D)

Two documents D₁ and D₂ are equivalent if:

    D₁ ≅ D₂  ⟺  H(D₁) = H(D₂)

This has practical implications for the writing suite. When comparing
two versions of a screenplay, the relevant question is not only "what
is different in the text" but "what editorial events produced this
difference." A deletion followed by a rewrite has a different identity
from a gradual transformation, even if the final texts are similar.

---

## Irreversibility

Spherepop events are irreversible: once an event has occurred, it cannot
be undone in a way that erases it from history. What appears to be an
"undo" operation is, in Spherepop terms, a new event — a compensating
action that appends to H rather than subtracting from it.

This is directly analogous to Git's model: `git revert` does not erase
history; it adds a new commit that reverses the effect of a prior one.

The irreversibility principle has a methodological consequence for
revision work: all transforms in this suite are designed to be applied
to explicit, named, version-controlled working copies rather than
silently overwriting files. The preferred workflow is:

    1. Checkpoint: git commit -m "pre-rewrite state"
    2. Apply: rsvp-rewrite --pass lamphrodyne_smooth scene.fountain
    3. Review: git diff
    4. Accept or revert: git add / git checkout

---

## Pop, Bind, Collapse

In the Spherepop computational model, the three primitive operations are:

    pop      — evaluate and remove the top event from a context
    bind     — attach a computation to a pending event
    collapse — reduce a nested event structure to a single event

In the text editing context these correspond roughly to:

    pop      — apply a queued transform to a text span and consume it
    bind     — associate a diagnostic result with a specific patch
    collapse — merge a multi-step revision sequence into a single committed delta

The rewrite engine implements a simplified version of this model: each
`apply_pass` call is a pop; the diagnostic reports produced by entropy
and flow tools are bindings; the final `git commit` is a collapse.

---

## History as Document Identity

Because identity is defined through event history, the RSVP writing suite
treats the Git repository as a first-class component of the authorship
environment. The repository is not just a backup mechanism. It is the
arena in which Spherepop event histories are recorded and made inspectable.

This means the following practices are structurally consistent with the
framework:

- Small, named commits at each significant revision event
- Branch-per-draft for major structural experiments
- Commit messages that name the RSVP operation performed
  (e.g. "entropy_bleed_reduce: act 2 dialogue", "torsion_sharpen: scene 14")

These practices make the editorial field history readable and auditable,
which is a direct expression of the Spherepop principle that computation
is its history.
