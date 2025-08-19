"""
Main Runner object. This object handles data I/O and metadata for a single
run instance
"""

import bisect
import copy
import json
import logging
import os
from datetime import datetime
import time
from typing import Dict, Optional, Union

from remotemanager.dataset.files_mixin import ExtraFilesMixin
from remotemanager.dataset.runnerstates import RunnerState
from remotemanager.utils.format_iterable import format_iterable
from remotemanager.utils.verbosity import VerboseMixin, Verbosity
from remotemanager.script.script import Script
from remotemanager.storage.database import Database
from remotemanager.storage.sendablemixin import INTERNAL_STORAGE_KEYS
from remotemanager.storage.sendablemixin import SendableMixin
from remotemanager.storage.trackedfile import TrackedFile
from remotemanager.utils import object_from_uuid, _time_format, ensure_list
from remotemanager.utils.uuid import UUIDMixin, generate_uuid

logger = logging.getLogger(__name__)


SERIALISED_STORAGE_KEY = INTERNAL_STORAGE_KEYS["SERIALISED_STORAGE_KEY"]

LOCALWINERROR = """Local runs on windows machines are not supported.
Please use a URL which connects to a non-windows machine or consider using
Docker to continue."""


def format_time(t: datetime) -> str:
    """
    Format the datetime object into a dict key

    Args:
        t (datetime.time):
            time object to be formatted to string

    Returns:
        (str):
            formatted time
    """
    return t.strftime(_time_format)


