import time
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional, TypeAlias, Union

from dotevals.metrics import Metric

# Type aliases for score values and data structures
Primitive: TypeAlias = bool | int | float | str | None
JSONValue: TypeAlias = Primitive | dict[str, "JSONValue"] | list["JSONValue"]
ScoreValue: TypeAlias = (
    bool | int | float | str | dict[str, Primitive] | list[Primitive]
)
DatasetRow: TypeAlias = dict[str, JSONValue]
Metadata: TypeAlias = dict[str, Primitive]


class EvaluationStatus(Enum):
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Evaluation:
    evaluation_name: str
    status: EvaluationStatus
    started_at: float
    metadata: dict[str, str] = field(default_factory=dict)
    completed_at: float | None = None


@dataclass
class Result:
    prompt: str | None
    scores: list["Score"]
    error: str | None = None
    model_response: str | None = None

    def __init__(
        self,
        *scores: "Score",
        prompt: str | None = None,
        error: str | None = None,
        model_response: str | None = None,
    ) -> None:
        self.prompt = prompt
        self.scores = list(scores)
        self.error = error
        self.model_response = model_response


@dataclass
class Score:
    name: str
    value: ScoreValue
    metrics: list[Metric]
    metadata: Metadata = field(default_factory=dict)


@dataclass
class Record:
    """Record of evaluating a single dataset item"""

    result: Result
    item_id: int
    dataset_row: DatasetRow = field(default_factory=dict)
    error: str | None = None
    timestamp: float = field(default_factory=time.time)


class EvaluationSummary:
    """Aggregated results of a full evaluation"""

    def __init__(self, results: list[Record]) -> None:
        self.results = results
        self.summary = self.compute_summary()

    def compute_summary(self) -> dict[str, dict[str, float | int]]:
        summary: dict[str, dict[str, float | int]] = defaultdict(dict)

        # First pass: determine the expected score structure from successful results
        expected_scores: list[tuple[str, list[Metric]]] = []
        for result in self.results:
            if result.error is None and result.result.scores:
                expected_scores = [
                    (score.name, score.metrics) for score in result.result.scores
                ]
                break

        # Regorganize the results by evaluator and metric
        aggregated_results: dict[str, dict[Metric, list[ScoreValue]]] = defaultdict(
            lambda: defaultdict(list)
        )
        for result in self.results:
            if result.error is not None:
                # For error cases, add False values for each expected score
                for score_name, metrics in expected_scores:
                    for metric in metrics:
                        aggregated_results[score_name][metric].append(False)
            else:
                # For successful cases, use actual scores
                for score in result.result.scores:
                    for metric in score.metrics:
                        aggregated_results[score.name][metric].append(score.value)

        for evaluator_name, metrics_values in aggregated_results.items():
            for metric_func, values in metrics_values.items():
                summary[evaluator_name][metric_func.__name__] = metric_func(values)  # type: ignore[arg-type]

        return summary
