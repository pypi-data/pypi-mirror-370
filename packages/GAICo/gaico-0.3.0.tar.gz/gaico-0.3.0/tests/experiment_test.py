from typing import Any, Dict, List
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from gaico.experiment import DEFAULT_METRICS_TO_RUN, REGISTERED_METRICS, Experiment
from gaico.metrics.base import BaseMetric  # For mocking


# Test Data and Fixtures
@pytest.fixture
def sample_llm_responses_single() -> Dict[str, str]:
    return {
        "ModelA": "This is a response from Model A.",
        "ModelB": "Model B provides this answer.",
        "ModelC": "Another response from Model C.",
    }


@pytest.fixture
def sample_reference_answer_single() -> str:
    return "This is the reference answer."


@pytest.fixture
def sample_llm_responses_batch() -> Dict[str, List[str]]:
    return {
        "ModelX": ["Response X1", "Response X2", "Response X3"],
        "ModelY": ["Response Y1", "Response Y2", "Response Y3"],
    }


@pytest.fixture
def sample_reference_answer_batch() -> List[str]:
    return ["Ref1", "Ref2", "Ref3"]


@pytest.fixture
def mock_metric_class_factory(monkeypatch):
    """
    Factory to create mock metric classes and instances.
    Adjusted to return lists of scores, as Experiment now always passes lists to calculate.
    """
    created_mocks = {}

    def _factory(metric_name, score_to_return=0.5, sub_scores=None, init_raises=None, num_items=1):
        mock_metric_instance = MagicMock(spec=BaseMetric)
        if sub_scores:
            # If sub_scores is a dict, assume it's for a single item, wrap in list for num_items
            if isinstance(sub_scores, dict):
                mock_metric_instance.calculate.return_value = [sub_scores] * num_items
            else:  # Assume it's already a list of dicts for batch
                mock_metric_instance.calculate.return_value = sub_scores
        else:
            # If score_to_return is a single float, wrap in list for num_items
            if isinstance(score_to_return, (int, float)):
                mock_metric_instance.calculate.return_value = [score_to_return] * num_items
            else:  # Assume it's already a list of floats for batch
                mock_metric_instance.calculate.return_value = score_to_return

        mock_metric_class = MagicMock(spec=type(BaseMetric))
        if init_raises:
            mock_metric_class.side_effect = init_raises  # To simulate ImportError on __init__
        else:
            mock_metric_class.return_value = mock_metric_instance

        # Store mock and original to ensure proper teardown
        original_metric = REGISTERED_METRICS.get(metric_name)
        monkeypatch.setitem(REGISTERED_METRICS, metric_name, mock_metric_class)
        if metric_name not in created_mocks:
            created_mocks[metric_name] = (mock_metric_class, original_metric)

        return mock_metric_class, mock_metric_instance

    yield _factory

    # Teardown: Restore original REGISTERED_METRICS if modified by monkeypatch
    for metric_name, (mock_class, original_metric) in created_mocks.items():
        if original_metric is not None:
            monkeypatch.setitem(REGISTERED_METRICS, metric_name, original_metric)
        elif metric_name in REGISTERED_METRICS and REGISTERED_METRICS[metric_name] == mock_class:
            monkeypatch.delitem(REGISTERED_METRICS, metric_name, raising=False)


# Experiment Initialization Tests
def test_experiment_init_single_success(
    sample_llm_responses_single, sample_reference_answer_single
):
    exp = Experiment(sample_llm_responses_single, sample_reference_answer_single)
    assert exp.is_batch is False
    assert exp.llm_responses == {k: [v] for k, v in sample_llm_responses_single.items()}
    assert exp.reference_answer == [sample_reference_answer_single]
    assert list(exp.models) == list(sample_llm_responses_single.keys())


