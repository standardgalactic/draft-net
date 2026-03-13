from __future__ import annotations

import argparse
import json
from pathlib import Path

import torch

from draftnet.cli.common import build_parser, resolve_config
from draftnet.data.manifest import load_manifest
from draftnet.data.text_loader import TextBridgeDataset
from draftnet.models.bridge import BridgeMLP
from draftnet.models.planner import replay_bridge


def main() -> None:
    parser = build_parser("Replay a learned trajectory bridge")
    parser.add_argument("--checkpoint", required=True)
    parser.add_argument("--trajectory", required=True)
    parser.add_argument("--steps", type=int, default=8)
    args = parser.parse_args()
    config = resolve_config(args.config)

    trajectories = [t for t in load_manifest(config["manifest_path"]) if t.trajectory_id == args.trajectory]
    if not trajectories:
        raise SystemExit(f"trajectory not found: {args.trajectory}")
    dataset = TextBridgeDataset(trajectories, embedding_dim=config["encoder"]["embedding_dim"], curriculum_level=1)
    first = dataset[0]

    model = BridgeMLP(dim=config["encoder"]["embedding_dim"], hidden_dim=config["model"]["hidden_dim"], dropout=config["model"].get("dropout", 0.1))
    checkpoint = torch.load(args.checkpoint, map_location="cpu")
    model.load_state_dict(checkpoint["model_state"])
    model.eval()

    z0 = first["z0"].unsqueeze(0)
    zT = first["zT"].unsqueeze(0)
    latents = replay_bridge(model, z0, zT, steps=args.steps)
    serializable = [latent.squeeze(0).tolist() for latent in latents]
    print(json.dumps({"trajectory": args.trajectory, "predicted_latents": serializable}, indent=2))


if __name__ == "__main__":
    main()
