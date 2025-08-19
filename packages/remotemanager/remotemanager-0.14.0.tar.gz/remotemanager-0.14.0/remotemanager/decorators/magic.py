import ast
import warnings

from IPython.core.magic import Magics, magics_class, cell_magic, needs_local_scope

import logging
from remotemanager import Dataset

logger = logging.getLogger(__name__)


@magics_class
class RCell(Magics):
    """
    Magic function that allows running an ipython cell on a remote machine
    with minimal lines of code.
    """

    @cell_magic
    @needs_local_scope
    def sanzu(self, line: str, cell: str, local_ns: dict) -> None:
        """
        Execute a decorators cell using an implicit remote Dataset

        Args:
            line:
                magic line, includes arguments for cell and Dataset
            cell:
                Cell contents
            local_ns:
                dict containing current notebook runtime attributes
        """

        def clean_line(inpstr: str) -> str:
            inpstr = inpstr.split("#")[0].strip()  # remove comments
            inpstr = inpstr.strip(",")  # remove any trailing commas
            return inpstr

        # split cell into sanzu args, function args and the actual cell content
        sanzu = [clean_line(line)]  # prime sanzu storage with initial line
        sargs = []
        spull = []
        cell_actual = []

        cell = cell.strip()

        if len(cell) == 0:
            raise ValueError("Cell has no content!")
        for line in cell.split("\n"):
            if line.startswith("%%"):
                if "sanzu" in line:
                    sanzu.append(clean_line(line.split("sanzu ")[-1]))
                elif "sargs" in line:
                    sargs.append(clean_line(line.split("sargs ")[1]))
                elif "spull" in line:
                    spull.append(clean_line(line.split("spull ")[1]))
            else:
                cell_actual.append(line)

        # clean the args, in case the cell is initialised with an empty `sanzu`
        sanzu = [line for line in sanzu if line != ""]

        logger.info("sanzu: %s", sanzu)
        logger.info("sargs: %s", sargs)
        logger.info("spull: %s", spull)
        logger.info("cell: %s", cell_actual)

        args = self.extract_in_scope(",".join(sanzu), local_ns)
        fargs = self.extract_in_scope(",".join(sargs), local_ns)
        fstr = self.parse_line(cell_actual, list(fargs), spull)

        logger.info("generated function string %s", fstr)
        logger.info("Dataset args: %s", args)
        logger.info("Function args: %s", fargs)

        run_skip = args.pop("skip", True)
        # Build the runner and run
        try:
            del local_ns["magic_dataset"]
        except KeyError:
            pass
        ds = Dataset(function=fstr, skip=run_skip, **args)
        ds.append_run(args=fargs)
        ds.run(skip=run_skip)

        if ds.run_cmd is not None and ds.run_cmd.stderr:
            raise RuntimeError(f"error detected in magic run: {ds.run_cmd.stderr}")
        ds.wait(1)
        ds.fetch_results()

        local_ns["magic_dataset"] = ds

        if ds.runners[0].is_failed:
            warnings.warn(
                "Sanzu encountered an exception, see below, "
                "or access magic_dataset.errors"
            )
            raise RuntimeError(ds.runners[0].error)

        for name in spull:
            logger.debug("looking for pull target %s", name)
            local_ns[name] = ds.results[0].get(name, None)

        return ds.results[0]

    def parse_line(self, cell: list, fargs: list, pull: list):
        """
        Generate a callable function from the remaining cell content

        Args:
            pull:
                (list): list of object names to add to return instead of final line
            cell:
                (list): cell content
            fargs:
                (list): function arguments

        Returns:
            (str): formatted function string
        """
        cell = [line for line in cell if line != ""]

        fstr = ["def __sanzu_fn("]
        if len(fargs) > 0:
            fstr[0] += ", ".join(fargs) + ", "
        fstr[0] += "):"

        fstr += [f"\t{line}" for line in cell]

        fstr = "\n".join(fstr)

        if len(pull) == 0:
            # Validate the function string and add a return
            fstr = self.parse_tree(fstr, add_return=True)
        else:
            fstr += (
                "\n\t_return_object = {}"
                f"\n\tfor _name in ({pull}):"
                "\n\t\t_return_object[_name] = locals().get(_name, None)"
                "\n\treturn _return_object"
            )
            fstr = self.parse_tree(fstr, add_return=False)

        return fstr

    def extract_in_scope(self, line: str, local_ns: dict):
        """
        This will convert a line to a dictionary of arguments.

        It is separated out because we are going to have to selectively
        populate the local scope with `local_ns`.
        """

        def kwargs_to_dict(**kwargs):
            return kwargs

        for k, v in local_ns.items():
            if k in line:
                locals()[k] = v

        return eval("kwargs_to_dict(" + line + ")")

    def parse_tree(self, fstr, add_return: bool = True):
        """
        This routine adds a return to the end of our generated function.
        """
        # current code, try to use this first
        if hasattr(ast, "unparse"):
            tree = ast.parse(fstr)
            node = tree.body[0]
            if add_return and isinstance(node.body[-1], ast.Expr):
                node.body[-1] = ast.Return(value=node.body[-1].value)

            return ast.unparse(tree)

        lines = fstr.split("\n")
        if add_return:
            # need to add a return, but check for cases to avoid
            rline = lines[-1]

            # check to see if the last line is indented
            # in most cases this should not be returned
            indent = round((len(rline) - len(rline.lstrip())) / 4)

            # generate the spacing from the indent
            spacer = "\t" * (indent + 1)

            # however, cells ending in an if statement can still return, check for this
            # try:
            #     penultimate = lines[-2].strip()
            # except IndexError:
            #     penultimate = ""
            #
            # skip_indent = indent > 0 and not penultimate.startswith("if")

            # ast.unparse does NOT have this behaviour, so comment it out
            skip_indent = indent > 0

            # need to check for an assignment
            # assume this is the case if there is only alphanumeric chars before the
            # first "=" character.
            # that is to say, foo="bar" has the letters f, o, o before
            # whereas func(a=10) contains the `(` char, and should be returned

            # this is inefficient but it's for compatibility reasons
            search = rline.replace(" ", "").strip()
            skip_assignment = False
            for char in search:
                # variable_names should not trip this
                if char in ("_", "."):
                    continue
                # loop has reached an = without exiting, don't add a return
                if char == "=":
                    skip_assignment = True
                    break
                # loop has reached a non-alphanumeric char before =, break
                if not char.isalnum():
                    break

            if skip_indent:
                pass
            elif skip_assignment:
                pass
            else:
                rline = f"{spacer}return {rline.strip()}"

                lines[-1] = rline

        return "\n".join(lines)