def test_experiment_init_single_reference_answer_none_success(sample_llm_responses_single, capsys):
    first_model_name = list(sample_llm_responses_single.keys())[0]
    first_model_response = sample_llm_responses_single[first_model_name]

    exp = Experiment(sample_llm_responses_single, reference_answer=None)
    assert exp.is_batch is False
    assert exp.llm_responses == {k: [v] for k, v in sample_llm_responses_single.items()}
    assert exp.reference_answer == [first_model_response]

    captured = capsys.readouterr()
    assert "Warning: reference_answer was not provided for Experiment." in captured.out
    assert f"Using responses from model '{first_model_name}' as the reference." in captured.out


def test_experiment_init_batch_success(sample_llm_responses_batch, sample_reference_answer_batch):
    exp = Experiment(sample_llm_responses_batch, sample_reference_answer_batch)
    assert exp.is_batch is True
    assert exp.llm_responses == sample_llm_responses_batch
    assert exp.reference_answer == sample_reference_answer_batch
    assert list(exp.models) == list(sample_llm_responses_batch.keys())


def test_experiment_init_batch_ref_none(sample_llm_responses_batch, capsys):
    first_model_name = list(sample_llm_responses_batch.keys())[0]
    first_model_responses = sample_llm_responses_batch[first_model_name]

    exp = Experiment(sample_llm_responses_batch, reference_answer=None)
    assert exp.is_batch is True
    assert exp.llm_responses == sample_llm_responses_batch
    assert exp.reference_answer == first_model_responses

    captured = capsys.readouterr()
    assert "Warning: reference_answer was not provided for Experiment." in captured.out
    assert f"Using responses from model '{first_model_name}' as the reference." in captured.out


def test_experiment_init_batch_single_ref_broadcast(sample_llm_responses_batch):
    single_ref = "A single reference for all batch items."
    expected_ref_list = [single_ref] * len(list(sample_llm_responses_batch.values())[0])

    exp = Experiment(sample_llm_responses_batch, single_ref)
    assert exp.is_batch is True
    assert exp.llm_responses == sample_llm_responses_batch
    assert exp.reference_answer == expected_ref_list


def test_experiment_init_reference_answer_none_empty_llm_responses():
    with pytest.raises(ValueError, match="llm_responses cannot be empty."):
        Experiment({}, reference_answer=None)


def test_experiment_init_invalid_llm_responses_type():
    with pytest.raises(TypeError, match="llm_responses must be a dictionary."):
        Experiment(["not", "a", "dict"], "ref")


def test_experiment_init_invalid_llm_responses_content():
    with pytest.raises(ValueError, match="llm_responses keys must be strings"):
        Experiment({1: "val"}, "ref")


def test_experiment_init_inconsistent_batch_lengths(sample_llm_responses_batch):
    inconsistent_responses = sample_llm_responses_batch.copy()
    inconsistent_responses["ModelZ"] = ["Short", "List"]  # Length 2, others are 3
    with pytest.raises(ValueError, match="All model response lists must have the same length."):
        Experiment(inconsistent_responses, ["Ref1", "Ref2", "Ref3"])


def test_experiment_init_mixed_single_batch_inputs(sample_llm_responses_single):
    mixed_responses = sample_llm_responses_single.copy()
    mixed_responses["ModelD"] = ["List", "Response"]  # Mixed with single strings
    with pytest.raises(ValueError, match="Inconsistent input types."):
        Experiment(mixed_responses, "ref")


def test_experiment_init_ref_length_mismatch_with_batch(sample_llm_responses_batch):
    short_ref = ["Ref1", "Ref2"]
    with pytest.raises(ValueError, match="The reference_answer list must have the same length"):
        Experiment(sample_llm_responses_batch, short_ref)


def test_experiment_init_list_ref_for_single_item_exp(sample_llm_responses_single):
    list_ref = ["Ref1", "Ref2"]
    with pytest.raises(
        ValueError, match="A list-like reference_answer was provided for a single-item experiment."
    ):
        Experiment(sample_llm_responses_single, list_ref)


