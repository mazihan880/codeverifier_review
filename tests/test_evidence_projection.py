from codeverifier.schema import Region
from codeverifier.training.evidence_projection import TeacherCandidate, project_target


def test_projection_uses_execution_verdict_and_supported_regions():
    target = project_target(
        "wa",
        [Region(10, 12)],
        [
            TeacherCandidate("brief", (Region(1, 2),), "AC"),
            TeacherCandidate("supported rationale", (Region(10, 12),), "AC"),
        ],
        0.8,
    )
    assert target.verdict == "WA"
    assert target.regions == (Region(10, 12),)
    assert target.rationale == "supported rationale"
