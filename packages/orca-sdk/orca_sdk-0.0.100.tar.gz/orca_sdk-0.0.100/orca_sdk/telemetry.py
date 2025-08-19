from __future__ import annotations

import logging
import os
from abc import ABC
from datetime import datetime
from typing import TYPE_CHECKING, Any, Iterable, Literal, Self, overload

from httpx import Timeout

from ._utils.common import UNSET
from .client import (
    LabelPredictionWithMemoriesAndFeedback,
    PredictionFeedbackCategory,
    PredictionFeedbackRequest,
    ScorePredictionWithMemoriesAndFeedback,
    UpdatePredictionRequest,
    orca_api,
)
from .memoryset import (
    LabeledMemoryLookup,
    LabeledMemoryset,
    ScoredMemoryLookup,
    ScoredMemoryset,
)

if TYPE_CHECKING:
    from .classification_model import ClassificationModel
    from .regression_model import RegressionModel

TelemetryMode = Literal["off", "on", "sync", "async"]
"""
Mode for saving telemetry. One of:

- `"off"`: Do not save telemetry
- `"on"`: Save telemetry asynchronously unless the `ORCA_SAVE_TELEMETRY_SYNCHRONOUSLY` environment variable is set.
- `"sync"`: Save telemetry synchronously
- `"async"`: Save telemetry asynchronously
"""


def _get_telemetry_config(override: TelemetryMode | None = None) -> tuple[bool, bool]:
    return (
        override != "off",
        os.getenv("ORCA_SAVE_TELEMETRY_SYNCHRONOUSLY", "0") != "0" or override == "sync",
    )


def _parse_feedback(feedback: dict[str, Any]) -> PredictionFeedbackRequest:
    category = feedback.get("category", None)
    if category is None:
        raise ValueError("`category` must be specified")
    prediction_id = feedback.get("prediction_id", None)
    if prediction_id is None:
        raise ValueError("`prediction_id` must be specified")
    output: PredictionFeedbackRequest = {
        "prediction_id": prediction_id,
        "category_name": category,
    }
    if "value" in feedback:
        output["value"] = feedback["value"]
    if "comment" in feedback:
        output["comment"] = feedback["comment"]
    return output


class FeedbackCategory:
    """
    A category of feedback for predictions.

    Categories are created automatically, the first time feedback with a new name is recorded.
    The value type of the category is inferred from the first recorded value. Subsequent feedback
    for the same category must be of the same type. Categories are not model specific.

    Attributes:
        id: Unique identifier for the category.
        name: Name of the category.
        value_type: Type that values for this category must have.
        created_at: When the category was created.
    """

    id: str
    name: str
    value_type: type[bool] | type[float]
    created_at: datetime

    def __init__(self, category: PredictionFeedbackCategory):
        self.id = category["id"]
        self.name = category["name"]
        self.value_type = bool if category["type"] == "BINARY" else float
        self.created_at = datetime.fromisoformat(category["created_at"])

    @classmethod
    def all(cls) -> list[FeedbackCategory]:
        """
        Get a list of all existing feedback categories.

        Returns:
            List with information about all existing feedback categories.
        """
        return [FeedbackCategory(category) for category in orca_api.GET("/telemetry/feedback_category")]

    @classmethod
    def drop(cls, name: str) -> None:
        """
        Drop all feedback for this category and drop the category itself, allowing it to be
        recreated with a different value type.

        Warning:
            This will delete all feedback in this category across all models.

        Params:
            name: Name of the category to drop.

        Raises:
            LookupError: If the category is not found.
        """
        orca_api.DELETE("/telemetry/feedback_category/{name_or_id}", params={"name_or_id": name})
        logging.info(f"Deleted feedback category {name} with all associated feedback")

    def __repr__(self):
        return "FeedbackCategory({" + f"name: {self.name}, " + f"value_type: {self.value_type}" + "})"


class AddMemorySuggestions:
    suggestions: list[tuple[str, str]]
    memoryset_id: str
    model_id: str
    prediction_id: str

    def __init__(self, suggestions: list[tuple[str, str]], memoryset_id: str, model_id: str, prediction_id: str):
        self.suggestions = suggestions
        self.memoryset_id = memoryset_id
        self.model_id = model_id
        self.prediction_id = prediction_id

    def __repr__(self):
        return (
            "AddMemorySuggestions({"
            + f"suggestions: {self.suggestions}, "
            + f"memoryset_id: {self.memoryset_id}, "
            + f"model_id: {self.model_id}, "
            + f"prediction_id: {self.prediction_id}"
            + "})"
        )

    def apply(self) -> None:
        memoryset = LabeledMemoryset.open(self.memoryset_id)
        label_name_to_label = {label_name: label for label, label_name in enumerate(memoryset.label_names)}
        memoryset.insert(
            [{"value": suggestion[0], "label": label_name_to_label[suggestion[1]]} for suggestion in self.suggestions]
        )


