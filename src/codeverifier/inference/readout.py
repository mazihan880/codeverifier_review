from collections.abc import Mapping


def read_verdict(prediction: Mapping) -> str:
    value = str(prediction["verdict"]).upper().strip()
    if not value:
        raise ValueError("verdict must be nonempty")
    return value


def label_score(logits: Mapping[str, float], positive_label: str) -> float:
    if positive_label not in logits:
        raise ValueError("positive label is absent from logits")
    maximum = max(logits.values())
    denominator = sum(pow(2.718281828459045, value - maximum) for value in logits.values())
    return pow(2.718281828459045, logits[positive_label] - maximum) / denominator
