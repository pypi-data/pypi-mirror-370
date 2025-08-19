import logging
import os
from typing import Generator
from uuid import uuid4

import pytest
from datasets import ClassLabel, Dataset, Features, Value

from ._utils.auth import _create_api_key, _delete_org
from .classification_model import ClassificationModel
from .client import orca_api
from .credentials import OrcaCredentials
from .datasource import Datasource
from .embedding_model import PretrainedEmbeddingModel
from .memoryset import LabeledMemoryset, ScoredMemoryset
from .regression_model import RegressionModel

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

os.environ["ORCA_API_URL"] = os.environ.get("ORCA_API_URL", "http://localhost:1584/")

os.environ["ORCA_SAVE_TELEMETRY_SYNCHRONOUSLY"] = "true"


def skip_in_prod(reason: str):
    """Custom decorator to skip tests when running against production API"""
    PROD_API_URLs = ["https://api.orcadb.ai", "https://api.dev.orcadb.ai"]
    return pytest.mark.skipif(
        os.environ["ORCA_API_URL"] in PROD_API_URLs,
        reason=reason,
    )


def skip_in_ci(reason: str):
    """Custom decorator to skip tests when running in CI"""
    return pytest.mark.skipif(
        os.environ.get("GITHUB_ACTIONS", "false") == "true",
        reason=reason,
    )


def _create_org_id():
    # UUID start to identify test data (0xtest...)
    return "10e50000-0000-4000-a000-" + str(uuid4())[24:]


@pytest.fixture()
def base_url_reset():
    original_base_url = orca_api.base_url
    yield
    orca_api.base_url = original_base_url


@pytest.fixture(scope="session")
def org_id():
    return _create_org_id()


@pytest.fixture(autouse=True, scope="session")
def api_key(org_id) -> Generator[str, None, None]:
    api_key = _create_api_key(org_id=org_id, name="orca_sdk_test")
    OrcaCredentials.set_api_key(api_key, check_validity=True)
    yield api_key
    _delete_org(org_id)


@pytest.fixture(autouse=True)
def authenticated(api_key):
    OrcaCredentials.set_api_key(api_key, check_validity=False)


@pytest.fixture()
def unauthenticated(api_key):
    OrcaCredentials.set_api_key(str(uuid4()), check_validity=False)
    yield
    # Need to reset the api key to the original api key so following tests don't fail
    OrcaCredentials.set_api_key(api_key, check_validity=False)


@pytest.fixture()
def other_org_id():
    return _create_org_id()


@pytest.fixture()
def unauthorized(api_key, other_org_id):
    different_api_key = _create_api_key(org_id=other_org_id, name="orca_sdk_test_other_org")
    OrcaCredentials.set_api_key(different_api_key, check_validity=False)
    yield
    OrcaCredentials.set_api_key(api_key, check_validity=False)
    _delete_org(other_org_id)


@pytest.fixture(scope="session")
def label_names():
    return ["soup", "cats"]


SAMPLE_DATA = [
    {"value": "i love soup", "label": 0, "key": "g1", "score": 0.1, "source_id": "s1"},
    {"value": "cats are cute", "label": 1, "key": "g1", "score": 0.9, "source_id": "s2"},
    {"value": "soup is good", "label": 0, "key": "g1", "score": 0.1, "source_id": "s3"},
    {"value": "i love cats", "label": 1, "key": "g1", "score": 0.9, "source_id": "s4"},
    {"value": "everyone loves cats", "label": 1, "key": "g1", "score": 0.9, "source_id": "s5"},
    {"value": "soup is great for the winter", "label": 0, "key": "g1", "score": 0.1, "source_id": "s6"},
    {"value": "hot soup on a rainy day!", "label": 0, "key": "g1", "score": 0.1, "source_id": "s7"},
    {"value": "cats sleep all day", "label": 1, "key": "g1", "score": 0.9, "source_id": "s8"},
    {"value": "homemade soup recipes", "label": 0, "key": "g1", "score": 0.1, "source_id": "s9"},
    {"value": "cats purr when happy", "label": 1, "key": "g2", "score": 0.9, "source_id": "s10"},
    {"value": "chicken noodle soup is classic", "label": 0, "key": "g1", "score": 0.1, "source_id": "s11"},
    {"value": "kittens are baby cats", "label": 1, "key": "g2", "score": 0.9, "source_id": "s12"},
    {"value": "soup can be served cold too", "label": 0, "key": "g1", "score": 0.1, "source_id": "s13"},
    {"value": "cats have nine lives", "label": 1, "key": "g2", "score": 0.9, "source_id": "s14"},
    {"value": "tomato soup with grilled cheese", "label": 0, "key": "g1", "score": 0.1, "source_id": "s15"},
    {"value": "cats are independent animals", "label": 1, "key": "g2", "score": 0.9, "source_id": "s16"},
]


