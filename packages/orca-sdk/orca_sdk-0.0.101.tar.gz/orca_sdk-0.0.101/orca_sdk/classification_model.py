from __future__ import annotations

import logging
from contextlib import contextmanager
from datetime import datetime
from typing import Any, Generator, Iterable, Literal, cast, overload

from datasets import Dataset

from ._shared.metrics import ClassificationMetrics, calculate_classification_metrics
from ._utils.common import UNSET, CreateMode, DropMode
from .client import (
    BootstrapClassificationModelMeta,
    BootstrapClassificationModelResult,
    ClassificationModelMetadata,
    PredictiveModelUpdate,
    RACHeadType,
    orca_api,
)
from .datasource import Datasource
from .job import Job
from .memoryset import (
    FilterItem,
    FilterItemTuple,
    LabeledMemoryset,
    _is_metric_column,
    _parse_filter_item_from_tuple,
)
from .telemetry import (
    ClassificationPrediction,
    TelemetryMode,
    _get_telemetry_config,
    _parse_feedback,
)


class BootstrappedClassificationModel:

    datasource: Datasource | None
    memoryset: LabeledMemoryset | None
    classification_model: ClassificationModel | None
    agent_output: BootstrapClassificationModelResult | None

    def __init__(self, metadata: BootstrapClassificationModelMeta):
        self.datasource = Datasource.open(metadata["datasource_meta"]["id"])
        self.memoryset = LabeledMemoryset.open(metadata["memoryset_meta"]["id"])
        self.classification_model = ClassificationModel.open(metadata["model_meta"]["id"])
        self.agent_output = metadata["agent_output"]

    def __repr__(self):
        return (
            "BootstrappedClassificationModel({\n"
            f"    datasource: {self.datasource},\n"
            f"    memoryset: {self.memoryset},\n"
            f"    classification_model: {self.classification_model},\n"
            f"    agent_output: {self.agent_output},\n"
            "})"
        )


