import random
from uuid import uuid4

import pytest
from datasets.arrow_dataset import Dataset

from .classification_model import ClassificationModel
from .conftest import skip_in_prod
from .datasource import Datasource
from .embedding_model import PretrainedEmbeddingModel
from .memoryset import LabeledMemoryset, ScoredMemory, ScoredMemoryset, Status

"""
Test Performance Note:

Creating new `LabeledMemoryset` objects is expensive, so this test file applies the following optimizations:

- Two fixtures are used to manage memorysets:
    - `readonly_memoryset` is a session-scoped fixture shared across tests that do not modify state.
      It should only be used in nullipotent tests.
    - `writable_memoryset` is a function-scoped, regenerating fixture.
      It can be used in tests that mutate or delete the memoryset, and will be reset before each test.

- To minimize fixture overhead, tests using `writable_memoryset` should combine related behaviors.
  For example, prefer a single `test_delete` that covers both single and multiple deletion cases,
  rather than separate `test_delete_single` and `test_delete_multiple` tests.
"""


def test_create_memoryset(readonly_memoryset: LabeledMemoryset, hf_dataset: Dataset, label_names: list[str]):
    assert readonly_memoryset is not None
    assert readonly_memoryset.name == "test_readonly_memoryset"
    assert readonly_memoryset.embedding_model == PretrainedEmbeddingModel.GTE_BASE
    assert readonly_memoryset.label_names == label_names
    assert readonly_memoryset.insertion_status == Status.COMPLETED
    assert isinstance(readonly_memoryset.length, int)
    assert readonly_memoryset.length == len(hf_dataset)
    assert readonly_memoryset.index_type == "IVF_FLAT"
    assert readonly_memoryset.index_params == {"n_lists": 100}


def test_create_memoryset_unauthenticated(unauthenticated, datasource):
    with pytest.raises(ValueError, match="Invalid API key"):
        LabeledMemoryset.create("test_memoryset", datasource)


def test_create_memoryset_invalid_input(datasource):
    # invalid name
    with pytest.raises(ValueError, match=r"Invalid input:.*"):
        LabeledMemoryset.create("test memoryset", datasource)


def test_create_memoryset_already_exists_error(hf_dataset, label_names, readonly_memoryset):
    memoryset_name = readonly_memoryset.name
    with pytest.raises(ValueError):
        LabeledMemoryset.from_hf_dataset(memoryset_name, hf_dataset, label_names=label_names)
    with pytest.raises(ValueError):
        LabeledMemoryset.from_hf_dataset(memoryset_name, hf_dataset, label_names=label_names, if_exists="error")


def test_create_memoryset_already_exists_open(hf_dataset, label_names, readonly_memoryset):
    # invalid label names
    with pytest.raises(ValueError):
        LabeledMemoryset.from_hf_dataset(
            readonly_memoryset.name,
            hf_dataset,
            label_names=["turtles", "frogs"],
            if_exists="open",
        )
    # different embedding model
    with pytest.raises(ValueError):
        LabeledMemoryset.from_hf_dataset(
            readonly_memoryset.name,
            hf_dataset,
            label_names=label_names,
            embedding_model=PretrainedEmbeddingModel.DISTILBERT,
            if_exists="open",
        )
    opened_memoryset = LabeledMemoryset.from_hf_dataset(
        readonly_memoryset.name,
        hf_dataset,
        embedding_model=PretrainedEmbeddingModel.GTE_BASE,
        if_exists="open",
    )
    assert opened_memoryset is not None
    assert opened_memoryset.name == readonly_memoryset.name
    assert opened_memoryset.length == len(hf_dataset)


def test_open_memoryset(readonly_memoryset, hf_dataset):
    fetched_memoryset = LabeledMemoryset.open(readonly_memoryset.name)
    assert fetched_memoryset is not None
    assert fetched_memoryset.name == readonly_memoryset.name
    assert fetched_memoryset.length == len(hf_dataset)
    assert fetched_memoryset.index_type == "IVF_FLAT"
    assert fetched_memoryset.index_params == {"n_lists": 100}


def test_open_memoryset_unauthenticated(unauthenticated, readonly_memoryset):
    with pytest.raises(ValueError, match="Invalid API key"):
        LabeledMemoryset.open(readonly_memoryset.name)