# to_dataframe() Tests
@pytest.mark.parametrize("is_batch_test", [False, True])
def test_to_dataframe_single_metric(
    sample_llm_responses_single,
    sample_reference_answer_single,
    sample_llm_responses_batch,
    sample_reference_answer_batch,
    mock_metric_class_factory,
    is_batch_test,
):
    if is_batch_test:
        llm_responses = sample_llm_responses_batch
        reference_answer = sample_reference_answer_batch
        num_items = len(reference_answer)
    else:
        llm_responses = sample_llm_responses_single
        reference_answer = sample_reference_answer_single
        num_items = 1

    mock_jaccard_class, mock_jaccard_instance = mock_metric_class_factory(
        "Jaccard", score_to_return=0.7, num_items=num_items
    )

    exp = Experiment(llm_responses, reference_answer)
    df = exp.to_dataframe(metrics=["Jaccard"])

    assert isinstance(df, pd.DataFrame)
    assert len(df) == len(llm_responses) * num_items
    assert "Jaccard" in df["metric_name"].unique()
    assert "model_name" in df.columns
    assert "score" in df.columns
    if is_batch_test:
        assert "item_index" in df.columns

    # Check calculate was called with correct args for one model
    # The calculate method of the mock metric should receive lists
    for model_name, gen_list in exp.llm_responses.items():
        mock_jaccard_instance.calculate.assert_any_call(gen_list, exp.reference_answer)

    assert all(df["score"] == 0.7)


@pytest.mark.parametrize("is_batch_test", [False, True])
def test_to_dataframe_multiple_metrics(
    sample_llm_responses_single,
    sample_reference_answer_single,
    sample_llm_responses_batch,
    sample_reference_answer_batch,
    mock_metric_class_factory,
    is_batch_test,
):
    if is_batch_test:
        llm_responses = sample_llm_responses_batch
        reference_answer = sample_reference_answer_batch
        num_items = len(reference_answer)
        rouge_sub_scores = [{"rouge1": 0.6, "rougeL": 0.5}] * num_items
    else:
        llm_responses = sample_llm_responses_single
        reference_answer = sample_reference_answer_single
        num_items = 1
        # The mock factory will wrap this in a list for the calculate call
        rouge_sub_scores = {"rouge1": 0.6, "rougeL": 0.5}

    mock_j_class, mock_j_inst = mock_metric_class_factory(
        "Jaccard", score_to_return=0.7, num_items=num_items
    )
    mock_r_class, mock_r_inst = mock_metric_class_factory(
        "ROUGE", sub_scores=rouge_sub_scores, num_items=num_items
    )

    exp = Experiment(llm_responses, reference_answer)
    df = exp.to_dataframe(metrics=["Jaccard", "ROUGE"])

    # For each item, Jaccard produces 1 row, ROUGE produces 2 (rouge1, rougeL). Total 3 rows per item.
    assert len(df) == len(llm_responses) * num_items * 3
    assert "Jaccard" in df["metric_name"].values
    assert "ROUGE_rouge1" in df["metric_name"].values
    assert "ROUGE_rougeL" in df["metric_name"].values
    if is_batch_test:
        assert "item_index" in df.columns

    for model_name, gen_list in exp.llm_responses.items():
        mock_j_inst.calculate.assert_any_call(gen_list, exp.reference_answer)
        mock_r_inst.calculate.assert_any_call(gen_list, exp.reference_answer)


