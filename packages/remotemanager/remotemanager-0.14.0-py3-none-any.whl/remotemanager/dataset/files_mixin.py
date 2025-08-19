import os
from typing import List

from remotemanager.storage import TrackedFile


class ExtraFilesMixin:
    """
    Provides extra files related functionality to Runner and Dataset

    Requires either:
    - implementation of _extra_files dict
    - implementation of extra_files_send/recv properties

    Also requires a run_path property
    """

    run_path = NotImplemented
    local_dir = NotImplemented
    _extra_files = {}

    def _convert_files(self, files: list, recv: bool = False) -> List[TrackedFile]:
        """
        Attempts to convert any
        """
        output = []
        for file in files:
            if isinstance(file, TrackedFile):
                output.append(file)
                continue

            if isinstance(file, str):
                # handle a string type path/to/file.ext structure
                path, name = os.path.split(file)

                rpath = self.run_path
                lpath = os.getcwd()

                if recv:
                    lpath = os.path.join(lpath, self.local_dir)
                    rpath = os.path.join(rpath, path)
                else:
                    lpath = os.path.join(lpath, path)

                output.append(TrackedFile(lpath, rpath, name))
                continue

            if isinstance(file, dict):
                # handle a dict type {path/to/file.ext: path} structure
                lpath, name = os.path.split(list(file.keys())[0])
                rpath = list(file.values())[0]

                if recv:
                    lpath = self.local_dir if lpath == "" else lpath
                    rpath = os.path.join(self.run_path, rpath)
                else:
                    lpath = os.path.join(os.getcwd(), lpath)
                    rpath = os.path.join(self.run_path, rpath)

                output.append(TrackedFile(lpath, rpath, name))
                continue

            raise ValueError(f"Unhandled filetype {type(file)}")

        return output

    @property
    def extra_files(self) -> dict:
        """
        Returns the extra files set for this runner
        """
        return {"send": self.extra_files_send, "recv": self.extra_files_recv}

    @property
    def extra_files_send(self) -> list:
        """Methods for Dataset, should be overridden in Runner"""
        return self._convert_files(self._extra_files["send"])

    @property
    def extra_files_recv(self) -> list:
        """Methods for Dataset, should be overridden in Runner"""
        return self._convert_files(self._extra_files["recv"], recv=True)
