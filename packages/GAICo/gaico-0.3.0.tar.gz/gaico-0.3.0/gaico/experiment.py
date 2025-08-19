from typing import Any, Callable, Dict, List, Optional

import pandas as pd

from gaico.metrics import (
    BLEU,
    ROUGE,
    BERTScore,
    CosineSimilarity,
    JaccardSimilarity,
    JSDivergence,
    LevenshteinDistance,
    SequenceMatcherSimilarity,
)

from .metrics.audio import AudioSNRNormalized, AudioSpectrogramDistance
from .metrics.base import BaseMetric
from .metrics.image import ImageAverageHash, ImageHistogramMatch, ImageSSIM
from .metrics.structured import PlanningJaccard, PlanningLCS, TimeSeriesDTW, TimeSeriesElementDiff
from .thresholds import apply_thresholds, apply_thresholds_to_df, get_default_thresholds
from .utils import prepare_results_dataframe

# Import plt from visualize to check availability and use for showing plots
# Use an alias to avoid conflict if user imports plt
from .visualize import plot_metric_comparison, plot_radar_comparison
from .visualize import plt as viz_plt

REGISTERED_METRICS: Dict[str, type[BaseMetric]] = {
    "Jaccard": JaccardSimilarity,
    "Cosine": CosineSimilarity,
    "Levenshtein": LevenshteinDistance,
    "SequenceMatcher": SequenceMatcherSimilarity,
    "BLEU": BLEU,
    "ROUGE": ROUGE,
    "JSD": JSDivergence,  # Note: This is JSDivergence for text
    "BERTScore": BERTScore,
    "PlanningLCS": PlanningLCS,
    "PlanningJaccard": PlanningJaccard,
    "TimeSeriesElementDiff": TimeSeriesElementDiff,
    "TimeSeriesDTW": TimeSeriesDTW,
    "ImageSSIM": ImageSSIM,
    "ImageAverageHash": ImageAverageHash,
    "ImageHistogramMatch": ImageHistogramMatch,
    "AudioSNR": AudioSNRNormalized,
    "AudioSpectrogramDistance": AudioSpectrogramDistance,
}
DEFAULT_METRICS_TO_RUN = [
    "Jaccard",
    "Cosine",
    "Levenshtein",
    "SequenceMatcher",
    "BLEU",
    "ROUGE",
    "JSD",
    "BERTScore",
]


