from __future__ import annotations

import argparse

import torch

from draftnet.cli.common import build_parser, resolve_config
from draftnet.data.manifest import load_manifest
from draftnet.data.text_loader import TextBridgeDataset
from draftnet.eval.fidelity import path_fidelity
from draftnet.models.bridge import BridgeMLP


def main() -> None:
    parser = build_parser("Evaluate a Draft-Net bridge model")
    parser.add_argument("--checkpoint", required=True)
    args = parser.parse_args()
    config = resolve_config(args.config)

    trajectories = load_manifest(config["manifest_path"])
    dataset = TextBridgeDataset(
        trajectories,
        embedding_dim=config["encoder"]["embedding_dim"],
        curriculum_level=config["training"]["curriculum_level"],
    )
    model = BridgeMLP(
        dim=config["encoder"]["embedding_dim"],
        hidden_dim=config["model"]["hidden_dim"],
        dropout=config["model"].get("dropout", 0.1),
    )
    checkpoint = torch.load(args.checkpoint, map_location="cpu")
    model.load_state_dict(checkpoint["model_state"])
    model.eval()

    predicted = []
    target = []
    with torch.no_grad():
        for item in dataset:
            pred = model(item["z0"].unsqueeze(0), item["zT"].unsqueeze(0), item["t"])
            predicted.append(pred.squeeze(0).tolist())
            target.append(item["zt"].tolist())

    metrics = path_fidelity(predicted, target)
    for key, value in metrics.items():
        print(f"{key}={value:.6f}")


if __name__ == "__main__":
    main()
