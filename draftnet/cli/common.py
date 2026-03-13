from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any, Dict

from draftnet.utils.io import load_yaml


def build_parser(description: str) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--config", required=True, help="Path to YAML configuration file")
    return parser


def resolve_config(path: str) -> Dict[str, Any]:
    cfg = load_yaml(path)
    base = cfg.get("base_config")
    if base:
        base_cfg = load_yaml(base)
        merged = base_cfg.copy()
        for key, value in cfg.items():
            if isinstance(value, dict) and isinstance(merged.get(key), dict):
                merged[key] = {**merged[key], **value}
            else:
                merged[key] = value
        return merged
    return cfg


def ensure_dir(path: str | Path) -> Path:
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p