def test_to_dataframe_default_metrics(
    sample_llm_responses_single,
    sample_reference_answer_single,
    mock_metric_class_factory,
    monkeypatch,
):
    mock_j_class, _ = mock_metric_class_factory("Jaccard", 0.1, num_items=1)
    mock_l_class, _ = mock_metric_class_factory("Levenshtein", 0.2, num_items=1)

    original_defaults = list(DEFAULT_METRICS_TO_RUN)
    # Patch the default list to only use our mocked metrics
    monkeypatch.setattr("gaico.experiment.DEFAULT_METRICS_TO_RUN", ["Jaccard", "Levenshtein"])

    exp = Experiment(sample_llm_responses_single, sample_reference_answer_single)
    df = exp.to_dataframe()  # metrics=None should use the patched defaults

    assert len(df) == len(sample_llm_responses_single) * 2  # 3 models * 2 metrics
    assert "Jaccard" in df["metric_name"].values
    assert "Levenshtein" in df["metric_name"].values

    # Restore original defaults
    monkeypatch.setattr("gaico.experiment.DEFAULT_METRICS_TO_RUN", original_defaults)


def test_to_dataframe_metric_init_fails(
    sample_llm_responses_single, sample_reference_answer_single, mock_metric_class_factory, capsys
):
    mock_j_class, mock_j_inst = mock_metric_class_factory(
        "Jaccard", score_to_return=0.7, num_items=1
    )
    # This metric will fail on instantiation
    mock_b_class, _ = mock_metric_class_factory(
        "BERTScore", init_raises=ImportError("torch not found"), num_items=1
    )

    exp = Experiment(sample_llm_responses_single, sample_reference_answer_single)
    df = exp.to_dataframe(metrics=["Jaccard", "BERTScore"])

    captured = capsys.readouterr()
    assert (
        "Warning: Metric 'BERTScore' will be skipped due to missing dependencies: torch not found"
        in captured.out
    )
    assert "Jaccard" in df["metric_name"].values
    assert "BERTScore" not in df["metric_name"].values  # Should be excluded
    assert len(df) == len(sample_llm_responses_single)  # Only Jaccard results should be present
    # Jaccard should still be calculated for all models
    assert mock_j_inst.calculate.call_count == len(sample_llm_responses_single)


# compare() Method Tests
@patch("gaico.experiment.plot_metric_comparison")
@patch("gaico.experiment.plot_radar_comparison")
@pytest.mark.parametrize("is_batch_test", [False, True])
def test_compare_basic_run_no_plot_no_csv(
    mock_plot_radar,
    mock_plot_metric,
    sample_llm_responses_single,
    sample_reference_answer_single,
    sample_llm_responses_batch,
    sample_reference_answer_batch,
    mock_metric_class_factory,
    is_batch_test,
):
    if is_batch_test:
        llm_responses = sample_llm_responses_batch
        reference_answer = sample_reference_answer_batch
        num_items = len(reference_answer)
    else:
        llm_responses = sample_llm_responses_single
        reference_answer = sample_reference_answer_single
        num_items = 1

    mock_j_class, mock_j_inst = mock_metric_class_factory("Jaccard", 0.7, num_items=num_items)

    exp = Experiment(llm_responses, reference_answer)
    results_df = exp.compare(metrics=["Jaccard"], plot=False, output_csv_path=None)

    assert isinstance(results_df, pd.DataFrame)
    assert "Jaccard" in results_df["metric_name"].values
    assert len(results_df) == len(llm_responses) * num_items

    for model_name, gen_list in exp.llm_responses.items():
        mock_j_inst.calculate.assert_any_call(gen_list, exp.reference_answer)

    mock_plot_metric.assert_not_called()
    mock_plot_radar.assert_not_called()


@patch("gaico.experiment.viz_plt")
@patch("gaico.experiment.plot_metric_comparison")
@patch("gaico.experiment.plot_radar_comparison")
def test_compare_with_single_metric_plot(
    mock_plot_radar,
    mock_plot_metric,
    mock_viz_plt,
    sample_llm_responses_single,
    sample_reference_answer_single,
    mock_metric_class_factory,
):
    mock_j_class, _ = mock_metric_class_factory("Jaccard", 0.7, num_items=1)
    mock_viz_plt.show = MagicMock()

    exp = Experiment(sample_llm_responses_single, sample_reference_answer_single)
    exp.compare(metrics=["Jaccard"], plot=True)

    mock_plot_metric.assert_called_once()
    call_args = mock_plot_metric.call_args[0]
    df_arg = call_args[0]
    assert isinstance(df_arg, pd.DataFrame)
    assert "Jaccard" in df_arg["metric_name"].values
    kwargs_arg = mock_plot_metric.call_args[1]
    assert kwargs_arg["metric_name"] == "Jaccard"

    mock_plot_radar.assert_not_called()
    mock_viz_plt.show.assert_called_once()


