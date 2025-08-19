"""
The Dependency module handles the chaining of Datasets.

It provides overrides for any linked Dataset to propagate required calls.
"""

import logging
import os.path
import warnings
from typing import List, Optional, Tuple, Union, TYPE_CHECKING

from remotemanager.utils.verbosity import Verbosity
from remotemanager.storage.sendablemixin import SendableMixin

# TYPE_CHECKING is false at runtime, so does not cause a circular dependency
if TYPE_CHECKING:
    from remotemanager.dataset.dataset import Dataset

logger = logging.getLogger(__name__)


class Dependency(SendableMixin):
    """
    Main Dependency class.

    .. note::
        This class is internal and should not be interacted with directly.

    Handles the chaining of Datasets and stores the "network".
    It provides overrides for any linked Dataset to propagate required calls.
    """

    _do_not_package = ["_network", "_ds_list_cache"]

    _ds_list_cache: List["Dataset"] = []

    def __init__(self):
        logger.info("new Dependency created")

        self._network: List[Tuple[Dataset, Dataset]] = []
        self._parents: List[str] = []
        self._children: List[str] = []

    def add_edge(self, primary: "Dataset", secondary: "Dataset") -> None:
        """
        Adds an "edge" to the dependency network.

        This edge represents a parent-child link.

        Args:
            primary (Dataset): Parent Dataset object.
            secondary (Dataset): Child Dataset object.
        """
        self._ds_list_cache = []  # invalidate cache
        pair = (primary, secondary)
        if pair not in self._network:
            logger.info("adding new edge %s", pair)

            self._parents.append(primary.short_uuid)
            self._children.append(secondary.short_uuid)

            self._network.append(pair)

    @property
    def network(self) -> List[Tuple["Dataset", "Dataset"]]:
        """Returns the internal dependency network.

        This is a list of tuples representing the parent-child relationship.

        Returns:
            List(Tuple(Dataset, Dataset)
        """
        return self._network

    def get_children(self, dataset: "Dataset") -> List["Dataset"]:
        """
        Collect and return all children for a given Dataset object.

        Args:
            dataset (Dataset): Dataset to query.

        Returns:
            List: List of children of the given Dataset.
        """
        tmp = [
            self.network[i][1]  # 1 is the parent
            for i in range(len(self._parents))
            if self._parents[i] == dataset.short_uuid
        ]
        return tmp

    def get_parents(self, dataset: "Dataset") -> List["Dataset"]:
        """
        Collect and return all parents for a given Dataset object.

        Args:
            dataset (Dataset): Dataset to query.

        Returns:
            List: List of parents of the given Dataset.
        """
        tmp = [
            self.network[i][0]  # 0 is the child
            for i in range(len(self._children))
            if self._children[i] == dataset.short_uuid
        ]
        return tmp

    @property
    def ds_list(self) -> List["Dataset"]:
        """
        Returns a flattened list of all datasets within the network.

        Returns:
            _type_: _description_
        """
        if len(getattr(self, "_ds_list_cache", [])) > 0:
            return self._ds_list_cache

        datasets = []
        for pair in self.network:
            for ds in pair:
                if ds not in datasets:
                    datasets.append(ds)

        self._ds_list_cache = datasets

        return datasets

    @property
    def runners(self) -> List:
        """
        Returns a list of all runners within the network.
        """
        runners = []
        for pair in self.network:
            for ds in pair:
                for runner in ds.runners:
                    runners.append(runner)
        return runners

    def update_db(self):
        """
        Ensure all datasets within a dependency update their databases together
        """
        for ds in self.ds_list:
            ds.update_db(dependency_call=True)

    def remove_run(self, ident: Union[int, str, dict]) -> bool:
        """
        Chains the Dataset.remove_run function to all Datasets within the dependency.

        Args:
            ident (Union[int, str, dict]): Runner identifier.

        Returns:
            bool: True if all runners were removed successfully, False otherwise.
        """
        out = []
        for ds in self.ds_list:
            out.append(ds.remove_run(ident=ident, dependency_call=True))

        return all(out)

    def clear_runs(self) -> None:
        """
        Remove all Runners from the Datasets.
        """
        for ds in self.ds_list:
            ds.wipe_runs(dependency_call=True, confirm=False)

    def clear_results(self, wipe: bool) -> None:
        """
        Ensure all datasets within a dependency clear their results together

        Args:
            wipe (bool): Additionally delete the local resultfiles if True
        """
        for ds in self.ds_list:
            ds.reset_runs(wipe, dependency_call=True, confirm=False)

    def wipe_local(self, files_only: bool = False) -> None:
        """
        Clears out the local directory.

        Args:
            files_only (bool, optional): Attepts to only delete files.
            Defaults to False, deleting the directory.
        """
        for ds in self.ds_list:
            ds.wipe_local(files_only=files_only, dependency_call=True, confirm=False)

    def wipe_remote(self, files_only: bool = False) -> None:
        """
        Clears out the remote directory.

        Args:
            files_only (bool, optional): Attepts to only delete files.
            Defaults to False, deleting the directory.
        """
        for ds in self.ds_list:
            ds.wipe_remote(files_only=files_only, dependency_call=True, confirm=False)

    def hard_reset(self, files_only: bool = False) -> None:
        """
        Hard resets all datasets. This will wipe local and remote directories.

        Args:
            files_only (bool, optional): Attepts to only delete files.
            Defaults to False, deleting the directory.
        """
        for ds in self.ds_list:
            ds.hard_reset(files_only=files_only, dependency_call=True, confirm=False)

    def append_run(
        self, caller, chain_run_args, run_args, force, lazy, *args, **kwargs
    ):
        """
        Appends runs with the same args to all datasets

        Args:
            lazy:
            caller:
                (Dataset): The dataset which defers to the dependency
            chain_run_args (bool):
                for dependency runs, will not propagate run_args to other datasets in
                the chain if False (defaults True)
            run_args (dict):
                runner arguments
            force (bool):
                force append if True
            lazy (bool):
                do not update the database after this append (ensure you call
                ``update_db()`` after appends are complete, or use the
                ``lazy_append()`` contex)
            *args:
                append_run args
            **kwargs:
                append_run keyword args

        Returns:
            None
        """
        logger.info("appending run from %s", caller)

        datasets = self.ds_list
        logger.info("There are %s datasets in the chain)", len(datasets))

        if chain_run_args:
            logger.info("chain_args is True, propagating")
            kwargs.update(run_args)

        for ds in datasets:
            if ds == caller:
                caller_args = {k: v for k, v in kwargs.items()}
                caller_args.update(run_args)
                ds.append_run(
                    dependency_call=True, force=force, lazy=lazy, *args, **caller_args
                )
            else:
                ds.append_run(
                    dependency_call=True, force=force, lazy=lazy, *args, **kwargs
                )

            if not lazy:
                ds.database.update(ds.pack())

    def finish_append(self) -> None:
        """
        Propagates the completion of runner append to all datasets in the chain.
        """
        for ds in self.ds_list:
            ds.finish_append(dependency_call=True, print_summary=False)

    @staticmethod
    def get_runner_remote_filepath(runner, workdir: str, filetype: str) -> str:
        """
        Generates the relative remote path from workdir to a runner file
        The file is specified by filetype
        """
        file = None
        if filetype == "resultfile":
            file = runner.resultfile
        elif filetype == "runfile":
            file = runner.runfile

        if file is None:
            raise ValueError(f"unknown filetype {filetype}")

        file = file.relative_remote_path(workdir)
        if not os.path.isabs(file):
            file = os.path.join("$sourcedir", file)
        return file

    def stage(
        self,
        # uuids: List[str] = None,
        force: bool = False,
        extra: str = "",
        force_ignores_success: bool = False,
        verbose: Optional[Verbosity] = None,
        **run_args,
    ) -> bool:
        """
        Handles the Dataset Staging for a dependency situation.
        Args:
            dry_run (bool):
                create files, but do not run
            extra: str
                extra text to add to runner jobscripts
            force_ignores_success (bool):
                If True, `force` will submit only failed runners
            verbose:
                Sets local verbose level
        """
        logger.info("dependency internal stage call")

        if verbose is not None:
            verbose = Verbosity(verbose)
        else:
            verbose = self.ds_list[0].verbose

        for ds in self.ds_list:
            if ds.remote_dir != self.ds_list[0].remote_dir:
                msg = (
                    "Chained datasets cannot have mismatched remote_dirs!: "
                    f"{ds.remote_dir} & {self.ds_list[0].remote_dir}\n"
                    "You can use separate run_dirs to provide runtime isolation"
                )
                logger.critical(msg)
                raise RuntimeError(msg)
            if len(ds.runners) != len(self.ds_list[0].runners):
                msg = (
                    "Datasets do not have matching numbers of runners!: "
                    f"{len(ds.runners)} vs {len(self.ds_list[0].runners)}"
                )
                logger.critical(msg)
                raise RuntimeError(msg)

        verbose.print("Staging Dependency", level=1)

        run_args["force"] = force

        if all(r.state == "staged" for r in self.runners) and not force:
            verbose.print("All runners already staged, skipping", level=1)
            return False

        # grab all global extra jobscript content from the datasets
        global_extra = []
        for ds in self.ds_list:
            if ds._global_run_extra is not None:
                global_extra.append(ds._global_run_extra)

        bash_cache = []
        staged = 0  # prevent unbound variable
        for i, ds in enumerate(self.ds_list):
            staged = 0
            verbose.print(f"  [{i}] {ds}", level=1, end="... ")
            verbose.print("", level=2)  # newline for higher verbose levels

            ds_run_dir = ds.run_dir or ds.remote_dir
            if ds.submitter not in bash_cache:
                bash_cache.append(ds.submitter)

            parent_datasets = self.get_parents(ds)
            child_datasets = self.get_children(ds)
            if len(parent_datasets) > 1:
                warnings.warn(
                    "Multiple parents detected. "
                    "Variable passing in this instance is unstable!"
                )

            for i, runner in enumerate(ds.runners):
                # section checks that the parent result exists, exiting if not
                parent_check = []
                for parent in parent_datasets:
                    parent_resultfile = self.get_runner_remote_filepath(
                        parent.runners[i], ds_run_dir, "resultfile"
                    )
                    parent_runfile = self.get_runner_remote_filepath(
                        parent.runners[i], ds_run_dir, "runfile"
                    )

                    parent_check.append(
                        f'export parent_result="{parent_resultfile}"\n'
                        f"if [ ! -f $parent_result ]; then\n"
                        f'\techo "Parent result not found at '
                        f'$parent_result" >> "{runner.errorfile.name}" && exit 1;\n'
                        f"fi\n"
                    )

                    # TODO this is broken with multiple parents
                    lstr = (
                        f"runfile = os.path.expandvars('{parent_runfile}')\n"
                        f"resultfile = os.path.expandvars('{parent_resultfile}')\n"
                        f"if os.path.getmtime(runfile) > "
                        f"os.path.getmtime(resultfile):\n"
                        f'\traise RuntimeError("outdated '
                        f'result file for parent")\n'
                        f"repo.loaded = repo.{parent.serialiser.loadfunc_name}("
                        f"resultfile)"
                    )
                    runner._dependency_info["parent_import"] = lstr

                parent_check = "".join(parent_check)
                # section deals with submitting children
                child_submit = []
                for child in child_datasets:
                    child_runner = child.runners[i]
                    runline = child_runner.generate_runline(child=True)
                    child_submit.append(runline)

                ready = runner.stage(
                    python=ds.url.python,
                    repo=self.ds_list[0].repofile.name,
                    global_extra="\n".join(global_extra),
                    extra=extra,
                    parent_check=parent_check,
                    child_submit=child_submit,
                    force_ignores_success=force_ignores_success,
                    verbose=verbose,
                    **run_args,
                )

                ds.sanitise_run_arg_paths(runner.derived_run_args)

                if ready:
                    staged += 1
            verbose.print(f"Done, {staged}/{len(ds.runners)} Runners staged", level=1)

        if staged == 0:
            logger.info("no runners completed the run assessment, skipping")
            verbose.print("No Runners staged", level=1)
            return False

        # deal with master file directly
        master_content = [
            f"source {self.ds_list[0].bash_repo.name}\n### runs ###",
            "export sourcedir=$PWD",
        ]

        for runner in self.ds_list[0].runners:
            runline = runner.generate_runline(child=False)
            master_content.append(runline)

        self.ds_list[0].master_script.write(master_content)

        # generate python repository
        self.ds_list[0]._write_to_repo(skip_function=True)
        self.ds_list[0].repofile.append("\n### Functions ###")
        for ds in self.ds_list:
            content = [f"# function for {ds}:\n", ds.function.source]
            self.ds_list[0].repofile.append("".join(content))

        # generate bash repository
        self.ds_list[0]._write_to_bash_repo(bash_cache)

        verbose.print("Done", level=1)
        return True

    def transfer(
        self,
        # uuids: List[str] = None,
        force: bool = False,
        extra: str = "",
        force_ignores_success: bool = False,
        verbose: Optional[Verbosity] = None,
        **run_args,
    ) -> bool:
        """
        Transfer the files to the remote
        """
        logger.info("dependency internal run call")

        if verbose is not None:
            verbose = Verbosity(verbose)
        else:
            verbose = self.ds_list[0].verbose

        staged = self.stage(
            dependency_call=True,
            extra=extra,
            force=force,
            force_ignores_success=force_ignores_success,
            verbose=verbose,
            **run_args,
        )
        # taken from Dataset.transfer
        uuid_cache = []
        for runner in self.runners:
            if not runner.derived_run_args.get("force", False):
                if runner.state < "staged":
                    continue
                if runner.state >= "transferred":
                    continue

            self.ds_list[0].transport.queue_for_push(runner.jobscript)
            if self.ds_list[0].function is not None:
                self.ds_list[0].transport.queue_for_push(runner.runfile)

            logger.info("queuing extra files to send")
            for file in runner.extra_files_send:
                self.ds_list[0].transport.queue_for_push(file)

            uuid_cache.append(runner.uuid)

        if len(uuid_cache) == 0 and not staged:
            verbose.print("No Transfer required", level=1)
            return False

        if len(uuid_cache) == 1:
            verbose.print("Transferring for 1 Runner", level=1)
        else:
            verbose.print(f"Transferring for {len(uuid_cache)} Runners", level=1)

        self.ds_list[0].prepare_for_transfer()

        # queue
        self.ds_list[0].transport.queue_for_push(self.ds_list[0].master_script)
        self.ds_list[0].transport.queue_for_push(self.ds_list[0].repofile)
        self.ds_list[0].transport.queue_for_push(self.ds_list[0].bash_repo)

        self.ds_list[0].transport.transfer()
        for ds in self.ds_list:
            ds.set_runner_states("transferred")
        return True

    def run(
        self,
        force: bool = False,
        dry_run: bool = False,
        verbose: Union[None, int, bool, Verbosity] = None,
        # uuids: list = None,
        extra: str = "",
        force_ignores_success: bool = False,
        **run_args,
    ) -> bool:
        """
        Handles the Dataset Run for a dependency situation.

        Args:
            dry_run (bool):
                create files, but do not run
            extra: str
                extra text to add to runner jobscripts
            force_ignores_success (bool):
                If True, `force` will submit only failed runners
            verbose:
                Sets local verbose level
        """
        logger.info("dependency internal run call")

        if verbose is not None:
            verbose = Verbosity(verbose)
        else:
            verbose = self.ds_list[0].verbose

        run_args["force"] = force

        cmd = (
            f"cd {self.ds_list[0].remote_dir} && "
            f"{self.ds_list[0].url.shell} {self.ds_list[0].master_script.name}"
        )
        asynchronous = False
        if not dry_run:
            self.transfer(
                extra=extra,
                force_ignores_success=force_ignores_success,
                verbose=verbose,
                **run_args,
            )

            uuid_cache = []
            asynchronous = False
            # check first here, since that's what's actually being executed
            for runner in self.ds_list[0].runners:
                if not runner.derived_run_args.get("force", False):
                    if runner.state < "transferred":
                        continue
                    if runner.state >= "submit pending":
                        continue

                if runner.derived_run_args["asynchronous"]:
                    asynchronous = True

                uuid_cache.append(runner.uuid)

            if len(uuid_cache) == 0:
                verbose.print("Remotely executing 1 Runner", level=1)
                return False

            if len(uuid_cache) == 1:
                verbose.print("Remotely executing 1 Runner", level=1)
            else:
                verbose.print(f"Remotely executing {len(uuid_cache)} Runners", level=1)

            for ds in self.ds_list:
                ds.set_runner_states(state="submit pending")
        else:
            for ds in self.ds_list:
                ds.set_runner_states(state="dry run")

            msg = f"launch command: {cmd}"
            logger.info(msg)
            verbose.print(msg, 1)

        self.ds_list[0]._run_cmd = self.ds_list[0].url.cmd(
            cmd, asynchronous=asynchronous, dry_run=dry_run, verbose=verbose
        )
        return True

    def update_runners(self):
        """
        Manifest only needs to be collected once, then all the runners
        can be updated by that call
        """
        runners = []
        for ds in self.ds_list:
            runners += ds.runners

        self.ds_list[0].update_runners(runners=runners, dependency_call=True)

    def check_failure(self):
        """
        Raises a RuntimeError if an error is detected in any of the runners

        Relies on the runner.is_failed property
        """
        for ds in self.ds_list:
            for runner in ds.runners:
                if runner.is_failed:
                    ds.fetch_results()
                    raise RuntimeError(
                        f"Detected a failure in dataset {ds}:\n{ds.errors}"
                    )
