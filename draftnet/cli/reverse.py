from __future__ import annotations

import argparse
import json

import torch

from draftnet.cli.common import build_parser, resolve_config
from draftnet.models.bridge import BridgeMLP


def main() -> None:
    parser = build_parser("Reverse-plan a trajectory in latent space")
    parser.add_argument("--checkpoint", required=True)
    parser.add_argument("--latent-json", required=False, help="JSON list representing a terminal latent state")
    parser.add_argument("--steps", type=int, default=8)
    args = parser.parse_args()
    config = resolve_config(args.config)

    model = BridgeMLP(dim=config["encoder"]["embedding_dim"], hidden_dim=config["model"]["hidden_dim"], dropout=config["model"].get("dropout", 0.1))
    checkpoint = torch.load(args.checkpoint, map_location="cpu")
    model.load_state_dict(checkpoint["model_state"])
    model.eval()

    if args.latent_json:
        zT = torch.tensor(json.loads(args.latent_json), dtype=torch.float32).unsqueeze(0)
    else:
        zT = torch.zeros(1, config["encoder"]["embedding_dim"], dtype=torch.float32)
    z0 = torch.zeros_like(zT)
    plan = []
    with torch.no_grad():
        for i in reversed(range(1, args.steps)):
            t = torch.tensor([[i / args.steps]], dtype=torch.float32)
            pred = model(z0, zT, t)
            plan.append(pred.squeeze(0).tolist())
    print(json.dumps({"reverse_plan": plan}, indent=2))


if __name__ == "__main__":
    main()
