from remotemanager.storage.sendablemixin import SendableMixin
from remotemanager.utils import ensure_filetype


class serial(SendableMixin):
    """
    Baseclass for holding serialisation methods. Subclass this class when
    implementing new serialisation methods
    """

    def __init__(self):
        pass

    def dump(self, obj, file: str) -> None:
        """
        Dump object `obj` to file `file`

        Base behaviour tries to write the output of ``self.dumps`` to a file.
        Overwrite for custom behaviour

        Args:
            obj:
                object to be dumped
            file (str):
                filepath to dump to

        Returns:
            None
        """
        file = ensure_filetype(file, self.extension)

        with open(file, self.write_mode) as o:
            o.write(self.dumps(obj))

    def load(self, file: str):
        """
        Load previously dumped data from file ``file``

        Base behaviour tries to load file via ``self.dumps``
        Overwrite for custom behaviour

        Args:
            file (str):
                filepath to load

        Returns:
            Stored object
        """

        file = ensure_filetype(file, self.extension)

        with open(file, self.read_mode) as o:
            data = self.loads(o.read())

        return data

    def dumps(self, obj):
        raise NotImplementedError

    def loads(self, string):
        raise NotImplementedError

    @staticmethod
    def wrap_to_list(obj):
        """
        Preserves the python tying of a set or tuple by inserting an identifier
        at the start.

        If passed with a list starting with this identifier, it will unwrap the typing,
        restoring the type.
        """
        proxy = {set: "~SERIALISEDSET~", tuple: "~SERIALISEDTUPLE~"}

        if isinstance(obj, tuple):
            return [proxy[tuple]] + list(obj)

        elif isinstance(obj, set):
            return [proxy[set]] + list(obj)

        elif isinstance(obj, list) and obj[0] in proxy.values():
            storedtype = obj[0]
            data = obj[1:]

            oldtype = list(proxy.keys())[list(proxy.values()).index(storedtype)]

            return oldtype(data)

        return obj

    @property
    def extension(self) -> str:
        """
        Returns (str):
            intended file extension
        """
        return f".{self.callstring}"

    @property
    def importstring(self) -> str:
        """
        Returns (str):
            Module name to import.
            See subclasses for examples
        """
        return f"import {self.callstring}"

    @property
    def callstring(self) -> str:
        """
        Returns (str):
            Intended string for calling this module's dump.
            See subclasses for examples
        """
        raise NotImplementedError

    @property
    def bytes(self) -> bool:
        """
        Set to True if serialiser requires open(..., 'wb')
        """
        return False

    @property
    def write_mode(self):
        """
        Mode for writing to dumped files.
        """
        if self.bytes:
            return "wb+"
        return "w+"

    @property
    def read_mode(self):
        """
        Mode for reading dumped files.
        """
        if self.bytes:
            return "rb"
        return "r"

    @property
    def loadstring(self) -> str:
        return "load"

    @property
    def dumpstring(self) -> str:
        return "dump"

    @property
    def loadfunc_name(self):
        return "remote_load"

    @property
    def dumpfunc_name(self):
        return "remote_dump"

    def dumpfunc(self) -> str:
        lines = [
            f"\ndef {self.dumpfunc_name}(obj, file):",
            f"\t{self.importstring}",
            f'\tif not file.endswith("{self.extension}"):',
            f'\t\tfile = file + "{self.extension}"',
            f'\twith open(file, "{self.write_mode}") as o:',
            f"\t\t{self.callstring}.{self.dumpstring}(obj, o)",
        ]

        return "\n".join(lines)

    def loadfunc(self) -> str:
        lines = [
            f"\ndef {self.loadfunc_name}(file):",
            f"\t{self.importstring}",
            f'\tif not file.endswith("{self.extension}"):',
            f'\t\tfile = file + "{self.extension}"',
            f'\twith open(file, "{self.read_mode}") as o:',
            f"\t\treturn {self.callstring}.{self.loadstring}(o)",
        ]

        return "\n".join(lines)
