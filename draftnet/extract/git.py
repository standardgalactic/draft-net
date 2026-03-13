from __future__ import annotations

from pathlib import Path
from typing import Iterable, List

from git import Repo

from draftnet.extract.diffs import diff_summary
from draftnet.extract.tex import TexNormalizationConfig, normalize_tex, structural_stats
from draftnet.types import DraftState, DraftTrajectory
from draftnet.utils.hashing import hash_text
from draftnet.utils.io import write_text


def iter_matching_files(repo: Repo, file_globs: Iterable[str]) -> List[str]:
    tree = repo.head.commit.tree
    paths: List[str] = []
    for blob in tree.traverse():
        if blob.type != "blob":
            continue
        path = blob.path
        if any(Path(path).match(g) for g in file_globs):
            paths.append(path)
    return sorted(set(paths))


def collect_file_history(repo_path: str, file_path: str) -> List[str]:
    repo = Repo(repo_path)
    commits = list(repo.iter_commits(paths=file_path))
    commits.reverse()
    return [c.hexsha for c in commits]


def build_trajectory_from_git(repo_path: str, file_path: str, out_dir: str, norm: TexNormalizationConfig) -> DraftTrajectory:
    repo = Repo(repo_path)
    commit_hashes = collect_file_history(repo_path, file_path)
    state_dir = Path(out_dir) / Path(file_path).stem
    state_dir.mkdir(parents=True, exist_ok=True)
    states: List[DraftState] = []
    prev_text: str | None = None

    for idx, commit_hash in enumerate(commit_hashes):
        commit = repo.commit(commit_hash)
        raw_text = repo.git.show(f"{commit_hash}:{file_path}")
        text = normalize_tex(raw_text, norm) if file_path.endswith(".tex") else raw_text
        state_path = state_dir / f"{idx:04d}_{Path(file_path).name}"
        write_text(state_path, text)
        summary = None if prev_text is None else diff_summary(prev_text, text)
        stats = structural_stats(text) if file_path.endswith(".tex") else {}
        states.append(
            DraftState(
                step=idx,
                content_path=str(state_path),
                content_hash=hash_text(text),
                timestamp=commit.committed_datetime.isoformat(),
                author=getattr(commit.author, "name", None),
                diff_from_prev=summary,
                metadata={"commit": commit_hash, "source_file": file_path, **stats},
            )
        )
        prev_text = text

    return DraftTrajectory(
        trajectory_id=Path(file_path).stem,
        modality="latex" if file_path.endswith(".tex") else "text",
        source="git",
        states=states,
        metadata={"repo_path": repo_path, "file_path": file_path},
    )
