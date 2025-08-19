from typing import Optional


def ask_confirm(
    msg: str = "Confirm action?",
    default: Optional[bool] = False,
):
    options = "[Y]/n" if default else "y/[N]"

    inp = input(f"{msg} {options}")

    if inp == "":
        inp = "y" if default else "n"

    if inp.lower().strip() == "y":
        return True
    return False
