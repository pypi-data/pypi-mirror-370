from collections import defaultdict
from pathlib import Path

from sandboxes.models.dataset_item import DatasetItem
from sandboxes.models.registry import (
    Dataset,
    LocalRegistryInfo,
    Registry,
    RemoteRegistryInfo,
)
from sandboxes.tasks.client import TasksClient


class RegistryClient:
    DEFAULT_REGISTRY_URL = ""  # TODO(alexgshaw) add a default registry.

    def __init__(self, url: str | None = None, path: Path | None = None):
        self._url = url
        self._path = path
        self._tasks_client = TasksClient()

        self._init_registry()

    @classmethod
    def from_info(cls, info: LocalRegistryInfo | RemoteRegistryInfo):
        if isinstance(info, LocalRegistryInfo):
            return cls(path=Path(info.path))
        elif isinstance(info, RemoteRegistryInfo):
            return cls(url=info.url)
        else:
            raise ValueError(f"Unsupported registry info type: {type(info)}")

    def _init_registry(self):
        if self._url is not None:
            self._registry = Registry.from_url(self._url)
        elif self._path is not None:
            self._registry = Registry.from_path(self._path)
        else:
            raise ValueError("Either url or path must be provided")

    @property
    def datasets(self) -> dict[str, dict[str, Dataset]]:
        datasets = defaultdict(dict)
        for dataset in self._registry.datasets:
            datasets[dataset.name][dataset.version] = dataset
        return datasets

    def download_dataset(
        self,
        name: str,
        version: str,
        overwrite: bool = False,
        output_dir: Path | None = None,
    ) -> list[DatasetItem]:
        dataset = next(
            (
                dataset
                for dataset in self._registry.datasets
                if dataset.name == name and dataset.version == version
            ),
            None,
        )

        if dataset is None:
            raise ValueError(f"Dataset {name}@{version} not found")

        paths = self._tasks_client.download_tasks(
            task_ids=[task_id.to_source_task_id() for task_id in dataset.tasks],
            overwrite=overwrite,
            output_dir=output_dir,
        )

        return [
            DatasetItem(
                name=task_id.get_name(),
                path=path,
            )
            for task_id, path in zip(dataset.tasks, paths)
        ]
