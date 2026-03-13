from draftnet.extract.tex import TexNormalizationConfig, normalize_tex, structural_stats


def test_normalize_tex_comments():
    text = "hello % note\n\\section{A}\n"
    cfg = TexNormalizationConfig(strip_comments=True)
    out = normalize_tex(text, cfg)
    assert "%" not in out


def test_structural_stats_counts_sections():
    stats = structural_stats("\\section{X}\n\\subsection{Y}\n")
    assert stats["sections"] == 1
    assert stats["subsections"] == 1
