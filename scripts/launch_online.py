import argparse
import subprocess
from pathlib import Path

import yaml


def load(path: str) -> dict:
    with Path(path).open() as handle:
        return yaml.safe_load(handle)


def command(config: dict, model: str, dataset: str, output: str, adapter: str) -> list[str]:
    values = {
        "--model": model,
        "--dataset": dataset,
        "--external_plugins": adapter,
        "--tuner_type": config.get("train_type", ""),
        "--torch_dtype": config.get("dtype", ""),
        "--learning_rate": config.get("learning_rate", ""),
        "--weight_decay": config.get("weight_decay", ""),
        "--max_steps": config.get("updates", ""),
        "--max_length": config.get("max_input_length", ""),
        "--max_completion_length": config.get("max_generation_length", ""),
        "--lr_scheduler_type": config.get("lr_scheduler", ""),
        "--warmup_ratio": config.get("warmup_ratio", ""),
        "--seed": config.get("seed", ""),
        "--num_generations": config.get("sampling", {}).get("responses_per_prompt", ""),
        "--temperature": config.get("sampling", {}).get("temperature", ""),
        "--output_dir": output,
    }
    result = ["swift", "rlhf", "--rlhf_type", "grpo"]
    for key, value in values.items():
        if value != "":
            result.extend([key, str(value)])
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--dataset", required=True)
    parser.add_argument("--adapter", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--dry-run", action="store_true")
    arguments = parser.parse_args()
    invocation = command(
        load(arguments.config),
        arguments.model,
        arguments.dataset,
        arguments.output,
        arguments.adapter,
    )
    print(" ".join(invocation))
    if not arguments.dry_run:
        subprocess.run(invocation, check=True)


if __name__ == "__main__":
    main()
