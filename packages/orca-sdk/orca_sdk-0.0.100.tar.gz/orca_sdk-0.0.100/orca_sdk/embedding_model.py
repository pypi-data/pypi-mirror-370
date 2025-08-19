from __future__ import annotations

from abc import abstractmethod
from datetime import datetime
from typing import TYPE_CHECKING, Literal, Sequence, cast, get_args, overload

from ._shared.metrics import ClassificationMetrics, RegressionMetrics
from ._utils.common import UNSET, CreateMode, DropMode
from .client import (
    EmbeddingEvaluationRequest,
    EmbeddingFinetuningMethod,
    EmbedRequest,
    FinetunedEmbeddingModelMetadata,
    FinetuneEmbeddingModelRequest,
    PretrainedEmbeddingModelMetadata,
    PretrainedEmbeddingModelName,
    orca_api,
)
from .datasource import Datasource
from .job import Job, Status

if TYPE_CHECKING:
    from .memoryset import LabeledMemoryset


class _EmbeddingModel:
    embedding_dim: int
    max_seq_length: int
    uses_context: bool
    supports_instructions: bool

    def __init__(
        self, *, name: str, embedding_dim: int, max_seq_length: int, uses_context: bool, supports_instructions: bool
    ):
        self.embedding_dim = embedding_dim
        self.max_seq_length = max_seq_length
        self.uses_context = uses_context
        self.supports_instructions = supports_instructions

    @classmethod
    @abstractmethod
    def all(cls) -> Sequence[_EmbeddingModel]:
        pass

    def _get_instruction_error_message(self) -> str:
        """Get error message for instruction not supported"""
        if isinstance(self, FinetunedEmbeddingModel):
            return f"Model {self.name} does not support instructions. Instruction-following is only supported by models based on instruction-supporting models."
        elif isinstance(self, PretrainedEmbeddingModel):
            return f"Model {self.name} does not support instructions. Instruction-following is only supported by instruction-supporting models."
        else:
            raise ValueError("Invalid embedding model")

    @overload
    def embed(self, value: str, max_seq_length: int | None = None, prompt: str | None = None) -> list[float]:
        pass

    @overload
    def embed(
        self, value: list[str], max_seq_length: int | None = None, prompt: str | None = None
    ) -> list[list[float]]:
        pass

    def embed(
        self, value: str | list[str], max_seq_length: int | None = None, prompt: str | None = None
    ) -> list[float] | list[list[float]]:
        """
        Generate embeddings for a value or list of values

        Params:
            value: The value or list of values to embed
            max_seq_length: The maximum sequence length to truncate the input to
            prompt: Optional prompt for prompt-following embedding models.

        Returns:
            A matrix of floats representing the embedding for each value if the input is a list of
                values, or a list of floats representing the embedding for the single value if the
                input is a single value
        """
        payload: EmbedRequest = {
            "values": value if isinstance(value, list) else [value],
            "max_seq_length": max_seq_length,
            "prompt": prompt,
        }
        if isinstance(self, PretrainedEmbeddingModel):
            embeddings = orca_api.POST(
                "/gpu/pretrained_embedding_model/{model_name}/embedding",
                params={"model_name": cast(PretrainedEmbeddingModelName, self.name)},
                json=payload,
                timeout=30,  # may be slow in case of cold start
            )
        elif isinstance(self, FinetunedEmbeddingModel):
            embeddings = orca_api.POST(
                "/gpu/finetuned_embedding_model/{name_or_id}/embedding",
                params={"name_or_id": self.id},
                json=payload,
                timeout=30,  # may be slow in case of cold start
            )
        else:
            raise ValueError("Invalid embedding model")
        return embeddings if isinstance(value, list) else embeddings[0]

    @overload
    def evaluate(
        self,
        datasource: Datasource,
        *,
        value_column: str = "value",
        label_column: str,
        score_column: None = None,
        eval_datasource: Datasource | None = None,
        subsample: int | None = None,
        neighbor_count: int = 5,
        batch_size: int = 32,
        weigh_memories: bool = True,
        background: Literal[True],
    ) -> Job[ClassificationMetrics]:
        pass

    @overload
    def evaluate(
        self,
        datasource: Datasource,
        *,
        value_column: str = "value",
        label_column: str,
        score_column: None = None,
        eval_datasource: Datasource | None = None,
        subsample: int | None = None,
        neighbor_count: int = 5,
        batch_size: int = 32,
        weigh_memories: bool = True,
        background: Literal[False] = False,
    ) -> ClassificationMetrics:
        pass

    @overload
    def evaluate(
        self,
        datasource: Datasource,
        *,
        value_column: str = "value",
        label_column: None = None,
        score_column: str,
        eval_datasource: Datasource | None = None,
        subsample: int | None = None,
        neighbor_count: int = 5,
        batch_size: int = 32,
        weigh_memories: bool = True,
        background: Literal[True],
    ) -> Job[RegressionMetrics]:
        pass

    @overload
    def evaluate(
        self,
        datasource: Datasource,
        *,
        value_column: str = "value",
        label_column: None = None,
        score_column: str,
        eval_datasource: Datasource | None = None,
        subsample: int | None = None,
        neighbor_count: int = 5,
        batch_size: int = 32,
        weigh_memories: bool = True,
        background: Literal[False] = False,
    ) -> RegressionMetrics:
        pass

    def evaluate(
        self,
        datasource: Datasource,
        *,
        value_column: str = "value",
        label_column: str | None = None,
        score_column: str | None = None,
        eval_datasource: Datasource | None = None,
        subsample: int | None = None,
        neighbor_count: int = 5,
        batch_size: int = 32,
        weigh_memories: bool = True,
        background: bool = False,
    ) -> (
        ClassificationMetrics
        | RegressionMetrics
        | Job[ClassificationMetrics]
        | Job[RegressionMetrics]
        | Job[ClassificationMetrics | RegressionMetrics]
    ):
        """
        Evaluate the finetuned embedding model
        """
        payload: EmbeddingEvaluationRequest = {
            "datasource_name_or_id": datasource.id,
            "datasource_label_column": label_column,
            "datasource_value_column": value_column,
            "datasource_score_column": score_column,
            "eval_datasource_name_or_id": eval_datasource.id if eval_datasource is not None else None,
            "subsample": subsample,
            "neighbor_count": neighbor_count,
            "batch_size": batch_size,
            "weigh_memories": weigh_memories,
        }
        if isinstance(self, PretrainedEmbeddingModel):
            response = orca_api.POST(
                "/pretrained_embedding_model/{model_name}/evaluation",
                params={"model_name": self.name},
                json=payload,
            )
        elif isinstance(self, FinetunedEmbeddingModel):
            response = orca_api.POST(
                "/finetuned_embedding_model/{name_or_id}/evaluation",
                params={"name_or_id": self.id},
                json=payload,
            )
        else:
            raise ValueError("Invalid embedding model")

        def get_result(task_id: str) -> ClassificationMetrics | RegressionMetrics:
            if isinstance(self, PretrainedEmbeddingModel):
                res = orca_api.GET(
                    "/pretrained_embedding_model/{model_name}/evaluation/{task_id}",
                    params={"model_name": self.name, "task_id": task_id},
                )["result"]
            elif isinstance(self, FinetunedEmbeddingModel):
                res = orca_api.GET(
                    "/finetuned_embedding_model/{name_or_id}/evaluation/{task_id}",
                    params={"name_or_id": self.id, "task_id": task_id},
                )["result"]
            else:
                raise ValueError("Invalid embedding model")
            assert res is not None
            return RegressionMetrics(**res) if "mse" in res else ClassificationMetrics(**res)

        job = Job(response["task_id"], lambda: get_result(response["task_id"]))
        return job if background else job.result()


