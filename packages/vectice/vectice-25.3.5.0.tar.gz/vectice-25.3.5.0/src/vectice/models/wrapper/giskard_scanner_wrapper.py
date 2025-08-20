from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable

if TYPE_CHECKING:
    from giskard.scanner.scanner import ScanReport  # type: ignore[reportMissingImports]
    from pandas import DataFrame


from giskard import Dataset, Model, scan  # type: ignore[reportMissingImports]
from giskard.scanner.scanner import ScanReport  # type: ignore[reportMissingImports]


def giskard_scan_llm_wrapper(
    context_retrieval_pipeline: Any | None = None,
    model_prediction_function: Callable | None = None,
    custom_model: Model | None = None,
    feature_names: list[str] | None = None,
    model_name: str | None = None,
    model_description: str | None = None,
    question_dataset: DataFrame | None = None,
    dataset_target: str | None = None,
    scan_only: list[str] = ["hallucination"],
    scan_max_issues_per_detector: int = 10,
) -> ScanReport:
    """Wrapper function to configure and execute a model scan using Giskard's scanning capabilities.
    Scans which are executed are harmful content and hallucinations.

    This function initializes a scan configuration by setting up the index, extracting relevant
    data, and configuring a prediction function for the model. If no custom prediction function is
    provided, a default one is created.

    Args:
        index_zip_path (str): The file path to the zipped index containing the preprocessed data.
        index_extract_dir (str): The directory where the index will be extracted.
        qa_testset_path (str): The file path to the QA test set used for model evaluation.
        model_predict_fn (Callable | None, optional): Custom prediction function for the model.
            Defaults to None, which will use a predefined function with simulated injections.
        model_type (str | None, optional): The type of model being scanned (e.g., "LLM", "classification").
            Defaults to None.
        model_name (str | None, optional): A name for the model being scanned. Defaults to None.
        model_description (str | None, optional): A description of the model. Defaults to None.
        feature_names (list[str] | None, optional): List of feature names to be used during the scan.
            Defaults to None.

    Returns:
        ScanReport: A report containing the results of the scan, highlighting issues related to
        the model's responses.

    Example:
        report = giskard_scan_wrapper(
            index_zip_path="/path/to/index.zip",
            index_extract_dir="/path/to/extracted/index",
            qa_testset_path="/path/to/qa_testset.jsonl",
            model_type="LLM",
            model_name="Test Model",
            model_description="A large language model for testing purposes.",
            feature_names=["question"]
        )
    """
    if isinstance(custom_model, Callable):
        # Define a custom Giskard model wrapper for the serialization.
        ### generic custom model
        giskard_model = custom_model(
            model=context_retrieval_pipeline,
            model_type="text_generation",  # type: ignore[reportArgumentType]
            name=model_name,
            description=model_description,
            feature_names=feature_names,
        )
    elif context_retrieval_pipeline and model_prediction_function:
        giskard_model = Model(
            model=context_retrieval_pipeline,
            # assumption for now...
            model_postprocessing_function=model_prediction_function,
            model_type="text_generation",  # type: ignore[reportArgumentType]
            name=model_name,
            description=model_description,
            feature_names=feature_names,
        )
    elif model_prediction_function and (custom_model is None and context_retrieval_pipeline is None):
        giskard_model = Model(
            model=model_prediction_function,
            # assumption for now...
            model_type="text_generation",  # type: ignore[reportArgumentType]
            name=model_name,
            description=model_description,
            feature_names=feature_names,
        )
    else:
        raise ValueError("no model")
    # used to validate the model, done prior to scan.
    giskard_dataset = None
    if question_dataset is not None:
        giskard_dataset = Dataset(question_dataset, dataset_target)

    return scan(giskard_model, giskard_dataset, only=scan_only, max_issues_per_detector=scan_max_issues_per_detector)  # type: ignore[reportCallIssue]
