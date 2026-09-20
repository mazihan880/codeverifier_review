from dataclasses import dataclass

import torch


@dataclass(frozen=True)
class RVPGConfig:
    epsilon_lower: float
    epsilon_upper: float
    beta: float
    alpha_verdict: float
    alpha_region: float


def token_advantages(
    global_utilities: torch.Tensor,
    region_utilities: torch.Tensor,
    verdict_mask: torch.Tensor,
    region_masks: torch.Tensor,
    region_reference: torch.Tensor,
    config: RVPGConfig,
) -> torch.Tensor:
    if global_utilities.ndim != 2:
        raise ValueError("global_utilities must have shape [groups, responses]")
    group_mean = global_utilities.mean(dim=1, keepdim=True)
    global_advantage = config.alpha_verdict * (global_utilities - group_mean)
    local_advantage = config.alpha_region * (region_utilities - region_reference)
    batch, sequence = verdict_mask.shape
    result = torch.zeros((batch, sequence), dtype=global_utilities.dtype, device=global_utilities.device)
    result = result + verdict_mask.to(result.dtype) * global_advantage.reshape(-1, 1)
    result = result + (region_masks.to(result.dtype) * local_advantage.reshape(batch, -1, 1)).sum(dim=1)
    return result


def rvpg_loss(
    log_probabilities: torch.Tensor,
    old_log_probabilities: torch.Tensor,
    reference_log_probabilities: torch.Tensor,
    advantages: torch.Tensor,
    attention_mask: torch.Tensor,
    config: RVPGConfig,
) -> torch.Tensor:
    valid = attention_mask.to(log_probabilities.dtype)
    lengths = valid.sum(dim=-1).clamp_min(1.0)
    response_ratio = torch.exp(((log_probabilities - old_log_probabilities) * valid).sum(dim=-1) / lengths)
    detached_ratio = response_ratio.detach().unsqueeze(-1) * torch.exp(log_probabilities - log_probabilities.detach())
    unclipped = detached_ratio * advantages
    clipped = detached_ratio.clamp(1.0 - config.epsilon_lower, 1.0 + config.epsilon_upper) * advantages
    policy = -torch.minimum(unclipped, clipped)
    difference = reference_log_probabilities - log_probabilities
    kl = torch.exp(difference) - difference - 1.0
    return ((policy + config.beta * kl) * valid).sum(dim=-1).div(lengths).mean()
