import functools
import logging
import operator
import os.path
import shutil
import time
import warnings
from typing import Union, Any

import yaml

from remotemanager.utils import get_version, ensure_filetype, recursive_dict_update
from remotemanager.utils.version import Version

logger = logging.getLogger(__name__)

# this list marks points where datasets cannot be carried through
barriers = {
    ("<=", "0.11.x"): ("==", "0.12.x"),  # engine difference
    ("==", "0.12.x"): (">=", "0.13.x"),  # engine difference
}


class Database:
    """
    Database file handler for use in the Dataset.

    .. warning::
        Interacting with this object directly could cause unstable behaviour.
        It is best to allow Dataset to handle the Database

    Args:
        file (str):
            filename to write to
    """

    _versionkey = "~database-version~"

    def __init__(self, file):
        file = ensure_filetype(file, "yaml")

        self._path = file
        self._storage = self._read()
        self._tree = None

    def _read(self) -> dict:
        """
        Wipes the tree cache and reads from the database file, creating it if
        it does not already exist.
        """
        self._tree = None  # wipe tree cache
        logger.info("reading %s", self._path)
        try:
            with open(self._path, "r") as o:
                data = yaml.safe_load(o)
        except FileNotFoundError:
            logger.warning("file not found, creating")
            data = {Database._versionkey: get_version()}
            self._write(data)
        check_version = True
        try:
            version = data.pop(Database._versionkey)
        except KeyError:
            check_version = False
            version = "0.0.0"

        logger.info("database file version: %s", version)

        oldversion = Version(version)
        currentversion = Version(get_version())
        if check_version and oldversion < currentversion:
            msg = (
                f"database file (version {version}) is less than "
                f"current remotemanager install version ({currentversion})"
            )
            warnings.warn(msg)
            logger.warning(msg)

            if not check_version_barriers(oldversion, currentversion, barriers):
                backup_file = self.backup()

                msg = (
                    f"{oldversion} cannot be upgraded to {currentversion}. "
                    f"\nThe dataset was backed up locally to {backup_file}, it is "
                    f"recommended that you downgrade before continuing. This can "
                    f"be done with:\n`pip install remotemanager=={oldversion}`"
                    "\nIf you haven't already, consider creating a virtual "
                    "environment.\nTo ignore this warning and continue, remove the "
                    f"`~database-version~: {oldversion}` line from the bottom of "
                    f"the database file."
                )

                logger.error(msg)
                raise RuntimeError(msg) from None
        # url storage is blocked as of 0.13.4, strip it
        uuid = self._get_first_key(data)
        if uuid is not None and data[uuid].get("_url", None) is not None:
            del data[uuid]["_url"]

        return data

    def _write(self, data: dict):
        """
        Clears the tree cache and writes to the file

        Args:
            data (dict):
                writes `data` to the database file
        """
        self._tree = None  # wipe tree cache

        data[Database._versionkey] = get_version()

        tmp_path = self._path + ".tmp"
        with open(tmp_path, "w+") as o:
            yaml.dump(data=data, stream=o, sort_keys=False)

        timeout = 5
        t0 = time.time()
        while not os.path.exists(tmp_path):
            # if the file isn't ready yet, the move will raise a strange error
            # waiting can help with this
            time.sleep(0.1)

            if time.time() > t0 + timeout:
                raise RuntimeError(
                    f"Database file {tmp_path} was never created "
                    f"after {timeout}s. This is usually caused by "
                    f"a naming clash, if you have concurrent Datasets, "
                    f"consider giving them differing names."
                )

        shutil.move(tmp_path, self._path)

    def read(self):
        """
        Read the database file
        """
        self._storage = self._read()

    def write(self):
        """
        Write the database to file
        """
        self._write(self._storage)

    def update(self, payload):
        """
        Update the database with payload (dict)

        Args:
            payload (dict):
                Dictionary to recursively update with. Usually called with the
                output of object.pack()
        """

        logger.info("updating stored info")

        self._storage = recursive_dict_update(self._storage, payload)
        self.write()

    def _get_first_key(self, d: dict) -> Any:
        if len(d) == 0:
            return None
        firstkey = next(iter(d))

        data_uuid = d.get(firstkey, {}).get("_uuid", None)
        if data_uuid != firstkey:
            return None

        return firstkey

    @property
    def stored_uuid(self) -> Union[str, None]:
        return self._get_first_key(self._storage)

    @property
    def path(self):
        """
        Path to current database file
        """
        return self._path

    @property
    def tree(self) -> list:
        """
        Returns a list of path-like strings for the stored database dict

        Returns (list):
            List of path-like strings
        """
        if self._tree is not None:
            return self._tree
        self._tree = self.climb(self._storage)
        return self._tree

    def climb(self, data: dict, branch: list = None) -> list:
        """
        "climb" a dictionary tree, returning a list of path-like strings for
        each element

        .. note::
            This method is intended for use within the `tree` property, and
            could cause unintended behaviour if called directly, though will
            allow you to produce a `tree` like list for any dictionary. Use
            with caution.

        Args:
            data (dict):
                dictionary to treat
            branch (list):
                current branch, used for recursion

        Returns (list):
            list of path-like strings
        """

        if branch is None:
            branch = []

        joinchar = "/"

        ret = []

        if len(data) == 0:
            ret.append(joinchar.join(branch))

        for key in data:
            tmp = []
            if isinstance(data[key], dict):
                tmp.append(key)
                ret += self.climb(data[key], branch + tmp)
            else:
                ret.append(joinchar.join(branch + [key]))
        return ret

    def find(self, key: str, greedy: bool = False) -> dict:
        """
        Find the first instance of key within the database tree

        Args:
            key:
                key (uuid) to look for
            greedy:
                returns the first value found if True. Faster, but does not respect
                the tree "layers"

        Returns:
            database tree below key
        """

        def get_minimum_path(p: str, k: str) -> list:
            """
            Returns the path segments of path p up to target k

            >>> get_minimum_path("a/b/c/d/", "b")
            >>> ["a", "b"]

            Args:
                p:
                    /path/containing/target/k/value
                k:
                    target within path p

            Returns:
                list of steps within path, leading to k
            """
            fullpath = p.split("/")
            return fullpath[: fullpath.index(k) + 1]

        target = None
        for path in self.tree:
            if key in path:
                tmp = get_minimum_path(path, key)
                if greedy:
                    target = tmp
                    break
                # we should prefer targets lower down the tree
                if target is None or len(tmp) < len(target):
                    target = tmp

        if target is None:
            return {}

        data = chain_get(self._storage, target)

        return data

    def backup(self, file=None) -> str:
        """
        Back up the database file to `file`, defaults to `{self.path}.bk`

        Args:
            file:
                backup file target location

        Returns:
            backup file path
        """
        if file is None:
            file = f"{self.path}.bk"

        shutil.copyfile(self.path, file)

        return file


def chain_get(d: dict, keys: list):
    """
    Get item from a nested dict using a list of keys

    Args:
        d (dict):
            nested dict to query
        keys (list):
            list of keys to use

    Returns:
        item from nested dict `d` at [list, of, keys]
    """
    return functools.reduce(operator.getitem, keys, d)


def check_version_barriers(old: Version, new: Version, barriers: dict) -> bool:
    """
    Takes two versions, and a dict of {old: new} that contain breaking changes

    Returns True if the two versions are compatible, False otherwise

    Args:
        old:
            old version
        new:
            new version
        barriers:
            dictionary of incompatible {old: new} parings.

            Uses the syntax of Version.match
    """
    dispatch = {
        "==": operator.eq,
        "!=": operator.ne,
        "<": operator.lt,
        ">": operator.gt,
        "<=": operator.le,
        ">=": operator.ge,
    }
    for a, b in barriers.items():
        a_op, a_ver = a
        b_op, b_ver = b

        if dispatch[a_op](old, a_ver) and dispatch[b_op](new, b_ver):
            return False

    return True
