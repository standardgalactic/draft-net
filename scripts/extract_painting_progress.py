#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from draftnet.data.manifest import save_manifest
from draftnet.extract.image_progress import build_image_trajectory


def main() -> None:
    parser = argparse.ArgumentParser(description='Build Draft-Net image trajectories from progress-shot folders')
    parser.add_argument('--input-dir', required=True, help='Directory containing per-painting subdirectories of ordered images')
    parser.add_argument('--output-manifest', required=True)
    args = parser.parse_args()

    root = Path(args.input_dir)
    trajectories = []
    for subdir in sorted(p for p in root.iterdir() if p.is_dir()):
        paths = [p for p in sorted(subdir.iterdir()) if p.suffix.lower() in {'.npy', '.npz', '.ppm', '.pgm'}]
        if len(paths) < 2:
            continue
        trajectories.append(build_image_trajectory(subdir.name, paths))
    save_manifest(args.output_manifest, trajectories)
    print(f'wrote {len(trajectories)} trajectories to {args.output_manifest}')


if __name__ == '__main__':
    main()