class _Prediction(ABC):
    prediction_id: str | None
    confidence: float
    anomaly_score: float | None

    def __init__(
        self,
        prediction_id: str | None,
        *,
        label: int | None,
        label_name: str | None,
        score: float | None,
        confidence: float,
        anomaly_score: float | None,
        memoryset: LabeledMemoryset | ScoredMemoryset,
        model: ClassificationModel | RegressionModel,
        telemetry: LabelPredictionWithMemoriesAndFeedback | ScorePredictionWithMemoriesAndFeedback | None = None,
        logits: list[float] | None = None,
        input_value: str | None = None,
    ):
        self.prediction_id = prediction_id
        self.label = label
        self.label_name = label_name
        self.score = score
        self.confidence = confidence
        self.anomaly_score = anomaly_score
        self.memoryset = memoryset
        self.model = model
        self.__telemetry = telemetry if telemetry else None
        self.logits = logits
        self._input_value = input_value

    @property
    def _telemetry(self) -> LabelPredictionWithMemoriesAndFeedback | ScorePredictionWithMemoriesAndFeedback:
        # for internal use only, do not document
        if self.__telemetry is None:
            if self.prediction_id is None:
                raise ValueError("Cannot fetch telemetry with no prediction ID")
            self.__telemetry = orca_api.GET(
                "/telemetry/prediction/{prediction_id}", params={"prediction_id": self.prediction_id}
            )
        return self.__telemetry

    @property
    def input_value(self) -> str:
        if self._input_value is not None:
            return self._input_value
        assert isinstance(self._telemetry["input_value"], str)
        return self._telemetry["input_value"]

    @property
    def memory_lookups(self) -> list[LabeledMemoryLookup] | list[ScoredMemoryLookup]:
        if "label" in self._telemetry:
            return [
                LabeledMemoryLookup(self._telemetry["memoryset_id"], lookup) for lookup in self._telemetry["memories"]
            ]
        else:
            return [
                ScoredMemoryLookup(self._telemetry["memoryset_id"], lookup) for lookup in self._telemetry["memories"]
            ]

    @property
    def feedback(self) -> dict[str, bool | float]:
        return {
            f["category_name"]: (
                f["value"] if f["category_type"] == "CONTINUOUS" else True if f["value"] == 1 else False
            )
            for f in self._telemetry["feedbacks"]
        }

    @property
    def tags(self) -> set[str]:
        return set(self._telemetry["tags"])

    @property
    def explanation(self) -> str:
        if self._telemetry["explanation"] is None:
            self._telemetry["explanation"] = orca_api.GET(
                "/telemetry/prediction/{prediction_id}/explanation",
                params={"prediction_id": self._telemetry["prediction_id"]},
                parse_as="text",
                timeout=30,
            )
        return self._telemetry["explanation"]

    def explain(self, refresh: bool = False) -> None:
        """
        Print an explanation of the prediction as a stream of text.

        Params:
            refresh: Force the explanation agent to re-run even if an explanation already exists.
        """
        if not refresh and self._telemetry["explanation"] is not None:
            print(self._telemetry["explanation"])
        else:
            with orca_api.stream(
                "GET",
                f"/telemetry/prediction/{self.prediction_id}/explanation?refresh={refresh}",
                timeout=Timeout(connect=3, read=None),
            ) as res:
                for chunk in res.iter_text():
                    print(chunk, end="")
            print()  # final newline

    @overload
    @classmethod
    def get(cls, prediction_id: str) -> Self:  # type: ignore -- this takes precedence
        pass

    @overload
    @classmethod
    def get(cls, prediction_id: Iterable[str]) -> list[Self]:
        pass

    @classmethod
    def get(cls, prediction_id: str | Iterable[str]) -> Self | list[Self]:
        """
        Fetch a prediction or predictions

        Params:
            prediction_id: Unique identifier of the prediction or predictions to fetch

        Returns:
            Prediction or list of predictions

        Raises:
            LookupError: If no prediction with the given id is found

        Examples:
            Fetch a single prediction:
            >>> LabelPrediction.get("0195019a-5bc7-7afb-b902-5945ee1fb766")
            LabelPrediction({
                label: <positive: 1>,
                confidence: 0.95,
                anomaly_score: 0.1,
                input_value: "I am happy",
                memoryset: "my_memoryset",
                model: "my_model"
            })

            Fetch multiple predictions:
            >>> LabelPrediction.get([
            ...     "0195019a-5bc7-7afb-b902-5945ee1fb766",
            ...     "019501a1-ea08-76b2-9f62-95e4800b4841",
            ... ])
            [
                LabelPrediction({
                    label: <positive: 1>,
                    confidence: 0.95,
                    anomaly_score: 0.1,
                    input_value: "I am happy",
                    memoryset: "my_memoryset",
                    model: "my_model"
                }),
                LabelPrediction({
                    label: <negative: 0>,
                    confidence: 0.05,
                    anomaly_score: 0.2,
                    input_value: "I am sad",
                    memoryset: "my_memoryset", model: "my_model"
                }),
            ]
        """
        from .classification_model import ClassificationModel
        from .regression_model import RegressionModel

        def create_prediction(
            prediction: LabelPredictionWithMemoriesAndFeedback | ScorePredictionWithMemoriesAndFeedback,
        ) -> Self:

            if "label" in prediction:
                memoryset = LabeledMemoryset.open(prediction["memoryset_id"])
                model = ClassificationModel.open(prediction["model_id"])
            else:
                memoryset = ScoredMemoryset.open(prediction["memoryset_id"])
                model = RegressionModel.open(prediction["model_id"])

            return cls(
                prediction_id=prediction["prediction_id"],
                label=prediction.get("label", None),
                label_name=prediction.get("label_name", None),
                score=prediction.get("score", None),
                confidence=prediction["confidence"],
                anomaly_score=prediction["anomaly_score"],
                memoryset=memoryset,
                model=model,
                telemetry=prediction,
            )

        if isinstance(prediction_id, str):
            return create_prediction(
                orca_api.GET("/telemetry/prediction/{prediction_id}", params={"prediction_id": prediction_id})
            )
        else:
            return [
                create_prediction(prediction)
                for prediction in orca_api.POST("/telemetry/prediction", json={"prediction_ids": list(prediction_id)})
            ]

    def refresh(self):
        """Refresh the prediction data from the OrcaCloud"""
        if self.prediction_id is None:
            raise ValueError("Cannot refresh prediction with no prediction ID")
        self.__dict__.update(self.get(self.prediction_id).__dict__)

    def _update(
        self,
        *,
        tags: set[str] | None = UNSET,
        expected_label: int | None = UNSET,
        expected_score: float | None = UNSET,
    ) -> None:
        if self.prediction_id is None:
            raise ValueError("Cannot update prediction with no prediction ID")

        payload: UpdatePredictionRequest = {}
        if tags is not UNSET:
            payload["tags"] = [] if tags is None else list(tags)
        if expected_label is not UNSET:
            payload["expected_label"] = expected_label
        if expected_score is not UNSET:
            payload["expected_score"] = expected_score
        orca_api.PATCH(
            "/telemetry/prediction/{prediction_id}", params={"prediction_id": self.prediction_id}, json=payload
        )
        self.refresh()

    def add_tag(self, tag: str) -> None:
        """
        Add a tag to the prediction

        Params:
            tag: Tag to add to the prediction
        """
        self._update(tags=self.tags | {tag})

    def remove_tag(self, tag: str) -> None:
        """
        Remove a tag from the prediction

        Params:
            tag: Tag to remove from the prediction
        """
        self._update(tags=self.tags - {tag})

    def record_feedback(
        self,
        category: str,
        value: bool | float,
        *,
        comment: str | None = None,
    ):
        """
        Record feedback for the prediction.

        We support recording feedback in several categories for each prediction. A
        [`FeedbackCategory`][orca_sdk.telemetry.FeedbackCategory] is created automatically,
        the first time feedback with a new name is recorded. Categories are global across models.
        The value type of the category is inferred from the first recorded value. Subsequent
        feedback for the same category must be of the same type.

        Params:
            category: Name of the category under which to record the feedback.
            value: Feedback value to record, should be `True` for positive feedback and `False` for
                negative feedback or a [`float`][float] between `-1.0` and `+1.0` where negative
                values indicate negative feedback and positive values indicate positive feedback.
            comment: Optional comment to record with the feedback.

        Examples:
            Record whether a suggestion was accepted or rejected:
            >>> prediction.record_feedback("accepted", True)

            Record star rating as normalized continuous score between `-1.0` and `+1.0`:
            >>> prediction.record_feedback("rating", -0.5, comment="2 stars")

        Raises:
            ValueError: If the value does not match previous value types for the category, or is a
                [`float`][float] that is not between `-1.0` and `+1.0`.
        """
        orca_api.PUT(
            "/telemetry/prediction/feedback",
            json=[
                _parse_feedback(
                    {"prediction_id": self.prediction_id, "category": category, "value": value, "comment": comment}
                )
            ],
        )
        self.refresh()

    def delete_feedback(self, category: str) -> None:
        """
        Delete prediction feedback for a specific category.

        Params:
            category: Name of the category of the feedback to delete.

        Raises:
            ValueError: If the category is not found.
        """
        if self.prediction_id is None:
            raise ValueError("Cannot delete feedback with no prediction ID")

        orca_api.PUT(
            "/telemetry/prediction/feedback",
            json=[PredictionFeedbackRequest(prediction_id=self.prediction_id, category_name=category, value=None)],
        )
        self.refresh()


