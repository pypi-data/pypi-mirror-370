from remotemanager import Dataset


class SanzuWrapper:
    """
    Decorator class to allow you to

    Wrap a function with `@SanzuFunction` to store:

    >>> from remotemanager import URL
    >>> url = URL(...)
    >>> @SanzuFunction(url=url)
    >>> def func(val):
    >>>     return val
    >>> func(val=3)  # creates a Dataset and runs this function on `url`

    Call this function will transparently create a Dataset, execute
    the function remotely (synchronously), and return the result.

    The function should be called with explicitly named keyword arguments,
    but logic exists to attempt to match args to kwargs
    """

    def __init__(self, function, *args, **kwargs):
        self._ds = Dataset(function=function, *args, **kwargs)

    def __call__(self, *args, **kwargs):
        # to enable an *args call, iterate over the signature, attempting to inject
        # at each kwarg
        for i, arg in enumerate(args):
            # strip any type hinting. e.g. `x: int = 10` should become `x`
            argname = self.dataset.function.args[i].split()[0].strip(":")

            if argname in kwargs:
                raise ValueError(f"Got multiple values for arg {argname}")

            kwargs[argname] = arg

        runner = self._ds.append_run(kwargs, return_runner=True)
        runner.run()

        self._ds.wait(only_runner=runner)
        self._ds.fetch_results()

        return runner.result

    @property
    def dataset(self) -> Dataset:
        """
        Return the current Dataset used for this function

        Returns:
            (Dataset): associated Dataset
        """
        return self._ds


def SanzuFunction(*args, **kwargs):
    """
    Actual decorator wrapper for SanzuFunction

    In order to make a decorator callable, Python seems to require an actual function
    call that returns the class.

    Args:
        *args:
            args to pass through to the Dataset
        **kwargs:
            kwargs to pass through to the Dataset

    Returns:
        decorator
    """
    if len(args) > 0 and hasattr(args[0], "__call__"):
        # calling the decorator with no args places the function in the first arg
        return SanzuWrapper(args[0], **kwargs)

    # Otherwise, capture the function via standard decorator
    def decorate(function):
        return SanzuWrapper(function, *args, **kwargs)

    return decorate
