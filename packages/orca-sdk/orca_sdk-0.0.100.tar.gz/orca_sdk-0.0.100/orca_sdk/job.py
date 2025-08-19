from __future__ import annotations

import time
from datetime import datetime, timedelta
from enum import Enum
from typing import Callable, Generic, TypedDict, TypeVar, cast

from tqdm.auto import tqdm

from .client import TaskStatus, orca_api


class JobConfig(TypedDict):
    refresh_interval: int
    show_progress: bool
    max_wait: int


class Status(Enum):
    """Status of a cloud job in the task queue"""

    # the INITIALIZED state should never be returned by the API
    INITIALIZED = "INITIALIZED"
    """The job has been initialized"""

    DISPATCHED = "DISPATCHED"
    """The job has been queued and is waiting to be processed"""

    PROCESSING = "PROCESSING"
    """The job is being processed"""

    COMPLETED = "COMPLETED"
    """The job has been completed successfully"""

    FAILED = "FAILED"
    """The job has failed"""

    ABORTING = "ABORTING"
    """The job is being aborted"""

    ABORTED = "ABORTED"
    """The job has been aborted"""


TResult = TypeVar("TResult")


class Job(Generic[TResult]):
    """
    Handle to a job that is run in the OrcaCloud

    Attributes:
        id: Unique identifier for the job
        type: Type of the job
        status: Current status of the job
        steps_total: Total number of steps in the job, present if the job started processing
        steps_completed: Number of steps completed in the job, present if the job started processing
        completion: Percentage of the job that has been completed, present if the job started processing
        exception: Exception that occurred during the job, present if the status is `FAILED`
        value: Value of the result of the job, present if the status is `COMPLETED`
        created_at: When the job was queued for processing
        updated_at: When the job was last updated
        refreshed_at: When the job status was last refreshed

    Note:
        Accessing status and related attributes will refresh the job status in the background.
    """

    id: str
    type: str
    status: Status
    steps_total: int | None
    steps_completed: int | None
    exception: str | None
    value: TResult | None
    updated_at: datetime
    created_at: datetime
    refreshed_at: datetime

    @property
    def completion(self) -> float:
        """
        Percentage of the job that has been completed, present if the job started processing
        """
        return (self.steps_completed or 0) / self.steps_total if self.steps_total is not None else 0

    # Global configuration for all jobs
    config: JobConfig = {
        "refresh_interval": 3,
        "show_progress": True,
        "max_wait": 60 * 60,
    }

    def __repr__(self) -> str:
        return "Job({" + f" type: {self.type}, status: {self.status}, completion: {self.completion:.0%} " + "})"

    @classmethod
    def set_config(
        cls, *, refresh_interval: int | None = None, show_progress: bool | None = None, max_wait: int | None = None
    ):
        """
        Set global configuration for running jobs

        Args:
            refresh_interval: Time to wait between polling the job status in seconds, default is 3
            show_progress: Whether to show a progress bar when calling the wait method, default is True
            max_wait: Maximum time to wait for the job to complete in seconds, default is 1 hour
        """
        if refresh_interval is not None:
            cls.config["refresh_interval"] = refresh_interval
        if show_progress is not None:
            cls.config["show_progress"] = show_progress
        if max_wait is not None:
            cls.config["max_wait"] = max_wait

    @classmethod
    def query(
        cls,
        status: Status | list[Status] | None = None,
        type: str | list[str] | None = None,
        limit: int = 100,
        offset: int = 0,
        start: datetime | None = None,
        end: datetime | None = None,
    ) -> list[Job]:
        """
        Query the job queue for jobs matching the given filters

        Args:
            status: Optional status or list of statuses to filter by
            type: Optional type or list of types to filter by
            limit: Maximum number of jobs to return
            offset: Offset into the list of jobs to return
            start: Optional minimum creation time of the jobs to query for
            end: Optional maximum creation time of the jobs to query for

        Returns:
            List of jobs matching the given filters
        """
        paginated_tasks = orca_api.GET(
            "/task",
            params={
                "status": (
                    [s.value for s in status]
                    if isinstance(status, list)
                    else status.value if isinstance(status, Status) else None
                ),
                "type": type,
                "limit": limit,
                "offset": offset,
                "start_timestamp": start.isoformat() if start is not None else None,
                "end_timestamp": end.isoformat() if end is not None else None,
            },
        )

        # can't use constructor because it makes an API call, so we construct the objects manually
        return [
            (
                lambda t: (
                    obj := cls.__new__(cls),
                    setattr(obj, "id", t["id"]),
                    setattr(obj, "type", t["type"]),
                    setattr(obj, "status", Status(t["status"])),
                    setattr(obj, "steps_total", t["steps_total"]),
                    setattr(obj, "steps_completed", t["steps_completed"]),
                    setattr(obj, "exception", t["exception"]),
                    setattr(obj, "value", cast(TResult, t["result"]) if t["result"] is not None else None),
                    setattr(obj, "updated_at", datetime.fromisoformat(t["updated_at"])),
                    setattr(obj, "created_at", datetime.fromisoformat(t["created_at"])),
                    setattr(obj, "refreshed_at", datetime.now()),
                    obj,
                )[-1]
            )(t)
            for t in paginated_tasks["items"]
        ]

    def __init__(self, id: str, get_value: Callable[[], TResult | None] | None = None):
        """
        Create a handle to a job in the job queue

        Args:
            id: Unique identifier for the job
            get_value: Optional function to customize how the value is resolved, if not provided the result will be a dict
        """
        self.id = id
        task = orca_api.GET("/task/{task_id}", params={"task_id": id})

        self._get_value = get_value or (
            lambda: cast(TResult | None, orca_api.GET("/task/{task_id}", params={"task_id": id})["result"])
        )
        self.type = task["type"]
        self.status = Status(task["status"])
        self.steps_total = task["steps_total"]
        self.steps_completed = task["steps_completed"]
        self.exception = task["exception"]
        self.value = (
            None
            if task["status"] != "COMPLETED"
            else (
                get_value()
                if get_value is not None
                else cast(TResult, task["result"]) if task["result"] is not None else None
            )
        )
        self.updated_at = datetime.fromisoformat(task["updated_at"])
        self.created_at = datetime.fromisoformat(task["created_at"])
        self.refreshed_at = datetime.now()

    def refresh(self, throttle: float = 0):
        """
        Refresh the status and progress of the job

        Params:
            throttle: Minimum time in seconds between refreshes
        """
        current_time = datetime.now()
        # Skip refresh if last refresh was too recent
        if (current_time - self.refreshed_at) < timedelta(seconds=throttle):
            return
        self.refreshed_at = current_time

        status_info = orca_api.GET("/task/{task_id}/status", params={"task_id": self.id})
        self.status = Status(status_info["status"])
        if status_info["steps_total"] is not None:
            self.steps_total = status_info["steps_total"]
        if status_info["steps_completed"] is not None:
            self.steps_completed = status_info["steps_completed"]

        self.exception = status_info["exception"]
        self.updated_at = datetime.fromisoformat(status_info["updated_at"])

        if status_info["status"] == "COMPLETED":
            self.value = self._get_value()

    def __getattribute__(self, name: str):
        # if the attribute is not immutable, refresh the job if it hasn't been refreshed recently
        if name in ["status", "updated_at", "steps_total", "steps_completed", "exception", "value"]:
            self.refresh(self.config["refresh_interval"])
        return super().__getattribute__(name)

    def wait(
        self, show_progress: bool | None = None, refresh_interval: int | None = None, max_wait: int | None = None
    ) -> None:
        """
        Block until the job is complete

        Params:
            show_progress: Show a progress bar while waiting for the job to complete
            refresh_interval: Polling interval in seconds while waiting for the job to complete
            max_wait: Maximum time to wait for the job to complete in seconds

        Note:
            The defaults for the config parameters can be set globally using the
            [`set_config`][orca_sdk.Job.set_config] method.

            This method will not return the result or raise an exception if the job fails. Call
            [`result`][orca_sdk.Job.result] instead if you want to get the result.

        Raises:
            RuntimeError: If the job times out
        """
        start_time = time.time()
        show_progress = show_progress if show_progress is not None else self.config["show_progress"]
        refresh_interval = refresh_interval if refresh_interval is not None else self.config["refresh_interval"]
        max_wait = max_wait if max_wait is not None else self.config["max_wait"]
        pbar = None
        while True:
            # setup progress bar if steps total is known
            if not pbar and self.steps_total is not None and show_progress:
                desc = " ".join(self.type.split("_")).lower()
                pbar = tqdm(total=self.steps_total, desc=desc)

            # return if job is complete
            if self.status in [Status.COMPLETED, Status.FAILED, Status.ABORTED]:
                if pbar:
                    pbar.update(self.steps_total - pbar.n)
                    pbar.close()
                return

            # raise error if job timed out
            if (time.time() - start_time) > max_wait:
                raise RuntimeError(f"Job {self.id} timed out after {max_wait}s")

            # update progress bar
            if pbar and self.steps_completed is not None:
                pbar.update(self.steps_completed - pbar.n)

            # sleep before retrying
            time.sleep(refresh_interval)

    def result(
        self, show_progress: bool | None = None, refresh_interval: int | None = None, max_wait: int | None = None
    ) -> TResult:
        """
        Block until the job is complete and return the result value

        Params:
            show_progress: Show a progress bar while waiting for the job to complete
            refresh_interval: Polling interval in seconds while waiting for the job to complete
            max_wait: Maximum time to wait for the job to complete in seconds

        Note:
            The defaults for the config parameters can be set globally using the
            [`set_config`][orca_sdk.Job.set_config] method.

            This method will raise an exception if the job fails. Use [`wait`][orca_sdk.Job.wait]
            if you just want to wait for the job to complete without raising errors on failure.

        Returns:
            The result value of the job

        Raises:
            RuntimeError: If the job fails or times out
        """
        if self.value is not None:
            return self.value
        self.wait(show_progress, refresh_interval, max_wait)
        if self.status != Status.COMPLETED:
            raise RuntimeError(f"Job failed with exception: {self.exception}")
        assert self.value is not None
        return self.value


def abort(self, show_progress: bool = False, refresh_interval: int = 1, max_wait: int = 20) -> None:
    """
    Abort the job

    Params:
        show_progress: Optionally show a progress bar while waiting for the job to abort
        refresh_interval: Polling interval in seconds while waiting for the job to abort
        max_wait: Maximum time to wait for the job to abort in seconds
    """
    orca_api.DELETE("/task/{task_id}/abort", params={"task_id": self.id})
    self.wait(show_progress, refresh_interval, max_wait)
