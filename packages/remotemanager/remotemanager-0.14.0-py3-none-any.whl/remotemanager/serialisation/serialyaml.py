import yaml

from remotemanager.serialisation.serial import serial


class serialyaml(serial):
    """
    subclass of serial, implementing yaml methods
    """

    def dumps(self, obj):
        obj = self.wrap_to_list(obj)
        return yaml.dump(obj)

    def loads(self, string):
        loaded = yaml.safe_load(string)

        return self.wrap_to_list(loaded)

    @property
    def callstring(self):
        return "yaml"

    @property
    def loadstring(self) -> str:
        return "safe_load"

    def dumpfunc(self) -> str:
        lines = [
            f"\ndef {self.dumpfunc_name}(obj, file):",
            f"\t{self.importstring}",
            "\tif isinstance(obj, (set, tuple)):",
            "\t\tobj = list(obj)",
            f'\tif not file.endswith("{self.extension}"):',
            f'\t\tfile = file + "{self.extension}"',
            f'\twith open(file, "{self.write_mode}") as o:',
            f"\t\t{self.callstring}.{self.dumpstring}(obj, o)",
        ]

        return "\n".join(lines)
