from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Dict

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import shap
from scipy.stats import chi2_contingency, ks_2samp
from sklearn.metrics import auc, confusion_matrix, precision_score, recall_score, roc_curve

if TYPE_CHECKING:
    from matplotlib.container import BarContainer
    from numpy import ndarray
    from numpy.typing import ArrayLike
    from pandas import DataFrame

    from vectice.models.validation import TestSuiteReturnType

_logger = logging.getLogger(__name__)


def plot_roc_curve(
    training_df: DataFrame,
    testing_df: DataFrame,
    target_column: str,
    predictor: Any,
    predict_proba_train: ArrayLike | None,
    predict_proba_test: ArrayLike,
    threshold: float,
) -> TestSuiteReturnType | None:
    from vectice.models.validation import TestSuiteReturnType

    if predict_proba_train is not None:
        training_prediction_proba = predict_proba_train
    else:
        # Todo what if no predict_proba
        training_prediction_proba = predictor.predict_proba(training_df)[:, 1]

    testing_prediction_proba = predict_proba_test

    fpr_train, tpr_train, _ = roc_curve(training_df[target_column], training_prediction_proba)
    roc_auc_train = auc(fpr_train, tpr_train)

    fpr_test, tpr_test, _ = roc_curve(testing_df[target_column], testing_prediction_proba)
    roc_auc_test = auc(fpr_test, tpr_test)

    file_path = "ROC_CURVE.png"

    plt.figure(figsize=(8, 6))
    plt.plot(fpr_train, tpr_train, color="green", linestyle="--", label=f"Train ROC curve (AUC = {roc_auc_train:.2f})")
    plt.plot(fpr_test, tpr_test, color="blue", label=f"Test ROC curve (AUC = {roc_auc_test:.2f})")
    plt.plot([0, 1], [0, 1], color="red", linestyle="--")
    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    plt.title("Receiver Operating Characteristic (ROC) Curve")
    plt.legend()
    plt.grid(True)
    plt.savefig(file_path)
    plt.close()

    return TestSuiteReturnType(
        metrics={"_ROC_auc_train": roc_auc_train, "_ROC_auc_test": roc_auc_test},
        properties={},
        tables=[],
        attachments=[file_path],
    )


def conf_matrix(
    training_df: DataFrame,
    testing_df: DataFrame,
    target_column: str,
    predictor: Any,
    predict_proba_train: ArrayLike | None,
    predict_proba_test: ArrayLike,
    threshold: float,
) -> TestSuiteReturnType:
    from vectice.models.validation import TestSuiteReturnType

    testing_prediction_proba = predict_proba_test
    testing_prediction = (testing_prediction_proba >= threshold).astype(int)  # pyright: ignore[reportOperatorIssue]

    cm = confusion_matrix(testing_df[target_column], testing_prediction)
    total_samples = np.sum(cm)

    precision = precision_score(testing_df[target_column], testing_prediction)
    recall = recall_score(testing_df[target_column], testing_prediction)

    # Plot confusion matrix
    plt.figure(figsize=(10, 8))
    sns.heatmap(cm, annot=True, cmap="Blues", fmt="d", annot_kws={"fontsize": 12}, cbar=False)
    for i in range(len(cm)):
        for j in range(len(cm)):
            plt.text(
                j + 0.5,
                i + 0.75,
                f"{cm[i][j]/total_samples*100:.2f}%",
                ha="center",
                va="center",
                color="black",
                fontsize=12,
            )
    plt.xlabel("Predicted Label")
    plt.ylabel("True Label")
    plt.title(f"Confusion Matrix\nPrecision: {precision:.2f}, Recall: {recall:.2f}")

    # Save the plot
    file_path = "Confusion_matrix_plot.png"
    plt.savefig(file_path)
    plt.close()

    return TestSuiteReturnType(
        metrics={"_precision_test": precision, "_recall_test": recall},
        properties={"Threshold": threshold},
        tables=[],
        attachments=[file_path],
    )


