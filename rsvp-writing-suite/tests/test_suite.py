"""
tests/test_suite.py
===================
Integration and unit tests for the RSVP writing suite.

Run with:  python -m pytest tests/ -v
Or:        python -m pytest tests/test_suite.py -v
"""

import sys
import os
import math
import json
import pytest

# Ensure the package root is on sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from rsvp.metrics import entropy, scalar_density, embed, displacement, cosine_similarity, Metrics
from rsvp.document import Patch, Document
from rsvp.parser import parse_fountain, parse_prose, parse
from rsvp.entropy import analyse as entropy_analyse, format_quickfix, format_json as entropy_json
from rsvp.flow import analyse as flow_analyse
from rsvp.persona import build_profiles, compute_signatures, influence_field
from rsvp.beats import analyse as beats_analyse
from rsvp.rewrite import (
    redundancy_reduce, lamphrodyne_smooth,
    torsion_sharpen, entropy_bleed_reduce, apply_all
)


# ── Fixtures ──────────────────────────────────────────────────────────────────

FOUNTAIN_SAMPLE = """\
INT. ARCHIVE — NIGHT

A woman studies drawings spread across a table.

MARIAN
I found what was left of them.

HENRIK
That's not nothing.

MARIAN
It depends on what you were looking for.

EXT. COURTYARD — NIGHT

Rain. Two figures cross the empty square.

HENRIK
If you publish this you'll have every crank in Europe writing to you.

MARIAN
They're already writing to me.
"""

PROSE_SAMPLE = """\
# On Structure

Every system that persists converts irreversibility into identity.
The arrow of time is the condition under which structured things exist.

## Entropy

High entropy is often confused with disorder.
The confusion costs us the ability to read structure clearly.
A dense technical passage has high entropy and high coherence simultaneously.
"""


# ── Metrics tests ─────────────────────────────────────────────────────────────

class TestMetrics:

    def test_entropy_empty(self):
        assert entropy("") == 0.0

    def test_entropy_single_token(self):
        # Single repeated token → entropy = 0
        assert entropy("the the the the") == 0.0

    def test_entropy_uniform(self):
        # All distinct tokens → entropy = log2(N)
        text = "alpha beta gamma delta"
        e = entropy(text)
        assert e == pytest.approx(math.log2(4), rel=1e-6)

    def test_entropy_positive_mixed(self):
        e = entropy("The quick brown fox jumps over the lazy dog")
        assert e > 0.0

    def test_scalar_density_common(self):
        # All common words → lower density
        s = scalar_density("the and is it a to of")
        assert s < scalar_density("phenomenological substrate irreversibility")

    def test_embed_length(self):
        v = embed("some text here")
        assert len(v) == 16

    def test_embed_normalized(self):
        v = embed("constrained transformation entropy")
        norm = math.sqrt(sum(x*x for x in v))
        assert norm == pytest.approx(1.0, rel=1e-5)

    def test_embed_empty(self):
        v = embed("")
        assert v == [0.0] * 16

    def test_displacement_identical(self):
        v = embed("some text")
        assert displacement(v, v) == pytest.approx(0.0, abs=1e-10)

    def test_displacement_different(self):
        v1 = embed("the quick brown fox")
        v2 = embed("entropy field irreversibility substrate")
        assert displacement(v1, v2) > 0.0

    def test_cosine_self(self):
        v = embed("recursive scalar vector plenum")
        assert cosine_similarity(v, v) == pytest.approx(1.0, rel=1e-5)

    def test_cosine_empty(self):
        assert cosine_similarity([], []) == 0.0

    def test_metrics_class(self):
        m = Metrics()
        assert m.entropy("hello world") == entropy("hello world")
        assert m.scalar("hello world") == scalar_density("hello world")


# ── Parser tests ──────────────────────────────────────────────────────────────

