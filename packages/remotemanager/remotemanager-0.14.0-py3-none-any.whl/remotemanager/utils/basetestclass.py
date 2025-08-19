"""
base testing class to reduce code duplication
"""

import os
import shutil
import time
from typing import List, Union, Callable

import pytest

from remotemanager import Dataset
from remotemanager.connection.url import URL
from remotemanager.utils import random_string


class BaseTestClass:
    datasets = []
    files = []
    kwarg_list = []
    fn_list = []

    reset_url_before_teardown = False

    _wait_interval = 0.1
    _wait_timeout = 5

    @pytest.fixture(scope="function", autouse=True)
    def wrap(self):
        # print("Initialising test")
        self.setUp()

        yield  # test runs here

        print("Tearing down class")
        self.tearDown()

    def setUp(self):
        self.datasets: List[Dataset] = []
        self.files: List[str] = []

        self.kwarg_list = []
        self.fn_list = []

    def tearDown(self, wait_ds: bool = True):
        """Clean up"""

        if self.reset_url_before_teardown:
            for ds in self.datasets:
                ds.url = URL()

        if wait_ds:
            for ds in self.datasets:
                try:
                    ds.wait(self._wait_interval, self._wait_timeout)
                except RuntimeError:
                    pass

        for ds in self.datasets:
            self.destroy_dataset(ds)

        for file in self.files:
            try_remove(file)

        self.datasets = []
        self.files = []
        self.kwarg_list = []
        self.fn_list = []

    @property
    def ds(self) -> Dataset:
        return self.datasets[-1]

    def create_dataset(
        self, function, recreate: bool = False, **dataset_kwargs
    ) -> Dataset:
        """Generate a dataset for test usage"""
        print(f"creating dataset with function {function}")

        randstr = self.random_string()

        if "local_dir" not in dataset_kwargs:
            dataset_kwargs["local_dir"] = f"temp_local_{randstr}"

            ldir = dataset_kwargs["local_dir"]
            if os.path.exists(ldir):
                raise ValueError(f"local path {ldir} already exists!")

        if "remote_dir" not in dataset_kwargs:
            dataset_kwargs["remote_dir"] = f"temp_remote_{randstr}"

            rdir = dataset_kwargs["remote_dir"]
            if os.path.exists(rdir):
                raise ValueError(f"remote path {rdir} already exists!")

        if "skip" not in dataset_kwargs and not recreate:
            dataset_kwargs["skip"] = False
        if "name" not in dataset_kwargs and not recreate:
            dataset_kwargs["name"] = f"dataset_{randstr[:8]}"

        ds = Dataset(function=function, **dataset_kwargs)

        self.datasets.append(ds)
        print(f"created dataset with args {dataset_kwargs}")
        print(f"there are now {len(self.datasets)} datasets")

        self.kwarg_list.append(dataset_kwargs)
        self.fn_list.append(function)

        return ds

    def create_datasets(self, functions: list, **dataset_kwargs) -> list:
        randstr = self.random_string()

        link = dataset_kwargs.pop("link", True)

        if "local_dir" not in dataset_kwargs:
            dataset_kwargs["local_dir"] = f"temp_local_{randstr}"

        if "remote_dir" not in dataset_kwargs:
            dataset_kwargs["remote_dir"] = f"temp_remote_{randstr}"

        datasets = []
        for i, fn in enumerate(functions):
            dataset_kwargs["name"] = f"dataset_{i}_{fn.__name__}_{randstr}"
            ds = self.create_dataset(fn, **dataset_kwargs)

            if i > 0 and link:
                datasets[-1].set_downstream(ds)
            datasets.append(ds)

        return datasets

    @property
    def previous_ds_kwargs(self) -> dict:
        if len(self.kwarg_list) == 0:
            return {}
        return self.kwarg_list[-1]

    @property
    def previous_ds_fn(self) -> Union[Callable, None]:
        if len(self.fn_list) == 0:
            return None
        return self.fn_list[-1]

    def recreate_previous_dataset(self, **dataset_kwargs) -> Dataset:
        """
        Attempt to recreate the previously generated dataset

        .. note::
            Uses skip=True by default
        """
        kwargs = self.previous_ds_kwargs

        kwargs.update(dataset_kwargs)

        if "skip" not in dataset_kwargs:
            kwargs["skip"] = True

        print(f"(re) creating ds with kwargs {kwargs}")

        return Dataset(function=self.previous_ds_fn, **kwargs)

    def create_random_file(
        self,
        content: Union[str, None] = None,
        directory: Union[str, None] = None,
    ) -> str:
        if directory is not None and not os.path.exists(directory):
            os.makedirs(directory)

        filename = f"temp_{self.random_string()}"
        if directory is not None:
            filename = os.path.join(directory, filename)

        if content is not None:
            content = str(content) or ""
            with open(filename, encoding="utf8", mode="w+") as o:
                o.write(content)

        # store the filenames for later removal
        # Note that any copies will not be tracked
        self.files.append(filename)

        return filename

    def random_string(self, len: int = 16):
        return random_string(len=len)

    @staticmethod
    def destroy_dataset(dataset: Dataset):
        dataset.hard_reset(files_only=False, dependency_call=True, confirm=False)

        try_remove(dataset.dbfile)
        try_remove(dataset.local_dir)
        try_remove(dataset.remote_dir)

    def run_ds(self, interval=0.1, timeout=5, **kwargs) -> list:
        time.sleep(0.5)
        if len(self.datasets) == 0:
            return []

        self.ds.run(**kwargs)
        self.ds.wait(interval=interval, timeout=timeout)
        self.ds.fetch_results()

        return self.ds.results


def try_remove(f):
    try:
        os.remove(f)
    except IsADirectoryError:
        shutil.rmtree(f)
    except FileNotFoundError:
        pass


def create_large_input(layers: int, width: int) -> dict:
    """
    Creates a large nested dictionary for testing purposes.

    Args:
        layers (int): The number of nested dictionaries.
        width (int): The size of each dictionary.

    Returns:
       dict: A nested dictionary with the specified number of layers and size.
    """

    if layers > 1:
        upper_layer = create_large_input(layers - 1, width)

        tmp = {i: upper_layer for i in range(width)}
    else:
        tmp = {i: i for i in range(width)}

    return tmp