def test_open_memoryset_not_found():
    with pytest.raises(LookupError):
        LabeledMemoryset.open(str(uuid4()))


def test_open_memoryset_invalid_input():
    with pytest.raises(ValueError, match=r"Invalid input:.*"):
        LabeledMemoryset.open("not valid id")


def test_open_memoryset_unauthorized(unauthorized, readonly_memoryset):
    with pytest.raises(LookupError):
        LabeledMemoryset.open(readonly_memoryset.name)


def test_all_memorysets(readonly_memoryset: LabeledMemoryset):
    memorysets = LabeledMemoryset.all()
    assert len(memorysets) > 0
    assert any(memoryset.name == readonly_memoryset.name for memoryset in memorysets)


def test_all_memorysets_unauthenticated(unauthenticated):
    with pytest.raises(ValueError, match="Invalid API key"):
        LabeledMemoryset.all()


def test_all_memorysets_unauthorized(unauthorized, readonly_memoryset):
    assert readonly_memoryset not in LabeledMemoryset.all()


def test_drop_memoryset_unauthenticated(unauthenticated, readonly_memoryset):
    with pytest.raises(ValueError, match="Invalid API key"):
        LabeledMemoryset.drop(readonly_memoryset.name)


def test_drop_memoryset_not_found():
    with pytest.raises(LookupError):
        LabeledMemoryset.drop(str(uuid4()))
    # ignores error if specified
    LabeledMemoryset.drop(str(uuid4()), if_not_exists="ignore")


def test_drop_memoryset_unauthorized(unauthorized, readonly_memoryset):
    with pytest.raises(LookupError):
        LabeledMemoryset.drop(readonly_memoryset.name)


def test_update_memoryset_attributes(writable_memoryset: LabeledMemoryset):
    original_label_names = writable_memoryset.label_names
    writable_memoryset.set(description="New description")
    assert writable_memoryset.description == "New description"

    writable_memoryset.set(description=None)
    assert writable_memoryset.description is None

    writable_memoryset.set(name="New_name")
    assert writable_memoryset.name == "New_name"

    writable_memoryset.set(name="test_writable_memoryset")
    assert writable_memoryset.name == "test_writable_memoryset"

    assert writable_memoryset.label_names == original_label_names

    writable_memoryset.set(label_names=["New label 1", "New label 2"])
    assert writable_memoryset.label_names == ["New label 1", "New label 2"]


def test_search(readonly_memoryset: LabeledMemoryset):
    memory_lookups = readonly_memoryset.search(["i love soup", "cats are cute"])
    assert len(memory_lookups) == 2
    assert len(memory_lookups[0]) == 1
    assert len(memory_lookups[1]) == 1
    assert memory_lookups[0][0].label == 0
    assert memory_lookups[1][0].label == 1


def test_search_count(readonly_memoryset: LabeledMemoryset):
    memory_lookups = readonly_memoryset.search("i love soup", count=3)
    assert len(memory_lookups) == 3
    assert memory_lookups[0].label == 0
    assert memory_lookups[1].label == 0
    assert memory_lookups[2].label == 0


def test_get_memory_at_index(readonly_memoryset: LabeledMemoryset, hf_dataset: Dataset, label_names: list[str]):
    memory = readonly_memoryset[0]
    assert memory.value == hf_dataset[0]["value"]
    assert memory.label == hf_dataset[0]["label"]
    assert memory.label_name == label_names[hf_dataset[0]["label"]]
    assert memory.source_id == hf_dataset[0]["source_id"]
    assert memory.score == hf_dataset[0]["score"]
    assert memory.key == hf_dataset[0]["key"]
    last_memory = readonly_memoryset[-1]
    assert last_memory.value == hf_dataset[-1]["value"]
    assert last_memory.label == hf_dataset[-1]["label"]


def test_get_range_of_memories(readonly_memoryset: LabeledMemoryset, hf_dataset: Dataset):
    memories = readonly_memoryset[1:3]
    assert len(memories) == 2
    assert memories[0].value == hf_dataset["value"][1]
    assert memories[1].value == hf_dataset["value"][2]


