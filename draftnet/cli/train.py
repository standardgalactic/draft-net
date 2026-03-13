from __future__ import annotations

import argparse
from pathlib import Path

import torch
from torch.utils.data import DataLoader

from draftnet.cli.common import build_parser, ensure_dir, resolve_config
from draftnet.data.collate import collate_bridge_batch
from draftnet.data.manifest import load_manifest
from draftnet.data.text_loader import TextBridgeDataset
from draftnet.losses.bridge_loss import bridge_loss
from draftnet.models.bridge import BridgeMLP


def main() -> None:
    parser = build_parser("Train a Draft-Net bridge model")
    parser.add_argument("--checkpoint-out", default=None)
    args = parser.parse_args()
    config = resolve_config(args.config)

    manifest = load_manifest(config["manifest_path"])
    embed_dim = config["encoder"]["embedding_dim"]
    curriculum_level = config["training"]["curriculum_level"]
    batch_size = config["training"]["batch_size"]
    epochs = config["training"]["epochs"]
    lr = config["training"]["learning_rate"]
    device = torch.device(config["training"].get("device", "cpu"))

    dataset = TextBridgeDataset(manifest, embedding_dim=embed_dim, curriculum_level=curriculum_level)
    loader = DataLoader(dataset, batch_size=batch_size, shuffle=True, collate_fn=collate_bridge_batch)
    model = BridgeMLP(dim=embed_dim, hidden_dim=config["model"]["hidden_dim"], dropout=config["model"].get("dropout", 0.1)).to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr)

    model.train()
    for epoch in range(epochs):
        running = 0.0
        batches = 0
        for batch in loader:
            z0 = batch["z0"].to(device)
            zT = batch["zT"].to(device)
            zt = batch["zt"].to(device)
            t = batch["t"].to(device)
            pred = model(z0, zT, t)
            loss = bridge_loss(pred, zt)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            running += float(loss.item())
            batches += 1
        avg = running / max(batches, 1)
        print(f"epoch={epoch + 1} loss={avg:.6f}")

    checkpoint = args.checkpoint_out or str(ensure_dir(config.get("experiment_dir", "experiments")) / "bridge.pt")
    torch.save({"model_state": model.state_dict(), "config": config}, checkpoint)
    print(f"saved checkpoint to {checkpoint}")


if __name__ == "__main__":
    main()