class ClassificationPrediction(_Prediction):
    """
    Labeled prediction result from a [`ClassificationModel`][orca_sdk.ClassificationModel]

    Attributes:
        prediction_id: Unique identifier of this prediction used for feedback
        label: Label predicted by the model
        label_name: Human-readable name of the label
        confidence: Confidence of the prediction
        anomaly_score: Anomaly score of the input
        input_value: The input value used for the prediction
        expected_label: Expected label for the prediction, useful when evaluating the model
        expected_label_name: Human-readable name of the expected label
        memory_lookups: Memories used by the model to make the prediction
        explanation: Natural language explanation of the prediction, only available if the model
            has the Explain API enabled
        tags: Tags for the prediction, useful for filtering and grouping predictions
        model: Model used to make the prediction
        memoryset: Memoryset that was used to lookup memories to ground the prediction
    """

    label: int
    label_name: str
    logits: list[float] | None
    model: ClassificationModel
    memoryset: LabeledMemoryset

    def __repr__(self):
        return (
            "ClassificationPrediction({"
            + f"label: <{self.label_name}: {self.label}>, "
            + f"confidence: {self.confidence:.2f}, "
            + (f"anomaly_score: {self.anomaly_score:.2f}, " if self.anomaly_score is not None else "")
            + f"input_value: '{str(self.input_value)[:100] + '...' if len(str(self.input_value)) > 100 else self.input_value}'"
            + "})"
        )

    @property
    def memory_lookups(self) -> list[LabeledMemoryLookup]:
        assert "label" in self._telemetry
        return [LabeledMemoryLookup(self._telemetry["memoryset_id"], lookup) for lookup in self._telemetry["memories"]]

    @property
    def expected_label(self) -> int | None:
        assert "label" in self._telemetry
        return self._telemetry["expected_label"]

    @property
    def expected_label_name(self) -> str | None:
        assert "label" in self._telemetry
        return self._telemetry["expected_label_name"]

    def update(
        self,
        *,
        tags: set[str] | None = UNSET,
        expected_label: int | None = UNSET,
    ) -> None:
        """
        Update the prediction.

        Note:
            If a field is not provided, it will default to [UNSET][orca_sdk.UNSET] and not be updated.

        Params:
            tags: New tags to set for the prediction. Set to `None` to remove all tags.
            expected_label: New expected label to set for the prediction. Set to `None` to remove.
        """
        self._update(tags=tags, expected_label=expected_label)

    def recommend_action(self, *, refresh: bool = False) -> tuple[str, str]:
        """
        Get an action recommendation for improving this prediction.

        Analyzes the prediction and suggests the most effective action to improve model
        performance, such as adding memories, detecting mislabels, removing duplicates,
        or finetuning.

        Params:
            refresh: Force the action recommendation agent to re-run even if a recommendation already exists

        Returns:
            Tuple of (action, rationale) where:
            - action: The recommended action ("add_memories", "detect_mislabels", "remove_duplicates", or "finetuning") that would resolve the mislabeling
            - rationale: Explanation for why this action was recommended

        Raises:
            ValueError: If the prediction has no prediction ID
            RuntimeError: If the lighthouse API key is not configured

        Examples:
            Get action recommendation for an incorrect prediction:
            >>> action, rationale = prediction.recommend_action()
            >>> print(f"Recommended action: {action}")
            >>> print(f"Rationale: {rationale}")
        """
        if self.prediction_id is None:
            raise ValueError("Cannot get action recommendation with no prediction ID")

        response = orca_api.GET(
            "/telemetry/prediction/{prediction_id}/action",
            params={"prediction_id": self.prediction_id},
            timeout=30,
        )
        return (response["action"], response["rationale"])

    def generate_memory_suggestions(self, *, num_memories: int = 3) -> AddMemorySuggestions:
        """
        Generate synthetic memory suggestions to improve this prediction.

        Creates new example memories that are similar to the input but have clearer
        signals for the expected label. These can be added to the memoryset to improve
        model performance on similar inputs.

        Params:
            num_memories: Number of memory suggestions to generate (default: 3)

        Returns:
            List of dictionaries that can be directly passed to memoryset.insert().
            Each dictionary contains:
            - "value": The suggested memory text
            - "label": The suggested label as an integer

        Raises:
            ValueError: If the prediction has no prediction ID
            RuntimeError: If the lighthouse API key is not configured

        Examples:
            Generate memory suggestions for an incorrect prediction:
            >>> suggestions = prediction.generate_memory_suggestions(num_memories=3)
            >>> for suggestion in suggestions:
            ...     print(f"Value: {suggestion['value']}, Label: {suggestion['label']}")
            >>>
            >>> # Add suggestions directly to memoryset
            >>> model.memoryset.insert(suggestions)
        """
        if self.prediction_id is None:
            raise ValueError("Cannot generate memory suggestions with no prediction ID")

        response = orca_api.GET(
            "/telemetry/prediction/{prediction_id}/memory_suggestions",
            params={"prediction_id": self.prediction_id, "num_memories": num_memories},
            timeout=30,
        )

        return AddMemorySuggestions(
            suggestions=[(m["value"], m["label_name"]) for m in response["memories"]],
            memoryset_id=self.memoryset.id,
            model_id=self.model.id,
            prediction_id=self.prediction_id,
        )


