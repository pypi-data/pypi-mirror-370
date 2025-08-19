import json
import os
import tempfile
from typing import cast
from uuid import uuid4

import numpy as np
import pandas as pd
import pyarrow as pa
import pytest
from datasets import Dataset

from .datasource import Datasource


def test_create_datasource(datasource, hf_dataset):
    assert datasource is not None
    assert datasource.name == "test_datasource"
    assert datasource.length == len(hf_dataset)


def test_create_datasource_unauthenticated(unauthenticated, hf_dataset):
    with pytest.raises(ValueError, match="Invalid API key"):
        Datasource.from_hf_dataset("test_datasource", hf_dataset)


def test_create_datasource_already_exists_error(hf_dataset, datasource):
    with pytest.raises(ValueError):
        Datasource.from_hf_dataset("test_datasource", hf_dataset, if_exists="error")


def test_create_datasource_already_exists_return(hf_dataset, datasource):
    returned_dataset = Datasource.from_hf_dataset("test_datasource", hf_dataset, if_exists="open")
    assert returned_dataset is not None
    assert returned_dataset.name == "test_datasource"
    assert returned_dataset.length == len(hf_dataset)


def test_open_datasource(datasource):
    fetched_datasource = Datasource.open(datasource.name)
    assert fetched_datasource is not None
    assert fetched_datasource.name == datasource.name
    assert fetched_datasource.length == len(datasource)


def test_open_datasource_unauthenticated(datasource, unauthenticated):
    with pytest.raises(ValueError, match="Invalid API key"):
        Datasource.open("test_datasource")


def test_open_datasource_invalid_input():
    with pytest.raises(ValueError, match=r"Invalid input:.*"):
        Datasource.open("not valid id")


def test_open_datasource_not_found():
    with pytest.raises(LookupError):
        Datasource.open(str(uuid4()))


def test_open_datasource_unauthorized(datasource, unauthorized):
    with pytest.raises(LookupError):
        Datasource.open(datasource.id)


def test_all_datasources(datasource):
    datasources = Datasource.all()
    assert len(datasources) > 0
    assert any(datasource.name == datasource.name for datasource in datasources)


def test_all_datasources_unauthenticated(unauthenticated):
    with pytest.raises(ValueError, match="Invalid API key"):
        Datasource.all()


def test_drop_datasource(hf_dataset):
    Datasource.from_hf_dataset("datasource_to_delete", hf_dataset)
    assert Datasource.exists("datasource_to_delete")
    Datasource.drop("datasource_to_delete")
    assert not Datasource.exists("datasource_to_delete")


def test_drop_datasource_unauthenticated(datasource, unauthenticated):
    with pytest.raises(ValueError, match="Invalid API key"):
        Datasource.drop(datasource.id)


def test_drop_datasource_not_found():
    with pytest.raises(LookupError):
        Datasource.drop(str(uuid4()))
    # ignores error if specified
    Datasource.drop(str(uuid4()), if_not_exists="ignore")


def test_drop_datasource_unauthorized(datasource, unauthorized):
    with pytest.raises(LookupError):
        Datasource.drop(datasource.id)


def test_drop_datasource_invalid_input():
    with pytest.raises(ValueError, match=r"Invalid input:.*"):
        Datasource.drop("not valid id")


def test_from_list():
    # Test creating datasource from list of dictionaries
    data = [
        {"column1": 1, "column2": "a"},
        {"column1": 2, "column2": "b"},
        {"column1": 3, "column2": "c"},
    ]
    datasource = Datasource.from_list(f"test_list_{uuid4()}", data)
    assert datasource.name.startswith("test_list_")
    assert datasource.length == 3
    assert "column1" in datasource.columns
    assert "column2" in datasource.columns


def test_from_dict():
    # Test creating datasource from dictionary of columns
    data = {
        "column1": [1, 2, 3],
        "column2": ["a", "b", "c"],
    }
    datasource = Datasource.from_dict(f"test_dict_{uuid4()}", data)
    assert datasource.name.startswith("test_dict_")
    assert datasource.length == 3
    assert "column1" in datasource.columns
    assert "column2" in datasource.columns


def test_from_pandas():
    # Test creating datasource from pandas DataFrame
    df = pd.DataFrame(
        {
            "column1": [1, 2, 3],
            "column2": ["a", "b", "c"],
        }
    )
    datasource = Datasource.from_pandas(f"test_pandas_{uuid4()}", df)
    assert datasource.name.startswith("test_pandas_")
    assert datasource.length == 3
    assert "column1" in datasource.columns
    assert "column2" in datasource.columns


def test_from_arrow():
    # Test creating datasource from pyarrow Table
    table = pa.table(
        {
            "column1": [1, 2, 3],
            "column2": ["a", "b", "c"],
        }
    )
    datasource = Datasource.from_arrow(f"test_arrow_{uuid4()}", table)
    assert datasource.name.startswith("test_arrow_")
    assert datasource.length == 3
    assert "column1" in datasource.columns
    assert "column2" in datasource.columns


def test_from_list_already_exists():
    # Test the if_exists parameter with from_list
    data = [{"column1": 1, "column2": "a"}]
    name = f"test_list_exists_{uuid4()}"

    # Create the first datasource
    datasource1 = Datasource.from_list(name, data)
    assert datasource1.length == 1

    # Try to create again with if_exists="error" (should raise)
    with pytest.raises(ValueError):
        Datasource.from_list(name, data, if_exists="error")

    # Try to create again with if_exists="open" (should return existing)
    datasource2 = Datasource.from_list(name, data, if_exists="open")
    assert datasource2.id == datasource1.id
    assert datasource2.name == datasource1.name


