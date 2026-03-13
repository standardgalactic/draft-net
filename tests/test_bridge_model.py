import torch

from draftnet.models.bridge import BridgeMLP


def test_bridge_output_shape():
    model = BridgeMLP(dim=8, hidden_dim=16)
    z0 = torch.zeros(2, 8)
    zT = torch.ones(2, 8)
    t = torch.tensor([0.5, 0.25])
    out = model(z0, zT, t)
    assert out.shape == (2, 8)
