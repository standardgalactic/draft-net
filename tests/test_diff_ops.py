from draftnet.extract.diffs import diff_summary


def test_diff_summary_has_counts():
    summary = diff_summary("abc", "abXYZc")
    assert summary["inserted_chars"] >= 0
    assert "diff" in summary