@pytest.fixture(scope="session")
def hf_dataset(label_names: list[str]) -> Dataset:
    return Dataset.from_list(
        SAMPLE_DATA,
        features=Features(
            {
                "value": Value("string"),
                "label": ClassLabel(names=label_names),
                "key": Value("string"),
                "score": Value("float"),
                "source_id": Value("string"),
            }
        ),
    )


@pytest.fixture(scope="session")
def datasource(hf_dataset: Dataset) -> Datasource:
    datasource = Datasource.from_hf_dataset("test_datasource", hf_dataset)
    return datasource


EVAL_DATASET = [
    {"value": "chicken noodle soup is the best", "label": 1, "score": 0.9},  # mislabeled
    {"value": "cats are cute", "label": 0, "score": 0.1},  # mislabeled
    {"value": "soup is great for the winter", "label": 0, "score": 0.1},
    {"value": "i love cats", "label": 1, "score": 0.9},
]


@pytest.fixture(scope="session")
def eval_datasource() -> Datasource:
    eval_datasource = Datasource.from_list("eval_datasource", EVAL_DATASET)
    return eval_datasource


@pytest.fixture(scope="session")
def eval_dataset() -> Dataset:
    eval_dataset = Dataset.from_list(EVAL_DATASET)
    return eval_dataset


@pytest.fixture(scope="session")
def readonly_memoryset(datasource: Datasource) -> LabeledMemoryset:
    memoryset = LabeledMemoryset.create(
        "test_readonly_memoryset",
        datasource=datasource,
        embedding_model=PretrainedEmbeddingModel.GTE_BASE,
        source_id_column="source_id",
        max_seq_length_override=32,
        index_type="IVF_FLAT",
        index_params={"n_lists": 100},
    )
    return memoryset


@pytest.fixture(scope="function")
def writable_memoryset(datasource: Datasource, api_key: str) -> Generator[LabeledMemoryset, None, None]:
    """
    Function-scoped fixture that provides a writable memoryset for tests that mutate state.

    This fixture creates a fresh `LabeledMemoryset` named 'test_writable_memoryset' before each test.
    After the test, it attempts to restore the memoryset to its initial state by deleting any added entries
    and reinserting sample data — unless the memoryset has been dropped by the test itself, in which case
    it will be recreated on the next invocation.

    Note: Re-creating the memoryset from scratch is surprisingly more expensive than cleaning it up.
    """
    # It shouldn't be possible for this memoryset to already exist
    memoryset = LabeledMemoryset.create(
        "test_writable_memoryset",
        datasource=datasource,
        embedding_model=PretrainedEmbeddingModel.GTE_BASE,
        source_id_column="source_id",
        max_seq_length_override=32,
        if_exists="open",
    )
    try:
        yield memoryset
    finally:
        # Restore the memoryset to a clean state for the next test.
        OrcaCredentials.set_api_key(api_key, check_validity=False)

        if LabeledMemoryset.exists("test_writable_memoryset"):
            memoryset.refresh()

            memory_ids = [memoryset[i].memory_id for i in range(len(memoryset))]

            if memory_ids:
                memoryset.delete(memory_ids)
            memoryset.refresh()
            assert len(memoryset) == 0
            memoryset.insert(SAMPLE_DATA)
        # If the test dropped the memoryset, do nothing — it will be recreated on the next use.


@pytest.fixture(scope="session")
def classification_model(readonly_memoryset: LabeledMemoryset) -> ClassificationModel:
    model = ClassificationModel.create(
        "test_classification_model",
        readonly_memoryset,
        num_classes=2,
        memory_lookup_count=3,
        description="test_description",
    )
    return model


# Add scored memoryset and regression model fixtures
@pytest.fixture(scope="session")
def scored_memoryset(datasource: Datasource) -> ScoredMemoryset:
    memoryset = ScoredMemoryset.create(
        "test_scored_memoryset",
        datasource=datasource,
        embedding_model=PretrainedEmbeddingModel.GTE_BASE,
        source_id_column="source_id",
        max_seq_length_override=32,
        index_type="IVF_FLAT",
        index_params={"n_lists": 100},
    )
    return memoryset


@pytest.fixture(scope="session")
def regression_model(scored_memoryset: ScoredMemoryset) -> RegressionModel:
    model = RegressionModel.create(
        "test_regression_model",
        scored_memoryset,
        memory_lookup_count=3,
        description="test_regression_description",
    )
    return model