class TestParser:

    def test_fountain_scene_headings(self):
        doc = parse_fountain(FOUNTAIN_SAMPLE)
        scenes = [p for p in doc.patches if p.kind == "scene_heading"]
        assert len(scenes) == 2
        assert "ARCHIVE" in scenes[0].label
        assert "COURTYARD" in scenes[1].label

    def test_fountain_dialogue(self):
        doc = parse_fountain(FOUNTAIN_SAMPLE)
        dialogue = [p for p in doc.patches if p.kind == "dialogue"]
        assert len(dialogue) >= 3

    def test_fountain_characters(self):
        doc = parse_fountain(FOUNTAIN_SAMPLE)
        speakers = {p.speaker for p in doc.patches if p.speaker}
        assert "MARIAN" in speakers
        assert "HENRIK" in speakers

    def test_fountain_no_empty_patches(self):
        doc = parse_fountain(FOUNTAIN_SAMPLE)
        for p in doc.patches:
            assert p.text.strip() != ""

    def test_prose_paragraphs(self):
        doc = parse_prose(PROSE_SAMPLE)
        paragraphs = [p for p in doc.patches if p.kind == "paragraph"]
        assert len(paragraphs) >= 2

    def test_prose_sections(self):
        doc = parse_prose(PROSE_SAMPLE)
        sections = [p for p in doc.patches if p.kind == "section"]
        assert len(sections) >= 2

    def test_auto_detect_fountain(self):
        doc = parse(FOUNTAIN_SAMPLE, fmt="auto")
        kinds = {p.kind for p in doc.patches}
        assert "scene_heading" in kinds

    def test_auto_detect_prose(self):
        doc = parse(PROSE_SAMPLE, fmt="auto")
        kinds = {p.kind for p in doc.patches}
        assert "section" in kinds or "paragraph" in kinds


# ── Entropy analysis tests ────────────────────────────────────────────────────

class TestEntropyAnalysis:

    def test_reports_produced(self):
        doc = parse_fountain(FOUNTAIN_SAMPLE)
        reports = entropy_analyse(doc)
        assert len(reports) == len(doc.patches)

    def test_scores_are_floats(self):
        doc = parse_prose(PROSE_SAMPLE)
        reports = entropy_analyse(doc)
        for r in reports:
            assert isinstance(r.score, float)
            assert r.score >= 0.0

    def test_quickfix_format(self):
        doc = parse_fountain(FOUNTAIN_SAMPLE, source="test.fountain")
        reports = entropy_analyse(doc, entropy_threshold=0.0)  # flag everything
        qf = format_quickfix(reports, "test.fountain")
        for line in qf.splitlines():
            assert "test.fountain:" in line

    def test_json_format(self):
        doc = parse_prose(PROSE_SAMPLE)
        reports = entropy_analyse(doc)
        data = json.loads(entropy_json(reports))
        assert isinstance(data, list)
        assert all("entropy" in item for item in data)

    def test_flagging_threshold(self):
        doc = parse_fountain(FOUNTAIN_SAMPLE)
        reports_low  = entropy_analyse(doc, entropy_threshold=0.0)
        reports_high = entropy_analyse(doc, entropy_threshold=999.0)
        assert sum(r.flagged for r in reports_low) >= sum(r.flagged for r in reports_high)


# ── Flow analysis tests ───────────────────────────────────────────────────────

class TestFlowAnalysis:

    def test_reports_produced(self):
        doc = parse_fountain(FOUNTAIN_SAMPLE)
        reports = flow_analyse(doc)
        assert len(reports) == len(doc.patches)

    def test_flag_values(self):
        doc = parse_fountain(FOUNTAIN_SAMPLE)
        reports = flow_analyse(doc)
        valid_flags = {"stagnation", "torsion", "strong", "ok"}
        for r in reports:
            assert r.flag in valid_flags

    def test_last_patch_zero_flow(self):
        doc = parse_prose(PROSE_SAMPLE)
        reports = flow_analyse(doc)
        # Last patch has no successor → flow magnitude should be 0
        assert reports[-1].flow_magnitude == pytest.approx(0.0, abs=1e-10)


# ── Persona analysis tests ────────────────────────────────────────────────────

