from typing import Optional
from remotemanager.storage.sendablemixin import SendableMixin


class RunnerState(SendableMixin):
    """
    State tracker for a runner
    """

    _states = {
        "invalid": -1,  # invalid state for comparisons
        "created": 0,  # runner exists
        "staged": 1,  # run files dumped to local dir
        "reset": 1,  # runner has been reset
        "dry run": 1,  # was staged and dry run
        "ready": 2,  # local files dumped, dataset files created. Ready to go
        "transferred": 2.5,  # files were sent to the remote
        "submit pending": 3,  # command was executed on the remote
        "started": 3,  # job reports that it started remotely
        "submitted": 4,  # confirmed running/queued by presence of an empty error file
        "completed": 5,  # valid result file exists
        "failed": 5,  # valid error file exists
        "satisfied": 6,  # files have been retrieved
        "copied": None,  # runner has been copied from another dataset
    }

    def __init__(self, state: str, value: Optional[int] = None):
        self._state = ""
        self._success = None

        if state == "copied":
            self._value = value or 0
        else:
            try:
                self._value = RunnerState._states[state]
            except KeyError as ex:
                raise ValueError(f"invalid state; {state}") from ex

        self.state = state

        if self.state == "completed":
            self._success = True
        elif self.state == "failed":
            self._success = False

        self.extra = None

    def __str__(self):
        output = [self.state]
        if self.value > 5 and self.success is not None:
            output.append("(failed)" if self.failed else "(success)")

        if self.extra is not None:
            output.append(f"({self.extra})")

        return " ".join(output)

    def __repr__(self):
        return f'RunnerState("{self.state}")'

    @property
    def finished(self):
        """Returns True if this state is considered "finished" """
        return self.value > 4

    @property
    def state(self) -> str:
        return self._state

    @state.setter
    def state(self, state: str):
        if state not in RunnerState._states:
            raise ValueError(f"invalid state; {state}")

        self._state = state

    @property
    def success(self):
        return self._success

    @success.setter
    def success(self, success):
        self._success = success

    @property
    def failed(self):
        if self < "completed":
            return False
        return not self.success

    @property
    def value(self) -> int:
        if hasattr(self, "_value"):
            return self._value
        return RunnerState._states.get(self.state, -1)

    def _prepare_compare(self, other):
        try:
            if not isinstance(other, RunnerState):
                other = RunnerState(other)
        except ValueError:
            return RunnerState("invalid")

        return other

    def __eq__(self, other):
        return self.state == self._prepare_compare(other).state

    def __lt__(self, other):
        return self.value < self._prepare_compare(other).value

    def __gt__(self, other):
        return self.value > self._prepare_compare(other).value

    def __le__(self, other):
        if self.value <= self._prepare_compare(other).value:
            return True
        return self == other

    def __ge__(self, other):
        if self.value >= self._prepare_compare(other).value:
            return True
        return self == other
