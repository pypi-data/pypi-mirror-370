"""Small container class for tracking runner insertion"""

from remotemanager.storage import SendableMixin


class SummaryInstance(SendableMixin):
    """
    Tracks a Runner insert instance

    Args:
        runner_id:
            uuid of runner
        mode:
            append mode: force, skip, etc.
        quiet:
            True if silent append
    """

    __slots__ = ["runner_id", "mode", "quiet"]

    def __init__(self, runner_id: str, mode: str, quiet: bool):
        self.runner_id = runner_id
        self.mode = mode
        self.quiet = quiet

    def __repr__(self):
        return f"{self.runner_id}: {self.mode}"