class TestPersonaAnalysis:

    def test_profiles_extracted(self):
        doc = parse_fountain(FOUNTAIN_SAMPLE)
        profiles = build_profiles(doc)
        assert "MARIAN" in profiles
        assert "HENRIK" in profiles

    def test_dialogue_counts(self):
        doc = parse_fountain(FOUNTAIN_SAMPLE)
        profiles = build_profiles(doc)
        assert len(profiles["MARIAN"].dialogue_patches) >= 2
        assert len(profiles["HENRIK"].dialogue_patches) >= 2

    def test_signatures_computed(self):
        doc = parse_fountain(FOUNTAIN_SAMPLE)
        m = Metrics()
        profiles = build_profiles(doc)
        compute_signatures(profiles, m)
        for prof in profiles.values():
            assert len(prof.mean_embedding) == 16
            assert prof.voice_entropy >= 0.0

    def test_influence_field_shape(self):
        doc = parse_fountain(FOUNTAIN_SAMPLE)
        profiles = build_profiles(doc)
        fields = influence_field(profiles, len(doc.patches))
        for name, field_vec in fields.items():
            assert len(field_vec) == len(doc.patches)
            assert all(v >= 0.0 for v in field_vec)


# ── Beat analysis tests ───────────────────────────────────────────────────────

class TestBeatAnalysis:

    def test_reports_produced(self):
        doc = parse_fountain(FOUNTAIN_SAMPLE)
        reports = beats_analyse(doc)
        assert len(reports) >= 1

    def test_beat_types_valid(self):
        doc = parse_fountain(FOUNTAIN_SAMPLE)
        reports = beats_analyse(doc)
        valid = {"pivot", "sink", "stagnation", "drive", "normal"}
        for r in reports:
            assert r.beat_type in valid

    def test_scene_labels_populated(self):
        doc = parse_fountain(FOUNTAIN_SAMPLE)
        reports = beats_analyse(doc)
        assert any(r.scene_label != "" for r in reports)


# ── Rewrite tests ─────────────────────────────────────────────────────────────

class TestRewrite:

    def test_redundancy_reduce_removes_duplicates(self):
        text = "He waited.\nHe waited.\nThe door did not open.\nHe waited."
        result, ann = redundancy_reduce(text)
        lines = result.splitlines()
        assert lines.count("He waited.") == 1
        assert "The door did not open." in result
        assert "removed" in ann

    def test_redundancy_reduce_no_change(self):
        text = "alpha\nbeta\ngamma"
        result, ann = redundancy_reduce(text)
        assert result == text
        assert "0 duplicate" in ann

    def test_lamphrodyne_smooth_runs(self):
        text = "She crossed the room. Slowly. Her heels on the marble."
        result, ann = lamphrodyne_smooth(text)
        assert isinstance(result, str)
        assert isinstance(ann, str)

    def test_torsion_sharpen_removes_hedges(self):
        text = "MARCUS: Well, I know what you think.\nYou're wrong."
        result, ann = torsion_sharpen(text)
        assert "Well," not in result
        assert "You're wrong." in result
        assert "removed" in ann

    def test_entropy_bleed_returns_annotation(self):
        text = "The phenomenological substrate exhibits irreversible lamphrodyne dynamics."
        result, ann = entropy_bleed_reduce(text)
        # Text should be unchanged; annotation surfaces candidates
        assert result == text
        assert "hapax" in ann

    def test_apply_all_returns_annotations(self):
        text = "He waited.\nHe waited.\nWell, slowly.\nThe door."
        result, annotations = apply_all(text)
        assert isinstance(result, str)
        assert len(annotations) == 4
        assert all(isinstance(a, str) for a in annotations)


# ── Document model tests ──────────────────────────────────────────────────────

class TestDocument:

    def test_compute_fields(self):
        doc = parse_prose(PROSE_SAMPLE)
        m = Metrics()
        doc.compute_fields(m)
        for p in doc.patches:
            assert p.scalar_density is not None
            assert p.entropy is not None
            assert p.flow_magnitude is not None
            assert p.curvature is not None

    def test_high_entropy_patches(self):
        doc = parse_prose(PROSE_SAMPLE)
        m = Metrics()
        doc.compute_fields(m)
        flagged = doc.high_entropy_patches(threshold=0.0)
        assert len(flagged) == len(doc.patches)  # everything flagged at threshold=0

    def test_dialogue_by_character(self):
        doc = parse_fountain(FOUNTAIN_SAMPLE)
        by_char = doc.dialogue_by_character()
        assert "MARIAN" in by_char
        assert all(p.kind == "dialogue" for patches in by_char.values() for p in patches)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