def test_from_dict_already_exists():
    # Test the if_exists parameter with from_dict
    data = {"column1": [1], "column2": ["a"]}
    name = f"test_dict_exists_{uuid4()}"

    # Create the first datasource
    datasource1 = Datasource.from_dict(name, data)
    assert datasource1.length == 1

    # Try to create again with if_exists="error" (should raise)
    with pytest.raises(ValueError):
        Datasource.from_dict(name, data, if_exists="error")

    # Try to create again with if_exists="open" (should return existing)
    datasource2 = Datasource.from_dict(name, data, if_exists="open")
    assert datasource2.id == datasource1.id
    assert datasource2.name == datasource1.name


def test_from_pandas_already_exists():
    # Test the if_exists parameter with from_pandas
    df = pd.DataFrame({"column1": [1], "column2": ["a"]})
    name = f"test_pandas_exists_{uuid4()}"

    # Create the first datasource
    datasource1 = Datasource.from_pandas(name, df)
    assert datasource1.length == 1

    # Try to create again with if_exists="error" (should raise)
    with pytest.raises(ValueError):
        Datasource.from_pandas(name, df, if_exists="error")

    # Try to create again with if_exists="open" (should return existing)
    datasource2 = Datasource.from_pandas(name, df, if_exists="open")
    assert datasource2.id == datasource1.id
    assert datasource2.name == datasource1.name


def test_from_arrow_already_exists():
    # Test the if_exists parameter with from_arrow
    table = pa.table({"column1": [1], "column2": ["a"]})
    name = f"test_arrow_exists_{uuid4()}"

    # Create the first datasource
    datasource1 = Datasource.from_arrow(name, table)
    assert datasource1.length == 1

    # Try to create again with if_exists="error" (should raise)
    with pytest.raises(ValueError):
        Datasource.from_arrow(name, table, if_exists="error")

    # Try to create again with if_exists="open" (should return existing)
    datasource2 = Datasource.from_arrow(name, table, if_exists="open")
    assert datasource2.id == datasource1.id
    assert datasource2.name == datasource1.name


def test_from_disk_csv():
    # Test creating datasource from CSV file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        f.write("column1,column2\n1,a\n2,b\n3,c")
        f.flush()

        try:
            datasource = Datasource.from_disk(f"test_csv_{uuid4()}", f.name)
            assert datasource.length == 3
            assert "column1" in datasource.columns
            assert "column2" in datasource.columns
        finally:
            os.unlink(f.name)


def test_from_disk_json():
    # Test creating datasource from JSON file
    import json

    data = [{"column1": 1, "column2": "a"}, {"column1": 2, "column2": "b"}]

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(data, f)
        f.flush()

        try:
            datasource = Datasource.from_disk(f"test_json_{uuid4()}", f.name)
            assert datasource.length == 2
            assert "column1" in datasource.columns
            assert "column2" in datasource.columns
        finally:
            os.unlink(f.name)


def test_from_disk_already_exists():
    # Test the if_exists parameter with from_disk
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        f.write("column1,column2\n1,a")
        f.flush()

        try:
            name = f"test_disk_exists_{uuid4()}"

            # Create the first datasource
            datasource1 = Datasource.from_disk(name, f.name)
            assert datasource1.length == 1

            # Try to create again with if_exists="error" (should raise)
            with pytest.raises(ValueError):
                Datasource.from_disk(name, f.name, if_exists="error")

            # Try to create again with if_exists="open" (should return existing)
            datasource2 = Datasource.from_disk(name, f.name, if_exists="open")
            assert datasource2.id == datasource1.id
            assert datasource2.name == datasource1.name
        finally:
            os.unlink(f.name)


def test_to_list(hf_dataset, datasource):
    assert datasource.to_list() == hf_dataset.to_list()


def test_download_datasource(hf_dataset, datasource):
    with tempfile.TemporaryDirectory() as temp_dir:
        # Dataset download
        datasource.download(temp_dir)
        downloaded_hf_dataset_dir = f"{temp_dir}/{datasource.name}"
        assert os.path.exists(downloaded_hf_dataset_dir)
        assert os.path.isdir(downloaded_hf_dataset_dir)
        assert not os.path.exists(f"{downloaded_hf_dataset_dir}.zip")
        dataset_from_downloaded_hf_dataset = Dataset.load_from_disk(downloaded_hf_dataset_dir)
        assert dataset_from_downloaded_hf_dataset.column_names == hf_dataset.column_names
        assert dataset_from_downloaded_hf_dataset.to_dict() == hf_dataset.to_dict()

        # JSON download
        datasource.download(temp_dir, file_type="json")
        downloaded_json_file = f"{temp_dir}/{datasource.name}.json"
        assert os.path.exists(downloaded_json_file)
        with open(downloaded_json_file, "r") as f:
            content = json.load(f)
            assert content == hf_dataset.to_list()

        # CSV download
        datasource.download(temp_dir, file_type="csv")
        downloaded_csv_file = f"{temp_dir}/{datasource.name}.csv"
        assert os.path.exists(downloaded_csv_file)
        dataset_from_downloaded_csv = cast(Dataset, Dataset.from_csv(downloaded_csv_file))
        assert dataset_from_downloaded_csv.column_names == hf_dataset.column_names
        assert (
            dataset_from_downloaded_csv.remove_columns("score").to_dict()
            == hf_dataset.remove_columns("score").to_dict()
        )
        assert np.allclose(dataset_from_downloaded_csv["score"], hf_dataset["score"])