class _ModelDescriptor:
    """
    Descriptor for lazily loading embedding models with IDE autocomplete support.

    This class implements the descriptor protocol to provide lazy loading of embedding models
    while maintaining IDE autocomplete functionality. It delays the actual loading of models
    until they are accessed, which improves startup performance.

    The descriptor pattern works by defining how attribute access is handled. When a class
    attribute using this descriptor is accessed, the __get__ method is called, which then
    retrieves or initializes the actual model on first access.
    """

    def __init__(self, name: str):
        """
        Initialize a model descriptor.

        Args:
            name: The name of the embedding model in PretrainedEmbeddingModelName
        """
        self.name = name
        self.model = None  # Model is loaded lazily on first access

    def __get__(self, instance, owner_class):
        """
        Descriptor protocol method called when the attribute is accessed.

        This method implements lazy loading - the actual model is only initialized
        the first time it's accessed. Subsequent accesses will use the cached model.

        Args:
            instance: The instance the attribute was accessed from, or None if accessed from the class
            owner_class: The class that owns the descriptor

        Returns:
            The initialized embedding model

        Raises:
            AttributeError: If no model with the given name exists
        """
        # When accessed from an instance, redirect to class access
        if instance is not None:
            return self.__get__(None, owner_class)

        # Load the model on first access
        if self.model is None:
            try:
                self.model = PretrainedEmbeddingModel._get(cast(PretrainedEmbeddingModelName, self.name))
            except (KeyError, AttributeError):
                raise AttributeError(f"No embedding model named {self.name}")

        return self.model


