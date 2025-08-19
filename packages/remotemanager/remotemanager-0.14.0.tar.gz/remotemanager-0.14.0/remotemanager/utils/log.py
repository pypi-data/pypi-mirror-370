import logging
import os.path

from .format_iterable import format_iterable


class Handler:
    """
    Handler class for the global logging. Allows for limited user control
    """

    _levels = {
        "CRITICAL": logging.CRITICAL,
        "ERROR": logging.ERROR,
        "WARNING": logging.WARNING,
        "INFO": logging.INFO,
        "DEBUG": logging.DEBUG,
    }

    _filetype = ".log"
    _default_file = "remotemanager"
    _defaultpath = f"{_default_file}{_filetype}"

    def __init__(self):
        self._base = logging.getLogger("remotemanager")

        self._external = logging.getLogger("remotemanager.EXTERNAL")
        self._external.setLevel(10)  # external calls should always be logged

        self._path = Handler._defaultpath
        self._mode = "w"
        self._level = "WARNING"  # default to WARNING

        self._base.setLevel(Handler._levels[self._level])

        self._update_handlers()

    def refresh(self):
        """
        deletes and re-creates the log
        """
        self._delete_log(warn=False, force=True)
        self._update_handlers()

    @property
    def level(self):
        """
        Return the string format of the current logging level
        """
        return self._level

    @property
    def path(self):
        """
        Attribute determining the current log path
        """
        return self._path

    @property
    def write_mode(self):
        """
        returns the current write-mode of the logger
        """
        return self._mode

    @write_mode.setter
    def write_mode(self, mode):
        self._mode = mode
        self._update_handlers()

    @property
    def overwrite(self):
        return "w" in self._mode

    @overwrite.setter
    def overwrite(self, mode):
        if mode:
            self._mode = "w"
        else:
            self._mode = "a"
        self._update_handlers()

    @property
    def empty(self):
        return _check_log_empty(self._path)

    @level.setter
    def level(self, level):
        """
        Sets the logging level to `level`

        Arguments:
            level (str):
                Update the logging level. See the _levels attribute for
                valid options
        """
        level = level.upper()
        if level not in Handler._levels.keys():
            raise ValueError(f"log level must be one of {list(Handler._levels.keys())}")
        self._base.setLevel(Handler._levels[level])
        self._level = level

    @path.setter
    def path(self, newpath):
        """
        set logging path to newpath, deleting old log if it is empty

        Arguments:
            newpath (str):
                new path to log at
        """
        if newpath is None:
            newpath = ""
        path, file = os.path.split(newpath)
        if file == "":
            file = Handler._defaultpath
        if path == "":
            path = "."

        newpath = os.path.join(path, file)
        if Handler._filetype not in newpath:
            path, file = os.path.split(newpath)
            newpath = os.path.join(path, f"{file}{Handler._filetype}")

        if not os.path.isdir(path):
            os.makedirs(path)

        self._delete_log(warn=False)

        self._path = newpath
        self._update_handlers()

    def _delete_log(self, warn: bool = False, force: bool = False):
        """
        Deletes the current log

        Arguments:
            warn (bool):
                warn the user if the log cannot be deleted
            force (bool):
                always delete
        """

        def delete_log(path):
            try:
                os.remove(path)
            except (PermissionError, FileNotFoundError):
                pass

        log_empty = _check_log_empty(self._path)
        if log_empty:
            delete_log(self._path)
        elif force:
            oldpath = self._path
            delete_log(self._path)
            if not log_empty:
                print(f"Force deleted log at {oldpath}")

    def _update_handlers(self):
        """
        refresh handlers attached to the logger
        """
        for handler in self._base.handlers:
            self._base.removeHandler(handler)
        file_handler = logging.FileHandler(self._path, mode=self._mode, delay=True)
        formatter = logging.Formatter(
            "[%(asctime)s %(levelname)-9s]: %(message)s",
            datefmt="%Y%m%d %H%M%S",
        )

        file_handler.setFormatter(formatter)
        self._base.addHandler(file_handler)

    # TODO(lbeal) can this be made more pythonic?

    def debug(self, msg, *args, **kwargs):
        """Direct passthrough for `debug` logging method"""
        if not isinstance(msg, str):
            msg = format_iterable(msg)
        self._external.debug(msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        """Direct passthrough for `info` logging method"""
        if not isinstance(msg, str):
            msg = format_iterable(msg)
        self._external.info(msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        """Direct passthrough for `warning` logging method"""
        if not isinstance(msg, str):
            msg = format_iterable(msg)
        self._external.warning(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        """Direct passthrough for `error` logging method"""
        if not isinstance(msg, str):
            msg = format_iterable(msg)
        self._external.error(msg, *args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        """Direct passthrough for `critical` logging method"""
        if not isinstance(msg, str):
            msg = format_iterable(msg)
        self._external.critical(msg, *args, **kwargs)


def _check_log_empty(path):
    """
    check that the log at path `path` is clean
    """
    try:
        with open(path, "r") as o:
            log = o.read()
    except FileNotFoundError:
        return True
    if log.strip() == "":
        return True
    return False
