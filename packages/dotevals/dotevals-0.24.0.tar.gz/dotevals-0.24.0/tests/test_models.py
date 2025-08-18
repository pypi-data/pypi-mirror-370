import time

from dotevals.metrics import accuracy
from dotevals.models import (
    Evaluation,
    EvaluationStatus,
    EvaluationSummary,
    Record,
    Result,
    Score,
)


def test_summary_empty_results():
    results = []
    summary = EvaluationSummary(results)
    assert isinstance(summary.summary, dict)
    assert len(summary.summary) == 0


def test_summary_simple():
    result1 = Result(Score("match", True, [accuracy()]), prompt="test1")
    result2 = Result(Score("match", True, [accuracy()]), prompt="test2")
    results = [
        Record(result1, 1),
        Record(result2, 2),
    ]
    summary = EvaluationSummary(results)
    assert isinstance(summary.summary, dict)
    assert summary.summary == {"match": {"accuracy": 1.0}}


def test_summary_two_scores_result():
    result1 = Result(
        Score("match_1", True, [accuracy()]),
        Score("match_2", False, [accuracy()]),
        prompt="test1",
    )
    result2 = Result(
        Score("match_1", True, [accuracy()]),
        Score("match_2", False, [accuracy()]),
        prompt="test2",
    )
    results = [
        Record(result1, 1),
        Record(result2, 2),
    ]
    summary = EvaluationSummary(results)
    assert isinstance(summary.summary, dict)
    assert summary.summary == {
        "match_1": {"accuracy": 1.0},
        "match_2": {"accuracy": 0.0},
    }


def test_evaluation_dataclass():
    """Test Evaluation dataclass."""
    eval = Evaluation(
        evaluation_name="test",
        status=EvaluationStatus.RUNNING,
        started_at=time.time(),
        metadata={"model": "gpt-4"},
    )
    assert eval.evaluation_name == "test"
    assert eval.status == EvaluationStatus.RUNNING
    assert eval.metadata == {"model": "gpt-4"}
    assert eval.completed_at is None


def test_result_with_error():
    """Test Result with error."""
    result = Result(Score("test", 0.5, []), error="Failed")
    assert result.error == "Failed"
    assert len(result.scores) == 1


def test_record_with_dataset_row():
    """Test Record with dataset row."""
    record = Record(
        Result(Score("test", 1.0, [])), item_id=0, dataset_row={"input": "test"}
    )
    assert record.dataset_row == {"input": "test"}
    assert record.item_id == 0
