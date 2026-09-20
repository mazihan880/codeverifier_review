# Data format

## Online training

The [training samples](../examples/training/online_cv_samples.jsonl) retain three fields from the original CV training records:

| Field | Content |
| --- | --- |
| `messages` | The verification prompt, including the task and numbered code |
| `verdict_gt` | The training verdict |
| `actual_changed_line_ranges` | Repair-line intervals, with inclusive, one-indexed endpoints |

Competition verdicts are `AC`, `WA`, `TLE`, and `CE`. Repository verdicts are `PASS` and `FAIL`. The included records contain online supervision, not assistant responses for SFT.

## Supervised fine-tuning

The SFT launcher passes `data.train` to Swift's `--dataset` argument. Supply chat records with a user prompt and an assistant target:

```json
{
  "messages": [
    {"role": "user", "content": "<verification prompt>"},
    {"role": "assistant", "content": "<structured target>"}
  ]
}
```

The recorded prompt uses the output fields `verdict`, `reason`, and `evidence`. Each evidence entry uses `start_line`, `end_line`, and `comment`.

## Python representation

The local `StructuredPrediction` class uses `rationale`, `regions`, and `verdict`; each `Region` has `start` and `end`. This is an internal representation, separate from the recorded prompt format.
