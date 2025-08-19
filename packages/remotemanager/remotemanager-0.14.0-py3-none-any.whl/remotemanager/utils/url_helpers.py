"""
This module holds some commodity functions for building a template.
"""


def conda_activate(environment, path_to_conda="~/miniconda3/bin"):
    """
    Returns the string needed to activate conda

    >>> print(conda_activate("base"))
    >>> eval "$(~/miniconda3/bin/conda shell.bash hook)"
    >>> conda activate base

    Args:
        environment (str):
            the name of the conda environment
        path_to_conda (str):
            the location (bin directory) of the conda executable
    Returns:
        (str) the value to add to your template
    """
    ostr = f'eval "$({path_to_conda}/conda shell.bash hook)"\n'
    ostr += f"conda activate {environment}\n"
    return ostr
