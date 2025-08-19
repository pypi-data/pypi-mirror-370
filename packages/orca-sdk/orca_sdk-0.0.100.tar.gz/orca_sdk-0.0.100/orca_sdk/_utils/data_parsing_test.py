import json
import pickle
import tempfile
from collections import namedtuple
from dataclasses import dataclass

import pandas as pd
import pytest
from datasets import Dataset
from datasets.exceptions import DatasetGenerationError
from torch.utils.data import DataLoader as TorchDataLoader
from torch.utils.data import Dataset as TorchDataset

from ..conftest import SAMPLE_DATA
from .data_parsing import hf_dataset_from_disk, hf_dataset_from_torch


class PytorchDictDataset(TorchDataset):
    def __init__(self):
        self.data = SAMPLE_DATA

    def __getitem__(self, i):
        return self.data[i]

    def __len__(self):
        return len(self.data)


def test_hf_dataset_from_torch_dict():
    # Given a Pytorch dataset that returns a dictionary for each item
    dataset = PytorchDictDataset()
    hf_dataset = hf_dataset_from_torch(dataset, ignore_cache=True)
    # Then the HF dataset should be created successfully
    assert isinstance(hf_dataset, Dataset)
    assert len(hf_dataset) == len(dataset)
    assert set(hf_dataset.column_names) == {"value", "label", "key", "score", "source_id"}


class PytorchTupleDataset(TorchDataset):
    def __init__(self):
        self.data = SAMPLE_DATA

    def __getitem__(self, i):
        return self.data[i]["value"], self.data[i]["label"]

    def __len__(self):
        return len(self.data)


def test_hf_dataset_from_torch_tuple():
    # Given a Pytorch dataset that returns a tuple for each item
    dataset = PytorchTupleDataset()
    # And the correct number of column names passed in
    hf_dataset = hf_dataset_from_torch(dataset, column_names=["value", "label"], ignore_cache=True)
    # Then the HF dataset should be created successfully
    assert isinstance(hf_dataset, Dataset)
    assert len(hf_dataset) == len(dataset)
    assert hf_dataset.column_names == ["value", "label"]


def test_hf_dataset_from_torch_tuple_error():
    # Given a Pytorch dataset that returns a tuple for each item
    dataset = PytorchTupleDataset()
    # Then the HF dataset should raise an error if no column names are passed in
    with pytest.raises(DatasetGenerationError):
        hf_dataset_from_torch(dataset, ignore_cache=True)


def test_hf_dataset_from_torch_tuple_error_not_enough_columns():
    # Given a Pytorch dataset that returns a tuple for each item
    dataset = PytorchTupleDataset()
    # Then the HF dataset should raise an error if not enough column names are passed in
    with pytest.raises(DatasetGenerationError):
        hf_dataset_from_torch(dataset, column_names=["value"], ignore_cache=True)


DatasetTuple = namedtuple("DatasetTuple", ["value", "label"])


class PytorchNamedTupleDataset(TorchDataset):
    def __init__(self):
        self.data = SAMPLE_DATA

    def __getitem__(self, i):
        return DatasetTuple(self.data[i]["value"], self.data[i]["label"])

    def __len__(self):
        return len(self.data)


def test_hf_dataset_from_torch_named_tuple():
    # Given a Pytorch dataset that returns a namedtuple for each item
    dataset = PytorchNamedTupleDataset()
    # And no column names are passed in
    hf_dataset = hf_dataset_from_torch(dataset, ignore_cache=True)
    # Then the HF dataset should be created successfully
    assert isinstance(hf_dataset, Dataset)
    assert len(hf_dataset) == len(dataset)
    assert hf_dataset.column_names == ["value", "label"]


@dataclass
class DatasetItem:
    text: str
    label: int


class PytorchDataclassDataset(TorchDataset):
    def __init__(self):
        self.data = SAMPLE_DATA

    def __getitem__(self, i):
        return DatasetItem(text=self.data[i]["value"], label=self.data[i]["label"])

    def __len__(self):
        return len(self.data)


def test_hf_dataset_from_torch_dataclass():
    # Given a Pytorch dataset that returns a dataclass for each item
    dataset = PytorchDataclassDataset()
    hf_dataset = hf_dataset_from_torch(dataset, ignore_cache=True)
    # Then the HF dataset should be created successfully
    assert isinstance(hf_dataset, Dataset)
    assert len(hf_dataset) == len(dataset)
    assert hf_dataset.column_names == ["text", "label"]


class PytorchInvalidDataset(TorchDataset):
    def __init__(self):
        self.data = SAMPLE_DATA

    def __getitem__(self, i):
        return [self.data[i]["value"], self.data[i]["label"]]

    def __len__(self):
        return len(self.data)


