from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class Region:
    start: int
    end: int

    def __post_init__(self):
        if self.start < 1 or self.end < self.start:
            raise ValueError("regions use one-indexed inclusive line intervals")

    def to_dict(self) -> dict[str, int]:
        return {"start": self.start, "end": self.end}


@dataclass(frozen=True)
class StructuredPrediction:
    rationale: str
    regions: tuple[Region, ...]
    verdict: str

    @classmethod
    def from_dict(cls, value: dict) -> "StructuredPrediction":
        regions = tuple(Region(int(item["start"]), int(item["end"])) for item in value.get("regions", []))
        return cls(str(value.get("rationale", "")), regions, str(value["verdict"]).upper())

    def to_dict(self) -> dict:
        return {
            "rationale": self.rationale,
            "regions": [region.to_dict() for region in self.regions],
            "verdict": self.verdict,
        }


def normalize_regions(regions: Iterable[Region]) -> tuple[Region, ...]:
    return tuple(sorted(regions, key=lambda region: (region.start, region.end)))