def explainability(
    training_df: DataFrame,
    testing_df: DataFrame,
    target_column: str,
    predictor: Any,
    predict_proba_train: ArrayLike | None,
    predict_proba_test: ArrayLike,
    threshold: float,
) -> TestSuiteReturnType:
    from vectice.models.validation import TestSuiteReturnType

    explainer = shap.Explainer(predictor, training_df.drop(columns=[target_column]))
    shap_values = explainer(training_df.drop(columns=[target_column]).head(1000))
    shap.summary_plot(
        shap_values[:, :, 0], training_df.drop(columns=[target_column]).head(1000), max_display=10, show=False
    )
    summary_plot_path = "SHAP_summary_plot.png"
    plt.savefig(summary_plot_path, bbox_inches="tight")
    plt.close()

    return TestSuiteReturnType(metrics={}, properties={}, tables=[], attachments=[summary_plot_path])


def feature_importance(
    training_df: DataFrame,
    testing_df: DataFrame,
    target_column: str,
    predictor: Any,
    predict_proba_train: ArrayLike | None,
    predict_proba_test: ArrayLike,
    threshold: float,
) -> TestSuiteReturnType:
    from vectice.models.validation import TestSuiteReturnType

    explainer = shap.Explainer(predictor, training_df.drop(columns=[target_column]))
    shap_values = explainer(training_df.drop(columns=[target_column]).head(1000))
    clustering = shap.utils.hclust(
        training_df.drop(columns=[target_column]).head(1000), training_df[target_column].head(1000)
    )
    shap.plots.bar(shap_values[:, :, 0], clustering=clustering, max_display=10, show=False)

    feature_importance_path = "feature_importance.png"
    plt.savefig(feature_importance_path, bbox_inches="tight")
    plt.close()

    return TestSuiteReturnType(metrics={}, properties={}, tables=[], attachments=[feature_importance_path])


def cramers_v_score(x: ndarray[Any, Any], y: ndarray[Any, Any]) -> float:
    min_length = min(len(x), len(y), 4000)
    x = x[:min_length]
    y = y[:min_length]
    confusion_matrix = pd.crosstab(x, y)
    chi2 = chi2_contingency(confusion_matrix)[0]
    n = confusion_matrix.sum().sum()
    phi2 = chi2 / n
    r, k = confusion_matrix.shape
    phi2corr = max(0, phi2 - ((k - 1) * (r - 1)) / (n - 1))
    rcorr = r - ((r - 1) ** 2) / (n - 1)
    kcorr = k - ((k - 1) ** 2) / (n - 1)
    return np.sqrt(phi2corr / min((kcorr - 1), (rcorr - 1)))


def ks_score(x: ndarray[Any, Any], y: ndarray[Any, Any]) -> float:
    min_length = min(len(x), len(y), 4000)
    x = x[:min_length]
    y = y[:min_length]
    ks_statistic, _ = ks_2samp(x, y)

    return ks_statistic


def prediction_drift(
    training_df: DataFrame,
    testing_df: DataFrame,
    target_column: str,
    predictor: Any,
    predict_proba_train: ArrayLike | None,
    predict_proba_test: ArrayLike,
    threshold: float,
) -> TestSuiteReturnType:
    from vectice.models.validation import TestSuiteReturnType

    train_predictions = np.array(predict_proba_train)
    test_predictions = np.array(predict_proba_test)

    light_red = "#FF8A80"  # Light Red
    darker_blue = "#1565C0"  # Darker Blue
    sns.set_palette([darker_blue, light_red])

    _, ax = plt.subplots(figsize=(8, 6))

    sns.kdeplot(train_predictions, color=light_red, label="Train Predictions", fill=True)
    sns.kdeplot(test_predictions, color=darker_blue, label="Test Predictions", fill=True)

    # Plot vertical lines for means using the specified colors
    ax.axvline(  # pyright: ignore[reportAttributeAccessIssue]
        np.mean(train_predictions),  # pyright: ignore[reportArgumentType]
        color=light_red,
        linestyle="--",
        label="Train Mean",
    )
    ax.axvline(  # pyright: ignore[reportAttributeAccessIssue]
        np.mean(test_predictions),  # pyright: ignore[reportArgumentType]
        color=darker_blue,
        linestyle="--",
        label="Test Mean",
    )

    plt.xlabel("Predictions")
    plt.ylabel("Density")
    plt.title("Prediction Drift Plot (Kolmogorov-Smirnov drift score)")
    plt.legend()
    plt.grid(True)
    path = "Prediction_drift.png"

    # Calculate and print drift score
    drift_score = ks_score(train_predictions, test_predictions)

    # Set text position at the top
    text_x = 0.5
    text_y = 0.95
    if drift_score < 0.1:
        score_color = "green"
    elif 0.1 <= drift_score <= 0.2:
        score_color = "orange"
    else:
        score_color = "red"

    plt.text(
        text_x,
        text_y,
        f"Drift score = {drift_score:.2f}",
        ha="center",
        va="top",
        color=score_color,
        transform=ax.transAxes,  # pyright: ignore[reportAttributeAccessIssue]
    )

    plt.savefig(path, bbox_inches="tight")
    plt.close()

    return TestSuiteReturnType(
        metrics={}, properties={"_prediction_drift_score": drift_score}, tables=[], attachments=[path]
    )


