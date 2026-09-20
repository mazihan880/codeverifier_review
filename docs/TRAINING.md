# Training

The training recipe has two stages. Stage I turns execution and repair evidence into supervised targets. Stage II starts from that checkpoint, samples several responses for each prompt, and applies RVPG with separate verdict and line-region feedback.

```text
raw task + execution result + repair intervals + teacher candidates
                              │
                              ▼
                     evidence projection
                              │
                              ▼
                         Swift SFT
                              │
                              ▼
                    evidence-projected checkpoint
                              │
                ┌─────────────┴─────────────┐
                │                           │
          response groups              field masks
                │                           │
                └─────────────┬─────────────┘
                              ▼
                         RVPG update
                              │
                              ▼
                       online checkpoint
```

## 1. Prepare the data

Use the training split only. Do not reuse evaluation records or reward logs as model inputs. For each supervised item, provide:

- the rendered verification prompt;
- the execution verdict;
- inclusive, one-indexed repair-line intervals;
- teacher candidates containing a rationale, candidate regions, and a verdict.

`project_target` in [evidence_projection.py](../src/codeverifier/training/evidence_projection.py) projects these fields into a `StructuredPrediction`. The execution verdict is the target verdict; candidate regions are retained only when their interval IoU with a repair interval reaches the configured threshold.

The online split uses the original prompt and the supervision fields `verdict_gt` and `actual_changed_line_ranges`. Two rows are provided in [examples/training](../examples/training). The complete corpus is supplied separately through `data.train`.

## 2. Stage I: supervised fine-tuning

Start from the chosen base model. Fill one of `configs/sft/2b.yaml`, `4b.yaml`, or `9b.yaml` with the model size, optimizer settings, schedule, and local training paths. The templates intentionally contain empty values in this release.

Inspect the generated Swift command:

```bash
python scripts/launch_sft.py \
  --config configs/sft/9b.yaml \
  --model "<base-model-path>" \
  --output "<sft-output-directory>" \
  --dry-run
```

When the printed command is complete, remove `--dry-run`:

```bash
python scripts/launch_sft.py \
  --config configs/sft/9b.yaml \
  --model "<base-model-path>" \
  --output "<sft-output-directory>"
```

`launch_sft.py` delegates to `swift sft`. The resulting directory is the input checkpoint for Stage II. The SFT target format and the online-record format are different; do not pass `train_online*.jsonl` directly as an SFT assistant-target dataset.

## 3. Stage II: online RVPG

Start from the Stage I checkpoint. For each prompt, the online trainer:

1. samples a response group;
2. scores the verdict and the evidence-line regions against the training supervision;
3. computes group-normalized verdict advantages and region advantages;
4. routes each advantage to the output field that produced it;
5. applies asymmetric clipping and the KL term; and
6. saves checkpoints and resumes from the last complete checkpoint when requested.

The loss and routing implementation are in [rvpg.py](../src/codeverifier/training/rvpg.py). Fill `configs/online/2b.yaml`, `4b.yaml`, or `9b.yaml` with the paper-aligned values and paths before launching.

Inspect the exact Swift command first:

```bash
python scripts/launch_online.py \
  --config configs/online/9b.yaml \
  --model "<sft-checkpoint>" \
  --dataset "<online-training-jsonl>" \
  --adapter "<rvpg-swift-adapter>" \
  --output "<online-output-directory>" \
  --dry-run
```

After checking the printed command, remove `--dry-run` to launch:

```bash
python scripts/launch_online.py \
  --config configs/online/9b.yaml \
  --model "<sft-checkpoint>" \
  --dataset "<online-training-jsonl>" \
  --adapter "<rvpg-swift-adapter>" \
  --output "<online-output-directory>"
```

The adapter is responsible for connecting Swift rollout outputs to the CodeVerifier verdict/region scorer and for constructing `verdict_mask` and `region_masks`. This repository contains the framework-independent objective and does not claim that the adapter is bundled. In a cluster launch, place the printed command in the scheduler script, expose the model and dataset paths as variables, and keep rollout and training checkpoints under the same run directory.

## 4. Resume and check a run

Keep the SFT checkpoint, online output directory, configuration file, and dataset manifest together. A resumed run must point to a complete checkpoint and the same dataset contract. Before submission, inspect the command with `--dry-run`, then run:

```bash
python scripts/validate_release.py
python -m compileall -q src scripts tests
```

These commands check the release package only; they do not start training.
