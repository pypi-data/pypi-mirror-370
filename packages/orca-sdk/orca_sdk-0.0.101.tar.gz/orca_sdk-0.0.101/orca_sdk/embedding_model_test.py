import logging
from typing import get_args
from uuid import uuid4

import pytest

from .datasource import Datasource
from .embedding_model import (
    ClassificationMetrics,
    FinetunedEmbeddingModel,
    PretrainedEmbeddingModel,
    PretrainedEmbeddingModelName,
)
from .job import Status
from .memoryset import LabeledMemoryset


def test_open_pretrained_model():
    model = PretrainedEmbeddingModel.GTE_BASE
    assert model is not None
    assert isinstance(model, PretrainedEmbeddingModel)
    assert model.name == "GTE_BASE"
    assert model.embedding_dim == 768
    assert model.max_seq_length == 8192
    assert model is PretrainedEmbeddingModel.GTE_BASE


def test_open_pretrained_model_unauthenticated(unauthenticated):
    with pytest.raises(ValueError, match="Invalid API key"):
        PretrainedEmbeddingModel.GTE_BASE.embed("I love this airline")


def test_open_pretrained_model_not_found():
    with pytest.raises(LookupError):
        PretrainedEmbeddingModel._get("INVALID_MODEL")  # type: ignore


def test_all_pretrained_models():
    models = PretrainedEmbeddingModel.all()
    assert len(models) > 1
    if len(models) != len(get_args(PretrainedEmbeddingModelName)):
        logging.warning("Please regenerate the SDK client! Some pretrained model names are not exposed yet.")
    model_names = [m.name for m in models]
    assert all(m in model_names for m in get_args(PretrainedEmbeddingModelName))


def test_embed_text():
    embedding = PretrainedEmbeddingModel.GTE_BASE.embed("I love this airline", max_seq_length=32)
    assert embedding is not None
    assert isinstance(embedding, list)
    assert len(embedding) == 768
    assert isinstance(embedding[0], float)


def test_embed_text_unauthenticated(unauthenticated):
    with pytest.raises(ValueError, match="Invalid API key"):
        PretrainedEmbeddingModel.GTE_BASE.embed("I love this airline", max_seq_length=32)


def test_evaluate_pretrained_model(datasource: Datasource):
    metrics = PretrainedEmbeddingModel.GTE_BASE.evaluate(datasource=datasource, label_column="label")
    assert metrics is not None
    assert isinstance(metrics, ClassificationMetrics)
    assert metrics.accuracy > 0.5


@pytest.fixture(scope="session")
def finetuned_model(datasource) -> FinetunedEmbeddingModel:
    return PretrainedEmbeddingModel.DISTILBERT.finetune("test_finetuned_model", datasource)


def test_finetune_model_with_datasource(finetuned_model: FinetunedEmbeddingModel):
    assert finetuned_model is not None
    assert finetuned_model.name == "test_finetuned_model"
    assert finetuned_model.base_model == PretrainedEmbeddingModel.DISTILBERT
    assert finetuned_model.embedding_dim == 768
    assert finetuned_model.max_seq_length == 512
    assert finetuned_model._status == Status.COMPLETED


def test_finetune_model_with_memoryset(readonly_memoryset: LabeledMemoryset):
    finetuned_model = PretrainedEmbeddingModel.DISTILBERT.finetune(
        "test_finetuned_model_from_memoryset", readonly_memoryset
    )
    assert finetuned_model is not None
    assert finetuned_model.name == "test_finetuned_model_from_memoryset"
    assert finetuned_model.base_model == PretrainedEmbeddingModel.DISTILBERT
    assert finetuned_model.embedding_dim == 768
    assert finetuned_model.max_seq_length == 512
    assert finetuned_model._status == Status.COMPLETED


def test_finetune_model_already_exists_error(datasource: Datasource, finetuned_model):
    with pytest.raises(ValueError):
        PretrainedEmbeddingModel.DISTILBERT.finetune("test_finetuned_model", datasource)