class Runner(SendableMixin, ExtraFilesMixin, VerboseMixin, UUIDMixin):
    """
    The Runner class stores any info pertaining to this specific run. E.g.
    Arguments, result, run status, files, etc.

    .. warning::
        Interacting with this object directly could cause unstable behaviour.
        It is best to allow Dataset to handle the runners. If you require a
        single run, you should create a Dataset and append just that one run.
    """

    _defaults = {
        "skip": True,
        "force": False,
        "asynchronous": True,
        "local_dir": "temp_runner_local",
        "remote_dir": "temp_runner_remote",
    }

    _args_replaced_key = "~serialised_args~"

    _do_not_package = ["_serialiser", "_parent", "_database"]

    def __init__(
        self,
        arguments: dict,
        parent,
        self_id: str,
        extra_files_send: Union[list, str, None] = None,
        extra_files_recv: Union[list, str, None] = None,
        verbose: Union[None, int, bool, "Verbosity"] = None,
        extra: Optional[str] = None,
        **run_args,
    ):
        self.verbose = verbose

        self.run_args = run_args
        self._run_args_temp = {}  # temporary args for storing runtime overrides
        self.extra = extra

        self._extra_filenames_base = {
            "send": extra_files_send if extra_files_send is not None else [],
            "recv": extra_files_recv if extra_files_recv is not None else [],
        }
        self._extra_filenames_temp = {"send": [], "recv": []}

        if arguments is None:
            arguments = {}

        if not isinstance(arguments, dict):
            raise ValueError(f"runner arguments ({type(arguments)}) must be dict-type")

        # parent and id setting
        self._parent = parent
        self._parent_uuid = parent.uuid  # used for parent memory recovery

        self._id = self_id

        # check that we can properly serialise the args
        # this needs to be within the runner, so we can properly generate uuids
        self._args_replaced = False
        try:
            # check that the args can be sent via json
            self._args = json.loads(json.dumps(arguments))
            self._generate_uuid()
            logger.info("args pass a json dump, proceeding directly")
        except TypeError:
            # if they can't, fall back on the serialiser
            file = f"{self.parent.argfile}-{self.id}{self.serialiser.extension}"
            logger.info("args require treatment, using file %s", file)

            argfile = TrackedFile(self.parent.local_dir, self.remote_dir, file)
            if not os.path.isdir(self.parent.local_dir):
                os.makedirs(self.parent.local_dir)

            content = self.parent.serialiser.dumps(arguments)
            argfile.write(content)

            # adding the file in here forces the run_args to swap out
            # run_args for a repo.load
            arguments = {file: Runner._args_replaced_key}
            self._args = arguments
            self._args_replaced = True

            self._generate_uuid({"uuid_base": generate_uuid(str(content))})

            self._extra_filenames_base["send"].append(argfile)

        logger.info("new runner (id %s) created", self.uuid)

        self._dependency_info = {}

        self._history = {}
        self.set_state("created", force=True)
        self._last_submitted = 0
        self._run_state = None

        # store a reference for all trackedfiles for updating
        self._trackedfiles = {}

    def __hash__(self) -> int:
        return hash(self.uuid)

    def __repr__(self) -> str:
        return self.identifier

    def __deepcopy__(self, memo):
        """
        Override deepcopy, avoiding references to parent

        Initial code taken from this answer:
        https://stackoverflow.com/a/15774013
        """
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            if k in Runner._do_not_package:
                continue
            setattr(result, k, copy.deepcopy(v, memo))
        return result

    def _generate_uuid(self, extra=None):
        slug = {}
        slug.update(self.derived_run_args)

        if extra is not None:
            slug.update(extra)
        else:
            slug.update(self._args)

        self.generate_uuid(format_iterable(slug) + str(self.parent.uuid))

    @property
    def database(self) -> Database:
        """
        Returns the parent Dataset's database

        Returns:
            Database
        """
        return self.parent.database

    @property
    def parent(self):
        """Returns the parent Dataset object"""
        if self.is_missing("_parent"):
            self._parent = object_from_uuid(self._parent_uuid, "Dataset")
        return self._parent

    @property
    def identifier(self) -> str:
        """
        Returns a unique identifier for this,
        also used in the names of Runner created files.
        """
        return f"{self.parent.name}-{self.parent.short_uuid}-{self.id}"

    @property
    def serialiser(self):
        """Returns the parent Serialiser object"""
        return self.parent.serialiser

    @staticmethod
    def _set_defaults(kwargs: dict = None) -> dict:
        """
        Sets default arguments as expected. If used as a staticmethod, returns
        the defaults
        """

        if kwargs is None:
            kwargs = {}

        for k, v in Runner._defaults.items():
            if k not in kwargs:
                kwargs[k] = v

        return kwargs

    @property
    def id(self) -> str:
        """Returns this Runner's current ID"""
        return self._id

    @property
    def name(self) -> str:
        """Returns this Runner's name"""
        return self._id

    def _format_filename(self, ftype: str, ext: str) -> str:
        """
        Formats internal file names consistently.

        Args:
            ftype (str):
                file type. Jobscript, result file, etc.
            ext (str):
                file extension

        Returns:
            str: formatted filename
        """
        return f"{self.identifier}-{ftype}{ext}"

    def _trackedfile_factory(self, remote, ftype, extension):
        ext = self._format_filename(ftype, extension)
        return TrackedFile(self.local_dir, remote, ext)

    @property
    def runfile(self) -> TrackedFile:
        """
        Filename of the python runfile
        """
        file = self._trackedfiles.get("runfile", None)

        if file is None:
            ext = ".py" if self.parent.is_python else ".sh"
            file = self._trackedfile_factory(self.remote_dir, "run", ext)
            self._trackedfiles["runfile"] = file

        return file

    @property
    def jobscript(self) -> TrackedFile:
        """
        Filename of the run script
        """
        file = self._trackedfiles.get("jobscript", None)

        if file is None:
            file = self._trackedfile_factory(self.remote_dir, "jobscript", ".sh")
            self._trackedfiles["jobscript"] = file

        return file

    @property
    def resultfile(self) -> TrackedFile:
        """
        Result file name
        """
        file = self._trackedfiles.get("resultfile", None)

        if file is None:
            if self.parent.is_python:
                result_ext = self.parent.serialiser.extension
            else:
                result_ext = ".txt"
            file = self._trackedfile_factory(self.run_path, "result", result_ext)
            self._trackedfiles["resultfile"] = file

        return file

    @property
    def errorfile(self) -> TrackedFile:
        """
        File tracker for error dumpfile
        """
        file = self._trackedfiles.get("errorfile", None)

        if file is None:
            file = self._trackedfile_factory(self.run_path, "error", ".out")
            self._trackedfiles["errorfile"] = file

        return file

    @property
    def local_dir(self) -> str:
        """
        Local staging directory
        """
        return self.derived_run_args.get("local_dir")

    @local_dir.setter
    def local_dir(self, path: str) -> None:
        """
        Sets the local_dir
        """
        self.run_args["local_dir"] = path

    @property
    def remote_dir(self) -> str:
        """
        Target directory on the remote for transports
        """
        return self._replacehome(self.derived_run_args["remote_dir"])

    @remote_dir.setter
    def remote_dir(self, path: str) -> None:
        """
        Sets the remote_dir
        """
        logger.debug("setting remote dir to %s", path)
        self.run_args["remote_dir"] = path

    @property
    def run_path(self) -> Union[str, None]:
        """
        Intended running directory. If not set, uses remote_dir

        .. note::
            If both remote_dir and run_dir are set, the files will be
            transferred to remote_dir, and then executed within run_dir
        """
        if self.derived_run_args.get("run_dir", None) is not None:
            return os.path.join(self.remote_dir, self.derived_run_args["run_dir"])
        return self.remote_dir

    @property
    def run_dir(self) -> Union[str, None]:
        """
        Intended running directory. If not set, uses remote_dir

        .. note::
            If both remote_dir and run_dir are set, the files will be
            transferred to remote_dir, and then executed within run_dir
        """
        if (
            "run_dir" in self.derived_run_args
            and self.derived_run_args["run_dir"] is not None
        ):
            return self._replacehome(self.derived_run_args["run_dir"])
        return self.remote_dir

    @run_dir.setter
    def run_dir(self, run_dir: str) -> None:
        """
        Sets the run_dir
        """
        self.run_args["run_dir"] = run_dir

    def _replacehome(self, path):
        if "$HOME" in path:
            return path.replace("$HOME", self.parent.url.home)
        elif path.startswith("~"):
            return path.replace("~", self.parent.url.home)
        return path

    @property
    def derived_run_args(self) -> dict:
        """
        Returns the base run args.

        Returns:
            _run_args
        """
        base = copy.deepcopy(self.parent.run_args)

        base.update(self.run_args)
        base.update(self._run_args_temp)

        return base

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

    def set_run_args(self, keys: list, vals: list) -> None:
        """
        Set a list of `keys` to `vals

        .. note::
            List lengths must be the same

        Args:
            keys:
                list of keys to set
            vals:
                list of vals to set to
        """
        keys = ensure_list(keys)
        vals = ensure_list(vals)

        if len(keys) != len(vals):
            raise ValueError(
                f"number of keys ({len(keys)}) != number of vals ({len(vals)}"
            )

        for key, val in zip(keys, vals):
            self.run_args[key] = val

    def update_run_args(self, d: dict) -> None:
        """
        Update current global run args with a dictionary `d`

        Args:
            d:
                dict of new args
        """
        self.run_args.update(d)

    @property
    def args(self) -> dict:
        """
        Arguments for the function
        """
        if self._args is None:
            return {}
        return self._args

    @property
    def extra_files_send(self) -> list:
        """Returns the list of extra files to be sent"""
        send = self._extra_filenames_base["send"] + self._extra_filenames_temp["send"]
        return self._convert_files(send)

    @property
    def extra_files_recv(self) -> list:
        """Returns the list of extra files to be retrieved"""
        send = self._extra_filenames_base["recv"] + self._extra_filenames_temp["recv"]
        return self._convert_files(send, recv=True)

    @property
    def history(self) -> Dict[str, str]:
        """
        Sorted state history of this runner

        Returns:
            Dict[str, str]:
                A dictionary mapping timestamps to log messages
                Note that timestamps have a /{index} suffix to indicate sub-second
                precision.
                For example: "2025-01-20 10:00:00/0" is the first log message occuring
                at that time. Following events will be listed as `/1`, `/2`, until the
                next second.
        """
        # need a pair of lists, for times and log lines
        times = []
        lines = []
        for timestamp, log in self._history.items():
            # find the chronological sort point for this insertion
            bisect_point = bisect.bisect(times, timestamp)
            # insert timestamp and lines
            idx = 0
            for line in log:  # add all the lines from this time step
                insertion_point = bisect_point + idx
                idx += 1
                # insert if we're not at the end
                if insertion_point < len(times):
                    times.insert(insertion_point, timestamp)
                    lines.insert(insertion_point, line)
                else:  # else append to the end
                    times.append(timestamp)
                    lines.append(line)
        output = {}  # now convert these sorted lists into the correct format
        for i, t in enumerate(times):
            line = lines[i]
            # base timestring, modified with /instance mod
            base_timestring = format_time(datetime.fromtimestamp(t))
            idx = 0
            timestring = f"{base_timestring}/{idx}"
            while timestring in output:
                idx += 1
                timestring = f"{base_timestring}/{idx}"  # find a valid string
            output[timestring] = line
        return output

    @property
    def status_list(self) -> list:
        """
        Returns a list of status updates
        """
        return list(self.history.values())

    def insert_history(
        self,
        t: Union[datetime, int, float],
        newstate: str,
        force: bool = False,
    ) -> bool:
        """
        Insert a state into this runner's history

        Args:
            t (datetime.time):
                time this state change occurred
            newstate (str):
                status to update
            force (bool):
                skips checks if True
        """
        if isinstance(t, int):
            pass
        elif isinstance(t, float):
            t = int(t)
        elif isinstance(t, datetime):
            t = int(datetime.timestamp(t))
        else:
            try:
                t = int(t)
            except (TypeError, ValueError) as ex:
                raise ValueError(
                    f"time of type {type(t)} should be a datetime instance"
                ) from ex

        if isinstance(t, (int, float)):
            if t == 0:
                raise ValueError(f"invalid timestamp: {t}")

        if not force and t < self.last_submitted:
            logger.debug(
                "ignoring state %s, t=%s < last run %s",
                newstate,
                t,
                self.last_submitted,
            )
            return False

        # check that this state does not already exist
        if not force and newstate in self._history.get(t, []):
            return False

        logger.info(
            "(%s) updating runner %s history: %s -> %s",
            t,
            self.short_uuid,
            getattr(self, "state", None),
            newstate,
        )
        try:
            self._history[t].append(newstate)
        except KeyError:
            self._history[t] = [newstate]

        return True

    @property
    def state(self) -> RunnerState:
        """
        Returns the most recent runner state
        """
        return self._state

    @state.setter
    def state(self, newstate: str):
        self.set_state(newstate)

    def set_state(
        self,
        newstate: str,
        value: int = None,
        state_time: Union[datetime, int, float, None] = None,
        force: bool = False,
        check_state: bool = True,
    ) -> None:
        """
        Update the state and store within the runner history

        .. versionadded:: 0.9.3
            now checks the current state before setting, won't duplicate states unless
            force=True

        Args:
            newstate:
                state to set to
            value:
                exclusive to the "copied" state, allows setting of the value
            state_time:
                set the state at this time, rather than now
            force:
                skip currentstate checking if True
            check_state:
                raises a ValueError if True and newtate is not a valid state
        """
        if not force and self.state == newstate:
            return

        t = int(time.time())
        if state_time is None:
            state_time = datetime.fromtimestamp(t)

        inserted = self.insert_history(t=state_time, newstate=newstate, force=force)
        if not inserted:
            return

        if not check_state and newstate not in RunnerState._states:
            return

        self._state: RunnerState = RunnerState(newstate, value=value)

    @property
    def last_submitted(self) -> int:
        """
        Return the timestamp of the last submission time.
        If no submission has been made yet, returns -1.
        """
        return self.last_state_time("submit pending")

    def last_state_time(self, state: str) -> int:
        """
        Return the timestamp of the last time the state was changed.
        If no state change has been made yet, returns -1.
        """
        chronological_times = sorted(list(self._history.keys()))
        for ts in chronological_times[::-1]:
            if state in self._history[ts]:
                return ts
        return -1

    @property
    def submitter(self) -> str:
        """
        Return the submitter of this runner.
        """
        if self.derived_run_args.get("avoid_nodes", False):
            return self.parent.url.shell
        return self.parent.url.submitter

    def generate_runline(
        self,
        remote_dir: Union[str, None] = None,
        child: bool = False,
    ) -> str:
        """
        Generates a runline for this runner

        Args:
            submitter: submitter for this run
            remote_dir: override the remote directory
            child: Used by Dependencies, if this runner is a child, we should skip any
                path modifications
        """
        remote_dir = remote_dir or self.parent.master_script.remote_dir

        errorpath = self.errorfile.relative_remote_path(remote_dir)
        jobscript = self.jobscript.relative_remote_path(remote_dir)
        jobpath, jobfile = os.path.split(jobscript)

        submitter_cmd = self.submitter.split(" ", maxsplit=1)[0]
        runline = [
            f"submit_job_{submitter_cmd} {self.short_uuid} "
            f"{jobfile} {errorpath} {self.resultfile.name}"
        ]
        if self.remote_dir != self.run_path:
            runline.insert(0, f"mkdir -p {self.run_dir} &&")

        # get relative path to jobscript, but we must ``cd`` into it to stop any
        # run_dirs being created in the wrong remote
        if remote_dir != self.remote_dir:
            runline.insert(0, f"cd {jobpath} && ")

        asynchronous = self.derived_run_args["asynchronous"]
        if asynchronous and self.submitter == "bash":
            logger.debug('appending "&" for async run')
            runline.append("&")

        if child:
            runline.insert(0, "cd $sourcedir &&")

        return " ".join(runline)

    def stage(
        self,
        extra_files_send: list = None,
        extra_files_recv: list = None,
        repo: str = None,
        extra: str = None,
        parent_check: str = "",
        child_submit: list = None,
        force_ignores_success: bool = False,
        verbose: Union[None, int, bool, Verbosity] = None,
        **run_args,
    ) -> bool:
        """
        Prepare this runner for a run by creating files in the local dir

        Args:
            extra_files_send:
                list of extra files to send
            extra_files_recv:
                list of extra files to receive
            repo (str):
                override the repo target
            extra (str):
                extra lines to append to jobscript. This goes _last_.
            parent_check (str):
                INTERNAL, extra string to check that the parent result exists
            child_submit (list):
                INTERNAL, list of extra lines to submit children
            force_ignores_success (bool):
                If True, `force` takes priority over `is_success` check
            verbose:
                local verbosity
            run_args:
                temporary run args for this run

        Returns:
            bool: True if runner is ready
        """
        if self.parent.summary_only:
            verbose = Verbosity(0)
        elif verbose is not None:
            verbose = Verbosity(verbose)
        else:
            verbose = self.verbose
        self._run_args_temp = run_args
        # create the run_args for this run
        # start empty, so we don't overwrite, then update with stored and temp args
        # now we have our run_args, check if we're even running
        if not self.assess_run(
            self.derived_run_args,
            force_ignores_success=force_ignores_success,
            verbose=verbose,
        ):
            return False

        # clear out and recreate any TrackedFiles that might be from previous runs
        self._trackedfiles = {}
        # handle extra files the same as the args
        if extra_files_send is not None:
            self._extra_filenames_temp["send"] += ensure_list(extra_files_send)
        if extra_files_recv is not None:
            self._extra_filenames_temp["recv"] += ensure_list(extra_files_recv)

        if self.parent.is_python:
            self.generate_jobscript(
                parent_check=parent_check,
                child_submit=child_submit,
                extra=extra,
            )
            self.stage_python(
                repo=repo,
            )
        elif isinstance(self.parent.function, Script):
            self.generate_jobscript(
                parent_check=parent_check,
                child_submit=child_submit,
                extra=extra,
            )
            self.stage_script(
                script=self.parent.function,
            )
        else:
            self.stage_none(extra=extra)

        self.jobscript.chmod(755)
        self.runfile.chmod(755)

        # set state to staged and return
        self._result = None
        self._error = None
        self.state = "staged"

        # clear any existing error files
        try:
            os.remove(self.errorfile.local)
        except FileNotFoundError:
            pass
        return True

    def generate_jobscript(
        self, parent_check: str, child_submit: list, extra: str
    ) -> None:
        """
        Generates and writes the jobscript for this runner.

        Args:
            parent_check (str):
                Internal argument, the bash code to check for the parent result
            child_submit (list):
                Internal argument, the bash code to submit the child
            extra (str):
                Any extra content for the jobscript

        Returns:
            None
        """
        errorpath = self.errorfile.relative_remote_path(self.run_path)
        # jobscript writing
        if self.parent.is_python:
            exec_cmd = self.parent.url.python
        else:
            exec_cmd = self.parent.url.shell

        sourcedir_default = "if [ -z ${sourcedir} ] ; then export sourcedir=$PWD; fi"
        if self.run_path != self.remote_dir:
            logger.debug("run dir is separate to remote dir, appending extras")
            submit = (
                f"{sourcedir_default}\n"
                f"pydir=$PWD\n"
                f"{parent_check}cd {self.run_dir} && "
                f"source $sourcedir/{self.parent.bash_repo.name}\n"
                f"{exec_cmd} ${{pydir}}/{self.runfile.name} 2>> {errorpath}"
            )
        else:
            submit = (
                f"{sourcedir_default}\n"
                f"source $sourcedir/{self.parent.bash_repo.name}\n"
                f"{parent_check}{exec_cmd} {self.runfile.name} 2>> {errorpath}"
            )
            logger.debug("directly using script %s", submit)

        # generate the script proper
        # append or inject the submission lines
        submit_stub = "#SUBMISSION_SUBSTITUTION#"
        append_submit = True

        run_args = copy.deepcopy(self.derived_run_args)
        run_args["runner_extra"] = self.extra
        run_args["tmp_extra"] = extra

        script = self.parent._script_sub(**run_args)
        script_clean = []
        for line in script.split("\n"):
            if submit_stub in line:
                script_clean.append(submit)
                append_submit = False
            else:
                script_clean.append(line)
        # if we didn't replace the stub, append it to the script end
        if append_submit:
            script_clean.append(submit)
            logger.info("appended submit block")

        # if this runner has children, append the lines to submit them
        if child_submit is not None:
            for line in child_submit:
                script_clean.append(line)

        script = "\n".join(script_clean)
        self.jobscript.write(script, add_newline=self._parent.add_newline)

    def stage_python(self, repo: str) -> None:
        """
        Stage a "python" based run. Generates the python runfile.

        Args:
            repo (str): Remote relative path to the respository
        """
        # check if we have replaced args with a file, and use that if so
        if self._args_replaced:
            argstore = list(self.args.keys())[0]
            # args are stored in path at argstore we need the
            # relative path from run_dir, set up a temporary TrackedFile for this
            tmp = TrackedFile("", self.remote_dir, argstore)
            path = tmp.relative_remote_path(self.run_path)

            logger.debug("using argstore path %s", path)
            argline = f'kwargs = repo.{self.parent.serialiser.loadfunc_name}("{path}")'
        else:
            argline = f"kwargs = {self.args}"

        # python file writing
        # if repo is not overidden by a dependency, generate the import path here
        if repo is None:
            repo = self.parent.repofile.name

        # script proper
        runscript = [
            "import importlib.util, os, sys, time",
            "from datetime import datetime, timezone",
            "remote_path = os.path.expandvars('$sourcedir')",
            f"path = os.path.join(remote_path, '{repo}')",
            "spec = importlib.util.spec_from_file_location('repo', path)",
            "repo = importlib.util.module_from_spec(spec)",
            "spec.loader.exec_module(repo)\n",
            f"manifest = repo.Manifest('{self.short_uuid}')",
            "manifest.runner_mode = True",
            # need to add this instance of the manifest for the function
            "repo.manifest = manifest",
            "starttime = int(time.time())",
            "manifest.write('started')",
            "vmaj, vmin, vpat, *extra = sys.version_info",
            "if vmaj < 3:",
            "\tmanifest.write('failed - Python Version')",
            '\traise RuntimeError(f"Python version {vmaj}.{vmin}.{vpat} < 3.x.x")',
            argline,
            f"try:\n\tresult = repo.{self.parent.function.name}(**kwargs)",
            "except Exception:\n\tmanifest.write('failed')",
            "\traise",
            "else:",
            f"\tlast_reported_starttime = manifest.last_time('started').get('"  # comma
            f"{self.short_uuid}', -1)",
            "\tif last_reported_starttime <= starttime: # no output for outdated run",
            "\t\tmanifest.write('completed')",
            f"\t\trepo.{self.parent.serialiser.dumpfunc_name}"  # no comma
            f"(result, '{self.resultfile.name}')",
        ]
        # if this runner is a child, we need to import the previous results
        if self.parent.is_child:
            # if the script changes, the insert point may need to be updated
            runscript.insert(7, self._dependency_info["parent_import"])

        self.runfile.write("\n".join(runscript), add_newline=self._parent.add_newline)

    def stage_script(self, script: Script):
        """
        Stage a "script" based run. Generates the python runfile.

        Args:
            script (Script): Script entity to parameterise.
        """
        if self._args_replaced:
            raise RuntimeError(
                "Arguments have been replaced by a file "
                "(potentially for serialisation purposes). "
                "This is only compatible with a python function."
            )

        self.runfile.write(
            script.script(**self.args), add_newline=self._parent.add_newline
        )

    def stage_none(self, extra: str) -> None:
        """
        Fallback run mode when python or script are not used.

        Args:
            extra (str): Extra args
        """
        if self._args_replaced:
            raise RuntimeError(
                "Arguments have been replaced by a file "
                "(potentially for serialisation purposes). "
                "This is only compatible with a python function."
            )

        run_args = copy.deepcopy(self.derived_run_args)
        run_args["runner_extra"] = self.extra
        run_args["tmp_extra"] = extra

        run_args.update(self.args)

        script = self.parent._script_sub(**run_args)
        self.jobscript.write(script, add_newline=self._parent.add_newline)

    def assess_run(
        self,
        run_args: dict,
        force_ignores_success: bool = False,
        verbose: Union[None, int, bool, Verbosity] = None,
    ) -> bool:
        """
        Check whether this runner should be running.

        If `force` is True we always run

        If `skip` is True, we have to check if a run is ongoing, or a result exists

        Args:
            quiet:
                Do not print status if True
            run_args:
                Temporary args specific to this run instance
            force_ignores_success (bool):
                If True, `force` takes priority over `is_success` check
            verbose:
                local verbosity
        Returns:
            bool: True if runner has the green light
        """
        if verbose is not None:
            verbose = Verbosity(verbose)
        else:
            verbose = self.verbose
        logger.info("assessing run for runner %s", self)
        verbose.print(f"assessing run for runner {self}", end="... ", level=2)
        logger.info("run args: %s", format_iterable(run_args))

        if self.is_success and not force_ignores_success:
            msg = "ignoring run for successful runner"
            logger.info(msg)
            verbose.print(msg, level=2)
            self._run_state = "Skipped successful run"
            return False

        if run_args["force"]:
            msg = "force running"
            logger.info(msg)
            verbose.print(msg, level=2)
            self._run_state = "Forced"
            return True

        if run_args["skip"]:
            if self.is_finished:
                msg = "skipping already completed run"
                logger.info(msg)
                verbose.print(msg, level=2)
                self._run_state = "Skipped already completed run"
                return False

            if self.state >= "submit pending":
                msg = "skipping already submitted run"
                logger.info(msg)
                verbose.print(msg, level=2)
                self._run_state = "Skipped already submitted run"
                return False

            if self.state >= "staged":
                msg = "skipping stage for already staged run"
                logger.info(msg)
                verbose.print(msg, level=2)
                self._run_state = "Skipped staging already staged run"
                return False

        logger.info("running")
        verbose.print("running", level=2)
        self._run_state = "Run"
        return True

    @property
    def is_finished(self) -> Union[bool, None]:
        """
        Returns True if this runner has finished

        (None if the runner has not yet been submitted)
        """
        if not isinstance(self.state, RunnerState):
            raise RuntimeError("Runner state must be a RunnerState instance")
        logger.info("checking is_finished for %s. Current state: %s", self, self.state)
        if self.state < "submit pending":
            # run has not yet been submitted
            return None

        if self.state.finished:  # pylint: disable=E1101
            # run is finished
            return True

        logger.info("Not marked completed, returning False")
        return False

    @property
    def is_success(self) -> bool:
        """Returns True if this runner is considered to have succeeded"""
        return self.state.success  # pylint: disable=E1101

    @property
    def is_failed(self) -> Union[bool, None]:
        """
        Returns True if this runner is considered to have failed

        (None if incomplete)
        """
        if self.state < "completed":
            return False
        return not self.state.success  # pylint: disable=E1101

    def read_local_files(self, force: bool = False) -> None:
        """
        Reads all local files attached to this Runner.

        Fills out the resulting attributes (result, error, state, etc.)

        Returns:
            None
        """
        if not force and self.last_submitted == -1:
            return

        satisfied = False
        success = False
        if not force and self.state == "reset":
            logger.info("Runner is in a reset state, ignoring file read")
            return

        if os.path.isfile(self.resultfile.local):
            mtime = self.resultfile.local_mtime
            if force or mtime >= self.last_submitted:
                logger.info("reading recent results file")
                # need to change the serialiser if we have a txt output
                if not self.parent.is_python:
                    data = self.resultfile.content.strip()
                    if data == "":
                        data = None
                else:
                    data = self.parent.serialiser.load(self.resultfile.local)

                self.result = data

                satisfied = True
                success = True
            else:
                logger.info("local results file is outdated (file mtime)")
                logger.info(
                    "\tlast submitted vs file mtime: %s vs %s",
                    self.last_submitted,
                    mtime,
                )

        if os.path.isfile(self.errorfile.local):
            if force or os.path.getmtime(self.errorfile.local) > self.last_submitted:
                logger.info("reading recent error file")
                error_content = self.errorfile.content.strip().split("\n")[-1]

                if error_content != "":
                    self.error = error_content
                    satisfied = True
            else:
                logger.info("local error file is outdated")
                satisfied = False

        if satisfied and not self.state == "satisfied":
            self.state = "satisfied"
            self.state.success = success

    def verify_local_files(self) -> bool:
        """
        Check the existence of local files on disk

        Returns:
            (bool): True if everything is okay
        """
        if not self.state == "satisfied":
            return True

        return self.resultfile.exists_local and all(
            [f.exists_local for f in self.extra_files_recv]
        )

    @property
    def result(self):
        """Returns the result attribute, if available"""
        self.read_local_files()
        if self.is_failed:
            return RunnerFailedError(self.error)
        if hasattr(self, "_result"):
            try:
                if SERIALISED_STORAGE_KEY in self._result:
                    self._result = self.parent.serialiser.loads(self._result[1])
            except TypeError:
                pass
            except ValueError:
                pass
            return self._result
        return None

    @result.setter
    def result(self, result) -> None:
        """
        Creates and sets the result property, setting the state to "completed"

        Args:
            result:
                run result
        """
        self._result = result

    @property
    def error(self):
        """
        Error (If one exists)
        """
        self.read_local_files()
        if hasattr(self, "_error") and self._error is not None:
            return self._error.strip()
        return None

    @error.setter
    def error(self, error) -> None:
        """
        Creates and sets the error property

        Args:
            error:
                run error string
        """
        self._error = error

    @property
    def full_error(self) -> Union[str, None]:
        """
        Reads the error file, returning the full error

        Returns:
            str
        """
        if self.error is not None:
            return self.errorfile.content
        return None

    def clear_result(self, wipe: bool = True) -> None:
        """
        Clear the results properties and set the state to "reset", which blocks some
        functions until the runner is rerun

        Args:
            wipe:
                Additionally deletes the local files if True. Default True
        Returns:
            None
        """
        logger.info("clear_result called for runner %s", self)
        try:
            del self._result
            logger.info("deleted result attribute")
        except AttributeError:
            logger.info("no result attribute found")

        try:
            del self._error
            logger.info("deleted error attribute")
        except AttributeError:
            logger.info("no error attribute found")

        self._trackedfiles = {}
        self._extra_files_send = []
        self._extra_files_recv = []

        if wipe:
            if os.path.isfile(self.resultfile.local):
                os.remove(self.resultfile.local)
                logger.info("deleted result file")

            if os.path.isfile(self.errorfile.local):
                os.remove(self.errorfile.local)
                logger.info("deleted error file")

        self.state = "reset"

    def run(self, *args, **kwargs) -> None:
        """
        Run a single runner. See Dataset.run() for args.

        This function is inefficient and should not be used in a general workflow
        """
        logger.info("solo running runner %s", self)
        self.parent.run(uuids=[self.uuid], *args, **kwargs)


class RunnerFailedError:
    """
    Temporary "exception" to be passed in lieu of a missing result due to a failure.

    Args:
        message:
            error message
    """

    def __init__(self, message: str):
        self.message = message

    def __repr__(self):
        return f"RunnerFailedError('{self.message}')"

    def __hash__(self):
        return hash(self.message)

    def __eq__(self, other):
        return hash(self) == hash(other)
