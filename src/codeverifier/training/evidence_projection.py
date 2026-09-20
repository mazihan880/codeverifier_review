from dataclasses import dataclass
from typing import Iterable

from codeverifier.schema import Region, StructuredPrediction, normalize_regions


@dataclass(frozen=True)
class TeacherCandidate:
    rationale: str
    regions: tuple[Region, ...]
    verdict: str


def interval_iou(first: Region, second: Region) -> float:
    intersection = max(0, min(first.end, second.end) - max(first.start, second.start) + 1)
    union = max(first.end, second.end) - min(first.start, second.start) + 1
    return intersection / union


def select_regions(candidates: Iterable[TeacherCandidate], repair_regions: Iterable[Region], threshold: float) -> tuple[Region, ...]:
    references = tuple(repair_regions)
    selected: list[Region] = []
    for candidate in candidates:
        for region in candidate.regions:
            if any(interval_iou(region, reference) >= threshold for reference in references):
                selected.append(region)
    return normalize_regions(dict.fromkeys(selected))


def project_target(
    execution_verdict: str,
    repair_regions: Iterable[Region],
    candidates: Iterable[TeacherCandidate],
    threshold: float,
) -> StructuredPrediction:
    candidates = tuple(candidates)
    if not candidates:
        raise ValueError("evidence projection requires at least one teacher candidate")
    regions = select_regions(candidates, repair_regions, threshold)
    rationale = max(candidates, key=lambda candidate: len(candidate.rationale)).rationale
    return StructuredPrediction(rationale, regions, execution_verdict.upper())