class ClassificationModel:
    """
    A handle to a classification model in OrcaCloud

    Attributes:
        id: Unique identifier for the model
        name: Unique name of the model
        description: Optional description of the model
        memoryset: Memoryset that the model uses
        head_type: Classification head type of the model
        num_classes: Number of distinct classes the model can predict
        memory_lookup_count: Number of memories the model uses for each prediction
        weigh_memories: If using a KNN head, whether the model weighs memories by their lookup score
        min_memory_weight: If using a KNN head, minimum lookup score memories have to be over to not be ignored
        locked: Whether the model is locked to prevent accidental deletion
        created_at: When the model was created
    """

    id: str
    name: str
    description: str | None
    memoryset: LabeledMemoryset
    head_type: RACHeadType
    num_classes: int
    memory_lookup_count: int
    weigh_memories: bool | None
    min_memory_weight: float | None
    version: int
    locked: bool
    created_at: datetime

    def __init__(self, metadata: ClassificationModelMetadata):
        # for internal use only, do not document
        self.id = metadata["id"]
        self.name = metadata["name"]
        self.description = metadata["description"]
        self.memoryset = LabeledMemoryset.open(metadata["memoryset_id"])
        self.head_type = metadata["head_type"]
        self.num_classes = metadata["num_classes"]
        self.memory_lookup_count = metadata["memory_lookup_count"]
        self.weigh_memories = metadata["weigh_memories"]
        self.min_memory_weight = metadata["min_memory_weight"]
        self.version = metadata["version"]
        self.locked = metadata["locked"]
        self.created_at = datetime.fromisoformat(metadata["created_at"])

        self._memoryset_override_id: str | None = None
        self._last_prediction: ClassificationPrediction | None = None
        self._last_prediction_was_batch: bool = False

    def __eq__(self, other) -> bool:
        return isinstance(other, ClassificationModel) and self.id == other.id

    def __repr__(self):
        return (
            "ClassificationModel({\n"
            f"    name: '{self.name}',\n"
            f"    head_type: {self.head_type},\n"
            f"    num_classes: {self.num_classes},\n"
            f"    memory_lookup_count: {self.memory_lookup_count},\n"
            f"    memoryset: LabeledMemoryset.open('{self.memoryset.name}'),\n"
            "})"
        )

    @property
    def last_prediction(self) -> ClassificationPrediction:
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
        memoryset: LabeledMemoryset,
        head_type: RACHeadType = "KNN",
        *,
        description: str | None = None,
        num_classes: int | None = None,
        memory_lookup_count: int | None = None,
        weigh_memories: bool = True,
        min_memory_weight: float | None = None,
        if_exists: CreateMode = "error",
    ) -> ClassificationModel:
        """
        Create a new classification model

        Params:
            name: Name for the new model (must be unique)
            memoryset: Memoryset to attach the model to
            head_type: Type of model head to use
            num_classes: Number of classes this model can predict, will be inferred from memoryset if not specified
            memory_lookup_count: Number of memories to lookup for each prediction,
                by default the system uses a simple heuristic to choose a number of memories that works well in most cases
            weigh_memories: If using a KNN head, whether the model weighs memories by their lookup score
            min_memory_weight: If using a KNN head, minimum lookup score memories have to be over to not be ignored
            if_exists: What to do if a model with the same name already exists, defaults to
                `"error"`. Other option is `"open"` to open the existing model.
            description: Optional description for the model, this will be used in agentic flows,
                so make sure it is concise and describes the purpose of your model.

        Returns:
            Handle to the new model in the OrcaCloud

        Raises:
            ValueError: If the model already exists and if_exists is `"error"` or if it is
                `"open"` and the existing model has different attributes.

        Examples:
            Create a new model using default options:
            >>> model = ClassificationModel.create(
            ...    "my_model",
            ...    LabeledMemoryset.open("my_memoryset"),
            ... )

            Create a new model with non-default model head and options:
            >>> model = ClassificationModel.create(
            ...     name="my_model",
            ...     memoryset=LabeledMemoryset.open("my_memoryset"),
            ...     head_type=RACHeadType.MMOE,
            ...     num_classes=5,
            ...     memory_lookup_count=20,
            ... )
        """
        if cls.exists(name):
            if if_exists == "error":
                raise ValueError(f"Model with name {name} already exists")
            elif if_exists == "open":
                existing = cls.open(name)
                for attribute in {"head_type", "memory_lookup_count", "num_classes", "min_memory_weight"}:
                    local_attribute = locals()[attribute]
                    existing_attribute = getattr(existing, attribute)
                    if local_attribute is not None and local_attribute != existing_attribute:
                        raise ValueError(f"Model with name {name} already exists with different {attribute}")

                # special case for memoryset
                if existing.memoryset.id != memoryset.id:
                    raise ValueError(f"Model with name {name} already exists with different memoryset")

                return existing

        metadata = orca_api.POST(
            "/classification_model",
            json={
                "name": name,
                "memoryset_name_or_id": memoryset.id,
                "head_type": head_type,
                "memory_lookup_count": memory_lookup_count,
                "num_classes": num_classes,
                "weigh_memories": weigh_memories,
                "min_memory_weight": min_memory_weight,
                "description": description,
            },
        )
        return cls(metadata)

    @classmethod
    def open(cls, name: str) -> ClassificationModel:
        """
        Get a handle to a classification model in the OrcaCloud

        Params:
            name: Name or unique identifier of the classification model

        Returns:
            Handle to the existing classification model in the OrcaCloud

        Raises:
            LookupError: If the classification model does not exist
        """
        return cls(orca_api.GET("/classification_model/{name_or_id}", params={"name_or_id": name}))

    @classmethod
    def exists(cls, name_or_id: str) -> bool:
        """
        Check if a classification model exists in the OrcaCloud

        Params:
            name_or_id: Name or id of the classification model

        Returns:
            `True` if the classification model exists, `False` otherwise
        """
        try:
            cls.open(name_or_id)
            return True
        except LookupError:
            return False

    @classmethod
    def all(cls) -> list[ClassificationModel]:
        """
        Get a list of handles to all classification models in the OrcaCloud

        Returns:
            List of handles to all classification models in the OrcaCloud
        """
        return [cls(metadata) for metadata in orca_api.GET("/classification_model")]

    @classmethod
    def drop(cls, name_or_id: str, if_not_exists: DropMode = "error"):
        """
        Delete a classification model from the OrcaCloud

        Warning:
            This will delete the model and all associated data, including predictions, evaluations, and feedback.

        Params:
            name_or_id: Name or id of the classification model
            if_not_exists: What to do if the classification model does not exist, defaults to `"error"`.
                Other option is `"ignore"` to do nothing if the classification model does not exist.

        Raises:
            LookupError: If the classification model does not exist and if_not_exists is `"error"`
        """
        try:
            orca_api.DELETE("/classification_model/{name_or_id}", params={"name_or_id": name_or_id})
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
        orca_api.PATCH("/classification_model/{name_or_id}", params={"name_or_id": self.id}, json=update)
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
        value: list[str],
        expected_labels: list[int] | None = None,
        filters: list[FilterItemTuple] = [],
        tags: set[str] | None = None,
        save_telemetry: TelemetryMode = "on",
        prompt: str | None = None,
        use_lookup_cache: bool = True,
    ) -> list[ClassificationPrediction]:
        pass

    @overload
    def predict(
        self,
        value: str,
        expected_labels: int | None = None,
        filters: list[FilterItemTuple] = [],
        tags: set[str] | None = None,
        save_telemetry: TelemetryMode = "on",
        prompt: str | None = None,
        use_lookup_cache: bool = True,
    ) -> ClassificationPrediction:
        pass

    def predict(
        self,
        value: list[str] | str,
        expected_labels: list[int] | list[str] | int | str | None = None,
        filters: list[FilterItemTuple] = [],
        tags: set[str] | None = None,
        save_telemetry: TelemetryMode = "on",
        prompt: str | None = None,
        use_lookup_cache: bool = True,
    ) -> list[ClassificationPrediction] | ClassificationPrediction:
        """
        Predict label(s) for the given input value(s) grounded in similar memories

        Params:
            value: Value(s) to get predict the labels of
            expected_labels: Expected label(s) for the given input to record for model evaluation
            filters: Optional filters to apply during memory lookup
            tags: Tags to add to the prediction(s)
            save_telemetry: Whether to save telemetry for the prediction(s). One of
                * `"off"`: Do not save telemetry
                * `"on"`: Save telemetry asynchronously unless the `ORCA_SAVE_TELEMETRY_SYNCHRONOUSLY`
                  environment variable is set.
                * `"sync"`: Save telemetry synchronously
                * `"async"`: Save telemetry asynchronously
            prompt: Optional prompt to use for instruction-tuned embedding models

        Returns:
            Label prediction or list of label predictions

        Examples:
            Predict the label for a single value:
            >>> prediction = model.predict("I am happy", tags={"test"})
            ClassificationPrediction({label: <positive: 1>, confidence: 0.95, anomaly_score: 0.1, input_value: 'I am happy' })

            Predict the labels for a list of values:
            >>> predictions = model.predict(["I am happy", "I am sad"], expected_labels=[1, 0])
            [
                ClassificationPrediction({label: <positive: 1>, confidence: 0.95, anomaly_score: 0.1, input_value: 'I am happy'}),
                ClassificationPrediction({label: <negative: 0>, confidence: 0.05, anomaly_score: 0.1, input_value: 'I am sad'}),
            ]

            Using a prompt with an instruction-tuned embedding model:
            >>> prediction = model.predict("I am happy", prompt="Represent this text for sentiment classification:")
            ClassificationPrediction({label: <positive: 1>, confidence: 0.95, anomaly_score: 0.1, input_value: 'I am happy' })
        """

        parsed_filters = [
            _parse_filter_item_from_tuple(filter) if isinstance(filter, tuple) else filter for filter in filters
        ]

        if any(_is_metric_column(filter[0]) for filter in filters):
            raise ValueError(f"Cannot filter on {filters} - telemetry filters are not supported for predictions")

        if isinstance(expected_labels, int):
            expected_labels = [expected_labels]
        elif isinstance(expected_labels, str):
            expected_labels = [self.memoryset.label_names.index(expected_labels)]
        elif isinstance(expected_labels, list):
            expected_labels = [
                self.memoryset.label_names.index(label) if isinstance(label, str) else label
                for label in expected_labels
            ]

        telemetry_on, telemetry_sync = _get_telemetry_config(save_telemetry)
        response = orca_api.POST(
            "/gpu/classification_model/{name_or_id}/prediction",
            params={"name_or_id": self.id},
            json={
                "input_values": value if isinstance(value, list) else [value],
                "memoryset_override_name_or_id": self._memoryset_override_id,
                "expected_labels": expected_labels,
                "tags": list(tags or set()),
                "save_telemetry": telemetry_on,
                "save_telemetry_synchronously": telemetry_sync,
                "filters": cast(list[FilterItem], parsed_filters),
                "prompt": prompt,
                "use_lookup_cache": use_lookup_cache,
            },
        )

        if telemetry_on and any(p["prediction_id"] is None for p in response):
            raise RuntimeError("Failed to save prediction to database.")

        predictions = [
            ClassificationPrediction(
                prediction_id=prediction["prediction_id"],
                label=prediction["label"],
                label_name=prediction["label_name"],
                score=None,
                confidence=prediction["confidence"],
                anomaly_score=prediction["anomaly_score"],
                memoryset=self.memoryset,
                model=self,
                logits=prediction["logits"],
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
        expected_label_match: bool | None = None,
    ) -> list[ClassificationPrediction]:
        """
        Get a list of predictions made by this model

        Params:
            limit: Optional maximum number of predictions to return
            offset: Optional offset of the first prediction to return
            tag: Optional tag to filter predictions by
            sort: Optional list of columns and directions to sort the predictions by.
                Predictions can be sorted by `timestamp` or `confidence`.
            expected_label_match: Optional filter to only include predictions where the expected
                label does (`True`) or doesn't (`False`) match the predicted label

        Returns:
            List of label predictions

        Examples:
            Get the last 3 predictions:
            >>> predictions = model.predictions(limit=3, sort=[("timestamp", "desc")])
            [
                ClassificationPrediction({label: <positive: 1>, confidence: 0.95, anomaly_score: 0.1, input_value: 'I am happy'}),
                ClassificationPrediction({label: <negative: 0>, confidence: 0.05, anomaly_score: 0.1, input_value: 'I am sad'}),
                ClassificationPrediction({label: <positive: 1>, confidence: 0.90, anomaly_score: 0.1, input_value: 'I am ecstatic'}),
            ]


            Get second most confident prediction:
            >>> predictions = model.predictions(sort=[("confidence", "desc")], offset=1, limit=1)
            [ClassificationPrediction({label: <positive: 1>, confidence: 0.90, anomaly_score: 0.1, input_value: 'I am having a good day'})]

            Get predictions where the expected label doesn't match the predicted label:
            >>> predictions = model.predictions(expected_label_match=False)
            [ClassificationPrediction({label: <positive: 1>, confidence: 0.95, anomaly_score: 0.1, input_value: 'I am happy', expected_label: 0})]
        """
        predictions = orca_api.POST(
            "/telemetry/prediction",
            json={
                "model_id": self.id,
                "limit": limit,
                "offset": offset,
                "sort": [list(sort_item) for sort_item in sort],
                "tag": tag,
                "expected_label_match": expected_label_match,
            },
        )
        return [
            ClassificationPrediction(
                prediction_id=prediction["prediction_id"],
                label=prediction["label"],
                label_name=prediction["label_name"],
                score=None,
                confidence=prediction["confidence"],
                anomaly_score=prediction["anomaly_score"],
                memoryset=self.memoryset,
                model=self,
                telemetry=prediction,
            )
            for prediction in predictions
            if "label" in prediction
        ]

    def _evaluate_datasource(
        self,
        datasource: Datasource,
        value_column: str,
        label_column: str,
        record_predictions: bool,
        tags: set[str] | None,
        background: bool = False,
    ) -> ClassificationMetrics | Job[ClassificationMetrics]:
        response = orca_api.POST(
            "/classification_model/{model_name_or_id}/evaluation",
            params={"model_name_or_id": self.id},
            json={
                "datasource_name_or_id": datasource.id,
                "datasource_label_column": label_column,
                "datasource_value_column": value_column,
                "memoryset_override_name_or_id": self._memoryset_override_id,
                "record_telemetry": record_predictions,
                "telemetry_tags": list(tags) if tags else None,
            },
        )

        def get_value():
            res = orca_api.GET(
                "/classification_model/{model_name_or_id}/evaluation/{task_id}",
                params={"model_name_or_id": self.id, "task_id": response["task_id"]},
            )
            assert res["result"] is not None
            return ClassificationMetrics(**res["result"])

        job = Job(response["task_id"], get_value)
        return job if background else job.result()

    def _evaluate_dataset(
        self,
        dataset: Dataset,
        value_column: str,
        label_column: str,
        record_predictions: bool,
        tags: set[str],
        batch_size: int,
    ) -> ClassificationMetrics:
        predictions = [
            prediction
            for i in range(0, len(dataset), batch_size)
            for prediction in self.predict(
                dataset[i : i + batch_size][value_column],
                expected_labels=dataset[i : i + batch_size][label_column],
                tags=tags,
                save_telemetry="sync" if record_predictions else "off",
            )
        ]

        return calculate_classification_metrics(
            expected_labels=dataset[label_column],
            logits=[p.logits for p in predictions],
            anomaly_scores=[p.anomaly_score for p in predictions],
            include_curves=True,
        )

    @overload
    def evaluate(
        self,
        data: Datasource | Dataset,
        *,
        value_column: str = "value",
        label_column: str = "label",
        record_predictions: bool = False,
        tags: set[str] = {"evaluation"},
        batch_size: int = 100,
        background: Literal[True],
    ) -> Job[ClassificationMetrics]:
        pass

    @overload
    def evaluate(
        self,
        data: Datasource | Dataset,
        *,
        value_column: str = "value",
        label_column: str = "label",
        record_predictions: bool = False,
        tags: set[str] = {"evaluation"},
        batch_size: int = 100,
        background: Literal[False] = False,
    ) -> ClassificationMetrics:
        pass

    def evaluate(
        self,
        data: Datasource | Dataset,
        *,
        value_column: str = "value",
        label_column: str = "label",
        record_predictions: bool = False,
        tags: set[str] = {"evaluation"},
        batch_size: int = 100,
        background: bool = False,
    ) -> ClassificationMetrics | Job[ClassificationMetrics]:
        """
        Evaluate the classification model on a given dataset or datasource

        Params:
            data: Dataset or Datasource to evaluate the model on
            value_column: Name of the column that contains the input values to the model
            label_column: Name of the column containing the expected labels
            record_predictions: Whether to record [`ClassificationPrediction`][orca_sdk.telemetry.ClassificationPrediction]s for analysis
            tags: Optional tags to add to the recorded [`ClassificationPrediction`][orca_sdk.telemetry.ClassificationPrediction]s
            batch_size: Batch size for processing Dataset inputs (only used when input is a Dataset)
            background: Whether to run the operation in the background and return a job handle

        Returns:
            EvaluationResult containing metrics including accuracy, F1 score, ROC AUC, PR AUC, and anomaly score statistics

        Examples:
            >>> model.evaluate(datasource, value_column="text", label_column="airline_sentiment")
            ClassificationMetrics({
                accuracy: 0.8500,
                f1_score: 0.8500,
                roc_auc: 0.8500,
                pr_auc: 0.8500,
                anomaly_score: 0.3500 ± 0.0500,
            })
        """
        if isinstance(data, Datasource):
            return self._evaluate_datasource(
                datasource=data,
                value_column=value_column,
                label_column=label_column,
                record_predictions=record_predictions,
                tags=tags,
                background=background,
            )
        elif isinstance(data, Dataset):
            return self._evaluate_dataset(
                dataset=data,
                value_column=value_column,
                label_column=label_column,
                record_predictions=record_predictions,
                tags=tags,
                batch_size=batch_size,
            )
        else:
            raise ValueError(f"Invalid data type: {type(data)}")

    def finetune(self, datasource: Datasource):
        #  do not document until implemented
        raise NotImplementedError("Finetuning is not supported yet")

    @contextmanager
    def use_memoryset(self, memoryset_override: LabeledMemoryset) -> Generator[None, None, None]:
        """
        Temporarily override the memoryset used by the model for predictions

        Params:
            memoryset_override: Memoryset to override the default memoryset with

        Examples:
            >>> with model.use_memoryset(LabeledMemoryset.open("my_other_memoryset")):
            ...     predictions = model.predict("I am happy")
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
            Record whether predictions were correct or incorrect:
            >>> model.record_feedback({
            ...     "prediction": p.prediction_id,
            ...     "category": "correct",
            ...     "value": p.label == p.expected_label,
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

    @staticmethod
    def bootstrap_model(
        model_description: str,
        label_names: list[str],
        initial_examples: list[tuple[str, str]],
        num_examples_per_label: int,
        background: bool = False,
    ) -> Job[BootstrappedClassificationModel] | BootstrappedClassificationModel:
        response = orca_api.POST(
            "/agents/bootstrap_classification_model",
            json={
                "model_description": model_description,
                "label_names": label_names,
                "initial_examples": [{"text": text, "label_name": label_name} for text, label_name in initial_examples],
                "num_examples_per_label": num_examples_per_label,
            },
        )

        def get_result() -> BootstrappedClassificationModel:
            res = orca_api.GET(
                "/agents/bootstrap_classification_model/{task_id}", params={"task_id": response["task_id"]}
            )
            assert res["result"] is not None
            return BootstrappedClassificationModel(res["result"])

        job = Job(response["task_id"], get_result)
        return job if background else job.result()