class RegressionPrediction(_Prediction):
    """
    Score-based prediction result from a [`RegressionModel`][orca_sdk.RegressionModel]

    Attributes:
        prediction_id: Unique identifier of this prediction used for feedback
        score: Score predicted by the model
        confidence: Confidence of the prediction
        anomaly_score: Anomaly score of the input
        input_value: The input value used for the prediction
        expected_score: Expected score for the prediction, useful when evaluating the model
        memory_lookups: Memories used by the model to make the prediction
        explanation: Natural language explanation of the prediction, only available if the model
            has the Explain API enabled
        tags: Tags for the prediction, useful for filtering and grouping predictions
        model: Model used to make the prediction
        memoryset: Memoryset that was used to lookup memories to ground the prediction
    """

    score: float
    model: RegressionModel
    memoryset: ScoredMemoryset

    def __repr__(self):
        return (
            "RegressionPrediction({"
            + f"score: {self.score:.2f}, "
            + f"confidence: {self.confidence:.2f}, "
            + (f"anomaly_score: {self.anomaly_score:.2f}, " if self.anomaly_score is not None else "")
            + f"input_value: '{str(self.input_value)[:100] + '...' if len(str(self.input_value)) > 100 else self.input_value}'"
            + "})"
        )

    @property
    def memory_lookups(self) -> list[ScoredMemoryLookup]:
        assert "score" in self._telemetry
        return [ScoredMemoryLookup(self._telemetry["memoryset_id"], lookup) for lookup in self._telemetry["memories"]]

    @property
    def explanation(self) -> str:
        """The explanation for this prediction. Requires `lighthouse_client_api_key` to be set."""
        raise NotImplementedError("Explanation is not supported for regression predictions")

    @property
    def expected_score(self) -> float | None:
        assert "score" in self._telemetry
        return self._telemetry["expected_score"]

    def update(
        self,
        *,
        tags: set[str] | None = UNSET,
        expected_score: float | None = UNSET,
    ) -> None:
        """
        Update the prediction.

        Note:
            If a field is not provided, it will default to [UNSET][orca_sdk.UNSET] and not be updated.

        Params:
            tags: New tags to set for the prediction. Set to `None` to remove all tags.
            expected_score: New expected score to set for the prediction. Set to `None` to remove.
        """
        self._update(tags=tags, expected_score=expected_score)
