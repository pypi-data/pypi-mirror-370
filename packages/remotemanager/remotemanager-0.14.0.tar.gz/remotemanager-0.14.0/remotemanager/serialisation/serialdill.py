import dill

from remotemanager.serialisation.serial import serial


class serialdill(serial):
    """
    subclass of serial, implementing dill methods
    """

    def dumps(self, obj):
        return dill.dumps(obj)

    def loads(self, string):
        return dill.loads(string)

    @property
    def callstring(self):
        return "dill"

    @property
    def bytes(self):
        return True