@patch("gaico.experiment.viz_plt")
@patch("gaico.experiment.plot_metric_comparison")
@patch("gaico.experiment.plot_radar_comparison")
def test_compare_with_multiple_metrics_radar_plot(
    mock_plot_radar,
    mock_plot_metric,
    mock_viz_plt,
    sample_llm_responses_single,
    sample_reference_answer_single,
    mock_metric_class_factory,
):
    mock_j_class, _ = mock_metric_class_factory("Jaccard", 0.7, num_items=1)
    mock_l_class, _ = mock_metric_class_factory("Levenshtein", 0.6, num_items=1)
    mock_s_class, _ = mock_metric_class_factory(
        "SequenceMatcher", 0.5, num_items=1
    )  # Need 3+ for radar
    mock_viz_plt.show = MagicMock()

    exp = Experiment(sample_llm_responses_single, sample_reference_answer_single)
    exp.compare(metrics=["Jaccard", "Levenshtein", "SequenceMatcher"], plot=True)

    mock_plot_radar.assert_called_once()
    call_args_df = mock_plot_radar.call_args[0][0]
    assert isinstance(call_args_df, pd.DataFrame)
    assert "Jaccard" in call_args_df["metric_name"].values
    assert "Levenshtein" in call_args_df["metric_name"].values
    assert "SequenceMatcher" in call_args_df["metric_name"].values
    call_args_kwargs = mock_plot_radar.call_args[1]
    assert sorted(call_args_kwargs["metrics"]) == sorted(
        ["Jaccard", "Levenshtein", "SequenceMatcher"]
    )

    mock_plot_metric.assert_not_called()  # Should go to radar
    mock_viz_plt.show.assert_called_once()


@patch("gaico.experiment.viz_plt")
@patch("gaico.experiment.plot_metric_comparison")
@patch("gaico.experiment.plot_radar_comparison")
def test_compare_with_two_metrics_bar_plots(  # Test the case where radar is skipped for <3 metrics
    mock_plot_radar,
    mock_plot_metric,
    mock_viz_plt,
    sample_llm_responses_single,
    sample_reference_answer_single,
    mock_metric_class_factory,
    capsys,
):
    mock_j_class, _ = mock_metric_class_factory("Jaccard", 0.7, num_items=1)
    mock_l_class, _ = mock_metric_class_factory("Levenshtein", 0.6, num_items=1)
    mock_viz_plt.show = MagicMock()

    exp = Experiment(sample_llm_responses_single, sample_reference_answer_single)
    exp.compare(metrics=["Jaccard", "Levenshtein"], plot=True)

    captured = capsys.readouterr()
    assert "Generating bar plots instead of radar" in captured.out
    assert mock_plot_metric.call_count == 2  # One bar plot per metric
    mock_plot_radar.assert_not_called()
    assert mock_viz_plt.show.call_count == 2


@patch("gaico.experiment.viz_plt", None)  # Matplotlib not available
def test_compare_plot_true_but_matplotlib_unavailable(
    sample_llm_responses_single,
    sample_reference_answer_single,
    mock_metric_class_factory,
    capsys,
):
    mock_j_class, _ = mock_metric_class_factory("Jaccard", 0.7, num_items=1)
    exp = Experiment(sample_llm_responses_single, sample_reference_answer_single)
    exp.compare(metrics=["Jaccard"], plot=True)

    captured = capsys.readouterr()
    assert "Warning: Matplotlib/Seaborn are not installed. Skipping plotting." in captured.out


