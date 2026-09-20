import argparse
import subprocess
from pathlib import Path

import yaml


def load(path: str) -> dict:
    with Path(path).open() as handle:
        return yaml.safe_load(handle)


def command(config: dict, model: str, output: str) -> list[str]:
    values = {
        "--model": model,
        "--dataset": config.get("data", {}).get("train", ""),
        "--tuner_type": config.get("train_type", ""),
        "--torch_dtype": config.get("dtype", ""),
        "--num_train_epochs": config.get("epochs", ""),
        "--learning_rate": config.get("learning_rate", ""),
        "--weight_decay": config.get("weight_decay", ""),
        "--max_length": config.get("max_length", ""),
        "--warmup_ratio": config.get("warmup_ratio", ""),
        "--lr_scheduler_type": config.get("lr_scheduler", ""),
        "--seed": config.get("seed", ""),
        "--output_dir": output,
    }
    result = ["swift", "sft"]
    for key, value in values.items():
        if value != "":
            result.extend([key, str(value)])
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--dry-run", action="store_true")
    arguments = parser.parse_args()
    invocation = command(load(arguments.config), arguments.model, arguments.output)
    print(" ".join(invocation))
    if not arguments.dry_run:
        subprocess.run(invocation, check=True)


if __name__ == "__main__":
    main()