def test_finetune_model_already_exists_return(datasource: Datasource, finetuned_model):
    with pytest.raises(ValueError):
        PretrainedEmbeddingModel.GTE_BASE.finetune("test_finetuned_model", datasource, if_exists="open")

    new_model = PretrainedEmbeddingModel.DISTILBERT.finetune("test_finetuned_model", datasource, if_exists="open")
    assert new_model is not None
    assert new_model.name == "test_finetuned_model"
    assert new_model.base_model == PretrainedEmbeddingModel.DISTILBERT
    assert new_model.embedding_dim == 768
    assert new_model.max_seq_length == 512
    assert new_model._status == Status.COMPLETED


def test_finetune_model_unauthenticated(unauthenticated, datasource: Datasource):
    with pytest.raises(ValueError, match="Invalid API key"):
        PretrainedEmbeddingModel.DISTILBERT.finetune("test_finetuned_model_unauthenticated", datasource)


def test_use_finetuned_model_in_memoryset(datasource: Datasource, finetuned_model: FinetunedEmbeddingModel):
    memoryset = LabeledMemoryset.create(
        "test_memoryset_finetuned_model",
        datasource,
        embedding_model=finetuned_model,
    )
    assert memoryset is not None
    assert memoryset.name == "test_memoryset_finetuned_model"
    assert memoryset.embedding_model == finetuned_model
    assert memoryset.length == datasource.length


def test_open_finetuned_model(finetuned_model: FinetunedEmbeddingModel):
    model = FinetunedEmbeddingModel.open(finetuned_model.name)
    assert isinstance(model, FinetunedEmbeddingModel)
    assert model.id == finetuned_model.id
    assert model.name == finetuned_model.name
    assert model.base_model == PretrainedEmbeddingModel.DISTILBERT
    assert model.embedding_dim == 768
    assert model.max_seq_length == 512
    assert model == finetuned_model


def test_embed_finetuned_model(finetuned_model: FinetunedEmbeddingModel):
    embedding = finetuned_model.embed("I love this airline")
    assert embedding is not None
    assert isinstance(embedding, list)
    assert len(embedding) == 768
    assert isinstance(embedding[0], float)


def test_all_finetuned_models(finetuned_model: FinetunedEmbeddingModel):
    models = FinetunedEmbeddingModel.all()
    assert len(models) > 0
    assert any(model.name == finetuned_model.name for model in models)


def test_all_finetuned_models_unauthenticated(unauthenticated):
    with pytest.raises(ValueError, match="Invalid API key"):
        FinetunedEmbeddingModel.all()


def test_all_finetuned_models_unauthorized(unauthorized, finetuned_model: FinetunedEmbeddingModel):
    assert finetuned_model not in FinetunedEmbeddingModel.all()


def test_drop_finetuned_model(datasource: Datasource):
    PretrainedEmbeddingModel.DISTILBERT.finetune("finetuned_model_to_delete", datasource)
    assert FinetunedEmbeddingModel.open("finetuned_model_to_delete")
    FinetunedEmbeddingModel.drop("finetuned_model_to_delete")
    with pytest.raises(LookupError):
        FinetunedEmbeddingModel.open("finetuned_model_to_delete")


def test_drop_finetuned_model_unauthenticated(unauthenticated, datasource: Datasource):
    with pytest.raises(ValueError, match="Invalid API key"):
        PretrainedEmbeddingModel.DISTILBERT.finetune("finetuned_model_to_delete", datasource)


def test_drop_finetuned_model_not_found():
    with pytest.raises(LookupError):
        FinetunedEmbeddingModel.drop(str(uuid4()))
    # ignores error if specified
    FinetunedEmbeddingModel.drop(str(uuid4()), if_not_exists="ignore")


def test_drop_finetuned_model_unauthorized(unauthorized, finetuned_model: FinetunedEmbeddingModel):
    with pytest.raises(LookupError):
        FinetunedEmbeddingModel.drop(finetuned_model.id)


def test_supports_instructions():
    model = PretrainedEmbeddingModel.GTE_BASE
    assert not model.supports_instructions

    instruction_model = PretrainedEmbeddingModel.BGE_BASE
    assert instruction_model.supports_instructions


def test_use_explicit_instruction_prompt():
    model = PretrainedEmbeddingModel.BGE_BASE
    assert model.supports_instructions
    input = "Hello world"
    assert model.embed(input, prompt="Represent this sentence for sentiment retrieval:") != model.embed(input)