def label_drift(
    training_df: DataFrame,
    testing_df: DataFrame,
    target_column: str,
    predictor: Any,
    predict_proba_train: ArrayLike | None,
    predict_proba_test: ArrayLike,
    threshold: float,
) -> TestSuiteReturnType:
    from vectice.models.validation import TestSuiteReturnType

    train_labels = np.array(training_df[target_column])
    test_labels = np.array(testing_df[target_column])

    light_red = "#FF8A80"  # Light Red
    darker_blue = "#1565C0"  # Darker Blue
    sns.set_palette([darker_blue, light_red])

    _, ax = plt.subplots(figsize=(8, 6))

    bar_width = 0.35
    index = np.arange(2)

    train_counts = [np.sum(train_labels == 0) / len(train_labels), np.sum(train_labels == 1) / len(train_labels)]
    test_counts = [np.sum(test_labels == 0) / len(test_labels), np.sum(test_labels == 1) / len(test_labels)]

    train_bar = ax.bar(  # pyright: ignore[reportAttributeAccessIssue]
        index, train_counts, bar_width, label="Train Labels"
    )
    test_bar = ax.bar(  # pyright: ignore[reportAttributeAccessIssue]
        index + bar_width, test_counts, bar_width, label="Test Labels"
    )

    ax.set_xlabel("Labels")  # pyright: ignore[reportAttributeAccessIssue]
    ax.set_ylabel("Frequency")  # pyright: ignore[reportAttributeAccessIssue]
    ax.set_title("Label Drift Plot (Cramer's V drift score)")  # pyright: ignore[reportAttributeAccessIssue]
    ax.set_xticks(index + bar_width / 2)  # pyright: ignore[reportAttributeAccessIssue]
    ax.set_xticklabels(["0", "1"])  # pyright: ignore[reportAttributeAccessIssue]
    ax.legend()  # pyright: ignore[reportAttributeAccessIssue]

    def autolabel(bars: BarContainer):
        """Attach a text label above each bar in *bars*, displaying its height."""
        for bar in bars:
            height = bar.get_height()
            ax.annotate(  # pyright: ignore[reportAttributeAccessIssue]
                f"{height:.2f}",
                xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 3),
                textcoords="offset points",
                ha="center",
                va="bottom",
            )

    autolabel(train_bar)
    autolabel(test_bar)

    drift_score = cramers_v_score(train_labels, test_labels)
    if drift_score < 0.1:
        score_color = "green"
    elif 0.1 <= drift_score <= 0.2:
        score_color = "orange"
    else:
        score_color = "red"

    ax.text(  # pyright: ignore[reportAttributeAccessIssue]
        0.5,
        0.95,
        f"Drift score = {drift_score:.2f}",
        ha="center",
        va="top",
        color=score_color,
        transform=ax.transAxes,  # pyright: ignore[reportAttributeAccessIssue]
    )

    plt.tight_layout()
    path = "Label_drift.png"
    plt.savefig(path, bbox_inches="tight")
    plt.close()

    return TestSuiteReturnType(
        metrics={}, properties={"_label_drift_score": drift_score}, tables=[], attachments=[path]
    )


MAP_TEST: Dict[str, Any] = {
    "roc": plot_roc_curve,
    "cm": conf_matrix,
    "explainability": explainability,
    "feature_importance": feature_importance,
    "drift": [label_drift, prediction_drift],
    "binary_full_suite": [
        plot_roc_curve,
        conf_matrix,
        explainability,
        feature_importance,
        label_drift,
        prediction_drift,
    ],
}