class Experiment:
    """
    An abstraction to simplify plotting, applying thresholds, and generating CSVs
    for comparing LLM responses against reference answers using various metrics.
    """

    def __init__(
        self,
        llm_responses: Dict[str, Any],
        reference_answer: Optional[Any],
    ):
        """
        Initializes the Experiment for single or batch evaluation.

        :param llm_responses: A dictionary mapping model names (str) to their generated outputs.
                            For batch evaluation, values should be lists of outputs.
                            e.g., {"ModelA": ["resp1", "resp2"], "ModelB": ["resp1", "resp2"]}
        :type llm_responses: Dict[str, Any]
        :param reference_answer: A single reference output or a list of references for batch evaluation.
                                If None, the output(s) from the first model will be used as the reference.
        :type reference_answer: Optional[Any]
        :raises TypeError: If llm_responses is not a dictionary.
        :raises ValueError: If inputs are inconsistent (e.g., mixing single and list-like responses).
        """
        if not isinstance(llm_responses, dict):
            raise TypeError("llm_responses must be a dictionary.")
        if not all(isinstance(k, str) for k in llm_responses.keys()):
            raise ValueError("llm_responses keys must be strings (model names).")
        if not llm_responses:
            raise ValueError("llm_responses cannot be empty.")

        self.models = list(llm_responses.keys())
        self.custom_metrics: Dict[str, type[BaseMetric]] = {}

        # Determine if this is a batch/dataset evaluation based on the first model's response
        first_model_response = list(llm_responses.values())[0]
        self.is_batch = isinstance(first_model_response, (list, tuple, pd.Series))

        # Normalize all inputs to lists and validate consistency
        normalized_responses: Dict[str, List[Any]] = {}
        expected_len = -1

        for model_name, resp in llm_responses.items():
            is_resp_list_like = isinstance(resp, (list, tuple, pd.Series))
            if self.is_batch != is_resp_list_like:
                raise ValueError(
                    f"Inconsistent input types. All model responses must be either single items or list-like. "
                    f"Found mismatch for model '{model_name}'."
                )

            current_list = list(resp) if is_resp_list_like else [resp]
            normalized_responses[model_name] = current_list

            if expected_len == -1:
                expected_len = len(current_list)
            elif len(current_list) != expected_len:
                raise ValueError(
                    f"All model response lists must have the same length. "
                    f"Expected {expected_len}, but got {len(current_list)} for model '{model_name}'."
                )

        self.llm_responses = normalized_responses

        # Handle reference answer
        if reference_answer is None:
            first_model_name = self.models[0]
            self.reference_answer = self.llm_responses[first_model_name]  # This is already a list
            print(
                f"Warning: reference_answer was not provided for Experiment. "
                f"Using responses from model '{first_model_name}' as the reference."
            )
        else:
            is_ref_list_like = isinstance(reference_answer, (list, tuple, pd.Series))
            if self.is_batch and not is_ref_list_like:
                # Broadcast single reference to all items in the batch
                self.reference_answer = [reference_answer] * expected_len
            elif not self.is_batch and is_ref_list_like:
                raise ValueError(
                    "A list-like reference_answer was provided for a single-item experiment."
                )
            else:
                self.reference_answer = (
                    list(reference_answer) if is_ref_list_like else [reference_answer]
                )

        # Final length check for reference
        if len(self.reference_answer) != expected_len:
            raise ValueError(
                f"The reference_answer list must have the same length as the model response lists. "
                f"Expected {expected_len}, but got {len(self.reference_answer)}."
            )

        # The _raw_scores structure will now consistently hold lists of scores.
        self._raw_scores: Dict[str, Dict[str, List[Any]]] = {}
        self._results_df_cache: Optional[pd.DataFrame] = None
        self._thresholded_results_cache: Optional[Dict[str, Dict[str, Dict[str, Any]]]] = None

    def _calculate_scores_for_metric(self, metric_name: str) -> None:
        """
        Calculates scores for a given base metric across all models if not already done.
        Handles both single and batch inputs.

        :param metric_name: The name of the metric to calculate (e.g., "Jaccard", "ROUGE").
        :type metric_name: str
        """
        # Combine built-in and custom metrics for lookup
        combined_metrics = {**REGISTERED_METRICS, **self.custom_metrics}

        if metric_name not in combined_metrics:
            raise ValueError(f"Metric '{metric_name}' is not registered.")

        metric_cls = combined_metrics[metric_name]
        try:
            metric_instance = metric_cls()
        except ImportError as e:
            print(
                f"Warning: Metric '{metric_name}' cannot be initialized due to missing dependencies and will be skipped. Details: {e}"
            )
            # Mark as attempted but failed for all models
            for model_name in self.models:
                self._raw_scores.setdefault(model_name, {})[metric_name] = []
            return

        for model_name, gen_texts in self.llm_responses.items():
            if model_name not in self._raw_scores:
                self._raw_scores[model_name] = {}

            if metric_name not in self._raw_scores[model_name]:
                # gen_texts and self.reference_answer are guaranteed to be lists by __init__
                scores = metric_instance.calculate(gen_texts, self.reference_answer)
                self._raw_scores[model_name][metric_name] = scores
                self._results_df_cache = None  # Invalidate DataFrame cache

    def _get_runnable_metrics(self, requested_metrics: List[str]) -> List[str]:
        """
        Filters a list of requested metric names, returning only those
        that can be successfully instantiated (i.e., their dependencies are met).
        Considers both built-in and dynamically registered custom metrics.
        """
        runnable = []
        # Combine built-in and custom metrics for lookup
        combined_metrics = {**REGISTERED_METRICS, **self.custom_metrics}

        for metric_name in requested_metrics:
            if metric_name not in combined_metrics:
                print(f"Warning: Metric '{metric_name}' is not registered and will be skipped.")
                continue

            metric_cls = combined_metrics[metric_name]
            try:
                # Attempt to instantiate to check for ImportErrors from __init__
                _ = metric_cls()
                runnable.append(metric_name)
            except ImportError as e:
                print(
                    f"Warning: Metric '{metric_name}' will be skipped due to missing dependencies: {e}"
                )
            except Exception as e:  # Catch other potential init errors
                print(
                    f"Warning: Metric '{metric_name}' failed to initialize and will be skipped: {e}"
                )
        return runnable

    def _ensure_scores_calculated(self, base_metrics_to_calculate: List[str]):
        for metric_name in base_metrics_to_calculate:
            self._calculate_scores_for_metric(metric_name)

    def _get_internal_scores_df(self) -> pd.DataFrame:
        """
        Ensures all raw scores are converted to a DataFrame and caches it.
        This DataFrame contains all calculated metrics, flattened.
        """
        if self._results_df_cache is None:
            if not self._raw_scores:  # No scores calculated yet
                # This might happen if _get_scores_df is called before any metric calculation.
                # Calculate all default metrics as a baseline.
                # Ensure only runnable default metrics are calculated
                runnable_default_metrics = self._get_runnable_metrics(DEFAULT_METRICS_TO_RUN)
                self._ensure_scores_calculated(runnable_default_metrics)

            self._results_df_cache = prepare_results_dataframe(self._raw_scores)
        return (
            self._results_df_cache.copy() if self._results_df_cache is not None else pd.DataFrame()
        )

    def _get_filtered_scores_df(self, base_metrics_to_include: List[str]) -> pd.DataFrame:
        """
        Returns a DataFrame of scores, filtered to include only metrics
        derived from the provided list of base_metrics_to_include.
        Calculates scores if necessary.

        :param base_metrics_to_include: A list of base metric names (e.g., "Jaccard", "ROUGE").
        :type base_metrics_to_include: List[str]
        :return: A pandas DataFrame with columns "model_name", "metric_name", "score".
                 "metric_name" will contain flat metric names (e.g., "ROUGE_rouge1").
        :rtype: pd.DataFrame
        """
        # Ensure scores are calculated only for runnable metrics from the include list
        self._ensure_scores_calculated(base_metrics_to_include)

        full_df = self._get_internal_scores_df()  # Gets the cached or newly prepared full DF

        if full_df.empty:
            return pd.DataFrame(columns=["model_name", "metric_name", "score"])

        # Filter the full_df to include only flat metrics corresponding to base_metrics_to_include
        flat_metrics_to_keep = []
        all_df_metric_names = full_df["metric_name"].unique()

        # Iterate over the originally requested & runnable metrics
        for base_name in base_metrics_to_include:
            for df_m_name in all_df_metric_names:  # df_m_name can be 'ROUGE' or 'ROUGE_rouge1'
                if df_m_name == base_name or df_m_name.startswith(base_name + "_"):
                    flat_metrics_to_keep.append(df_m_name)

        if not flat_metrics_to_keep:  # No metrics matched
            return pd.DataFrame(columns=["model_name", "metric_name", "score"])

        return full_df[full_df["metric_name"].isin(list(set(flat_metrics_to_keep)))].copy()

    def to_dataframe(self, metrics: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Returns a DataFrame of scores for the specified metrics.
        If metrics is None, scores for all default metrics are returned.

        :param metrics: A list of base metric names (e.g., "Jaccard", "ROUGE"). Defaults to None.
        :type metrics: Optional[List[str]]
        :return: A pandas DataFrame with columns "model_name", "metric_name", "score".
                 "metric_name" will contain flat metric names (e.g., "ROUGE_rouge1").
        :rtype: pd.DataFrame
        """
        requested_metrics = metrics if metrics is not None else DEFAULT_METRICS_TO_RUN

        # Filter to only metrics that can actually run (dependencies met)
        runnable_metrics = self._get_runnable_metrics(requested_metrics)

        return self._get_filtered_scores_df(base_metrics_to_include=runnable_metrics)

    def _get_thresholded_results(
        self,
        flat_metrics_for_thresholding: List[str],
        custom_thresholds: Optional[Dict[str, float]],
        scores_df: pd.DataFrame,
    ) -> Dict[str, Dict[str, Dict[str, Any]]]:
        """
        Calculates and returns thresholded results for all models.
        Assumes scores_df contains the necessary flat_metrics.
        :param flat_metrics_for_thresholding: List of flat metric names to apply thresholds to.
        :type flat_metrics_for_thresholding: List[str]
        :param custom_thresholds: Optional dictionary mapping flat metric names to custom threshold values.
                                  If provided, these will override default thresholds.
        :type custom_thresholds: Optional[Dict[str, float]]
        :param scores_df: DataFrame containing scores with columns "model_name", "metric_name", "score".
                          This should already be filtered to include only relevant flat metrics.
        :type scores_df: pd.DataFrame
        :return: A dictionary mapping model names to their thresholded results.
                 Each model's results are a dictionary of flat metric names to their score and pass/fail status.
        :rtype: Dict[str, Dict[str, Dict[str, Any]]]
        """
        # Determine effective thresholds for each flat_metric_name
        default_threshold_map = get_default_thresholds()

        # This will store model_name -> {flat_metric_name: {score: val, passed: bool, ...}}
        all_models_thresholded_output: Dict = {}

        for model_name in self.models:
            model_scores_df = scores_df[
                (scores_df["model_name"] == model_name)
                & (scores_df["metric_name"].isin(flat_metrics_for_thresholding))
            ]

            if model_scores_df.empty:
                all_models_thresholded_output[model_name] = {}
                continue

            scores_for_model_dict = pd.Series(
                model_scores_df.score.values, index=model_scores_df.metric_name
            ).to_dict()

            # Determine thresholds to apply for this model's scores
            thresholds_for_this_model_apply = {}
            for flat_name, score_val in scores_for_model_dict.items():
                base_name_candidate = flat_name.split("_")[0]
                chosen_threshold_value = None

                if custom_thresholds:
                    if flat_name in custom_thresholds:
                        chosen_threshold_value = custom_thresholds[flat_name]
                    elif (
                        base_name_candidate in custom_thresholds and chosen_threshold_value is None
                    ):
                        chosen_threshold_value = custom_thresholds[base_name_candidate]

                if chosen_threshold_value is None:  # Fallback to defaults
                    # Defaults usually use base names.
                    if base_name_candidate in default_threshold_map:
                        chosen_threshold_value = default_threshold_map[base_name_candidate]
                    elif flat_name in default_threshold_map:  # Less common for defaults
                        chosen_threshold_value = default_threshold_map[flat_name]

                if chosen_threshold_value is not None:
                    thresholds_for_this_model_apply[flat_name] = chosen_threshold_value

            thresholded_for_model = apply_thresholds(
                scores_for_model_dict, thresholds_for_this_model_apply
            )
            all_models_thresholded_output[model_name] = thresholded_for_model

        self._thresholded_results_cache = all_models_thresholded_output  # Cache this
        return all_models_thresholded_output

    def register_metric(self, name: str, metric_class: type[BaseMetric]):
        """
        Registers a custom metric class for use in this Experiment instance.
        This allows users to extend GAICo with their own custom metrics
        and use them seamlessly with the Experiment's `compare()` and `summarize()` methods.

        :param name: The name to refer to this metric by (e.g., "MyCustomMetric").
        :type name: str
        :param metric_class: The class (must inherit from BaseMetric).
        :type metric_class: type[BaseMetric]
        :raises TypeError: If metric_class is not a subclass of gaico.BaseMetric.
        """
        if not issubclass(metric_class, BaseMetric):
            raise TypeError("metric_class must be a subclass of gaico.BaseMetric")
        self.custom_metrics[name] = metric_class
        print(f"Metric '{name}' registered successfully for this Experiment instance.")

    def summarize(
        self,
        metrics: Optional[List[str]] = None,
        custom_thresholds: Optional[Dict[str, float]] = None,
        agg_funcs: Optional[List[str]] = None,
    ) -> pd.DataFrame:
        """
        Calculates and returns a summary DataFrame with aggregated scores and pass rates
        for each model and metric.

        :param metrics: List of base metric names to include in the summary. If None, uses all
                        metrics that have been calculated or can be calculated.
        :type metrics: Optional[List[str]]
        :param custom_thresholds: Optional dictionary mapping flat metric names (e.g., "Jaccard", "ROUGE_rouge1")
                                  or base metric names (e.g., "ROUGE") to custom threshold values.
                                  If provided, these will override default thresholds for pass rate calculation.
        :type custom_thresholds: Optional[Dict[str, float]]
        :param agg_funcs: List of aggregation functions (as strings, e.g., 'mean', 'std', 'min', 'max')
                          to apply to scores. Defaults to ['mean', 'std'].
        :type agg_funcs: Optional[List[str]]
        :return: A summary DataFrame with aggregated scores and pass rates.
                 Columns will include 'model_name', and then aggregated score columns
                 (e.g., 'Jaccard_mean', 'ROUGE_rouge1_std') and pass rate columns
                 (e.g., 'Jaccard_pass_rate').
        :rtype: pd.DataFrame
        """
        if agg_funcs is None:
            agg_funcs = ["mean", "std"]

        # 1. Get the full results dataframe (calculates if not already)
        scores_df = self.to_dataframe(metrics=metrics)
        if scores_df.empty:
            print("No scores available to summarize.")
            return pd.DataFrame()

        # Ensure 'item_index' exists for batch processing, even if it's just 0 for single item
        if "item_index" not in scores_df.columns:
            scores_df["item_index"] = 0

        # 2. Calculate aggregated scores
        # Pivot to get metrics as columns for aggregation
        pivot_scores = scores_df.pivot_table(
            index=["item_index", "model_name"], columns="metric_name", values="score"
        )

        # Apply aggregation functions
        aggregated_scores = pivot_scores.groupby("model_name").agg(agg_funcs)  # type: ignore
        # Flatten multi-index columns (e.g., ('Jaccard', 'mean') -> 'Jaccard_mean')
        aggregated_scores.columns = [
            "_".join(col).strip() for col in aggregated_scores.columns.values
        ]
        aggregated_scores = aggregated_scores.reset_index()

        # 3. Calculate pass rates
        thresholded_df = apply_thresholds_to_df(scores_df, custom_thresholds)
        # Ensure 'item_index' exists for batch processing, even if it's just 0 for single item
        if "item_index" not in thresholded_df.columns:
            thresholded_df["item_index"] = 0

        # Calculate mean of 'passed_threshold' (True=1, False=0) for pass rate
        pass_rates = thresholded_df.pivot_table(
            index=["item_index", "model_name"], columns="metric_name", values="passed_threshold"
        )
        pass_rates = pass_rates.groupby("model_name").mean() * 100  # Convert to percentage
        pass_rates.columns = [f"{col}_pass_rate" for col in pass_rates.columns]
        pass_rates = pass_rates.reset_index()

        # 4. Join and return
        final_summary = pd.merge(aggregated_scores, pass_rates, on="model_name", how="outer")

        # Reorder columns to have model_name first
        cols = final_summary.columns.tolist()
        cols.remove("model_name")
        final_summary = final_summary[["model_name"] + sorted(cols)]

        return final_summary

    def compare(
        self,
        metrics: Optional[List[str]] = None,
        plot: bool = False,
        custom_thresholds: Optional[Dict[str, float]] = None,
        output_csv_path: Optional[str] = None,
        aggregate_func: Optional[Callable] = None,
        plot_title_suffix: str = "Comparison",
        radar_metrics_limit: int = 12,
    ) -> pd.DataFrame:
        """
        Compares models based on specified metrics, optionally plotting and generating a CSV.
        Handles both single-item and batch (dataset) evaluations.

        :param metrics: List of base metric names. If None, uses all default registered metrics.
        :type metrics: Optional[List[str]]
        :param plot: If True, generates and shows plots. For batch data, plots are aggregated.
        :type plot: bool
        :param custom_thresholds: Dictionary of metric names to threshold values.
        :type custom_thresholds: Optional[Dict[str, float]]
        :param output_csv_path: If provided, path to save a detailed CSV report.
        :type output_csv_path: Optional[str]
        :param aggregate_func: Aggregation function (e.g., np.mean) for plotting batch results.
        :type aggregate_func: Optional[Callable]
        :param plot_title_suffix: Suffix for plot titles.
        :type plot_title_suffix: str
        :param radar_metrics_limit: Maximum number of metrics for a radar plot.
        :type radar_metrics_limit: int
        :return: A pandas DataFrame containing the detailed scores for all items.
        :rtype: pd.DataFrame
        """
        requested_base_metrics = metrics if metrics is not None else DEFAULT_METRICS_TO_RUN
        runnable_base_metrics = self._get_runnable_metrics(requested_base_metrics)

        if not runnable_base_metrics:
            print("Warning: No runnable metrics found. Aborting compare.")
            return pd.DataFrame()

        # 1. Get DataFrame of scores (will include 'item_index' for batch runs)
        current_scores_df = self._get_filtered_scores_df(
            base_metrics_to_include=runnable_base_metrics
        )

        if current_scores_df.empty:
            print("No results to compare after processing metrics.")
            return current_scores_df

        # 2. Plotting (uses aggregation for batch data)
        if plot:
            if viz_plt is None:
                print("Warning: Matplotlib/Seaborn are not installed. Skipping plotting.")
            else:
                actual_flat_metrics_in_df = sorted(list(current_scores_df["metric_name"].unique()))
                num_actual_metrics = len(actual_flat_metrics_in_df)

                if num_actual_metrics == 0:
                    print("No metrics available for plotting.")
                elif num_actual_metrics == 1:
                    plot_metric_comparison(
                        current_scores_df,
                        metric_name=actual_flat_metrics_in_df[0],
                        aggregate_func=aggregate_func,
                        title=f"{actual_flat_metrics_in_df[0]} {plot_title_suffix}",
                    )
                    viz_plt.show()
                else:  # Multiple metrics -> Radar plot
                    metrics_for_radar = actual_flat_metrics_in_df
                    if len(actual_flat_metrics_in_df) > radar_metrics_limit:
                        print(
                            f"Warning: Too many metrics ({len(actual_flat_metrics_in_df)}) for radar plot. Plotting first {radar_metrics_limit}."
                        )
                        metrics_for_radar = actual_flat_metrics_in_df[:radar_metrics_limit]

                    if len(metrics_for_radar) >= 3:
                        plot_radar_comparison(
                            current_scores_df,
                            metrics=metrics_for_radar,
                            aggregate_func=aggregate_func,
                            title=f"Models {plot_title_suffix}",
                        )
                        viz_plt.show()
                    else:
                        print(
                            f"Warning: Only {len(metrics_for_radar)} metrics available. Generating bar plots instead of radar."
                        )
                        for metric_to_plot in metrics_for_radar:
                            plot_metric_comparison(
                                current_scores_df,
                                metric_name=metric_to_plot,
                                aggregate_func=aggregate_func,
                                title=f"{metric_to_plot} {plot_title_suffix}",
                            )
                            viz_plt.show()

        # 3. Generate CSV Report
        if output_csv_path:
            # Apply thresholds to the scores dataframe
            report_df = apply_thresholds_to_df(current_scores_df, custom_thresholds)

            if self.is_batch:
                # Create a DataFrame with the source texts for merging
                text_data = []
                for i in range(len(self.reference_answer)):
                    for model_name in self.models:
                        text_data.append(
                            {
                                "item_index": i,
                                "model_name": model_name,
                                "generated_text": self.llm_responses[model_name][i],
                                "reference_text": self.reference_answer[i],
                            }
                        )
                text_df = pd.DataFrame(text_data)
                # Merge scores with texts
                report_df = pd.merge(
                    text_df, report_df, on=["item_index", "model_name"], how="left"
                )
            else:  # Single item case
                report_df["generated_text"] = report_df["model_name"].map(
                    lambda m: self.llm_responses[m][0]
                )
                report_df["reference_text"] = self.reference_answer[0]

            # Reorder columns for clarity
            cols_order = [
                "item_index",
                "model_name",
                "metric_name",
                "score",
                "passed_threshold",
                "threshold_applied",
                "generated_text",
                "reference_text",
            ]
            final_cols = [c for c in cols_order if c in report_df.columns]
            report_df = report_df[final_cols]

            report_df.to_csv(output_csv_path, index=False)
            print(f"CSV report generated at: {output_csv_path}")

        return current_scores_df.copy()
