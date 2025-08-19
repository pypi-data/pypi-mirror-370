import jsonpickle

from remotemanager.serialisation.serial import serial


class serialjsonpickle(serial):
    """
    subclass of serial, implementing jsonpickle methods
    """

    def dumps(self, obj):
        return jsonpickle.encode(obj)

    def loads(self, string):
        return jsonpickle.decode(string)

    def dump(self, obj, file):
        with open(file, self.write_mode) as o:
            o.write(self.dumps(obj))

    def load(self, file):
        with open(file, self.read_mode) as o:
            return self.loads(o.read())

    def dumpfunc(self) -> str:
        lines = [
            f"\ndef {self.dumpfunc_name}(obj, file):",
            f"\t{self.importstring}",
            f'\tif not file.endswith("{self.extension}"):',
            f'\t\tfile = file + "{self.extension}"',
            f'\twith open(file, "{self.write_mode}") as o:',
            f"\t\to.write({self.callstring}.{self.dumpstring}(obj))",
        ]

        return "\n".join(lines)

    def loadfunc(self) -> str:
        lines = [
            f"\ndef {self.loadfunc_name}(file):",
            f"\t{self.importstring}",
            f'\tif not file.endswith("{self.extension}"):',
            f'\t\tfile = file + "{self.extension}"',
            f'\twith open(file, "{self.read_mode}") as o:',
            f"\t\treturn {self.callstring}.{self.loadstring}(o.read().strip())",
        ]  # noqa: E501

        return "\n".join(lines)

    @property
    def callstring(self) -> str:
        return "jsonpickle"

    @property
    def dumpstring(self) -> str:
        return "encode"

    @property
    def loadstring(self) -> str:
        return "decode"