def test_get_memory_by_id(readonly_memoryset: LabeledMemoryset, hf_dataset: Dataset):
    memory = readonly_memoryset.get(readonly_memoryset[0].memory_id)
    assert memory.value == hf_dataset[0]["value"]
    assert memory == readonly_memoryset[memory.memory_id]


def test_get_memories_by_id(readonly_memoryset: LabeledMemoryset, hf_dataset: Dataset):
    memories = readonly_memoryset.get([readonly_memoryset[0].memory_id, readonly_memoryset[1].memory_id])
    assert len(memories) == 2
    assert memories[0].value == hf_dataset[0]["value"]
    assert memories[1].value == hf_dataset[1]["value"]


def test_query_memoryset(readonly_memoryset: LabeledMemoryset):
    memories = readonly_memoryset.query(filters=[("label", "==", 1)])
    assert len(memories) == 8
    assert all(memory.label == 1 for memory in memories)
    assert len(readonly_memoryset.query(limit=2)) == 2
    assert len(readonly_memoryset.query(filters=[("metadata.key", "==", "g2")])) == 4


def test_query_memoryset_with_feedback_metrics(classification_model: ClassificationModel):
    prediction = classification_model.predict("Do you love soup?")
    feedback_name = f"correct_{random.randint(0, 1000000)}"
    prediction.record_feedback(category=feedback_name, value=prediction.label == 0)
    memories = prediction.memoryset.query(filters=[("label", "==", 0)], with_feedback_metrics=True)

    # Get the memory_ids that were actually used in the prediction
    used_memory_ids = {memory.memory_id for memory in prediction.memory_lookups}

    assert len(memories) == 8
    assert all(memory.label == 0 for memory in memories)
    for memory in memories:
        assert memory.feedback_metrics is not None
        if memory.memory_id in used_memory_ids:
            assert feedback_name in memory.feedback_metrics
            assert memory.feedback_metrics[feedback_name]["avg"] == 1.0
            assert memory.feedback_metrics[feedback_name]["count"] == 1
        else:
            assert feedback_name not in memory.feedback_metrics or memory.feedback_metrics[feedback_name]["count"] == 0
        assert isinstance(memory.lookup_count, int)


def test_query_memoryset_with_feedback_metrics_filter(classification_model: ClassificationModel):
    prediction = classification_model.predict("Do you love soup?")
    prediction.record_feedback(category="accurate", value=prediction.label == 0)
    memories = prediction.memoryset.query(
        filters=[("feedback_metrics.accurate.avg", ">", 0.5)], with_feedback_metrics=True
    )
    assert len(memories) == 3
    assert all(memory.label == 0 for memory in memories)
    for memory in memories:
        assert memory.feedback_metrics is not None
        assert memory.feedback_metrics["accurate"] is not None
        assert memory.feedback_metrics["accurate"]["avg"] == 1.0
        assert memory.feedback_metrics["accurate"]["count"] == 1


def test_query_memoryset_with_feedback_metrics_sort(classification_model: ClassificationModel):
    prediction = classification_model.predict("Do you love soup?")
    prediction.record_feedback(category="positive", value=1.0)
    prediction2 = classification_model.predict("Do you like cats?")
    prediction2.record_feedback(category="positive", value=-1.0)

    memories = prediction.memoryset.query(
        filters=[("feedback_metrics.positive.avg", ">=", -1.0)],
        sort=[("feedback_metrics.positive.avg", "desc")],
        with_feedback_metrics=True,
    )
    assert (
        len(memories) == 6
    )  # there are only 6 out of 16 memories that have a positive feedback metric. Look at SAMPLE_DATA in conftest.py
    assert memories[0].feedback_metrics["positive"]["avg"] == 1.0
    assert memories[-1].feedback_metrics["positive"]["avg"] == -1.0


