import pickle
from dataclasses import asdict, is_dataclass
from os import PathLike
from tempfile import TemporaryDirectory
from typing import Any, cast

from datasets import Dataset
from torch.utils.data import DataLoader as TorchDataLoader
from torch.utils.data import Dataset as TorchDataset


def parse_dict_like(item: Any, column_names: list[str] | None = None) -> dict:
    if isinstance(item, dict):
        return item

    if isinstance(item, tuple):
        if column_names is not None:
            assert len(item) == len(column_names)
            return {column_names[i]: item[i] for i in range(len(item))}
        elif hasattr(item, "_fields") and all(isinstance(field, str) for field in item._fields):  # type: ignore
            return {field: getattr(item, field) for field in item._fields}  # type: ignore
        else:
            raise ValueError("For datasets that return unnamed tuples, please provide column_names argument")

    if is_dataclass(item) and not isinstance(item, type):
        return asdict(item)

    raise ValueError(f"Cannot parse {type(item)}")


def parse_batch(batch: Any, column_names: list[str] | None = None) -> list[dict]:
    if isinstance(batch, list):
        return [parse_dict_like(item, column_names) for item in batch]

    batch = parse_dict_like(batch, column_names)
    keys = list(batch.keys())
    batch_size = len(batch[keys[0]])
    for key in keys:
        if not len(batch[key]) == batch_size:
            raise ValueError(f"Batch must consist of values of the same length, but {key} has length {len(batch[key])}")
    return [{key: batch[key][idx] for key in keys} for idx in range(batch_size)]


def hf_dataset_from_torch(
    torch_data: TorchDataLoader | TorchDataset, column_names: list[str] | None = None, ignore_cache=False
) -> Dataset:
    """
    Create a HuggingFace Dataset from a PyTorch DataLoader or Dataset.

    NOTE:  It's important to ignore the cached files when testing (i.e., ignore_cache=Ture), because
    cached results can ignore changes you've made to tests. This can make a test appear to succeed
    when it's actually broken or vice versa.

    Params:
        torch_data: A PyTorch DataLoader or Dataset object to create the HuggingFace Dataset from.
        column_names: Optional list of column names to use for the dataset. If not provided,
            the column names will be inferred from the data.
        ignore_cache: If True, the dataset will not be cached on disk.
    Returns:
        A HuggingFace Dataset object containing the data from the PyTorch DataLoader or Dataset.
    """
    if isinstance(torch_data, TorchDataLoader):
        dataloader = torch_data
    else:
        dataloader = TorchDataLoader(torch_data, batch_size=1, collate_fn=lambda x: x)

    def generator():
        for batch in dataloader:
            yield from parse_batch(batch, column_names=column_names)

    if ignore_cache:
        with TemporaryDirectory() as temp_dir:
            ds = Dataset.from_generator(generator, cache_dir=temp_dir)
    else:
        ds = Dataset.from_generator(generator)

    if not isinstance(ds, Dataset):
        raise ValueError(f"Failed to create dataset from generator: {type(ds)}")
    return ds


def hf_dataset_from_disk(file_path: str | PathLike) -> Dataset:
    """
    Load a dataset from disk into a HuggingFace Dataset object.

    Params:
        file_path: Path to the file on disk to create the memoryset from. The file type will
                be inferred from the file extension. The following file types are supported:

                - .pkl: [`Pickle`][pickle] files containing lists of dictionaries or dictionaries of columns
                - .json/.jsonl: [`JSON`][json] and [`JSON`] Lines files
                - .csv: [`CSV`][csv] files
                - .parquet: [`Parquet`](https://arrow.apache.org/docs/python/generated/pyarrow.parquet.ParquetFile.html#pyarrow.parquet.ParquetFile) files
                - dataset directory: Directory containing a saved HuggingFace [`Dataset`][datasets.Dataset]

    Returns:
        A HuggingFace Dataset object containing the loaded data.

    Raises:
        [`ValueError`][ValueError]: If the pickle file contains unsupported data types or if
            loading the dataset fails for any reason.
    """
    if str(file_path).endswith(".pkl"):
        data = pickle.load(open(file_path, "rb"))
        if isinstance(data, list):
            return Dataset.from_list(data)
        elif isinstance(data, dict):
            return Dataset.from_dict(data)
        else:
            raise ValueError(f"Unsupported pickle file: {file_path}")
    elif str(file_path).endswith(".json"):
        hf_dataset = Dataset.from_json(file_path)
    elif str(file_path).endswith(".jsonl"):
        hf_dataset = Dataset.from_json(file_path)
    elif str(file_path).endswith(".csv"):
        hf_dataset = Dataset.from_csv(file_path)
    elif str(file_path).endswith(".parquet"):
        hf_dataset = Dataset.from_parquet(file_path)
    else:
        try:
            hf_dataset = Dataset.load_from_disk(file_path)
        except Exception as e:
            raise ValueError(f"Failed to load dataset from disk: {e}")

    return cast(Dataset, hf_dataset)
