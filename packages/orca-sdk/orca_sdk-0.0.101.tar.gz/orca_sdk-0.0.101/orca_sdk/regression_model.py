from __future__ import annotations

import logging
from contextlib import contextmanager
from datetime import datetime
from typing import Any, Generator, Iterable, Literal, cast, overload

from datasets import Dataset

from ._shared.metrics import RegressionMetrics, calculate_regression_metrics
from ._utils.common import UNSET, CreateMode, DropMode
from .client import (
    PredictiveModelUpdate,
    RARHeadType,
    RegressionModelMetadata,
    orca_api,
)
from .datasource import Datasource
from .job import Job
from .memoryset import ScoredMemoryset
from .telemetry import (
    RegressionPrediction,
    TelemetryMode,
    _get_telemetry_config,
    _parse_feedback,
)

logger = logging.getLogger(__name__)


class RegressionModel:
    """
    A handle to a regression model in OrcaCloud

    Attributes:
        id: Unique identifier for the model
        name: Unique name of the model
        description: Optional description of the model
        memoryset: Memoryset that the model uses
        head_type: Regression head type of the model
        memory_lookup_count: Number of memories the model uses for each prediction
        locked: Whether the model is locked to prevent accidental deletion
        created_at: When the model was created
        updated_at: When the model was last updated
    """

    id: str
    name: str
    description: str | None
    memoryset: ScoredMemoryset
    head_type: RARHeadType
    memory_lookup_count: int
    version: int
    locked: bool
    created_at: datetime
    updated_at: datetime
    memoryset_id: str

    _last_prediction: RegressionPrediction | None
    _last_prediction_was_batch: bool
    _memoryset_override_id: str | None

    def __init__(self, metadata: RegressionModelMetadata):
        # for internal use only, do not document
        self.id = metadata["id"]
        self.name = metadata["name"]
        self.description = metadata["description"]
        self.memoryset = ScoredMemoryset.open(metadata["memoryset_id"])
        self.head_type = metadata["head_type"]
        self.memory_lookup_count = metadata["memory_lookup_count"]
        self.version = metadata["version"]
        self.locked = metadata["locked"]
        self.created_at = datetime.fromisoformat(metadata["created_at"])
        self.updated_at = datetime.fromisoformat(metadata["updated_at"])
        self.memoryset_id = metadata["memoryset_id"]

        self._memoryset_override_id = None
        self._last_prediction = None
        self._last_prediction_was_batch = False

    def __eq__(self, other) -> bool:
        return isinstance(other, RegressionModel) and self.id == other.id

    def __repr__(self):
        return (
            "RegressionModel({\n"
            f"    name: '{self.name}',\n"
            f"    head_type: {self.head_type},\n"
            f"    memory_lookup_count: {self.memory_lookup_count},\n"
            f"    memoryset: ScoredMemoryset.open('{self.memoryset.name}'),\n"
            "})"
        )

    @property
    def last_prediction(self) -> RegressionPrediction:
        """
        Last prediction made by the model

        Note:
            If the last prediction was part of a batch prediction, the last prediction from the
            batch is returned. If no prediction has been made yet, a [`LookupError`][LookupError]
            is raised.
        """
        if self._last_prediction_was_batch:
            logging.warning(
                "Last prediction was part of a batch prediction, returning the last prediction from the batch"
            )
        if self._last_prediction is None:
            raise LookupError("No prediction has been made yet")
        return self._last_prediction

    @classmethod
    def create(
        cls,
        name: str,
        memoryset: ScoredMemoryset,
        memory_lookup_count: int | None = None,
        description: str | None = None,
        if_exists: CreateMode = "error",
    ) -> RegressionModel:
        """
        Create a regression model.

        Params:
            name: Name of the model
            memoryset: The scored memoryset to use for prediction
            memory_lookup_count: Number of memories to retrieve for prediction. Defaults to 10.
            description: Description of the model
            if_exists: How to handle existing models with the same name

        Returns:
            RegressionModel instance

        Raises:
            ValueError: If a model with the same name already exists and if_exists is "error"
            ValueError: If the memoryset is empty
            ValueError: If memory_lookup_count exceeds the number of memories in the memoryset
        """
        existing = cls.exists(name)
        if existing:
            if if_exists == "error":
                raise ValueError(f"RegressionModel with name '{name}' already exists")
            elif if_exists == "open":
                existing = cls.open(name)
                for attribute in {"memory_lookup_count"}:
                    local_attribute = locals()[attribute]
                    existing_attribute = getattr(existing, attribute)
                    if local_attribute is not None and local_attribute != existing_attribute:
                        raise ValueError(f"Model with name {name} already exists with different {attribute}")

                # special case for memoryset
                if existing.memoryset_id != memoryset.id:
                    raise ValueError(f"Model with name {name} already exists with different memoryset")

                return existing

        metadata = orca_api.POST(
            "/regression_model",
            json={
                "name": name,
                "memoryset_name_or_id": memoryset.id,
                "memory_lookup_count": memory_lookup_count,
                "description": description,
            },
        )
        return cls(metadata)

    @classmethod
    def open(cls, name: str) -> RegressionModel:
        """
        Get a handle to a regression model in the OrcaCloud

        Params:
            name: Name or unique identifier of the regression model

        Returns:
            Handle to the existing regression model in the OrcaCloud

        Raises:
            LookupError: If the regression model does not exist
        """
        return cls(orca_api.GET("/regression_model/{name_or_id}", params={"name_or_id": name}))

    @classmethod
    def exists(cls, name_or_id: str) -> bool:
        """
        Check if a regression model exists in the OrcaCloud

        Params:
            name_or_id: Name or id of the regression model

        Returns:
            `True` if the regression model exists, `False` otherwise
        """
        try:
            cls.open(name_or_id)
            return True
        except LookupError:
            return False

    @classmethod
    def all(cls) -> list[RegressionModel]:
        """
        Get a list of handles to all regression models in the OrcaCloud

        Returns:
            List of handles to all regression models in the OrcaCloud
        """
        return [cls(metadata) for metadata in orca_api.GET("/regression_model")]

    @classmethod
    def drop(cls, name_or_id: str, if_not_exists: DropMode = "error"):
        """
        Delete a regression model from the OrcaCloud

        Warning:
            This will delete the model and all associated data, including predictions, evaluations, and feedback.

        Params:
            name_or_id: Name or id of the regression model
            if_not_exists: What to do if the regression model does not exist, defaults to `"error"`.
                Other option is `"ignore"` to do nothing if the regression model does not exist.

        Raises:
            LookupError: If the regression model does not exist and if_not_exists is `"error"`
        """
        try:
            orca_api.DELETE("/regression_model/{name_or_id}", params={"name_or_id": name_or_id})
            logging.info(f"Deleted model {name_or_id}")
        except LookupError:
            if if_not_exists == "error":
                raise

    def refresh(self):
        """Refresh the model data from the OrcaCloud"""
        self.__dict__.update(self.open(self.name).__dict__)

    def set(self, *, description: str | None = UNSET, locked: bool = UNSET) -> None:
        """
        Update editable attributes of the model.

        Note:
            If a field is not provided, it will default to [UNSET][orca_sdk.UNSET] and not be updated.

        Params:
            description: Value to set for the description
            locked: Value to set for the locked status

        Examples:
            Update the description:
            >>> model.set(description="New description")

            Remove description:
            >>> model.set(description=None)

            Lock the model:
            >>> model.set(locked=True)
        """
        update: PredictiveModelUpdate = {}
        if description is not UNSET:
            update["description"] = description
        if locked is not UNSET:
            update["locked"] = locked
        orca_api.PATCH("/regression_model/{name_or_id}", params={"name_or_id": self.id}, json=update)
        self.refresh()

    def lock(self) -> None:
        """Lock the model to prevent accidental deletion"""
        self.set(locked=True)

    def unlock(self) -> None:
        """Unlock the model to allow deletion"""
        self.set(locked=False)

    @overload
    def predict(
        self,
        value: str,
        expected_scores: float | None = None,
        tags: set[str] | None = None,
        save_telemetry: TelemetryMode = "on",
        prompt: str | None = None,
        use_lookup_cache: bool = True,
    ) -> RegressionPrediction: ...

    @overload
    def predict(
        self,
        value: list[str],
        expected_scores: list[float] | None = None,
        tags: set[str] | None = None,
        save_telemetry: TelemetryMode = "on",
        prompt: str | None = None,
        use_lookup_cache: bool = True,
    ) -> list[RegressionPrediction]: ...

    # TODO: add filter support
    def predict(
        self,
        value: str | list[str],
        expected_scores: float | list[float] | None = None,
        tags: set[str] | None = None,
        save_telemetry: TelemetryMode = "on",
        prompt: str | None = None,
        use_lookup_cache: bool = True,
    ) -> RegressionPrediction | list[RegressionPrediction]:
        """
        Make predictions using the regression model.

        Params:
            value: Input text(s) to predict scores for
            expected_scores: Expected score(s) for telemetry tracking
            tags: Tags to associate with the prediction(s)
            save_telemetry: Whether to save telemetry for the prediction(s), defaults to `True`,
                which will save telemetry asynchronously unless the `ORCA_SAVE_TELEMETRY_SYNCHRONOUSLY`
                environment variable is set to `"1"`. You can also pass `"sync"` or `"async"` to
                explicitly set the save mode.
            prompt: Optional prompt for instruction-tuned embedding models

        Returns:
            Single RegressionPrediction or list of RegressionPrediction objects

        Raises:
            ValueError: If expected_scores length doesn't match value length for batch predictions
        """
        telemetry_on, telemetry_sync = _get_telemetry_config(save_telemetry)
        response = orca_api.POST(
            "/gpu/regression_model/{name_or_id}/prediction",
            params={"name_or_id": self.id},
            json={
                "input_values": value if isinstance(value, list) else [value],
                "memoryset_override_name_or_id": self._memoryset_override_id,
                "expected_scores": (
                    expected_scores
                    if isinstance(expected_scores, list)
                    else [expected_scores] if expected_scores is not None else None
                ),
                "tags": list(tags or set()),
                "save_telemetry": telemetry_on,
                "save_telemetry_synchronously": telemetry_sync,
                "prompt": prompt,
                "use_lookup_cache": use_lookup_cache,
            },
        )

        if telemetry_on and any(p["prediction_id"] is None for p in response):
            raise RuntimeError("Failed to save prediction to database.")

        predictions = [
            RegressionPrediction(
                prediction_id=prediction["prediction_id"],
                label=None,
                label_name=None,
                score=prediction["score"],
                confidence=prediction["confidence"],
                anomaly_score=prediction["anomaly_score"],
                memoryset=self.memoryset,
                model=self,
                logits=None,
                input_value=input_value,
            )
            for prediction, input_value in zip(response, value if isinstance(value, list) else [value])
        ]
        self._last_prediction_was_batch = isinstance(value, list)
        self._last_prediction = predictions[-1]
        return predictions if isinstance(value, list) else predictions[0]

    def predictions(
        self,
        limit: int = 100,
        offset: int = 0,
        tag: str | None = None,
        sort: list[tuple[Literal["anomaly_score", "confidence", "timestamp"], Literal["asc", "desc"]]] = [],
    ) -> list[RegressionPrediction]:
        """
        Get a list of predictions made by this model

        Params:
            limit: Optional maximum number of predictions to return
            offset: Optional offset of the first prediction to return
            tag: Optional tag to filter predictions by
            sort: Optional list of columns and directions to sort the predictions by.
                Predictions can be sorted by `created_at`, `confidence`, `anomaly_score`, or `score`.

        Returns:
            List of score predictions

        Examples:
            Get the last 3 predictions:
            >>> predictions = model.predictions(limit=3, sort=[("created_at", "desc")])
            [
                RegressionPrediction({score: 4.5, confidence: 0.95, anomaly_score: 0.1, input_value: 'Great service'}),
                RegressionPrediction({score: 2.0, confidence: 0.90, anomaly_score: 0.1, input_value: 'Poor experience'}),
                RegressionPrediction({score: 3.5, confidence: 0.85, anomaly_score: 0.1, input_value: 'Average'}),
            ]

            Get second most confident prediction:
            >>> predictions = model.predictions(sort=[("confidence", "desc")], offset=1, limit=1)
            [RegressionPrediction({score: 4.2, confidence: 0.90, anomaly_score: 0.1, input_value: 'Good service'})]
        """
        predictions = orca_api.POST(
            "/telemetry/prediction",
            json={
                "model_id": self.id,
                "limit": limit,
                "offset": offset,
                "sort": [list(sort_item) for sort_item in sort],
                "tag": tag,
            },
        )
        return [
            RegressionPrediction(
                prediction_id=prediction["prediction_id"],
                label=None,
                label_name=None,
                score=prediction["score"],
                confidence=prediction["confidence"],
                anomaly_score=prediction["anomaly_score"],
                memoryset=self.memoryset,
                model=self,
                telemetry=prediction,
                logits=None,
                input_value=None,
            )
            for prediction in predictions
            if "score" in prediction
        ]

    def _evaluate_datasource(
        self,
        datasource: Datasource,
        value_column: str,
        score_column: str,
        record_predictions: bool,
        tags: set[str] | None,
        background: bool = False,
    ) -> RegressionMetrics | Job[RegressionMetrics]:
        response = orca_api.POST(
            "/regression_model/{model_name_or_id}/evaluation",
            params={"model_name_or_id": self.id},
            json={
                "datasource_name_or_id": datasource.id,
                "datasource_score_column": score_column,
                "datasource_value_column": value_column,
                "memoryset_override_name_or_id": self._memoryset_override_id,
                "record_telemetry": record_predictions,
                "telemetry_tags": list(tags) if tags else None,
            },
        )

        def get_value():
            res = orca_api.GET(
                "/regression_model/{model_name_or_id}/evaluation/{task_id}",
                params={"model_name_or_id": self.id, "task_id": response["task_id"]},
            )
            assert res["result"] is not None
            return RegressionMetrics(**res["result"])

        job = Job(response["task_id"], get_value)
        return job if background else job.result()

    def _evaluate_dataset(
        self,
        dataset: Dataset,
        value_column: str,
        score_column: str,
        record_predictions: bool,
        tags: set[str],
        batch_size: int,
        prompt: str | None = None,
    ) -> RegressionMetrics:
        predictions = [
            prediction
            for i in range(0, len(dataset), batch_size)
            for prediction in self.predict(
                dataset[i : i + batch_size][value_column],
                expected_scores=dataset[i : i + batch_size][score_column],
                tags=tags,
                save_telemetry="sync" if record_predictions else "off",
                prompt=prompt,
            )
        ]

        return calculate_regression_metrics(
            expected_scores=dataset[score_column],
            predicted_scores=[p.score for p in predictions],
            anomaly_scores=[p.anomaly_score for p in predictions],
        )

    @overload
    def evaluate(
        self,
        data: Datasource | Dataset,
        *,
        value_column: str = "value",
        score_column: str = "score",
        record_predictions: bool = False,
        tags: set[str] = {"evaluation"},
        batch_size: int = 100,
        prompt: str | None = None,
        background: Literal[True],
    ) -> Job[RegressionMetrics]:
        pass

    @overload
    def evaluate(
        self,
        data: Datasource | Dataset,
        *,
        value_column: str = "value",
        score_column: str = "score",
        record_predictions: bool = False,
        tags: set[str] = {"evaluation"},
        batch_size: int = 100,
        prompt: str | None = None,
        background: Literal[False] = False,
    ) -> RegressionMetrics:
        pass

    def evaluate(
        self,
        data: Datasource | Dataset,
        *,
        value_column: str = "value",
        score_column: str = "score",
        record_predictions: bool = False,
        tags: set[str] = {"evaluation"},
        batch_size: int = 100,
        prompt: str | None = None,
        background: bool = False,
    ) -> RegressionMetrics | Job[RegressionMetrics]:
        """
        Evaluate the regression model on a given dataset or datasource

        Params:
            data: Dataset or Datasource to evaluate the model on
            value_column: Name of the column that contains the input values to the model
            score_column: Name of the column containing the expected scores
            record_predictions: Whether to record [`RegressionPrediction`][orca_sdk.telemetry.RegressionPrediction]s for analysis
            tags: Optional tags to add to the recorded [`RegressionPrediction`][orca_sdk.telemetry.RegressionPrediction]s
            batch_size: Batch size for processing Dataset inputs (only used when input is a Dataset)
            prompt: Optional prompt for instruction-tuned embedding models
            background: Whether to run the operation in the background and return a job handle

        Returns:
            RegressionMetrics containing metrics including MAE, MSE, RMSE, R2, and anomaly score statistics

        Examples:
            >>> model.evaluate(datasource, value_column="text", score_column="rating")
            RegressionMetrics({
                mae: 0.2500,
                rmse: 0.3536,
                r2: 0.8500,
                anomaly_score: 0.3500 ± 0.0500,
            })

            >>> # Using with an instruction-tuned embedding model
            >>> model.evaluate(dataset,prompt="Represent this review for rating prediction:")
            RegressionMetrics({
            mae: 0.2000,
            rmse: 0.3000,
            r2: 0.9000,
            anomaly_score: 0.3000 ± 0.0400})
        """
        if isinstance(data, Datasource):
            return self._evaluate_datasource(
                datasource=data,
                value_column=value_column,
                score_column=score_column,
                record_predictions=record_predictions,
                tags=tags,
                background=background,
            )
        elif isinstance(data, Dataset):
            return self._evaluate_dataset(
                dataset=data,
                value_column=value_column,
                score_column=score_column,
                record_predictions=record_predictions,
                tags=tags,
                batch_size=batch_size,
                prompt=prompt,
            )
        else:
            raise ValueError(f"Invalid data type: {type(data)}")

    @contextmanager
    def use_memoryset(self, memoryset_override: ScoredMemoryset) -> Generator[None, None, None]:
        """
        Temporarily override the memoryset used by the model for predictions

        Params:
            memoryset_override: Memoryset to override the default memoryset with

        Examples:
            >>> with model.use_memoryset(ScoredMemoryset.open("my_other_memoryset")):
            ...     predictions = model.predict("Rate your experience")
        """
        self._memoryset_override_id = memoryset_override.id
        yield
        self._memoryset_override_id = None

    @overload
    def record_feedback(self, feedback: dict[str, Any]) -> None:
        pass

    @overload
    def record_feedback(self, feedback: Iterable[dict[str, Any]]) -> None:
        pass

    def record_feedback(self, feedback: Iterable[dict[str, Any]] | dict[str, Any]):
        """
        Record feedback for a list of predictions.

        We support recording feedback in several categories for each prediction. A
        [`FeedbackCategory`][orca_sdk.telemetry.FeedbackCategory] is created automatically,
        the first time feedback with a new name is recorded. Categories are global across models.
        The value type of the category is inferred from the first recorded value. Subsequent
        feedback for the same category must be of the same type.

        Params:
            feedback: Feedback to record, this should be dictionaries with the following keys:

                - `category`: Name of the category under which to record the feedback.
                - `value`: Feedback value to record, should be `True` for positive feedback and
                    `False` for negative feedback or a [`float`][float] between `-1.0` and `+1.0`
                    where negative values indicate negative feedback and positive values indicate
                    positive feedback.
                - `comment`: Optional comment to record with the feedback.

        Examples:
            Record whether predictions were accurate:
            >>> model.record_feedback({
            ...     "prediction": p.prediction_id,
            ...     "category": "accurate",
            ...     "value": abs(p.score - p.expected_score) < 0.5,
            ... } for p in predictions)

            Record star rating as normalized continuous score between `-1.0` and `+1.0`:
            >>> model.record_feedback({
            ...     "prediction": "123e4567-e89b-12d3-a456-426614174000",
            ...     "category": "rating",
            ...     "value": -0.5,
            ...     "comment": "2 stars"
            ... })

        Raises:
            ValueError: If the value does not match previous value types for the category, or is a
                [`float`][float] that is not between `-1.0` and `+1.0`.
        """
        orca_api.PUT(
            "/telemetry/prediction/feedback",
            json=[
                _parse_feedback(f) for f in (cast(list[dict], [feedback]) if isinstance(feedback, dict) else feedback)
            ],
        )