def test_insert_memories(writable_memoryset: LabeledMemoryset):
    writable_memoryset.refresh()
    prev_length = writable_memoryset.length
    writable_memoryset.insert(
        [
            dict(value="tomato soup is my favorite", label=0),
            dict(value="cats are fun to play with", label=1),
        ]
    )
    writable_memoryset.refresh()
    assert writable_memoryset.length == prev_length + 2
    writable_memoryset.insert(dict(value="tomato soup is my favorite", label=0, key="test", source_id="test"))
    writable_memoryset.refresh()
    assert writable_memoryset.length == prev_length + 3
    last_memory = writable_memoryset[-1]
    assert last_memory.value == "tomato soup is my favorite"
    assert last_memory.label == 0
    assert last_memory.metadata
    assert last_memory.metadata["key"] == "test"
    assert last_memory.source_id == "test"


@skip_in_prod("Production memorysets do not have session consistency guarantees")
def test_update_memories(writable_memoryset: LabeledMemoryset, hf_dataset: Dataset):
    # We've combined the update tests into one to avoid multiple expensive requests for a writable_memoryset

    # test updating a single memory
    memory_id = writable_memoryset[0].memory_id
    updated_memory = writable_memoryset.update(dict(memory_id=memory_id, value="i love soup so much"))
    assert updated_memory.value == "i love soup so much"
    assert updated_memory.label == hf_dataset[0]["label"]
    writable_memoryset.refresh()  # Refresh to ensure consistency after update
    assert writable_memoryset.get(memory_id).value == "i love soup so much"

    # test updating a memory instance
    memory = writable_memoryset[0]
    updated_memory = memory.update(value="i love soup even more")
    assert updated_memory is memory
    assert memory.value == "i love soup even more"
    assert memory.label == hf_dataset[0]["label"]

    # test updating multiple memories
    memory_ids = [memory.memory_id for memory in writable_memoryset[:2]]
    updated_memories = writable_memoryset.update(
        [
            dict(memory_id=memory_ids[0], value="i love soup so much"),
            dict(memory_id=memory_ids[1], value="cats are so cute"),
        ]
    )
    assert updated_memories[0].value == "i love soup so much"
    assert updated_memories[1].value == "cats are so cute"


def test_delete_memories(writable_memoryset: LabeledMemoryset):
    # We've combined the delete tests into one to avoid multiple expensive requests for a writable_memoryset

    # test deleting a single memory
    prev_length = writable_memoryset.length
    memory_id = writable_memoryset[0].memory_id
    writable_memoryset.delete(memory_id)
    with pytest.raises(LookupError):
        writable_memoryset.get(memory_id)
    assert writable_memoryset.length == prev_length - 1

    # test deleting multiple memories
    prev_length = writable_memoryset.length
    writable_memoryset.delete([writable_memoryset[0].memory_id, writable_memoryset[1].memory_id])
    assert writable_memoryset.length == prev_length - 2


def test_clone_memoryset(readonly_memoryset: LabeledMemoryset):
    cloned_memoryset = readonly_memoryset.clone(
        "test_cloned_memoryset", embedding_model=PretrainedEmbeddingModel.DISTILBERT
    )
    assert cloned_memoryset is not None
    assert cloned_memoryset.name == "test_cloned_memoryset"
    assert cloned_memoryset.length == readonly_memoryset.length
    assert cloned_memoryset.embedding_model == PretrainedEmbeddingModel.DISTILBERT
    assert cloned_memoryset.insertion_status == Status.COMPLETED


def test_embedding_evaluation(eval_datasource: Datasource):
    results = LabeledMemoryset.run_embedding_evaluation(
        eval_datasource, embedding_models=["CDE_SMALL"], neighbor_count=2
    )
    assert isinstance(results, list)
    assert len(results) == 1
    assert results[0] is not None
    assert results[0]["embedding_model_name"] == "CDE_SMALL"
    assert results[0]["embedding_model_path"] == "OrcaDB/cde-small-v1"


@pytest.fixture(scope="function")
async def test_group_potential_duplicates(writable_memoryset: LabeledMemoryset):
    writable_memoryset.insert(
        [
            dict(value="raspberry soup Is my favorite", label=0),
            dict(value="Raspberry soup is MY favorite", label=0),
            dict(value="rAspberry soup is my favorite", label=0),
            dict(value="raSpberry SOuP is my favorite", label=0),
            dict(value="rasPberry SOuP is my favorite", label=0),
            dict(value="bunny rabbit Is not my mom", label=1),
            dict(value="bunny rabbit is not MY mom", label=1),
            dict(value="bunny rabbit Is not my moM", label=1),
            dict(value="bunny rabbit is not my mom", label=1),
            dict(value="bunny rabbit is not my mom", label=1),
            dict(value="bunny rabbit is not My mom", label=1),
        ]
    )

    writable_memoryset.analyze({"name": "duplicate", "possible_duplicate_threshold": 0.97})
    response = writable_memoryset.get_potential_duplicate_groups()
    assert isinstance(response, list)
    assert sorted([len(res) for res in response]) == [5, 6]  # 5 favorite, 6 mom