@pytest.mark.parametrize("is_batch_test", [False, True])
def test_compare_with_csv_output(
    sample_llm_responses_single,
    sample_reference_answer_single,
    sample_llm_responses_batch,
    sample_reference_answer_batch,
    mock_metric_class_factory,
    tmp_path,
    is_batch_test,
):
    if is_batch_test:
        llm_responses = sample_llm_responses_batch
        reference_answer = sample_reference_answer_batch
        num_items = len(reference_answer)
        num_models = len(llm_responses)
    else:
        llm_responses = sample_llm_responses_single
        reference_answer = sample_reference_answer_single
        num_items = 1
        num_models = len(llm_responses)

    mock_j_class, _ = mock_metric_class_factory("Jaccard", 0.7, num_items=num_items)
    csv_path = tmp_path / "report.csv"

    exp = Experiment(llm_responses, reference_answer)
    exp.compare(metrics=["Jaccard"], output_csv_path=str(csv_path), plot=False)

    # Verify the CSV was created and has the correct content
    assert csv_path.exists()
    report_df = pd.read_csv(csv_path)

    assert len(report_df) == num_models * num_items

    if is_batch_test:
        # Check one row for correctness
        model_x_row_1 = report_df[
            (report_df["model_name"] == "ModelX") & (report_df["item_index"] == 1)
        ]
        assert not model_x_row_1.empty
        assert model_x_row_1["generated_text"].iloc[0] == "Response X2"
        assert model_x_row_1["reference_text"].iloc[0] == "Ref2"
        assert model_x_row_1["score"].iloc[0] == 0.7
    else:
        model_a_row = report_df[report_df["model_name"] == "ModelA"]
        assert not model_a_row.empty
        assert model_a_row["generated_text"].iloc[0] == "This is a response from Model A."
        assert model_a_row["score"].iloc[0] == 0.7


# New summarize() Method Tests
def test_summarize_basic(
    sample_llm_responses_batch, sample_reference_answer_batch, mock_metric_class_factory
):
    num_items = len(sample_reference_answer_batch)
    mock_j_class, _ = mock_metric_class_factory(
        "Jaccard", score_to_return=[0.7, 0.8, 0.6], num_items=num_items
    )
    mock_r_class, _ = mock_metric_class_factory(
        "ROUGE",
        sub_scores=[
            {"rouge1": 0.6, "rougeL": 0.5},
            {"rouge1": 0.7, "rougeL": 0.6},
            {"rouge1": 0.5, "rougeL": 0.4},
        ],
        num_items=num_items,
    )

    exp = Experiment(sample_llm_responses_batch, sample_reference_answer_batch)
    summary_df = exp.summarize(metrics=["Jaccard", "ROUGE"])

    assert isinstance(summary_df, pd.DataFrame)
    assert "model_name" in summary_df.columns
    assert "Jaccard_mean" in summary_df.columns
    assert "Jaccard_std" in summary_df.columns
    assert "Jaccard_pass_rate" in summary_df.columns
    assert "ROUGE_rouge1_mean" in summary_df.columns
    assert "ROUGE_rouge1_pass_rate" in summary_df.columns

    # Verify some calculated values (e.g., mean Jaccard for ModelX)
    # ModelX Jaccard scores: [0.7, 0.8, 0.6] -> mean 0.7
    model_x_summary = summary_df[summary_df["model_name"] == "ModelX"]
    assert not model_x_summary.empty
    assert pytest.approx(model_x_summary["Jaccard_mean"].iloc[0], 0.001) == 0.7
    assert pytest.approx(model_x_summary["Jaccard_std"].iloc[0], 0.001) == 0.1
    # Default Jaccard threshold is 0.5. All [0.7, 0.8, 0.6] pass.
    assert pytest.approx(model_x_summary["Jaccard_pass_rate"].iloc[0], 0.001) == 100.0

    # ModelX ROUGE_rouge1 scores: [0.6, 0.7, 0.5] -> mean 0.6
    # Default ROUGE threshold is 0.5. All [0.6, 0.7, 0.5] pass.
    assert pytest.approx(model_x_summary["ROUGE_rouge1_mean"].iloc[0], 0.001) == 0.6
    assert pytest.approx(model_x_summary["ROUGE_rouge1_pass_rate"].iloc[0], 0.001) == 100.0


