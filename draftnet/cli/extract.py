from __future__ import annotations

import argparse
from pathlib import Path

from git import Repo

from draftnet.cli.common import build_parser, resolve_config
from draftnet.data.manifest import save_manifest
from draftnet.extract.git import build_trajectory_from_git, iter_matching_files
from draftnet.extract.tex import TexNormalizationConfig


def main() -> None:
    parser = build_parser("Extract draft trajectories from Git histories")
    args = parser.parse_args()
    config = resolve_config(args.config)

    repo_path = config["repo_path"]
    repo = Repo(repo_path)
    file_globs = config.get("file_globs", ["*.tex"])
    output_dir = config.get("output_dir", "data/processed")
    manifest_path = config.get("manifest_path", "data/manifests/trajectories.jsonl")

    norm_cfg = TexNormalizationConfig(**config.get("normalization", {}))
    trajectories = []
    for file_path in iter_matching_files(repo, file_globs):
        trajectories.append(build_trajectory_from_git(repo_path, file_path, output_dir, norm_cfg))

    save_manifest(manifest_path, trajectories)
    print(f"Wrote {len(trajectories)} trajectories to {Path(manifest_path)}")


if __name__ == "__main__":
    main()
