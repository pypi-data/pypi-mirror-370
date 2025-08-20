"""
OrcaSDK is a Python library for building and using retrieval augmented models in the OrcaCloud.
"""

from ._utils.common import UNSET, CreateMode, DropMode
from .classification_model import ClassificationMetrics, ClassificationModel
from .client import orca_api
from .credentials import OrcaCredentials
from .datasource import Datasource
from .embedding_model import (
    FinetunedEmbeddingModel,
    PretrainedEmbeddingModel,
    PretrainedEmbeddingModelName,
)
from .job import Job, Status
from .memoryset import (
    CascadingEditSuggestion,
    FilterItemTuple,
    LabeledMemory,
    LabeledMemoryLookup,
    LabeledMemoryset,
    ScoredMemory,
    ScoredMemoryLookup,
    ScoredMemoryset,
)
from .regression_model import RegressionModel
from .telemetry import ClassificationPrediction, FeedbackCategory, RegressionPrediction

# only specify things that should show up on the root page of the reference docs because they are in private modules
__all__ = ["UNSET", "CreateMode", "DropMode"]
