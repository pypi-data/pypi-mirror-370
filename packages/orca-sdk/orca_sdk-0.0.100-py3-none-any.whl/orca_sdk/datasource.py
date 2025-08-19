from __future__ import annotations

import logging
import os
import tempfile
import zipfile
from datetime import datetime
from io import BytesIO
from os import PathLike
from pathlib import Path
from typing import Literal, Union, cast

import pandas as pd
import pyarrow as pa
from datasets import Dataset, DatasetDict
from httpx._types import FileTypes  # type: ignore
from pyarrow import parquet
from torch.utils.data import DataLoader as TorchDataLoader
from torch.utils.data import Dataset as TorchDataset
from tqdm.auto import tqdm

from ._utils.common import CreateMode, DropMode
from ._utils.data_parsing import hf_dataset_from_torch
from ._utils.tqdm_file_reader import TqdmFileReader
from .client import DatasourceMetadata, orca_api


def _upload_files_to_datasource(
    name: str,
    file_paths: list[Path],
    description: str | None = None,
) -> DatasourceMetadata:
    """
    Helper function to upload files to create a datasource using manual HTTP requests.

    This bypasses the generated client because it doesn't handle file uploads properly.

    Params:
        name: Name for the datasource
        file_paths: List of file paths to upload
        description: Optional description for the datasource

    Returns:
        Metadata for the created datasource
    """
    files: list[tuple[Literal["files"], FileTypes]] = []

    # Calculate total size for all files
    total_size = sum(file_path.stat().st_size for file_path in file_paths)

    with tqdm(total=total_size, unit="B", unit_scale=True, desc="Uploading") as pbar:
        for file_path in file_paths:
            buffered_reader = open(file_path, "rb")
            tqdm_reader = TqdmFileReader(buffered_reader, pbar)
            files.append(("files", (file_path.name, cast(bytes, tqdm_reader))))

        # Use manual HTTP request for file uploads
        metadata = orca_api.POST(
            "/datasource/upload",
            files=files,
            data={"name": name, "description": description},
        )

    return metadata


def _handle_existing_datasource(name: str, if_exists: CreateMode) -> Union["Datasource", None]:
    """
    Helper function to handle the common pattern of checking if a datasource exists
    and taking action based on the if_exists parameter.

    Params:
        name: Name of the datasource to check
        if_exists: What to do if a datasource with the same name already exists

    Returns:
        Datasource instance if opening existing, None if should proceed with creation

    Raises:
        ValueError: If the datasource already exists and if_exists is "error"
    """
    if Datasource.exists(name):
        if if_exists == "error":
            raise ValueError(f"Dataset with name {name} already exists")
        elif if_exists == "open":
            return Datasource.open(name)
    return None