def test_summarize_with_custom_thresholds(
    sample_llm_responses_batch, sample_reference_answer_batch, mock_metric_class_factory
):
    num_items = len(sample_reference_answer_batch)
    # Jaccard scores for each model will be [0.7, 0.4, 0.6]
    mock_j_class, _ = mock_metric_class_factory(
        "Jaccard", score_to_return=[0.7, 0.4, 0.6], num_items=num_items
    )
    # ROUGE_rouge1 scores for each model will be [0.6, 0.3, 0.5]
    mock_r_class, _ = mock_metric_class_factory(
        "ROUGE", sub_scores=[{"rouge1": 0.6}, {"rouge1": 0.3}, {"rouge1": 0.5}], num_items=num_items
    )

    exp = Experiment(sample_llm_responses_batch, sample_reference_answer_batch)
    summary_df = exp.summarize(
        metrics=["Jaccard", "ROUGE"], custom_thresholds={"Jaccard": 0.5, "ROUGE_rouge1": 0.4}
    )

    model_x_summary = summary_df[summary_df["model_name"] == "ModelX"]
    assert not model_x_summary.empty

    # Jaccard: [0.7, 0.4, 0.6]. Threshold 0.5. Pass: 0.7, 0.6 (2/3 = 66.67%)
    assert pytest.approx(model_x_summary["Jaccard_pass_rate"].iloc[0], 0.01) == (2 / 3) * 100

    # ROUGE_rouge1: [0.6, 0.3, 0.5]. Threshold 0.4. Pass: 0.6, 0.5 (2/3 = 66.67%)
    assert pytest.approx(model_x_summary["ROUGE_rouge1_pass_rate"].iloc[0], 0.01) == (2 / 3) * 100


def test_summarize_no_runnable_metrics(
    sample_llm_responses_batch, sample_reference_answer_batch, mock_metric_class_factory, capsys
):
    mock_metric_class_factory("Jaccard", init_raises=ImportError("fail J"), num_items=3)
    exp = Experiment(sample_llm_responses_batch, sample_reference_answer_batch)
    summary_df = exp.summarize(metrics=["Jaccard"])

    captured = capsys.readouterr()
    assert "Warning: Metric 'Jaccard' will be skipped due to missing dependencies" in captured.out
    assert "No scores available to summarize." in captured.out
    assert summary_df.empty


# New register_metric() Tests
class CustomTestMetric(BaseMetric):
    def _single_calculate(self, generated_item: Any, reference_item: Any, **kwargs: Any) -> float:
        return 0.99  # Dummy score


def test_register_metric_success(sample_llm_responses_single, sample_reference_answer_single):
    exp = Experiment(sample_llm_responses_single, sample_reference_answer_single)
    exp.register_metric("MyCustomMetric", CustomTestMetric)
    assert "MyCustomMetric" in exp.custom_metrics
    assert exp.custom_metrics["MyCustomMetric"] == CustomTestMetric


def test_register_metric_invalid_class(sample_llm_responses_single, sample_reference_answer_single):
    class NotABaseMetric:
        pass

    exp = Experiment(sample_llm_responses_single, sample_reference_answer_single)
    with pytest.raises(TypeError, match="metric_class must be a subclass of gaico.BaseMetric"):
        exp.register_metric("InvalidMetric", NotABaseMetric)
