import torch

from codeverifier.training.rvpg import RVPGConfig, rvpg_loss


def test_rvpg_loss_is_finite():
    values = torch.zeros((2, 4), requires_grad=True)
    loss = rvpg_loss(values, values.detach(), values.detach(), torch.ones((2, 4)), torch.ones((2, 4)), RVPGConfig(0.2, 0.2, 0.02, 1.0, 4.0))
    loss.backward()
    assert torch.isfinite(loss)
