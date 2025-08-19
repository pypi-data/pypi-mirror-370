import json

from remotemanager.serialisation.serial import serial


class serialjson(serial):
    """
    subclass of serial, implementing json methods
    """

    def dumps(self, obj):
        obj = self.wrap_to_list(obj)
        return json.dumps(obj)

    def loads(self, string):
        loaded = json.loads(string)

        return self.wrap_to_list(loaded)

    @property
    def callstring(self):
        return "json"