class PretrainedEmbeddingModel(_EmbeddingModel):
    """
    A pretrained embedding model

    **Models:**

    OrcaCloud supports a select number of small to medium sized embedding models that perform well on the
        [Hugging Face MTEB Leaderboard](https://huggingface.co/spaces/mteb/leaderboard).
        These can be accessed as class attributes. We currently support:

    - **`CDE_SMALL`**: Context-aware CDE small model from Hugging Face ([jxm/cde-small-v1](https://huggingface.co/jxm/cde-small-v1))
    - **`CLIP_BASE`**: Multi-modal CLIP model from Hugging Face ([sentence-transformers/clip-ViT-L-14](https://huggingface.co/sentence-transformers/clip-ViT-L-14))
    - **`GTE_BASE`**: Alibaba's GTE model from Hugging Face ([Alibaba-NLP/gte-base-en-v1.5](https://huggingface.co/Alibaba-NLP/gte-base-en-v1.5))
    - **`DISTILBERT`**: DistilBERT embedding model from Hugging Face ([distilbert-base-uncased](https://huggingface.co/distilbert-base-uncased))
    - **`GTE_SMALL`**: GTE-Small embedding model from Hugging Face ([Supabase/gte-small](https://huggingface.co/Supabase/gte-small))
    - **`E5_LARGE`**: E5-Large instruction-tuned embedding model from Hugging Face ([intfloat/multilingual-e5-large-instruct](https://huggingface.co/intfloat/multilingual-e5-large-instruct))
    - **`GIST_LARGE`**: GIST-Large embedding model from Hugging Face ([avsolatorio/GIST-large-Embedding-v0](https://huggingface.co/avsolatorio/GIST-large-Embedding-v0))
    - **`MXBAI_LARGE`**: Mixbreas's Large embedding model from Hugging Face ([mixedbread-ai/mxbai-embed-large-v1](https://huggingface.co/mixedbread-ai/mxbai-embed-large-v1))
    - **`QWEN2_1_5B`**: Alibaba's Qwen2-1.5B instruction-tuned embedding model from Hugging Face ([Alibaba-NLP/gte-Qwen2-1.5B-instruct](https://huggingface.co/Alibaba-NLP/gte-Qwen2-1.5B-instruct))
    - **`BGE_BASE`**: BAAI's BGE-Base instruction-tuned embedding model from Hugging Face ([BAAI/bge-base-en-v1.5](https://huggingface.co/BAAI/bge-base-en-v1.5))

    **Instruction Support:**

    Some models support instruction-following for better task-specific embeddings. You can check if a model supports instructions
    using the `supports_instructions` attribute.

    Examples:
        >>> PretrainedEmbeddingModel.CDE_SMALL
        PretrainedEmbeddingModel({name: CDE_SMALL, embedding_dim: 768, max_seq_length: 512})

        >>> # Using instruction with an instruction-supporting model
        >>> model = PretrainedEmbeddingModel.E5_LARGE
        >>> embeddings = model.embed("Hello world", prompt="Represent this sentence for retrieval:")

    Attributes:
        name: Name of the pretrained embedding model
        embedding_dim: Dimension of the embeddings that are generated by the model
        max_seq_length: Maximum input length (in tokens not characters) that this model can process. Inputs that are longer will be truncated during the embedding process
        uses_context: Whether the pretrained embedding model uses context
        supports_instructions: Whether this model supports instruction-following
    """

    # Define descriptors for model access with IDE autocomplete
    CDE_SMALL = _ModelDescriptor("CDE_SMALL")
    CLIP_BASE = _ModelDescriptor("CLIP_BASE")
    GTE_BASE = _ModelDescriptor("GTE_BASE")
    DISTILBERT = _ModelDescriptor("DISTILBERT")
    GTE_SMALL = _ModelDescriptor("GTE_SMALL")
    E5_LARGE = _ModelDescriptor("E5_LARGE")
    GIST_LARGE = _ModelDescriptor("GIST_LARGE")
    MXBAI_LARGE = _ModelDescriptor("MXBAI_LARGE")
    QWEN2_1_5B = _ModelDescriptor("QWEN2_1_5B")
    BGE_BASE = _ModelDescriptor("BGE_BASE")

    name: PretrainedEmbeddingModelName

    def __init__(self, metadata: PretrainedEmbeddingModelMetadata):
        # for internal use only, do not document
        self.name = metadata["name"]
        super().__init__(
            name=metadata["name"],
            embedding_dim=metadata["embedding_dim"],
            max_seq_length=metadata["max_seq_length"],
            uses_context=metadata["uses_context"],
            supports_instructions=(
                bool(metadata["supports_instructions"]) if "supports_instructions" in metadata else False
            ),
        )

    def __eq__(self, other) -> bool:
        return isinstance(other, PretrainedEmbeddingModel) and self.name == other.name

    def __repr__(self) -> str:
        return f"PretrainedEmbeddingModel({{name: {self.name}, embedding_dim: {self.embedding_dim}, max_seq_length: {self.max_seq_length}}})"

    @classmethod
    def all(cls) -> list[PretrainedEmbeddingModel]:
        """
        List all pretrained embedding models in the OrcaCloud

        Returns:
            A list of all pretrained embedding models available in the OrcaCloud
        """
        return [cls(metadata) for metadata in orca_api.GET("/pretrained_embedding_model")]

    _instances: dict[str, PretrainedEmbeddingModel] = {}

    @classmethod
    def _get(cls, name: PretrainedEmbeddingModelName) -> PretrainedEmbeddingModel:
        # for internal use only, do not document - we want people to use dot notation to get the model
        cache_key = str(name)
        if cache_key not in cls._instances:
            metadata = orca_api.GET(
                "/pretrained_embedding_model/{model_name}",
                params={"model_name": name},
            )
            cls._instances[cache_key] = cls(metadata)
        return cls._instances[cache_key]

    @classmethod
    def open(cls, name: PretrainedEmbeddingModelName) -> PretrainedEmbeddingModel:
        """
        Open an embedding model by name.

        This is an alternative method to access models for environments
        where IDE autocomplete for model names is not available.

        Params:
            name: Name of the model to open (e.g., "GTE_BASE", "CLIP_BASE")

        Returns:
            The embedding model instance

        Examples:
            >>> model = PretrainedEmbeddingModel.open("GTE_BASE")
        """
        try:
            # Always use the _get method which handles caching properly
            return cls._get(name)
        except (KeyError, AttributeError):
            raise ValueError(f"Unknown model name: {name}")

    @classmethod
    def exists(cls, name: str) -> bool:
        """
        Check if a pretrained embedding model exists by name

        Params:
            name: The name of the pretrained embedding model

        Returns:
            True if the pretrained embedding model exists, False otherwise
        """
        return name in get_args(PretrainedEmbeddingModelName)

    @overload
    def finetune(
        self,
        name: str,
        train_datasource: Datasource | LabeledMemoryset,
        *,
        eval_datasource: Datasource | None = None,
        label_column: str = "label",
        value_column: str = "value",
        training_method: EmbeddingFinetuningMethod = "classification",
        training_args: dict | None = None,
        if_exists: CreateMode = "error",
        background: Literal[True],
    ) -> Job[FinetunedEmbeddingModel]:
        pass

    @overload
    def finetune(
        self,
        name: str,
        train_datasource: Datasource | LabeledMemoryset,
        *,
        eval_datasource: Datasource | None = None,
        label_column: str = "label",
        value_column: str = "value",
        training_method: EmbeddingFinetuningMethod = "classification",
        training_args: dict | None = None,
        if_exists: CreateMode = "error",
        background: Literal[False] = False,
    ) -> FinetunedEmbeddingModel:
        pass

    def finetune(
        self,
        name: str,
        train_datasource: Datasource | LabeledMemoryset,
        *,
        eval_datasource: Datasource | None = None,
        label_column: str = "label",
        value_column: str = "value",
        training_method: EmbeddingFinetuningMethod = "classification",
        training_args: dict | None = None,
        if_exists: CreateMode = "error",
        background: bool = False,
    ) -> FinetunedEmbeddingModel | Job[FinetunedEmbeddingModel]:
        """
        Finetune an embedding model

        Params:
            name: Name of the finetuned embedding model
            train_datasource: Data to train on
            eval_datasource: Optionally provide data to evaluate on
            label_column: Column name of the label
            value_column: Column name of the value
            training_method: Training method to use
            training_args: Optional override for Hugging Face [`TrainingArguments`](transformers.TrainingArguments).
                If not provided, reasonable training arguments will be used for the specified training method
            if_exists: What to do if a finetuned embedding model with the same name already exists, defaults to
                `"error"`. Other option is `"open"` to open the existing finetuned embedding model.
            background: Whether to run the operation in the background and return a job handle

        Returns:
            The finetuned embedding model

        Raises:
            ValueError: If the finetuned embedding model already exists and `if_exists` is `"error"` or if it is `"open"`
                but the base model param does not match the existing model

        Examples:
            >>> datasource = Datasource.open("my_datasource")
            >>> model = PretrainedEmbeddingModel.CLIP_BASE
            >>> model.finetune("my_finetuned_model", datasource)
        """
        exists = FinetunedEmbeddingModel.exists(name)

        if exists and if_exists == "error":
            raise ValueError(f"Finetuned embedding model '{name}' already exists")
        elif exists and if_exists == "open":
            existing = FinetunedEmbeddingModel.open(name)

            if existing.base_model_name != self.name:
                raise ValueError(f"Finetuned embedding model '{name}' already exists, but with different base model")

            return existing

        from .memoryset import LabeledMemoryset

        payload: FinetuneEmbeddingModelRequest = {
            "name": name,
            "base_model": self.name,
            "label_column": label_column,
            "value_column": value_column,
            "training_method": training_method,
            "training_args": training_args or {},
        }
        if isinstance(train_datasource, Datasource):
            payload["train_datasource_name_or_id"] = train_datasource.id
        elif isinstance(train_datasource, LabeledMemoryset):
            payload["train_memoryset_name_or_id"] = train_datasource.id
        if eval_datasource is not None:
            payload["eval_datasource_name_or_id"] = eval_datasource.id

        res = orca_api.POST(
            "/finetuned_embedding_model",
            json=payload,
        )
        job = Job(
            res["finetuning_task_id"],
            lambda: FinetunedEmbeddingModel.open(res["id"]),
        )
        return job if background else job.result()


