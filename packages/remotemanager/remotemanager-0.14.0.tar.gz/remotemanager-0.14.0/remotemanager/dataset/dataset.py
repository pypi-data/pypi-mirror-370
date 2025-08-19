"""
Main Dataset module

This is the primary class used by the user
"""

# pylint: disable=protected-access
import collections
import copy
import gc
import json
import logging
import os
import pathlib
import re
import shutil
import time
import warnings
from typing import Any, Callable, Dict, List, Optional, Union
from zipfile import ZipFile

import yaml

from remotemanager.dataset.dataset_mixin import DetailMixin
import remotemanager.dataset.repo as repo
from remotemanager.dataset.runnerstates import RunnerState
from remotemanager.transport.transport import Transport
from remotemanager.serialisation.serial import serial
from remotemanager.serialisation.serialjson import serialjson
from remotemanager.connection.cmd import CMD
from remotemanager.connection.computer import Computer
from remotemanager.script.utils import try_value
from remotemanager.connection.url import URL
from remotemanager.dataset.dependency import Dependency
from remotemanager.dataset.files_mixin import ExtraFilesMixin
from remotemanager.dataset.function_generation import create_run_function
from remotemanager.dataset.lazy_append import LazyAppend
from remotemanager.dataset.runner import Runner, LOCALWINERROR
from remotemanager.dataset.summary_instance import SummaryInstance
from remotemanager.decorators.remotefunction import cached_functions
from remotemanager.utils.format_iterable import format_iterable
from remotemanager.utils.verbosity import VerboseMixin, Verbosity
from remotemanager.utils.confirm import ask_confirm
from remotemanager.script.script import Script
from remotemanager.storage import SendableMixin, TrackedFile
from remotemanager.storage.database import Database
from remotemanager.storage.function import Function
from remotemanager.utils import (
    get_version,
    ensure_list,
    ensure_filetype,
    check_dir_is_child,
)
from remotemanager.utils.uuid import UUIDMixin

logger = logging.getLogger(__name__)