def test_hf_dataset_from_torch_invalid_dataset():
    # Given a Pytorch dataset that returns a list for each item
    dataset = PytorchInvalidDataset()
    # Then the HF dataset should raise an error
    with pytest.raises(DatasetGenerationError):
        hf_dataset_from_torch(dataset, ignore_cache=True)


def test_hf_dataset_from_torchdataloader():
    # Given a Pytorch dataloader that returns a column-oriented batch of items
    dataset = PytorchDictDataset()

    def collate_fn(x: list[dict]):
        return {"value": [item["value"] for item in x], "label": [item["label"] for item in x]}

    dataloader = TorchDataLoader(dataset, batch_size=3, collate_fn=collate_fn)
    hf_dataset = hf_dataset_from_torch(dataloader, ignore_cache=True)
    # Then the HF dataset should be created successfully
    assert isinstance(hf_dataset, Dataset)
    assert len(hf_dataset) == len(dataset)
    assert hf_dataset.column_names == ["value", "label"]


def test_hf_dataset_from_disk_pickle_list():
    with tempfile.NamedTemporaryFile(suffix=".pkl") as temp_file:
        # Given a pickle file with test data that is a list
        test_data = [{"value": f"test_{i}", "label": i % 2} for i in range(30)]
        with open(temp_file.name, "wb") as f:
            pickle.dump(test_data, f)
        dataset = hf_dataset_from_disk(temp_file.name)
        # Then the HF dataset should be created successfully
        assert isinstance(dataset, Dataset)
        assert len(dataset) == 30
        assert dataset.column_names == ["value", "label"]


def test_hf_dataset_from_disk_pickle_dict():
    with tempfile.NamedTemporaryFile(suffix=".pkl") as temp_file:
        # Given a pickle file with test data that is a dict
        test_data = {"value": [f"test_{i}" for i in range(30)], "label": [i % 2 for i in range(30)]}
        with open(temp_file.name, "wb") as f:
            pickle.dump(test_data, f)
        dataset = hf_dataset_from_disk(temp_file.name)
        # Then the HF dataset should be created successfully
        assert isinstance(dataset, Dataset)
        assert len(dataset) == 30
        assert dataset.column_names == ["value", "label"]


def test_hf_dataset_from_disk_json():
    with tempfile.NamedTemporaryFile(suffix=".json") as temp_file:
        # Given a JSON file with test data
        test_data = [{"value": f"test_{i}", "label": i % 2} for i in range(30)]
        with open(temp_file.name, "w") as f:
            json.dump(test_data, f)
        dataset = hf_dataset_from_disk(temp_file.name)
        # Then the HF dataset should be created successfully
        assert isinstance(dataset, Dataset)
        assert len(dataset) == 30
        assert dataset.column_names == ["value", "label"]


def test_hf_dataset_from_disk_jsonl():
    with tempfile.NamedTemporaryFile(suffix=".jsonl") as temp_file:
        # Given a JSONL file with test data
        test_data = [{"value": f"test_{i}", "label": i % 2} for i in range(30)]
        with open(temp_file.name, "w") as f:
            for item in test_data:
                f.write(json.dumps(item) + "\n")
        dataset = hf_dataset_from_disk(temp_file.name)
        # Then the HF dataset should be created successfully
        assert isinstance(dataset, Dataset)
        assert len(dataset) == 30
        assert dataset.column_names == ["value", "label"]


def test_hf_dataset_from_disk_csv():
    with tempfile.NamedTemporaryFile(suffix=".csv") as temp_file:
        # Given a CSV file with test data
        test_data = [{"value": f"test_{i}", "label": i % 2} for i in range(30)]
        with open(temp_file.name, "w") as f:
            f.write("value,label\n")
            for item in test_data:
                f.write(f"{item['value']},{item['label']}\n")
        dataset = hf_dataset_from_disk(temp_file.name)
        # Then the HF dataset should be created successfully
        assert isinstance(dataset, Dataset)
        assert len(dataset) == 30
        assert dataset.column_names == ["value", "label"]


def test_hf_dataset_from_disk_parquet():
    with tempfile.NamedTemporaryFile(suffix=".parquet") as temp_file:
        # Given a Parquet file with test data
        data = {
            "value": [f"test_{i}" for i in range(30)],
            "label": [i % 2 for i in range(30)],
        }
        df = pd.DataFrame(data)
        df.to_parquet(temp_file.name)
        dataset = hf_dataset_from_disk(temp_file.name)
        # Then the HF dataset should be created successfully
        assert isinstance(dataset, Dataset)
        assert len(dataset) == 30
        assert dataset.column_names == ["value", "label"]