class FinetunedEmbeddingModel(_EmbeddingModel):
    """
    A finetuned embedding model in the OrcaCloud

    Attributes:
        name: Name of the finetuned embedding model
        embedding_dim: Dimension of the embeddings that are generated by the model
        max_seq_length: Maximum input length (in tokens not characters) that this model can process. Inputs that are longer will be truncated during the embedding process
        uses_context: Whether the model uses the memoryset to contextualize embeddings (acts akin to inverse document frequency in TFIDF features)
        id: Unique identifier of the finetuned embedding model
        base_model: Base model the finetuned embedding model was trained on
        created_at: When the model was finetuned
    """

    id: str
    name: str
    created_at: datetime
    updated_at: datetime
    base_model_name: PretrainedEmbeddingModelName
    _status: Status

    def __init__(self, metadata: FinetunedEmbeddingModelMetadata):
        # for internal use only, do not document
        self.id = metadata["id"]
        self.name = metadata["name"]
        self.created_at = datetime.fromisoformat(metadata["created_at"])
        self.updated_at = datetime.fromisoformat(metadata["updated_at"])
        self.base_model_name = metadata["base_model"]
        self._status = Status(metadata["finetuning_status"])

        super().__init__(
            name=metadata["name"],
            embedding_dim=metadata["embedding_dim"],
            max_seq_length=metadata["max_seq_length"],
            uses_context=metadata["uses_context"],
            supports_instructions=self.base_model.supports_instructions,
        )

    def __eq__(self, other) -> bool:
        return isinstance(other, FinetunedEmbeddingModel) and self.id == other.id

    def __repr__(self) -> str:
        return (
            "FinetunedEmbeddingModel({\n"
            f"    name: {self.name},\n"
            f"    embedding_dim: {self.embedding_dim},\n"
            f"    max_seq_length: {self.max_seq_length},\n"
            f"    base_model: PretrainedEmbeddingModel.{self.base_model_name}\n"
            "})"
        )

    @property
    def base_model(self) -> PretrainedEmbeddingModel:
        """Pretrained model the finetuned embedding model was based on"""
        return PretrainedEmbeddingModel._get(self.base_model_name)

    @classmethod
    def all(cls) -> list[FinetunedEmbeddingModel]:
        """
        List all finetuned embedding model handles in the OrcaCloud

        Returns:
            A list of all finetuned embedding model handles in the OrcaCloud
        """
        return [cls(metadata) for metadata in orca_api.GET("/finetuned_embedding_model")]

    @classmethod
    def open(cls, name: str) -> FinetunedEmbeddingModel:
        """
        Get a handle to a finetuned embedding model in the OrcaCloud

        Params:
            name: The name or unique identifier of a finetuned embedding model

        Returns:
            A handle to the finetuned embedding model in the OrcaCloud

        Raises:
            LookupError: If the finetuned embedding model does not exist
        """
        metadata = orca_api.GET(
            "/finetuned_embedding_model/{name_or_id}",
            params={"name_or_id": name},
        )
        return cls(metadata)

    @classmethod
    def exists(cls, name_or_id: str) -> bool:
        """
        Check if a finetuned embedding model with the given name or id exists.

        Params:
            name_or_id: The name or id of the finetuned embedding model

        Returns:
            True if the finetuned embedding model exists, False otherwise
        """
        try:
            cls.open(name_or_id)
            return True
        except LookupError:
            return False

    @classmethod
    def drop(cls, name_or_id: str, *, if_not_exists: DropMode = "error"):
        """
        Delete the finetuned embedding model from the OrcaCloud

        Params:
            name_or_id: The name or id of the finetuned embedding model

        Raises:
            LookupError: If the finetuned embedding model does not exist and `if_not_exists` is `"error"`
        """
        try:
            orca_api.DELETE(
                "/finetuned_embedding_model/{name_or_id}",
                params={"name_or_id": name_or_id},
            )
        except (LookupError, RuntimeError):
            if if_not_exists == "error":
                raise