class Dataset(SendableMixin, ExtraFilesMixin, DetailMixin, VerboseMixin, UUIDMixin):
    """
    Bulk holder for remote runs. The Dataset class handles anything regarding
    the runs as a group. Running, retrieving results, sending to remote, etc.

    Args:
        function (Callable, str, None):
            Function to run. Can either be the function object, source string or None
            If None, Runner will pass arguments to the `script` method
        url (URL):
            connection to remote (optional)
        transport (Transport):
            transport system to use, if a specific is required. Defaults to
            transport.rsync
        serialiser (serial):
            serialisation system to use, if a specific is required. Defaults
            to serial.serialjson
        script (str):
            callscript required to run the jobs in this dataset
        submitter (str):
            command to exec any scripts with. Defaults to "bash"
        name (str):
            optional name for this dataset. Will be used for runscripts
        extra_files_send(list, str):
            extra files to send with this run
        extra_files_recv(list, str):
            extra files to retrieve with this run
        skip (bool):
            skip dataset creation if possible. Defaults True
        extra:
            extra text to insert into the runner jobscripts
        global_run_args:
            any further (unchanging) arguments to be passed to the runner(s)

    Attributes:
        default_url (URL):
            a default url can be assigned to all Datasets.
    """

    _do_not_package = ["_database", "_url"]

    _manifest_file = "archive_manifest.txt"

    default_url = None

    def __init__(
        self,
        function: Union[Callable, str, None],
        url: Optional[URL] = None,
        dbfile: Optional[str] = None,
        transport: Optional[Transport] = None,
        serialiser: Optional[serial] = None,
        script: Optional[str] = None,
        shebang: Optional[str] = None,
        name: Optional[str] = None,
        extra_files_send: Optional[Union[List[str], str]] = None,
        extra_files_recv: Optional[Union[List[str], str]] = None,
        verbose: Optional[Union[int, bool, Verbosity]] = None,
        run_summary_limit: int = 25,
        add_newline: bool = True,
        skip: bool = True,
        extra: Optional[str] = None,
        **global_run_args,
    ):
        self.verbose = verbose

        self.verbose.print("Dataset initialised", 2)
        logger.info("dataset initialised")

        self.run_args = copy.deepcopy(Runner._defaults)
        # sanitise paths
        self.run_args = self.sanitise_run_arg_paths(self.run_args)

        self.run_args.update(global_run_args)
        self._global_run_extra = extra

        self._extra_files = {
            "send": (
                ensure_list(extra_files_send) if extra_files_send is not None else []
            ),
            "recv": (
                ensure_list(extra_files_recv) if extra_files_recv is not None else []
            ),
        }
        self._add_newline = add_newline

        self._last_run = -1

        self._serialiser = serialjson()
        self.serialiser = serialiser

        self._dependency = None
        self._do_not_recurse = False

        self._url = None
        self._computer = False
        if url is None:
            self.url = self.default_url
        else:
            self.url = url
        self._transport = None
        self.transport = transport

        if "submitter" in global_run_args:
            self.submitter = global_run_args["submitter"]
        if "shell" in global_run_args:
            self.shell = global_run_args["shell"]

        self._script = script or ""
        # Dataset shebang takes priority _only_ if manually set
        if shebang is not None:
            self.shebang = shebang

        # UUID generation: dataset uuid is equal to Function uuid for now
        # if the function does not exist, we need to take the URL uuid as backup
        if isinstance(function, Script):
            self._function = function
            source_uuid = self._function.uuid
        elif function is not None:
            self._function = Function(function)
            source_uuid = self._function.uuid
        else:
            logger.info("creating a dataset with no function")
            self._function = None
            source_uuid = self.url.uuid
            if not isinstance(url, Computer):
                logger.warning(
                    "Function is None, but the URL is not a Computer subclass"
                )
                print(
                    "Warning! The current url is "
                    "not a subclass of Computer, "
                    "the dataset may not function as expected."
                )
        self._name = None
        self.name = name or "dataset"
        self.generate_uuid(source_uuid + self.name)
        logger.info("uuid is %s", self.uuid)

        # now we have a name and uuid, deal with the files
        self._dbfile_override = dbfile
        self._repo_prefix = None

        if "dataset" in self.name.lower():
            dbfile_base = f"{self.name}-{self.short_uuid}"
        else:
            dbfile_base = f"dataset-{self.name}-{self.short_uuid}"

        self._dbfile = ensure_filetype(dbfile_base, "yaml")
        self.main_dir_env = f"DATASET_{self.short_uuid}_MAIN_DIR"
        self.argfile = f"args-{self.name}-{self.short_uuid}"

        self._run_cmd = None
        self._fresh_dataset = False
        if skip and os.path.isfile(self.dbfile):
            self._create_from_db()
        else:
            try:
                os.remove(self.dbfile)
                logger.info("deleted database file %s", self.dbfile)
            except FileNotFoundError:
                pass
            self._create_fresh()

        self._append_session = 0
        self._run_summary_limit = run_summary_limit

        logger.info("Dataset %s init complete)", self.name)

    def _create_from_db(self) -> None:
        logger.info("unpacking database from %s", self.dbfile)
        self.verbose.print(f"Unpacking Dataset from {self.dbfile}", 2)

        # create a "temporary" database from the found file
        self._database = Database(self.dbfile)
        old_uuid = self.database.stored_uuid  # get uuid by first key
        logger.info("unpacked uuid is %s", old_uuid)
        if old_uuid != self.uuid:
            logger.debug("current uuid is %s", self.uuid)
            dst = f"{self.dbfile}.old"

            dst = self.database.backup(dst)
            msg = (
                f"new and old UUID mismatch (did something change?)\n"
                f"Creating a fresh dataset and backing up the old dbfile at {dst}."
                f"\nUse Dataset.from_file('{dst}') to recover the old dataset."
            )
            logger.warning(msg)
            print(msg)
            self._create_fresh()
            return
        # update it with any new values
        self.update_db()
        # unpack from here to retrieve
        payload = self.database._storage[self.uuid]
        self.inject_payload(payload)

    def _create_fresh(self) -> None:
        logger.info("No database file found, creating anew")
        self.verbose.print(f"Creating a fresh Dataset w/ database at {self.dbfile}", 2)
        self._runs = collections.OrderedDict()
        self._uuids = []
        self._results = []

        # database property creates the database if it does not exist
        self.database._storage = {}
        self.update_db()
        self._fresh_dataset = True

    def __hash__(self) -> int:
        return hash(self.uuid)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, type(self)):
            return False
        return self.uuid == other.uuid

    def __repr__(self) -> str:
        return f"dataset-{self.name}-{self.short_uuid}"

    @classmethod
    def recreate(cls, *args, raise_if_not_found: bool = True, **kwargs) -> "Dataset":
        """
        Attempts to extract a dataset matching the given args from the python
        garbage collection interface

        Args:
            raise_if_not_found (bool):
                raise ValueError if the Dataset was not found
            *args:
                args as passed to Dataset
            **kwargs:
                keyword args as passed to Dataset
        Returns:
            Dataset
        """

        for obj in gc.get_objects():
            if isinstance(obj, cls):
                tmp = cls(*args, **kwargs)
                if obj == tmp:
                    print("returning stored obj")
                    return obj

        if raise_if_not_found:
            raise ValueError("Dataset with args not found!")

        return cls(*args, **kwargs)

    @classmethod
    def from_file(cls, file: str, url: Optional[URL] = None, **kwargs) -> "Dataset":  # type: ignore
        """
        Alias for Dataset.unpack(file=...)

        Args:
            file (str):
                Dataset dbfile
            url (URL):
                the URL to apply to this Dataset

        Returns:
            (Dataset): unpacked Dataset
        """
        ds = super().from_file(file=file, **kwargs)

        if url is not None:
            ds.url = url
        else:
            print("Warning! Creating Dataset from file with a default URL (localhost)")

        return ds

    @property
    def database(self) -> Database:
        """
        Access to the stored database object.
        Creates a connection if none exist.

        Returns (Database):
            Database
        """
        if self.is_missing("_database"):
            logger.debug("Database missing, regenerating from file %s", self.dbfile)
            payload = self.pack()
            if payload is None:
                raise RuntimeError(
                    "Packing paylood is None (did it get dumped to file somehow?)"
                )
            payload[Database._versionkey] = get_version()
            with open(self.dbfile, "w+", encoding="utf8") as o:
                yaml.dump(payload, o)

            self._database = Database(file=self.dbfile)
        return self._database

    @property
    def dbfile(self) -> str:
        """
        Name of the database file
        """
        if self._dbfile_override is not None:
            return ensure_filetype(self._dbfile_override, "yaml")
        return self._dbfile

    @dbfile.setter
    def dbfile(self, file: str) -> None:
        """
        Moves the stored database to `file`.

        Args:
            file:
                new file path
        """
        logger.debug("updating dbfile to %s", file)
        self.update_db()  # make sure the database is valid
        # make sure new path is valid
        path = ensure_filetype(file, "yaml")
        # move the old database to the new location
        shutil.move(self.dbfile, path)
        logger.debug("moved %s to %s", self.dbfile, path)
        self._dbfile = path  # update internal path

    def sanitise_run_arg_paths(self, run_args: dict) -> dict:
        """
        Checks for issues in the paths within the given run_args
        """
        if "remote_dir" in run_args:
            run_args["remote_dir"] = self.sanitise_path(run_args["remote_dir"])
        if "run_dir" in run_args:
            run_args["run_dir"] = self.sanitise_path(run_args["run_dir"])
        if "local_dir" in run_args:
            run_args["local_dir"] = self.sanitise_path(run_args["local_dir"])

        return run_args

    @staticmethod
    def sanitise_path(path) -> str:
        """
        Ensures a clean unix-type path
        """
        path = str(pathlib.PureWindowsPath(path).as_posix())

        if " " in path:
            raise ValueError(f"Space character detected in path {path}")

        return path

    @property
    def remote_dir(self) -> str:
        """
        Accesses the remote_dir property from the run args. Tries to fall back
        on run_dir if not found, then returns default as a last resort.
        """
        remote_dir = self.global_run_args.get("remote_dir", None)

        if remote_dir is None:
            return Runner._defaults["remote_dir"]
        return remote_dir

    @remote_dir.setter
    def remote_dir(self, path) -> None:
        self.run_args["remote_dir"] = self.sanitise_path(path)

        self.update_db()

    @property
    def run_dir(self) -> Union[str, None]:
        """
        Accesses the remote_dir property from the run args. Tries to fall back
        on run_dir if not found, then returns default as a last resort.
        """
        return self.global_run_args.get("run_dir", None)

    @run_dir.setter
    def run_dir(self, path) -> None:
        self.run_args["run_dir"] = self.sanitise_path(path)

        self.update_db()

    @property
    def run_path(self) -> str:
        """
        Accesses the remote_dir property from the run args. Tries to fall back
        on run_dir if not found, then returns default as a last resort.
        """
        if self.run_dir is not None:
            return os.path.join(self.remote_dir, self.run_dir)
        return self.remote_dir

    @property
    def local_dir(self) -> str:
        """
        Accesses the local_dir property from the run args. Returns default if
        not found.
        """
        local_dir = self.global_run_args.get("local_dir", None)

        if local_dir is None:
            return Runner._defaults["local_dir"]
        return local_dir

    @local_dir.setter
    def local_dir(self, path) -> None:
        self.run_args["local_dir"] = self.sanitise_path(path)

        self.update_db()

    @property
    def repo_prefix(self) -> str:
        """override for repo names and manifest file in a dependency situation"""
        if self._repo_prefix is None:
            self._repo_prefix = f"{self.name}-{self.short_uuid}"
        return self._repo_prefix

    @property
    def repofile(self) -> TrackedFile:
        """Returns the TrackedFile instance responsible for the repository"""
        fname = f"{self.repo_prefix}-repo.py"
        return TrackedFile(self.local_dir, self.remote_dir, fname)

    @property
    def bash_repo(self) -> TrackedFile:
        """Returns the TrackedFile instance responsible for the repository"""
        fname = f"{self.repo_prefix}-repo.sh"
        return TrackedFile(self.local_dir, self.remote_dir, fname)

    @property
    def master_script(self) -> TrackedFile:
        """Returns the TrackedFile instance responsible for the master script"""
        fname = f"{self.name}-{self.short_uuid}-master.sh"
        return TrackedFile(self.local_dir, self.remote_dir, fname)

    @property
    def manifest_log(self) -> TrackedFile:
        """Returns the TrackedFile instance responsible for the manifest"""
        fname = f"{self.repo_prefix}.manifest"
        return TrackedFile(self.local_dir, self.remote_dir, fname)

    @property
    def global_run_args(self) -> Dict[str, str]:
        """Returns the toplevel global run args"""
        return self.run_args

    def set_run_arg(self, key: str, val) -> None:
        """
        Set a single run arg `key` to `val`

        Args:
            key:
                name to set
            val:
                value to set to

        Returns:
            None
        """
        self.run_args[key] = val

    def set_run_args(self, keys: List[str], vals: List[str]) -> None:
        """
        Set a list of `keys` to `vals

        .. note::
            List lengths must be the same

        Args:
            keys:
                list of keys to set
            vals:
                list of vals to set to

        Returns:
            None
        """
        keys = ensure_list(keys)
        vals = ensure_list(vals)

        if len(keys) != len(vals):
            raise ValueError(
                f"number of keys ({len(keys)}) != number of vals ({len(vals)}"
            )

        for key, val in zip(keys, vals):
            self.run_args[key] = val

    def update_run_args(self, d: Dict[str, str]) -> None:
        """
        Update current global run args with a dictionary `d`

        Args:
            d:
                dict of new args

        Returns:
            None
        """
        self.run_args.update(d)

    @property
    def do_not_recurse(self) -> bool:
        """Internal function used for blocking recursion in dependency calls"""
        self._do_not_recurse = False
        return True

    @property
    def dependency(self) -> Union[Dependency, None]:
        """Returns the stored dependency"""
        return self._dependency

    @property
    def is_child(self) -> bool:
        """Returns True if this dataset is a child, False otherwise"""
        if self.dependency is None:
            return False
        return self.short_uuid in self.dependency._children

    @property
    def is_parent(self) -> bool:
        """Returns True if this dataset is a parent, False otherwise"""
        if self.dependency is None:
            return False
        return self.short_uuid in self.dependency._parents

    def _mirror_dependency(self, dataset: "Dataset") -> None:
        """Ensures bi-directional dependency links"""
        logger.info("connecting with dataset %s", dataset)
        if dataset.dependency is not None:
            logger.info("target has dependency, joining")
            self._dependency = dataset.dependency
        elif self.dependency is not None:
            logger.info("self has dependency, joining")
            dataset._dependency = self._dependency
        else:
            logger.info("creating a dependency and entering")
            self._dependency = Dependency()
            dataset._dependency = self.dependency

    def set_downstream(self, dataset: "Dataset") -> None:
        """Add a child to this dataset"""
        self._mirror_dependency(dataset)
        dataset._repo_prefix = self.repo_prefix

        # ignore type here, as _mirror_dependency sets this
        self.dependency.add_edge(self, dataset)  # type: ignore

        if not dataset.do_not_recurse:
            dataset._do_not_recurse = True
            dataset.set_upstream(self)
        self.update_db()

    def set_upstream(self, dataset: "Dataset") -> None:
        """Add a parent to this dataset"""
        self._mirror_dependency(dataset)
        self._repo_prefix = dataset.repo_prefix

        # ignore type here, as _mirror_dependency sets this
        self.dependency.add_edge(dataset, self)  # type: ignore

        if not dataset.do_not_recurse:
            dataset._do_not_recurse = True
            dataset.set_downstream(self)
        self.update_db()

    def pack(self, file: Optional[str] = None, **kwargs) -> Union[dict, None]:
        """
        Override for the SendableMixin.pack() method, ensuring the dataset is
        always below a ``uuid``

        Args:
            **kwargs:
                Any arguments to be passed onwards to the SendableMixin.pack()

        Returns:
            (dict) packing result
        """
        if len(kwargs) == 0:
            logger.info("Dataset override pack called")
        else:
            logger.info("Data override pack called with run_args")
            logger.info("%s", format_iterable(kwargs))
        data = super().pack(uuid=self._uuid, **kwargs)

        if file is not None:
            print(f"dumping payload to {file}")
            with open(file=file, mode="w+", encoding="utf8") as o:
                yaml.dump(data, o)
            return None

        return data

    def update_db(self, dependency_call: bool = False) -> None:
        """Force updates the database"""
        if self.dependency is not None and not dependency_call:
            return self.dependency.update_db()

        self.database.update(self.pack())

    def set_run_option(self, key: str, val) -> None:
        """
        Update a global run option `key` with value `val`

        Args:
            key (str):
                option to be updated
            val:
                value to set
        """
        warnings.warn("set_run_option is deprecated, use set_run_arg instead")
        self.run_args[key] = val

    def append_run(
        self,
        args: Optional[Dict[str, Any]] = None,
        arguments: Optional[Dict[str, Any]] = None,
        name: Optional[str] = None,
        extra_files_send: Optional[Union[list, str]] = None,
        extra_files_recv: Optional[Union[list, str]] = None,
        dependency_call: bool = False,
        verbose: Optional[Union[int, bool, Verbosity]] = None,
        quiet: bool = False,
        skip: bool = True,
        force: bool = False,
        lazy: bool = False,
        chain_run_args: bool = True,
        extra: Optional[str] = None,
        return_runner: bool = False,
        **run_args: Dict[str, str],
    ) -> Union[None, Runner]:
        """
        Serialise arguments for later runner construction

        Args:
            args (dict):
                dictionary of arguments to be unpacked
            arguments (dict):
                alias for args
            name (str):
                 append a runner under this name
            extra_files_send (list, str):
                extra files to send with this run
            extra_files_recv (list, str):
                extra files to retrieve with this run
            dependency_call (bool):
                True if called via the dependency handler
            verbose (int, Verbose, None):
                verbose level for this runner (defaults to Dataset level)
            quiet (bool):
                disable printing for this append if True
            skip (bool):
                ignores checks for an existing runner if set to False
            force (bool):
                always appends if True
            lazy (bool):
                performs a "lazy" append if True, skipping the dataset update. You MUST
                call ds.finish_append() after you are done appending to avoid strange
                behaviours
            chain_run_args (bool):
                for dependency runs, will not propagate run_args to other datasets in
                the chain if False (defaults True)
            extra:
                extra string to add to this runner
            return_runner:
                returns the appened (or matching) runner if True
            run_args:
                any extra arguments to pass to runner

        Returns:
            Runner if return_runner, else None
        """
        if quiet or lazy:
            verbose = Verbosity(0)
        elif verbose is not None:
            verbose = Verbosity(verbose)
        else:
            verbose = self.verbose

        logger.debug("#### Dataset append_run called")
        if args is None and arguments is not None:
            args = arguments

        if self.dependency is not None and not dependency_call:
            return self.dependency.append_run(
                caller=self,
                chain_run_args=chain_run_args,
                args=args,
                name=name,
                extra_files_send=extra_files_send,  # noqa: E251
                extra_files_recv=extra_files_recv,  # noqa: E251
                verbose=verbose,
                quiet=quiet,
                skip=skip,
                force=force,
                lazy=lazy,
                run_args=run_args,
                extra=extra,
                return_runner=return_runner,
            )

        extra_files_send = ensure_list(extra_files_send) + self._extra_files["send"]
        extra_files_recv = ensure_list(extra_files_recv) + self._extra_files["recv"]

        rnum = len(self.runners)
        if name is not None:
            run_args["name"] = name
            r_id = name

            if name in self.runner_dict:
                msg = f"{self} overwriting already existing runner {r_id}"
                logger.warning(msg)
                verbose.print(msg, 1)

        else:
            r_id = f"runner-{rnum}"

        tmp = Runner(
            arguments=args,
            parent=self,
            self_id=r_id,
            extra_files_send=extra_files_send,
            extra_files_recv=extra_files_recv,
            verbose=verbose,
            extra=extra,
            **run_args,
        )

        tmp.result_extension = self.serialiser.extension

        tmp = self.insert_runner(
            runner=tmp,
            skip=skip,
            force=force,
            lazy=lazy,
            quiet=quiet,
            return_runner=return_runner,
        )

        if return_runner:
            return tmp

    def insert_runner(
        self,
        runner: Runner,
        skip: bool = True,
        force: bool = False,
        lazy: bool = False,
        verbose: Union[None, int, bool, Verbosity] = None,
        quiet: bool = False,
        return_runner: bool = False,
    ) -> Union[None, Runner]:
        """
        Internal runner insertion.

        Args:
            runner: Runner object to insert
            skip: don't insert if it exists
            force: force inserts
            lazy: Attempts a lazy append if True (does not update DB)
            verbose: Verbosity level for this runner
            quiet: inserts runner quietly if True
            return_runner: Returns the runner object if True
        Returns:
            None or Runner
        """
        if quiet or lazy:
            verbose = Verbosity(0)
        elif verbose is not None:
            verbose = Verbosity(verbose)
        else:
            verbose = self.verbose

        if runner.parent != self:
            logger.info("inserting runner from another dataset, overriding parent")

            runner._parent = self
            runner._parent_uuid = self.uuid

        def append_to_log(r_id: str, mode: str, quiet: bool) -> None:
            session = f"append session {self._append_session}"
            insert = SummaryInstance(r_id, mode, quiet)
            try:
                self._append_log[session].append(insert)
            except KeyError:
                self._append_log[session] = [insert]

        r_id = runner.id

        if force or not skip:
            self._runs[r_id] = runner
            # regenerate a ``uuid`` so this runner can be properly tracked
            runner._generate_uuid({"r_id": r_id})

            self._uuids.append(runner.uuid)
            msg = f"force appended run {runner.name}"
            logger.info(msg)
            append_to_log(r_id, "forced", quiet)
            if verbose:
                verbose.print(msg, level=1)
        elif runner.uuid not in self._uuids:
            self._runs[r_id] = runner
            self._uuids.append(runner.uuid)
            msg = f"appended run {runner.name}"
            logger.info(msg)
            append_to_log(r_id, "appended", quiet)
            if verbose:
                verbose.print(msg, level=1)
        else:
            runner = self.get_runner(runner.uuid)
            msg = f"runner {runner.name} already exists"
            logger.info(msg)
            append_to_log(r_id, "skipped", quiet)
            if verbose:
                verbose.print(msg, level=1)

        if not lazy:
            self.finish_append(print_summary=False)

        if return_runner:
            return runner
        return None

    def finish_append(
        self,
        dependency_call: bool = False,
        print_summary: bool = True,
        verbose: Union[None, int, bool, Verbosity] = None,
    ) -> None:
        """
        Completes the append process by updating the database, and printing a summary
        if necessary

        Args:
            dependency_call:
                Will not attempt to relay to a dependency
                if True (called by dependency)
            print_summary:
                Prints a summary if True
            verbose:
                verbosity level for this call
        """
        if verbose is not None:
            verbose = Verbosity(verbose)
        else:
            verbose = self.verbose
        if print_summary and len(self._append_log) != 0:
            self._append_session += 1
            session = list(self._append_log.keys())[-1]
            summary = {}
            print_flag = False
            for instance in self._append_log[session]:
                if not instance.quiet:
                    print_flag = True
                try:
                    summary[instance.mode] += 1
                except KeyError:
                    summary[instance.mode] = 1
            msg = [f"Of {sum(summary.values())} appends:"]
            for mode, count in summary.items():
                msg.append(f"{count} {mode}")

            sessionlog = " ".join(msg)
            logger.info(sessionlog)
            if print_flag:
                verbose.print(sessionlog, 1)
                verbose.print("See get_append_log for more info", 1)

        logger.info("finishing append")
        if self.dependency is not None and not dependency_call:
            self.dependency.finish_append()
            return
        self.update_db()

    def lazy_append(self) -> LazyAppend:
        """Access a LazyAppend object, which handles the append finalisation"""
        return LazyAppend(self)

    def copy_runners(self, dataset: "Dataset") -> None:
        """Copy the runners from dataset over to this dataset"""
        for runner in dataset.runners:
            copied_runner = copy.deepcopy(runner)
            if runner.is_finished:
                copied_runner.set_state("copied", value=runner.state.value)
            else:
                copied_runner.set_state("copied", 0)

            self.insert_runner(copied_runner, lazy=True)
        self.finish_append(verbose=False)

    def remove_run(
        self,
        ident: Union[int, str, dict],
        dependency_call: bool = False,
        verbose: Union[None, int, bool, Verbosity] = None,
    ) -> bool:
        """
        Remove a runner with the given identifier. Search methods are identical
        get_runner(id)

        Args:
            ident:
                identifier
            dependency_call (bool):
                used by any dependencies that exist, prevents recursion
            verbose:
                local verbose level

        Returns:
            (bool): True if succeeded
        """
        if verbose is not None:
            verbose = Verbosity(verbose)
        else:
            verbose = self.verbose
        if not dependency_call and self.dependency is not None:
            return self.dependency.remove_run(ident)

        runner = self.get_runner(ident, dependency_call, verbose=0)

        if runner is None:
            logger.info(
                "could not find runner to remove",
            )
            return False

        del self._runs[runner.id]
        self._uuids.remove(runner.uuid)

        msg = f"removed runner {runner}"
        logger.info(msg)
        verbose.print(msg, level=1)

        # need to override attribute first, as updating can only add
        self.database._storage[self.uuid]["_runs"] = {}
        self.update_db()

        return True

    def get_runner(
        self,
        ident: Union[int, str, dict],
        dependency_call: bool = False,
        verbose: Union[None, int, bool, Verbosity] = None,
    ) -> Union[Runner, None]:
        """
        Collect a runner with the given identifier. Depending on the type of
        arg passed, there are different search methods:

        - int: the runners[ident] of the runner to remove
        - str: searches for a runner with the matching uuid
        - dict: attempts to find a runner with matching args

        Args:
            ident:
                identifier
            dependency_call (bool):
                used by the dependencies, runners cannot be removed via uuid in this
                case, as the uuids will not match between datasets

        Returns:
            (Runner): collected Runner, None if not available
        """
        if verbose is not None:
            verbose = Verbosity(verbose)
        else:
            verbose = self.verbose
        verbose.print("Searching for runner", level=2, end="... ")

        def get_by_id(ident) -> Union[None, Runner]:
            logger.info("getting runner by id %s", ident)
            verbose.print(f"by id {ident}", level=2, end=" ")
            try:
                key = list(self.runner_dict.keys())[ident]
                return self.runner_dict[key]
            except IndexError:
                return

        def get_by_str(ident) -> Union[None, Runner]:
            logger.info('getting runner by string "%s"', ident)
            verbose.print(f"by string {ident}", level=2, end=" ")

            if ident.lower() in self.runner_dict:
                return self.runner_dict[ident.lower()]

            if dependency_call:
                raise RuntimeError(
                    "Runners within a dependency cannot be removed by uuid\n"
                    f"If trying to remove by name, there may be an error ({ident})."
                )
            # assume uuid at this point, search first by matching the first 8 chars
            # short_uuid, then confirming with the full, if given
            if len(ident) == 64:
                logger.info(
                    "full uuid)",
                )
                for runner in self.runners:
                    if runner.uuid == ident:
                        return runner
            elif len(ident) == 8:
                logger.info(
                    "short uuid)",
                )
                for runner in self.runners:
                    if runner.short_uuid == ident:
                        return runner

        def get_by_dict(ident) -> Union[None, Runner]:
            verbose.print(f"by args {ident}", level=2, end=" ")
            logger.info("getting runner by args %s", ident)
            for r in self.runners:
                if format_iterable(r.args) == format_iterable(ident):
                    return r

        dispatch = {int: get_by_id, str: get_by_str, dict: get_by_dict}
        fn = dispatch.get(type(ident), None)

        if fn is None:
            raise RuntimeError(
                f"Could not find runner by identifier {ident} of type {type(ident)}"
            )
        runner = fn(ident)
        verbose.print(str(runner), level=2)
        return runner

    def wipe_runs(self, dependency_call: bool = False, confirm: bool = True) -> None:
        """
        Removes all runners

        Args:
            dependency_call (bool):
                used by any dependencies that exist, prevents recursion
            confirm (bool):
                Asks for confirmation if True
        """
        if confirm and not ask_confirm("Remove all Runners?"):
            return

        if not dependency_call and self.dependency is not None:
            self.dependency.clear_runs()
            return

        logger.info("wiping all runners and updating the db")

        self._uuids = []
        self._runs = {}

        self.database._storage[self.uuid]["_runs"] = {}
        self.update_db()

    def reset_runs(
        self, wipe: bool = False, dependency_call: bool = False, confirm: bool = True
    ) -> None:
        """
        Remove any results from the stored runners and attempt to delete their
        result files if `wipe=True`

        .. warning::
            This is a potentially destructive action, be careful with this
            method

        Args:
            wipe:
                Additionally deletes the local files if True. Default False
            dependency_call (bool):
                used by any dependencies that exist, prevents recursion
            confirm (bool):
                Asks for confirmation if True
        """
        if confirm and not ask_confirm("Reset all Runner results?"):
            return

        if not dependency_call and self.dependency is not None:
            self.dependency.clear_results(wipe)
            return

        logger.info("clearing results")
        for runner in self.runners:
            runner.clear_result(wipe)

    def collect_files(
        self,
        remote_check: bool,
        results_only: bool = False,
        extra_files_send: bool = True,
    ) -> list:
        """
        Collect created files

        Args:
            remote_check:
                search for remote paths if True
            results_only:
                only collect files that are returned from a run such as Results and
                extra_files_recv if True
            extra_files_send:
                collects extra_files_send if True

        Returns:
            list of filepaths
        """
        target = "remote" if remote_check else "local"

        targets = []

        if not results_only:
            targets = [
                getattr(self.master_script, target),
                getattr(self.repofile, target),
                getattr(self.bash_repo, target),
                getattr(self.manifest_log, target),
            ]

        # grab all runner files
        for runner in self.runners:
            # start with constants
            targets += [
                getattr(runner.resultfile, target),
                getattr(runner.errorfile, target),
            ]
            # add the jobscript and runfile if we want all files
            if not results_only:
                targets += [
                    getattr(runner.jobscript, target),
                    getattr(runner.runfile, target),
                ]

                # need extra files, within their remote/local dir
                # also needs to be a copy of this list to prevent
                # remote check contamination
                extras = [f for f in runner.extra_files_recv]
                if extra_files_send:
                    for file in runner.extra_files_send:
                        extras.append(file)

                for file in extras:
                    targets.append(getattr(file, target))

        # minimize length
        targets = list(set(targets))

        return targets

    def wipe_local(
        self,
        files_only: bool = True,
        dry_run: bool = False,
        dependency_call: bool = False,
        confirm: bool = True,
    ) -> None:
        """
        Clear out the local directory

        Args:
            files_only (bool):
                delete individual files instead of whole folders (preserves
                extra files)
            dry_run (bool):
                print targets and exit
            dependency_call (bool):
                used by any dependencies that exist, prevents recursion
            confirm (bool):
                Asks for confirmation if True
        """
        if confirm and not ask_confirm("Wipe the local directory?"):
            return

        if not dependency_call and self.dependency is not None:
            return self.dependency.wipe_local(files_only)

        if not files_only and not check_dir_is_child(os.getcwd(), self.local_dir):
            raise RuntimeError(
                f"local dir {self.local_dir} is not a child directory, "
                f"deleting could have catastrophic effects"
            )

        logger.debug("wiping local")

        if not files_only:
            targets = [self.local_dir]
            for runner in self.runners:
                if runner.local_dir not in targets:
                    targets.append(runner.local_dir)

            logger.debug("locals: %s", format_iterable(targets))
            if dry_run:
                for local in targets:
                    print(f"targeting local {local} for wipe")

            for local in targets:
                try:
                    shutil.rmtree(local)
                    logger.debug("%s removed)", local)
                except FileNotFoundError:
                    logger.debug("%s not found", local)

        else:
            logger.debug("file only wipe")
            targets = self.collect_files(remote_check=False, extra_files_send=False)

            logger.info("targets for wipe:|%s", format_iterable(targets))

            if dry_run:
                for local in targets:
                    print(f"targeting local {local} for wipe")

            for path in targets:
                try:
                    if "*" in path:
                        logger.debug("skipping wildcard: %s", path)
                        continue
                    os.remove(path)
                    logger.debug("removed: %s", path)
                except FileNotFoundError:
                    logger.debug("not found: %s", path)

    def wipe_remote(
        self,
        files_only: bool = True,
        dry_run: bool = False,
        dependency_call: bool = False,
        confirm: bool = True,
    ) -> None:
        """
        Clear out the remote directory (including run dir)

        Args:
            files_only (bool):
                delete individual files instead of whole folders (preserves
                extra files)
            dry_run (bool):
                print targets and exit
            dependency_call (bool):
                used by any dependencies that exist, prevents recursion
            confirm (bool):
                Asks for confirmation if True
        """
        if confirm and not ask_confirm("Wipe the remote directory?"):
            return
        logger.debug("wiping remote")

        if not dependency_call and self.dependency is not None:
            self.dependency.wipe_remote(files_only)
            return

        if not files_only:
            remotes = [self.remote_dir]
            for runner in self.runners:
                if runner.remote_dir not in remotes:
                    remotes.append(runner.remote_dir)
                if runner.run_path not in remotes:
                    remotes.append(runner.run_path)

            logger.debug("remotes: %s", format_iterable(remotes))
            if dry_run:
                for remote in remotes:
                    print(f"targeting remote {remote} for wipe")

            remotestr = ",".join(remotes)
            if len(remotes) > 1:
                cmd = f"rm -rf {{{remotestr}}}"
            else:
                cmd = f"rm -rf {remotestr}"

            self.url.cmd(cmd)

        else:
            logger.debug("file only wipe")
            targets = self.collect_files(remote_check=True)

            logger.info("targets for wipe:|%s", format_iterable(targets))

            # skip any wildcards
            targets = [t for t in targets if "*" not in t]

            cmd = ",".join(targets)
            cmd = f"rm -rf {{{cmd}}}"

            if dry_run:
                for remote in targets:
                    print(f"targeting remote {remote} for wipe")
                return

            self.url.cmd(cmd)

    def hard_reset(
        self,
        files_only: bool = True,
        dry_run: bool = False,
        dependency_call: bool = False,
        confirm: bool = True,
    ) -> None:
        """
        Hard reset the dataset, including wiping local and remote folders

        Args:
            files_only (bool):
                delete individual files instead of whole folders (preserves
                extra files)
            dry_run (bool):
                print targets and exit
            dependency_call (bool):
                used by any dependencies that exist, prevents recursion
            confirm (bool):
                Asks for confirmation if True
        """
        if confirm and not ask_confirm("Perform a hard reset?"):
            return

        if not dependency_call and self.dependency is not None:
            self.dependency.hard_reset(files_only)
            return

        self._dependency = None
        self.wipe_local(
            files_only, dry_run, dependency_call=dependency_call, confirm=False
        )
        self.wipe_remote(
            files_only, dry_run, dependency_call=dependency_call, confirm=False
        )
        self.wipe_runs(dependency_call=dependency_call, confirm=False)

        try:
            os.remove(self.dbfile)
        except FileNotFoundError:
            pass

    def backup(self, file=None, force: bool = False, full: bool = False) -> str:
        """
        Backs up the Dataset and any attached results/extra files to zip file

        Args:
            file:
                target path
            force:
                overwrite file if it exists
            full:
                only collects runner results if False (defaults ``False``)
        Returns:
            path to zip file
        """
        if file is None:
            file = f"{self.name}.zip"

        if not file.endswith(".zip"):
            raise ValueError(f'backup file "{file}" must be of .zip type')

        file = os.path.abspath(file)

        if os.path.isfile(file) and not force:
            raise RuntimeError(
                f'backup file "{file}" exists, use a different name or '
                f"force=True to overwrite"
            )

        logger.debug("writing to file %s", file)

        try:
            with open(Dataset._manifest_file, "w+", encoding="utf-8") as o:
                o.write(self.dbfile)

            with ZipFile(file, "w") as z:
                logger.info("storing file %s", self.database.path)
                z.write(self.database.path)
                z.write(Dataset._manifest_file)

                pwd = os.getcwd()
                for rfile in self.collect_files(
                    remote_check=False, results_only=not full
                ):
                    if not os.path.isfile(rfile):
                        continue
                    logger.info("storing file %s", rfile)
                    rfile = rfile.replace(pwd, ".")

                    z.write(rfile)
        finally:
            os.remove(Dataset._manifest_file)

        return file

    @classmethod
    def restore(cls, file, force: bool = False) -> "Dataset":
        """
        Restore from backup file `file`

        Args:
            file:
                File to restore from
            force:
                Set to True to overwrite any existing Dataset

        Returns:
            Dataset
        """
        # backup archive
        arch = ZipFile(file)
        # get the name of the Database file to recreate the Dataset
        with arch.open(name=Dataset._manifest_file, mode="r") as a:
            dbfile = a.read().decode("utf-8")
        if not force and os.path.exists(dbfile):
            raise RuntimeError(
                f"Dataset already exists, either restore with "
                f"force=True or delete the dbfile '{dbfile}'"
            )

        # extract all files that aren't the manifest
        files = [f for f in arch.namelist() if f is not Dataset._manifest_file]
        arch.extractall(members=files)
        # recreate and return
        dataset = Dataset.from_file(dbfile)

        if os.path.exists(Dataset._manifest_file):
            os.remove(Dataset._manifest_file)

        return dataset

    @property
    def runner_dict(self) -> dict:
        """
        Stored runners in dict form, where the keys are the append id
        """
        return dict(self._runs)

    @property
    def runners(self) -> List[Runner]:
        """
        Stored runners as a list
        """
        return list(self.runner_dict.values())

    @property
    def states(self) -> List[RunnerState]:
        """
        Runner states as a list of RunnerState
        """
        return [runner.state for runner in self.runners]

    @property
    def string_states(self) -> List[str]:
        """
        Runner states as a list of strings
        """
        return [runner.state.state for runner in self.runners]

    @property
    def function(self) -> Union[Function, Script, None]:
        """
        Currently stored Function wrapper
        """
        return self._function

    @property
    def is_python(self) -> bool:
        return isinstance(self.function, Function)

    @property
    def extra(self) -> Union[None, str]:
        """Returns the global level extra"""
        return self._global_run_extra

    @extra.setter
    def extra(self, extra: str) -> None:
        """Sets the global level extra"""
        self._global_run_extra = extra

    @property
    def shebang(self) -> str:
        """returns the url shebang"""
        return self.url.shebang

    @shebang.setter
    def shebang(self, shebang: str) -> None:
        """sets the url shebang"""
        self.url.shebang = shebang

    def _script_sub(self, avoid_nodes: bool = False, **sub_args) -> str:
        """
        Substitutes run argmuents into the computer script, if it exists

        Args:
            avoid_nodes (bool):
                ignore submission scripts if True
            **sub_args:
                jobscript arguments

        Returns:
            (str):
                jobscript
        """
        # generate a default script to be used if there's no script method
        default = [self.shebang, self._script]

        extra_cache = []
        url_extra = getattr(self.url, "extra", None)
        if try_value(url_extra) is not None:
            extra_cache.append(try_value(url_extra))

        if try_value(self.extra) is not None:
            extra_cache.append(try_value(self.extra))

        extras = ["runner_extra", "tmp_extra"]
        for key in extras:
            extra = sub_args.get(key, None)
            if extra is not None:
                extra_cache.append(extra)
        default += extra_cache
        default = "\n".join(default)
        if avoid_nodes:
            logger.info("creating a jobscript for the login nodes")
            return default
        if not self._computer:
            logger.info("not a computer, returning base script")
            return default
        if "name" not in sub_args:
            logger.info("name not found in args, appending self name %s", self.name)
            sub_args["name"] = self.name
        sub_args["extra"] = "\n".join(item for item in extra_cache if item != "")
        return self.url.script(**sub_args)

    @property
    def script(self, **sub_args) -> str:
        """
        Currently stored run script

        Args:
            sub_args:
                arguments to substitute into the script() method

        Returns:
            (str):
                arg-substituted script
        """
        sub_args.update(self.run_args)
        return self._script_sub(**sub_args)

    @script.setter
    def script(self, script: str) -> None:
        """
        Set the run script
        """
        if script == self.script:
            return
        self._script = script
        self.set_runner_states("created", force=True)
        self.verbose.print(
            "Warning! The script has changed, "
            "this will allow runners to be resubmitted!",
            level=1,
        )

    @property
    def add_newline(self) -> bool:
        """
        Returns True if add_newline is set

        This controls if scripts have an additional newline enforced at the end
        """
        return self._add_newline

    @add_newline.setter
    def add_newline(self, add_newline: bool) -> None:
        """Sets the add_newline property"""
        self._add_newline = add_newline

    @property
    def submitter(self) -> str:
        """Currently stored submission command"""
        return self.url.submitter

    @submitter.setter
    def submitter(self, submitter) -> None:
        """Set the submission command"""
        self.url.submitter = submitter

    @property
    def shell(self) -> str:
        return self.url.shell

    @shell.setter
    def shell(self, shell: str) -> None:
        self.url.shell = shell

    @property
    def url(self) -> URL:
        """
        Currently stored URL object
        """
        if not hasattr(self, "_url"):
            # noinspection PyTypeChecker
            self.url = None
        elif self._url is None:
            self.url = None
        return self._url

    @url.setter
    def url(self, url: Union[URL, None] = None) -> None:
        """
        Verifies and sets the URL to be used.
        Will create an empty (local) url connection if url is None

        Args:
            url (URL):
                url to be set
        """
        logger.info("new url is being set to %s", url)
        if url is None:
            logger.info("no URL specified for this dataset, creating localhost")
            self._url: URL = URL(verbose=self.verbose)
        else:
            if not isinstance(url, URL):
                raise ValueError("URL is not a valid URL instance")
            self._url = url

        if not type(url) == URL and issubclass(type(url), URL):  # noqa: E721
            self._computer = True

        timeout = self.run_args.get("timeout", None)
        max_timeouts = self.run_args.get("max_timeouts", None)

        self._url.timeout = timeout
        self._url.max_timeouts = max_timeouts

        try:
            self.transport.url = self.url
        except AttributeError:
            pass

    @property
    def transport(self) -> Transport:
        """
        Currently stored Transport system
        """
        if getattr(self.url, "_transport", None) is None:
            self.url._set_default_transport()
        return self.url.transport

    @transport.setter
    def transport(self, transport: Union[Transport, None] = None) -> None:
        """
        Updates URL transport to `transport`

        Args:
            transport (Transport):
                transport to be verified
        """
        self.url.transport = transport

    @property
    def serialiser(self) -> serial:
        """Returns the stored serialiser object"""
        if not hasattr(self, "_serialiser"):
            self.serialiser = None
        return self._serialiser

    @serialiser.setter
    def serialiser(self, serialiser: Union[serial, None] = None) -> None:
        """
        Verifies and sets the serialiser to be used.
        Will use serialjson if serialiser is None

        Args:
            serialiser (serialiser):
                serialiser to be verified
        """
        if serialiser is None:
            logger.info("no serialiser specified, creating basic json")
            self._serialiser: serial = serialjson()

        else:
            if not isinstance(serialiser, serial):
                raise ValueError("serialiser is not a valid serial instance")
            self._serialiser: serial = serialiser

    def remove_database(self) -> None:
        """Deletes the database file"""
        os.remove(self.dbfile)

    @property
    def name(self) -> str:
        """Name of this dataset"""
        return self._name

    @name.setter
    def name(self, name: str) -> None:
        """Sets the dataset name"""
        if not isinstance(name, str):
            try:
                raise ValueError(f"name {name} is not str type")
            except TypeError as ex:
                raise ValueError(f"name {name.__name__} is not str type") from ex

        self._name = name

    def set_runner_states(
        self,
        state: str,
        uuids: list = None,
        extra: str = None,
        force: bool = False,
    ) -> None:
        """
        Update runner states to `state`

        Args:
            (str) state:
                state to set
            (list) uuids:
                list of uuids to update, updates all if not passed
        """
        logger.info("updating runner states")
        runners = []
        if uuids is not None:
            logger.info("using uuid list: %s", uuids)
            for runner in self.runners:
                if runner.uuid in uuids:
                    runners.append(runner)
        else:
            runners = self.runners

        for runner in runners:
            runner.set_state(newstate=state, force=force)

            if extra is not None:
                runner.state.extra = extra

    def check_all_runner_states(self, state: str) -> bool:
        """
        Check all runner states against `state`, returning True if `all`
        runners have this state

        Args:
            state (str):
                state to check for

        Returns (bool):
            all(states)
        """
        return all([r == state for r in self.states])

    @property
    def last_run(self) -> Union[int, None]:
        """
        Returns the unix time of the last _run call

        Returns:
            (int): unix time of last  _run call, or None if impossible
        """
        if self._last_run > 0:
            return self._last_run
        return None

    @property
    def run_summary_limit(self) -> int:
        """
        If there are more runners than this number,
        the run output will be summed up rather than printed
        """
        return self._run_summary_limit

    @run_summary_limit.setter
    def run_summary_limit(self, lim: int) -> None:
        """Sets the run summary limit"""
        self._run_summary_limit = lim

    @property
    def summary_only(self) -> bool:
        """
        Returns True if the number of runners exceeds the summary limit.
        Otherwise, returns False.

        Used for printing a shortened output when running.
        """
        return len(self.runners) > self._run_summary_limit

    def retry_failed(self, *args, **kwargs) -> None:
        """
        Retries all failed runners

        Takes args and kwargs, passes them to run
        """
        kwargs["uuids"] = [r.uuid for r in self.failed]
        kwargs["force"] = True
        self.run(*args, **kwargs)

    def stage(
        self,
        uuids: List[str] = None,
        force: bool = False,
        dependency_call: bool = False,
        extra: str = "",
        force_ignores_success: bool = False,
        verbose: Verbosity = None,
        **run_args,
    ) -> bool:
        """
        Stage all runners, generating all files and preparing for
        transfer and execution.

        Returns a boolean, True if any new content was written.
        """
        if verbose is not None:
            verbose = Verbosity(verbose)
        else:
            verbose = self.verbose

        if self.dependency and not dependency_call:
            logger.info(
                "dataset %s is a part of a dependency chain, calling from there", self
            )
            return self.dependency.stage(
                force_ignores_success=force_ignores_success,
                extra=extra,
                verbose=verbose,
                **run_args,
            )
        verbose.print("Staging Dataset", level=1, end="... ")
        verbose.print("", level=2)  # newline for higher verbose levels

        run_args["force"] = force

        if uuids is not None:
            logger.info("Staging only runners %s", format_iterable(uuids))
        else:
            if all(r.state == "staged" for r in self.runners) and not force:
                verbose.print("All runners already staged, skipping", level=1)
                return False
            uuids = [r.uuid for r in self.runners]

        # first step is to handle the writing of the scripts to the local dir
        # the runners take care of this
        master_content = [
            "export sourcedir=$PWD",
            f"source $sourcedir/{self.bash_repo.name}",
        ]
        if self._fresh_dataset:
            master_content.append(f"rm -f {self.manifest_log.name}")
        # runner staging
        staged = False
        nstaged = 0
        for runner in self.runners:
            if runner.uuid not in uuids:
                logger.info(
                    "Runner %s (uuid %s) is not in selection", runner, runner.short_uuid
                )
                continue

            ready = runner.stage(
                extra=extra,
                force_ignores_success=force_ignores_success,
                verbose=verbose,
                **run_args,
            )

            self.sanitise_run_arg_paths(runner.derived_run_args)

            if ready:
                staged = True
                nstaged += 1
        # file writing
        bash_cache = []  # list of submitters to create bash functions for
        uuid_cache = []
        for runner in self.runners:
            if runner.uuid not in uuids:
                continue
            if not runner.derived_run_args.get("force", False):
                if runner.state < "staged":
                    continue
                if runner.state >= "submit pending":
                    continue

            if runner.submitter not in bash_cache:
                bash_cache.append(runner.submitter)

            runline = runner.generate_runline(remote_dir=self.remote_dir)
            master_content.append(runline)

            uuid_cache.append(runner.uuid)
            if runner.state < "staged":
                runner.set_state(newstate="staged", force=True)
            staged = True

        if not staged:
            logger.info("no runners completed the run assessment, skipping")
            verbose.print("No Runners staged", level=1)
            return staged

        # next, we need the repositories for the runners to import from
        self._write_to_repo()
        self._write_to_bash_repo(bash_cache=bash_cache)
        # write the master file
        self.master_script.write(master_content, add_newline=self.add_newline)
        verbose.print(f"Staged {nstaged}/{len(self.runners)} Runners", level=1)

        return staged

    def transfer(
        self,
        uuids: List[str] = None,
        force: bool = False,
        dependency_call: bool = False,
        extra: str = "",
        force_ignores_success: bool = False,
        verbose: Verbosity = None,
        **run_args,
    ) -> bool:
        """
        Transfer the files to the remote
        """
        if verbose is not None:
            verbose = Verbosity(verbose)
        else:
            verbose = self.verbose

        if self.dependency and not dependency_call:
            logger.info(
                "dataset %s is a part of a dependency chain, calling from there", self
            )
            return self.dependency.transfer(verbose=verbose)

        staged = self.stage(
            uuids=uuids,
            extra=extra,
            force=force,
            force_ignores_success=force_ignores_success,
            verbose=verbose,
            **run_args,
        )
        uuid_cache = []
        for runner in self.runners:
            if uuids is not None and runner.uuid not in uuids:
                continue
            if not runner.derived_run_args.get("force", False):
                if runner.state >= "transferred":
                    continue

            self.transport.queue_for_push(runner.jobscript)
            if self.function is not None:
                self.transport.queue_for_push(runner.runfile)

            logger.info("queuing extra files to send")
            for file in runner.extra_files_send:
                self.transport.queue_for_push(file)

            uuid_cache.append(runner.uuid)

        if len(uuid_cache) == 0 and not staged:
            verbose.print("No Transfer required", level=1)
            return False

        verbose.print(
            f"Transferring for {len(uuid_cache)}/{len(self.runners)} Runners", level=1
        )

        self.transport.queue_for_push(self.master_script)

        self.transport.queue_for_push(self.bash_repo)
        self.transport.queue_for_push(self.repofile)

        self.master_script.chmod(755)
        self.transport.transfer(verbose=verbose)

        self.set_runner_states("transferred", uuids=uuid_cache)
        return True

    def run(
        self,
        force: bool = False,
        dry_run: bool = False,
        verbose: Union[None, int, bool, Verbosity] = None,
        uuids: list = None,
        extra: str = "",
        force_ignores_success: bool = False,
        dependency_call: bool = False,
        **run_args,
    ) -> bool:
        """
        Run the functions

        Args:
            force (bool):
                force all runs to go through, ignoring checks
            dry_run (bool):
                create files, but do not run
            verbose:
                Sets local verbose level
            uuids (list):
                list of uuids to run
            extra:
                extra text to add to runner jobscripts
            failed_only (bool):
                If True, `force` will submit only failed runners
            force_ignores_success (bool):
                If True, `force` takes priority over `is_success` check
            dependency_call (bool):
                Internally used to block recursion issues with dependencies
            run_args:
                any arguments to pass to the runners during this run.
                will override any "global" arguments set at Dataset init
        """
        if verbose is not None:
            verbose = Verbosity(verbose)
        else:
            verbose = self.verbose

        if self.dependency and not dependency_call:
            logger.info(
                "dataset %s is a part of a dependency chain, calling from there", self
            )
            return self.dependency.run(
                dry_run=dry_run,
                force_ignores_success=force_ignores_success,
                extra=extra,
                verbose=verbose,
                **run_args,
            )

        self.avoid_runtime()
        runtime = int(time.time())
        logger.info("#### Dataset run called at %s", runtime)
        self._run_cmd = None

        run_args["force"] = force

        if os.name == "nt" and self.url.is_local:
            raise RuntimeError(LOCALWINERROR)

        if uuids is not None:
            logger.info("running only runners %s", format_iterable(uuids))

        self.transfer(
            uuids=uuids,
            extra=extra,
            force_ignores_success=force_ignores_success,
            verbose=verbose,
            **run_args,
        )

        uuid_cache = []
        asynchronous = False
        for runner in self.runners:
            if uuids is not None and runner.uuid not in uuids:
                continue
            if not runner.derived_run_args.get("force", False):
                if runner.state >= "submit pending":
                    continue

            if runner.derived_run_args["asynchronous"]:
                asynchronous = True

            uuid_cache.append(runner.uuid)

        if len(uuid_cache) == 0:
            return self._run_finalise(verbose=verbose, passthrough=False)

        verbose.print(
            f"Remotely executing {len(uuid_cache)}/{len(self.runners)} Runners", level=1
        )

        launch_cmd = self.shell
        cmd = f"cd {self.remote_dir} && {launch_cmd} {self.master_script.name}"
        if not dry_run:
            extra = None if not force else "forced"
            self.set_runner_states(
                state="submit pending", uuids=uuid_cache, extra=extra
            )
            self._run_cmd = self.url.cmd(cmd, asynchronous=asynchronous)
            self._fresh_dataset = False
        else:
            self.set_runner_states("dry run", uuids=uuid_cache)
            msg = f"launch command: {cmd}"
            logger.info(msg)
            verbose.print(msg, 1)
            self._run_cmd = self.url.cmd(
                cmd, asynchronous=asynchronous, verbose=verbose, dry_run=True
            )

        self._last_run = runtime
        return self._run_finalise(verbose=verbose, passthrough=not dry_run)

    def _write_to_repo(self, skip_function: bool = False) -> None:
        """
        Write out the repo file for this run

        Args:
            skip_function: Skip function dump if True. Used for dependencies.
        """
        repo_class_file = repo.__file__
        with open(repo_class_file, encoding="utf8") as o:
            base_file = o.read()
        # add manifest filename, and convert to list for appending
        base_file = [base_file.replace("{manifest_filename}", self.manifest_log.name)]
        self.repofile.write(base_file)

        content = []
        # no function to write if we are relying on the scripts
        if self.is_python:
            content += [
                "\n### serialiser functions ###",
                self.serialiser.dumpfunc(),
                self.serialiser.loadfunc(),
            ]
            # allow dependencies to skip the function and handle it themselves
            if not skip_function:
                try:
                    content += [
                        "\n### primary function ###",
                        self.function.source,
                    ]
                except AttributeError:
                    pass

        if len(cached_functions) != 0:
            content += [
                "\n### cached functions ###",
                *[f.source for f in cached_functions.values()],
            ]

        if len(content) == 0:
            return

        self.repofile.append("\n".join(content))

    def _write_to_bash_repo(self, bash_cache: List[str]) -> None:
        content = []
        for i, sub in enumerate(bash_cache):
            add_doc = i == len(bash_cache) - 1
            script_run = not self.is_python
            run_func = create_run_function(
                submitter=sub,
                script_run=script_run,
                add_docstring=add_doc,  # add docstring for first function only
                manifest_filename=self.manifest_log.name,
            )
            content.append(run_func)

        self.bash_repo.write(content)

    def _run_finalise(
        self,
        passthrough: bool,
        verbose: Union[None, int, bool, Verbosity] = None,
    ) -> bool:
        if verbose is not None:
            verbose = Verbosity(verbose)
        else:
            verbose = self.verbose
        if self.summary_only:
            run = 0
            skip = 0
            force = 0
            for runner in self.runners:
                if runner._run_state == "skip":
                    skip += 1
                elif runner._run_state == "run":
                    run += 1
                elif runner._run_state == "force":
                    run += 1
                    force += 1
            # condense the summary into a single line
            output = [f"Of {len(self.runners)} runners, {run} run,"]

            if force > 0:
                output.append(f"({force} forced)")
            if skip > 0:
                output.append(f"({skip} skipped)")

            output.append("see run_log for more info")

            msg = " ".join(output)
            logger.info(msg)
            verbose.print(msg, level=1)

        self.update_db()
        return passthrough

    @property
    def run_cmd(self) -> CMD:
        """
        Access to the storage of CMD objects used to run the scripts

        Returns:
            (list): List of CMD objects
        """
        return self._run_cmd

    def check_states(self, state: str) -> dict:
        """Call the repo "last_time" method remotely"""
        cmd = (
            f"cd {self.remote_dir} && "
            f"{self.url.python} {self.repofile.name} "
            f"None check_last {state}"
        )

        string = self.url.cmd(cmd).stdout
        result = json.loads(string)

        return result

    def check_started(self) -> dict:
        """Check when runners started remotely, using the manifest"""
        return self.check_states("started")

    @property
    def is_finished(self) -> list:
        """Queries the finished state of this Dataset"""
        return self._is_finished()

    @property
    def is_finished_force(self) -> list:
        """Queries the finished state of this Dataset"""
        return self._is_finished(force=True)

    def _is_finished(
        self,
        check_dependency: bool = True,
        dependency_call: bool = False,
        force: bool = False,
    ) -> list:
        """
        Query the runners and return their states

        Args:
            check_dependency: Checks the dependency if True
            dependency_call: Internal flag to prevent recursion errors
            force: passthrough for update_runners force
        """
        self.avoid_runtime()
        t = int(time.time())
        logger.info("#### _is_finished called at %s", t)
        fin = {r.uuid: r.is_finished for r in self.runners}

        if all(r.is_success for r in self.runners):
            logger.info("all runners are marked Succeeded, returning early")
            return list(fin.values())

        self.update_runners()

        if (
            self.run_cmd is not None
            and self.run_cmd.returncode is not None
            and self.run_cmd.is_finished
            and not self.run_cmd.succeeded
        ):
            stderr = self.run_cmd.communicate(ignore_errors=True)["stderr"]
            msg = f"Dataset encountered an issue:\n{stderr}"
            if force:
                warnings.warn(msg)
            else:
                raise RuntimeError(msg)

        if check_dependency and not dependency_call and self.dependency is not None:
            self.dependency.check_failure()

        fin = {r.uuid: r.is_finished for r in self.runners}

        return list(fin.values())

    @property
    def all_finished(self) -> bool:
        """
        Check if `all` runners have finished

        Returns (bool):
            True if all runners have completed their runs
        """
        return all(self.is_finished)

    @property
    def all_success(self) -> bool:
        """Returns True if all runners report that they have succeeded"""
        self._is_finished()
        return all([r.is_success for r in self.runners])

    def wait(
        self,
        interval: Union[int, float] = 10,
        timeout: Optional[Union[int, float]] = None,
        watch: bool = False,
        success_only: bool = False,
        only_runner: Optional[Runner] = None,
        force: bool = False,
    ) -> None:
        """
        Watch the calculation, printing updates as runners complete

        Args:
            interval:
                check interval time in seconds
            timeout:
                maximum time to wait in seconds
            watch:
                print an updating table of runner states
            success_only:
                Completion search ignores failed runs if True
            only_runner:
                wait for only this runner to complete
            force:
                Raises dataset level errors as errors if True

        Returns:
            None
        """

        def wait_condition() -> bool:
            states = self._is_finished(force=force)

            if only_runner is not None:
                return only_runner.is_finished
            if success_only:
                return self.all_success

            return all([s for s in states if s is not None])

        def print_status() -> None:
            from IPython.display import clear_output

            # noinspection PyUnboundLocalVariable
            clear_output(wait=True)
            print(f"watching {len(self.runners)} runners, with a {interval}s interval")

            if timeout:
                print(f"will time out if t > {timeout}")

            print(f"t={dt:.1f}")

            for runner in self.runners:
                statetxt = runner.state
                print(f"{runner.name}, {statetxt}")

        t0 = int(time.time())
        # check all non None states
        while not wait_condition():
            dt = int(time.time()) - t0

            if watch:
                print_status()

            if timeout is not None and dt > timeout:
                raise RuntimeError("wait timed out")

            time.sleep(interval)

        if watch:
            print_status()

    def fetch_results(
        self,
        results: bool = True,
        errors: bool = True,
        extras: bool = True,
        force: bool = False,
        verbose: Union[None, int, bool, Verbosity] = None,
    ):
        """
        Fetch results from the remote, and store them in the runner results property

        Args:
            results:
                fetch result files
            errors:
                fetch error files
            extras:
                fetch extra files
        Returns:
            None
        """
        if verbose is not None:
            verbose = Verbosity(verbose)
        else:
            verbose = self.verbose
        self.avoid_runtime()
        t = int(time.time())
        logger.info("#### fetch_results called at %s", t)

        # if we're going to rely on runner states, we should update them
        self._is_finished(check_dependency=False, force=force)

        transfer = False
        level = 3
        verbose.print("Fetching results", level=1)
        verbose.print("Checking Runner states", level=level)
        for runner in self.runners:
            verbose.print(f"\t{runner}", level=level, end="... ")
            if runner.state == "satisfied":
                verbose.print("Already marked Satisfied", level=level, end=", ")
                if not runner.verify_local_files():
                    logger.info(
                        "runner resultfile is missing locally, attempting a pull"
                    )
                    self.transport.queue_for_pull(runner.resultfile)
                    for file in runner.extra_files_recv:
                        self.transport.queue_for_pull(file)
                    transfer = True
                    verbose.print("with missing files", level=level, end="")
                else:
                    logger.info("runner is satisfied, no work needed")
                    verbose.print("no work needed", level=level, end="")

            elif runner.state == "completed":
                transfer = True
                verbose.print("Completed", level=level, end="")
                if results:
                    logger.info("runner marked as completed, pulling result")
                    self.transport.queue_for_pull(runner.resultfile)
                    verbose.print(", pulling result", level=level, end="")
                else:
                    logger.info("runner marked as completed, but ignoring result")
                    verbose.print("ignoring result", level=level, end="")

                if runner.errorfile.size != 0:
                    # There can be an error and result, so we should pull both
                    if errors:
                        verbose.print(", pulling error", level=level, end="")
                        self.transport.queue_for_pull(runner.errorfile)

                if extras:
                    verbose.print(", pulling extras", level=level, end="")
                    for file in runner.extra_files_recv:
                        self.transport.queue_for_pull(file)

            elif runner.state == "failed":
                transfer = True
                logger.info("runner marked as completed, pulling error")
                verbose.print(", runner marked as failed", level=level, end="")
                if errors:
                    self.transport.queue_for_pull(runner.errorfile)
                    verbose.print(", pulling error", level=level, end="")

            verbose.print("", level=level)

        if transfer:
            logger.info("a transfer was requested, transfer and read")
            self.transport.transfer(raise_errors=False, verbose=verbose)

            self.update_runners()

            for runner in self.runners:
                runner.read_local_files(force=force)

            for cmd in self.transport.cmds:
                if cmd.stderr:
                    warnings.warn(
                        f"\nWARNING! When transferring files, "
                        f"fetch_results encountered an error:\n{cmd.stderr}"
                    )
        else:
            verbose.print("No Transfer Required", level=1)

        self.update_db()

    def update_runners(
        self,
        runners: Union[list, None] = None,
        dependency_call: bool = False,
    ):
        """
        Collects the manifest file, updating runners

        Args:
            runners: list of runners to update, usually used for dependencies
            dependency_call: internal flag to avoid dependecy loops
        """
        if self.dependency is not None and not dependency_call:
            self.dependency.update_runners()

        if runners is None:
            runners = self.runners

        logger.debug("parsing log")
        manifest = repo.Manifest(instance_uuid=self.short_uuid)
        manifest.runner_mode = True

        log_collection = self.url.cmd(
            f"cat {self.manifest_log.remote}", raise_errors=False
        )
        if log_collection.succeeded:
            runner_data = manifest.parse_log(string=log_collection.stdout)

            for runner in runners:
                if runner.short_uuid in runner_data["log"]:
                    logger.debug("Runner %s:", runner)
                    for logline in runner_data["log"][runner.short_uuid]:
                        timestamp, data = logline
                        logger.debug("\t%s", logline)
                        runner.set_state(
                            newstate=data.strip(),
                            state_time=timestamp,
                            check_state=False,
                        )
                else:
                    logger.debug("Runner %s not found", runner)

    @property
    def results(self) -> list:
        """
        Access the results of the runners

        Returns (list):
            ``runner.result`` for each runner
        """
        self.avoid_runtime()
        logger.info("#### Dataset results called")
        # check first for errors
        n_errors = len([e for e in self.errors if e is not None])
        if n_errors != 0:
            msg = (
                f"Warning! Found {n_errors} error(s), also check the `errors` property!"
            )
            logger.warning(msg)
            self.verbose.print(msg, level=1)
        return [r.result for r in self.runners]

    @property
    def errors(self) -> list:
        """
        Access the errors of the runners

        Returns (list):
            ``runner.error`` for each runner
        """
        self.avoid_runtime()
        logger.info("#### Dataset errors called")
        return [r.error for r in self.runners]

    @property
    def failed(self) -> List[Runner]:
        """
        Returns a list of failed runners

        Returns:
            list of failed runners
        """
        return [r for r in self.runners if r.state.failed]

    def prepare_for_transfer(self) -> None:
        """Ensures that the Transport class is able to function"""
        # ensure transport url is synced
        self.transport.url = self.url

    def avoid_runtime(self) -> None:
        """
        Call for last_runtime sensitive operations such as is_finished and fetch_results

        Waits for 1s if we're too close to the saved _last_run time

        Returns:
            None
        """
        self.prepare_for_transfer()
        checktime = int(time.time())

        if checktime <= self._last_run:
            logger.info("call is too soon after last run, sleeping for 1s")
            time.sleep(1)


def line_starts_with_uuid(line: str) -> bool:
    """
    Checks if line starts with a short uuid

    returns True if line starts like "a1b2c3d4", False otherwise
    """
    search = re.compile(r"[0-9A-F]{8}", re.IGNORECASE)

    return re.match(search, line) is not None