def test_get_cascading_edits_suggestions(writable_memoryset: LabeledMemoryset):
    # Insert a memory to test cascading edits
    SOUP = 0
    CATS = 1
    query_text = "i love soup"  # from SAMPLE_DATA in conftest.py
    mislabeled_soup_text = "soup is comfort in a bowl"
    writable_memoryset.insert(
        [
            dict(value=mislabeled_soup_text, label=CATS),  # mislabeled soup memory
        ]
    )

    # Fetch the memory to update
    memory = writable_memoryset.query(filters=[("value", "==", query_text)])[0]

    # Update the label and get cascading edit suggestions
    suggestions = writable_memoryset.get_cascading_edits_suggestions(
        memory=memory,
        old_label=CATS,
        new_label=SOUP,
        max_neighbors=10,
        max_validation_neighbors=5,
    )

    # Validate the suggestions
    assert len(suggestions) == 1
    assert suggestions[0]["neighbor"]["value"] == mislabeled_soup_text


def test_analyze_invalid_analysis_name(readonly_memoryset: LabeledMemoryset):
    """Test that analyze() raises ValueError for invalid analysis names"""
    memoryset = LabeledMemoryset.open(readonly_memoryset.name)

    # Test with string input
    with pytest.raises(ValueError) as excinfo:
        memoryset.analyze("invalid_name")
    assert "Invalid analysis name: invalid_name" in str(excinfo.value)
    assert "Valid names are:" in str(excinfo.value)

    # Test with dict input
    with pytest.raises(ValueError) as excinfo:
        memoryset.analyze({"name": "invalid_name"})
    assert "Invalid analysis name: invalid_name" in str(excinfo.value)
    assert "Valid names are:" in str(excinfo.value)

    # Test with multiple analyses where one is invalid
    with pytest.raises(ValueError) as excinfo:
        memoryset.analyze("duplicate", "invalid_name")
    assert "Invalid analysis name: invalid_name" in str(excinfo.value)
    assert "Valid names are:" in str(excinfo.value)

    # Test with valid analysis names
    result = memoryset.analyze("duplicate", "cluster")
    assert isinstance(result, dict)
    assert "duplicate" in result
    assert "cluster" in result


def test_drop_memoryset(writable_memoryset: LabeledMemoryset):
    # NOTE: Keep this test at the end to ensure the memoryset is dropped after all tests.
    # Otherwise, it would be recreated on the next test run if it were dropped earlier, and
    # that's expensive.
    assert LabeledMemoryset.exists(writable_memoryset.name)
    LabeledMemoryset.drop(writable_memoryset.name)
    assert not LabeledMemoryset.exists(writable_memoryset.name)


def test_scored_memoryset(scored_memoryset: ScoredMemoryset):
    assert scored_memoryset.length == 16
    assert isinstance(scored_memoryset[0], ScoredMemory)
    assert scored_memoryset[0].value == "i love soup"
    assert scored_memoryset[0].score is not None
    assert scored_memoryset[0].metadata == {"key": "g1", "source_id": "s1", "label": 0}
    lookup = scored_memoryset.search("i love soup", count=1)
    assert len(lookup) == 1
    assert lookup[0].score < 0.11


@skip_in_prod("Production memorysets do not have session consistency guarantees")
def test_update_scored_memory(scored_memoryset: ScoredMemoryset):
    # we are only updating an inconsequential metadata field so that we don't affect other tests
    memory = scored_memoryset[0]
    assert memory.label == 0
    scored_memoryset.update(dict(memory_id=memory.memory_id, label=3))
    assert scored_memoryset[0].label == 3
    memory.update(label=4)
    assert scored_memoryset[0].label == 4