class Datasource:
    """
    A Handle to a datasource in the OrcaCloud

    A Datasource is a collection of data saved to the OrcaCloud that can be used to create a [`Memoryset`][orca_sdk.LabeledMemoryset].
    It can be created from a Hugging Face Dataset, a PyTorch DataLoader or Dataset, a list of dictionaries, a dictionary of columns, a pandas DataFrame, a pyarrow Table, or a local file.

    Attributes:
        id: Unique identifier for the datasource
        name: Unique name of the datasource
        description: Optional description of the datasource
        length: Number of rows in the datasource
        created_at: When the datasource was created
        columns: Dictionary of column names and types
    """

    id: str
    name: str
    description: str | None
    length: int
    created_at: datetime
    updated_at: datetime
    columns: dict[str, str]

    def __init__(self, metadata: DatasourceMetadata):
        # for internal use only, do not document
        self.id = metadata["id"]
        self.name = metadata["name"]
        self.length = metadata["length"]
        self.created_at = datetime.fromisoformat(metadata["created_at"])
        self.updated_at = datetime.fromisoformat(metadata["updated_at"])
        self.description = metadata["description"]
        self.columns = {
            column["name"]: (
                f"enum({', '.join(f'{option!r}' for option in column['enum_options'] or []) if 'enum_options' in column else ''})"
                if column["type"] == "ENUM"
                else "str" if column["type"] == "STRING" else column["type"].lower()
            )
            for column in metadata["columns"]
        }

    def __eq__(self, other) -> bool:
        return isinstance(other, Datasource) and self.id == other.id

    def __repr__(self) -> str:
        return (
            "Datasource({\n"
            + f"    name: '{self.name}',\n"
            + f"    length: {self.length},\n"
            + "    columns: {{\n        "
            + "\n        ".join([f"{k}: {v}" for k, v in self.columns.items()])
            + "\n    }}\n"
            + "})"
        )

    @classmethod
    def from_hf_dataset(
        cls, name: str, dataset: Dataset, if_exists: CreateMode = "error", description: str | None = None
    ) -> Datasource:
        """
        Create a new datasource from a Hugging Face Dataset

        Params:
            name: Required name for the new datasource (must be unique)
            dataset: The Hugging Face Dataset to create the datasource from
            if_exists: What to do if a datasource with the same name already exists, defaults to
                `"error"`. Other option is `"open"` to open the existing datasource.
            description: Optional description for the datasource

        Returns:
            A handle to the new datasource in the OrcaCloud

        Raises:
            ValueError: If the datasource already exists and if_exists is `"error"`
        """
        # Check if datasource already exists and handle accordingly
        existing = _handle_existing_datasource(name, if_exists)
        if existing is not None:
            return existing

        with tempfile.TemporaryDirectory() as tmp_dir:
            dataset.save_to_disk(tmp_dir)

            # Get all file paths in the directory
            file_paths = list(Path(tmp_dir).iterdir())

            # Use the helper function to upload files
            metadata = _upload_files_to_datasource(name, file_paths, description)
            return cls(metadata=metadata)

    @classmethod
    def from_hf_dataset_dict(
        cls,
        name: str,
        dataset_dict: DatasetDict,
        if_exists: CreateMode = "error",
        description: dict[str, str | None] | str | None = None,
    ) -> dict[str, Datasource]:
        """
        Create datasources from a Hugging Face DatasetDict

        Params:
            name: Name prefix for the new datasources, will be suffixed with the dataset name
            dataset_dict: The Hugging Face DatasetDict to create the datasources from
            if_exists: What to do if a datasource with the same name already exists, defaults to
                `"error"`. Other option is `"open"` to open the existing datasource.
            description: Optional description for the datasources, can be a string or a dictionary of dataset names to descriptions

        Returns:
            A dictionary of datasource handles, keyed by the dataset name

        Raises:
            ValueError: If a datasource already exists and if_exists is `"error"`
        """
        if description is None or isinstance(description, str):
            description = {dataset_name: description for dataset_name in dataset_dict.keys()}
        return {
            dataset_name: cls.from_hf_dataset(
                f"{name}_{dataset_name}", dataset, if_exists=if_exists, description=description[dataset_name]
            )
            for dataset_name, dataset in dataset_dict.items()
        }

    @classmethod
    def from_pytorch(
        cls,
        name: str,
        torch_data: TorchDataLoader | TorchDataset,
        column_names: list[str] | None = None,
        if_exists: CreateMode = "error",
        description: str | None = None,
    ) -> Datasource:
        """
        Create a new datasource from a PyTorch DataLoader or Dataset

        Params:
            name: Required name for the new datasource (must be unique)
            torch_data: The PyTorch DataLoader or Dataset to create the datasource from
            column_names: If the provided dataset or data loader returns unnamed tuples, this
                argument must be provided to specify the names of the columns.
            if_exists: What to do if a datasource with the same name already exists, defaults to
                `"error"`. Other option is `"open"` to open the existing datasource.
            description: Optional description for the datasource

        Returns:
            A handle to the new datasource in the OrcaCloud

        Raises:
            ValueError: If the datasource already exists and if_exists is `"error"`
        """
        hf_dataset = hf_dataset_from_torch(torch_data, column_names=column_names)
        return cls.from_hf_dataset(name, hf_dataset, if_exists=if_exists, description=description)

    @classmethod
    def from_list(
        cls, name: str, data: list[dict], if_exists: CreateMode = "error", description: str | None = None
    ) -> Datasource:
        """
        Create a new datasource from a list of dictionaries

        Params:
            name: Required name for the new datasource (must be unique)
            data: The list of dictionaries to create the datasource from
            if_exists: What to do if a datasource with the same name already exists, defaults to
                `"error"`. Other option is `"open"` to open the existing datasource.
            description: Optional description for the datasource

        Returns:
            A handle to the new datasource in the OrcaCloud

        Raises:
            ValueError: If the datasource already exists and if_exists is `"error"`

        Examples:
            >>> Datasource.from_list("my_datasource", [{"text": "Hello, world!", "label": 1}, {"text": "Goodbye", "label": 0}])
        """
        # Check if datasource already exists and handle accordingly
        existing = _handle_existing_datasource(name, if_exists)
        if existing is not None:
            return existing

        metadata = orca_api.POST(
            "/datasource",
            json={"name": name, "description": description, "content": data},
        )
        return cls(metadata=metadata)

    @classmethod
    def from_dict(
        cls, name: str, data: dict, if_exists: CreateMode = "error", description: str | None = None
    ) -> Datasource:
        """
        Create a new datasource from a dictionary of columns

        Params:
            name: Required name for the new datasource (must be unique)
            data: The dictionary of columns to create the datasource from
            if_exists: What to do if a datasource with the same name already exists, defaults to
                `"error"`. Other option is `"open"` to open the existing datasource.
            description: Optional description for the datasource

        Returns:
            A handle to the new datasource in the OrcaCloud

        Raises:
            ValueError: If the datasource already exists and if_exists is `"error"`

        Examples:
            >>> Datasource.from_dict("my_datasource", {"text": ["Hello, world!", "Goodbye"], "label": [1, 0]})
        """
        # Check if datasource already exists and handle accordingly
        existing = _handle_existing_datasource(name, if_exists)
        if existing is not None:
            return existing

        metadata = orca_api.POST(
            "/datasource",
            json={"name": name, "description": description, "content": data},
        )
        return cls(metadata=metadata)

    @classmethod
    def from_pandas(
        cls, name: str, dataframe: pd.DataFrame, if_exists: CreateMode = "error", description: str | None = None
    ) -> Datasource:
        """
        Create a new datasource from a pandas DataFrame

        Params:
            name: Required name for the new datasource (must be unique)
            dataframe: The pandas DataFrame to create the datasource from
            if_exists: What to do if a datasource with the same name already exists, defaults to
                `"error"`. Other option is `"open"` to open the existing datasource.
            description: Optional description for the datasource

        Returns:
            A handle to the new datasource in the OrcaCloud

        Raises:
            ValueError: If the datasource already exists and if_exists is `"error"`
        """
        dataset = Dataset.from_pandas(dataframe)
        return cls.from_hf_dataset(name, dataset, if_exists=if_exists, description=description)

    @classmethod
    def from_arrow(
        cls, name: str, pyarrow_table: pa.Table, if_exists: CreateMode = "error", description: str | None = None
    ) -> Datasource:
        """
        Create a new datasource from a pyarrow Table

        Params:
            name: Required name for the new datasource (must be unique)
            pyarrow_table: The pyarrow Table to create the datasource from
            if_exists: What to do if a datasource with the same name already exists, defaults to
                `"error"`. Other option is `"open"` to open the existing datasource.
            description: Optional description for the datasource

        Returns:
            A handle to the new datasource in the OrcaCloud

        Raises:
            ValueError: If the datasource already exists and if_exists is `"error"`
        """
        # Check if datasource already exists and handle accordingly
        existing = _handle_existing_datasource(name, if_exists)
        if existing is not None:
            return existing

        # Write to bytes buffer
        buffer = BytesIO()
        parquet.write_table(pyarrow_table, buffer)
        parquet_bytes = buffer.getvalue()

        metadata = orca_api.POST(
            "/datasource/upload",
            files=[("files", ("data.parquet", parquet_bytes))],
            data={"name": name, "description": description},
        )

        return cls(metadata=metadata)

    @classmethod
    def from_disk(
        cls, name: str, file_path: str | PathLike, if_exists: CreateMode = "error", description: str | None = None
    ) -> Datasource:
        """
        Create a new datasource from a local file

        Params:
            name: Required name for the new datasource (must be unique)
            file_path: Path to the file on disk to create the datasource from. The file type will
                be inferred from the file extension. The following file types are supported:

                - .pkl: [`Pickle`][pickle] files containing lists of dictionaries or dictionaries of columns
                - .json/.jsonl: [`JSON`][json] and [`JSON`] Lines files
                - .csv: [`CSV`][csv] files
                - .parquet: [`Parquet`][pyarrow.parquet.ParquetFile] files
                - dataset directory: Directory containing a saved HuggingFace [`Dataset`][datasets.Dataset]

            if_exists: What to do if a datasource with the same name already exists, defaults to
                `"error"`. Other option is `"open"` to open the existing datasource.
            description: Optional description for the datasource

        Returns:
            A handle to the new datasource in the OrcaCloud

        Raises:
            ValueError: If the datasource already exists and if_exists is `"error"`
        """
        # Check if datasource already exists and handle accordingly
        existing = _handle_existing_datasource(name, if_exists)
        if existing is not None:
            return existing

        file_path = Path(file_path)

        # For dataset directories, use the upload endpoint with multiple files
        if file_path.is_dir():
            return cls.from_hf_dataset(
                name, Dataset.load_from_disk(file_path), if_exists=if_exists, description=description
            )

        # For single files, use the helper function to upload files
        metadata = _upload_files_to_datasource(name, [file_path], description)

        return cls(metadata=metadata)

    @classmethod
    def open(cls, name_or_id: str) -> Datasource:
        """
        Get a handle to a datasource by name or id in the OrcaCloud

        Params:
            name_or_id: The name or unique identifier of the datasource to get

        Returns:
            A handle to the existing datasource in the OrcaCloud

        Raises:
            LookupError: If the datasource does not exist
        """
        return cls(orca_api.GET("/datasource/{name_or_id}", params={"name_or_id": name_or_id}))

    @classmethod
    def exists(cls, name_or_id: str) -> bool:
        """
        Check if a datasource exists in the OrcaCloud

        Params:
            name_or_id: The name or id of the datasource to check

        Returns:
            `True` if the datasource exists, `False` otherwise
        """
        try:
            cls.open(name_or_id)
            return True
        except LookupError:
            return False

    @classmethod
    def all(cls) -> list[Datasource]:
        """
        List all datasource handles in the OrcaCloud

        Returns:
            A list of all datasource handles in the OrcaCloud
        """
        return [cls(metadata) for metadata in orca_api.GET("/datasource")]

    @classmethod
    def drop(cls, name_or_id: str, if_not_exists: DropMode = "error") -> None:
        """
        Delete a datasource from the OrcaCloud

        Params:
            name_or_id: The name or id of the datasource to delete
            if_not_exists: What to do if the datasource does not exist, defaults to
                `"error"`. Other options are `"ignore"` to do nothing.

        Raises:
            LookupError: If the datasource does not exist and if_not_exists is `"error"`
        """
        try:
            orca_api.DELETE("/datasource/{name_or_id}", params={"name_or_id": name_or_id})
            logging.info(f"Deleted datasource {name_or_id}")
        except LookupError:
            if if_not_exists == "error":
                raise

    def __len__(self) -> int:
        return self.length

    def download(
        self, output_dir: str | PathLike, file_type: Literal["hf_dataset", "json", "csv"] = "hf_dataset"
    ) -> None:
        """
        Download the datasource to a specified path in the specified format type

        Params:
            output_dir: The local directory where the downloaded file will be saved.
            file_type: The type of file to download.

        Returns:
            None
        """
        extension = "zip" if file_type == "hf_dataset" else file_type
        output_path = Path(output_dir) / f"{self.name}.{extension}"
        with open(output_path, "wb") as download_file:
            with orca_api.stream("GET", f"/datasource/{self.id}/download", params={"file_type": file_type}) as response:
                total_chunks = int(response.headers["X-Total-Chunks"]) if "X-Total-Chunks" in response.headers else None
                with tqdm(desc=f"Downloading", total=total_chunks, disable=total_chunks is None) as progress:
                    for chunk in response.iter_bytes():
                        download_file.write(chunk)
                        progress.update(1)

        # extract the zip file
        if extension == "zip":
            extract_dir = Path(output_dir) / self.name
            with zipfile.ZipFile(output_path, "r") as zip_ref:
                zip_ref.extractall(extract_dir)
            output_path.unlink()  # Remove the zip file after extraction
            logging.info(f"Downloaded {extract_dir}")
        else:
            logging.info(f"Downloaded {output_path}")

    def to_list(self) -> list[dict]:
        """
        Convert the datasource to a list of dictionaries.

        Returns:
            A list of dictionaries representation of the datasource.
        """
        return orca_api.GET("/datasource/{name_or_id}/download", params={"name_or_id": self.id, "file_type": "json"})
