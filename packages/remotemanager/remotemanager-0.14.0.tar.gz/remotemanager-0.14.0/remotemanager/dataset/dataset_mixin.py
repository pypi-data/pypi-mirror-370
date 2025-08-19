class DetailMixin:
    """
    Mixin class to add get_*_log methods to a Dataset.
    """

    _append_log = {}
    runners = []

    def get_append_log(self) -> str:
        """Returns the log from the previous append session"""
        output = []
        for session, log in self._append_log.items():
            if len(self._append_log) <= 1:
                output = [f"{line}" for line in log]
                break

            output.append(f"{session}:")

            output += [f"\t{line}" for line in log]

        return "\n".join(output)

    def get_run_log(self) -> str:
        """
        Retrieves the log of the previous run attempt, providing more details
        """
        output = []
        for runner in self.runners:
            if runner.state > "transferred":
                output.append(f"{runner}: {runner._run_state}")

        return "\n".join(output)

    def print_run_log(self) -> None:
        """Prints the log of the previous run attempt"""
        print(self.get_run_log())
