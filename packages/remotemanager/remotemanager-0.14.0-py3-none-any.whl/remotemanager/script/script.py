"""
This module holds the Script class, which handles the generation and parameterization
of scripts.
"""

from __future__ import annotations

import copy
import logging
import os.path
import re
from os import PathLike
from typing import Optional, Union, Any, List

from remotemanager.script.utils import _get_expandables, try_value
from remotemanager.script.delayvar import DelayVar
from remotemanager.script.get_pragma import get_pragma
from remotemanager.script.substitution import (
    EMPTY_TREATMENT_STYLES,
    INVALID_EMPTY_TREATMENT,
    Substitution,
)
from remotemanager.storage.sendablemixin import SendableMixin
from remotemanager.utils.count_fstring_variables import count_fstring_variables
from remotemanager.utils.tokenizer import Tokenizer
from remotemanager.utils.uuid import UUIDMixin

logger = logging.getLogger(__name__)

DELETION_FLAG_LINE = "~marked_for_line_deletion~"
DELETION_FLAG_LOCAL = "~marked_for_local_deletion~"
PLACEHOLDER_PATTERN = r"#(\w+)(?::([^#]+))?#"
REPLACEMENT_PATTERN = r"#{name}(?::[^#]+)?#"
ESCAPE_SEQ_PATTERN = r"(?<!!\\)\\(?!\\)"


class EscapeStub:
    """
    Stub class for avoiding regex's internal escape sequence handling

    If the `repl` argument of `re.sub` is a callable, escape sequences will not be
    processed, allowing us to handle them at a later stage.

    This is important for allowing templates to escape the `:` character
    """

    __slots__ = ["content"]

    def __init__(self, content: Any):
        self.content: str = str(content)

    def __call__(self, *args, **kwargs) -> str:
        return self.content

    def __str__(self) -> str:
        return self.content

    def __repr__(self) -> str:
        return self.content


class Script(SendableMixin, UUIDMixin):
    """
    Class for a generic, parameterisable script.

    Args:
        template (str):
            Base script to use. Accepts #parameters#
    """

    __slots__ = [
        "_template",
        "_subs",
        "_empty_treatment",
        "_init_args",
        "_header_only",
        "_link_session_recursion_block",
        "_link_session_token_cache",
    ]

    def __init__(
        self,
        template: Union[str, None] = None,
        template_path: Union[str, None] = None,
        empty_treatment: str | None = None,
        header_only: bool = False,
        **init_args,
    ):
        if template is None:
            if template_path is None:
                raise ValueError("Either template or template_path must be provided")
            with open(file=template_path, mode="r", encoding="utf-8") as o:
                template = o.read()

        self._template: str = self._parse_input(template)

        self._subs: dict[str, Substitution] = {}
        self._init_args = init_args

        self._header_only = header_only

        self._empty_treatment = None
        self.empty_treatment = empty_treatment
        # cache for recursion blocking
        self._link_session_recursion_block = []
        self._link_session_token_cache = []

        self._extract_subs()
        self.generate_uuid(self.template)

    def __getattr__(self, item):
        if item != "_subs" and hasattr(self, "_subs") and item in self._subs:
            val = self._subs[item]
            logger.debug("returning alt __getattribute__ %s=%s", item, val)
            return val
        return object.__getattribute__(self, item)

    def __setattr__(self, key, value):
        try:
            self._subs[key].value = value
            if key in self._init_args:
                del self._init_args[key]
        except (AttributeError, KeyError):
            object.__setattr__(self, key, value)

    def __hash__(self) -> int:
        """
        We should return the hash of the template, not the output

        This means that two "different" scripts will be treated as equivalent,
        but if we're relying on the uuid of a script to generate a Dataset UUID for a
        non-function run, then we are physically unable to generate the UUID at init
        """
        return hash(self.template)

    def _parse_input(self, inp: Union[str, PathLike]) -> str:
        """
        Takes an input and checks if it is a file

        Args:
            inp (str, PathLike):
                input to check. May either be a "raw" template,
                or a path to a file containing one, for example
        """
        if os.path.isfile(inp) or isinstance(inp, PathLike):
            print(f"reading template from file: {inp}")
            with open(inp, mode="r", encoding="utf8") as o:
                data = o.read()
            return data
        return inp

    def _extract_subs(self) -> None:
        """
        Extract all substitution objects from the template
        """
        # wipe cache
        self._subs = {}
        # extract all replacement targets
        symbols = re.findall(PLACEHOLDER_PATTERN, self.template)  # noqa: W605
        logger.info("Found substitution targets within script:%s", symbols)

        for match in symbols:
            logger.debug("processing match %s", match)
            name = match[0].lower()
            kwargs = match[1]

            if name in self._subs:
                if kwargs is not None and kwargs != "":
                    raise ValueError(
                        f"Got more kwargs for already registered argument "
                        f"{name}: {kwargs}"
                    )
                logger.debug("\talready processed, continuing")
                continue
            if kwargs == "":
                tmp = Substitution.from_string(name)
            else:
                tmp = Substitution.from_string(":".join(match))
            existing = getattr(self, tmp.name, None)
            if existing is not None and not isinstance(existing, Substitution):
                raise ValueError(
                    f'Variable "{tmp.name}" already exists. This could '
                    f"cause unintended behaviour, please choose another "
                    f"name"
                )

            self._subs[tmp.name] = tmp

    def _link_subs(self) -> None:
        self._link_session_recursion_block = []
        self._link_session_token_cache = []
        for sub in self.sub_objects:
            sub._linked = False
        for sub in self.sub_objects:
            if sub._linked:
                continue
            self._process_sub_links(sub.name)

    def _convert_link_to_value_access(self, link: str, sub: Substitution) -> str:
        """
        Takes a {linked} string, and converts it to one that can be evaluated
        """
        # create "tokens" from the link. For example, `foo*bar` will contain tokens
        # `foo`, `*` and `bar`. From this we need to extract the names `foo`, `bar`
        # if they exist as substitutions
        tkn = Tokenizer(link)
        # for each of these names, check if it exists as a Substitution. If it
        # does, we need to access the `value` property to ensure that dynamic links
        # are respected.
        for name in tkn.names:
            if name in self._link_session_token_cache:
                tkn.exchange_name(name, f"{name}.value")

            elif name in self._subs:
                if name in self._link_session_recursion_block:
                    continue

                if not self._subs[name]._linked:
                    self._link_session_recursion_block.append(name)
                    self._process_sub_links(name)

                tkn.exchange_name(name, f"{name}.value")
                self._link_session_token_cache.append(name)
                # If the Sub currently being treated has been set as non-optional,
                # any children that are a part of its value must also not be optional
                if not sub._optional:
                    self._subs[name].optional = False

        return tkn.source

    def _process_sub_links(self, sub_name: str) -> None:
        sub = self._subs[sub_name]
        # take the example of a substitution;
        # #val:default={foo*bar}#
        # _get_expandables collects a list of all {expandable} f-string like items
        # within the target. So {foo*bar}, in this instance
        links = _get_expandables(sub.target)

        if len(links) == 0:
            sub._linked = True
            return  # no need to continue if there are no links

        if sub.static:
            return

        # now, evaluate the links and assign them to the correct locations
        # target_kwargs is a dict of {key:val} where objects can look like {value}
        for key, val in sub.target_kwargs.items():
            # we may have {multiple} {links} {within a value}
            # collect those with the same method as with the overall args
            inner_links = _get_expandables(val)
            if len(inner_links) == 0:
                continue

            # call eval with a limited scope to reduce security risks
            scope = self._subs.copy()
            # scope.update({"__builtins__": {}})  # type: ignore

            # We have two methods of evaluating the value:
            # "raw", where we strip the outer brackets and apply eval directly
            # This evaluation method preserves types, so is preferable
            # However it is ONLY possible if the entire string is evaluable,
            # otherwise it will clobber {int}_{int} style variables
            #
            # Secondly, we have "str" type, where we evaluate as an f-string
            # This has the downside that it will clobber iterables to stringtype
            #
            # Set up the evaluation functions here:
            def raw_eval(val):
                val = self._convert_link_to_value_access(val, sub)

                if val.startswith("{") and val.endswith("}"):
                    val = val[1:-1]

                try:
                    return eval(val, scope)
                except (TypeError, ValueError):
                    return None

            def str_eval(val):
                try:
                    # string type values may take the form {a}_{b}_{c}
                    # we need to evaluate each inner variable in turn and replace
                    # note that we cannot use f-string as a shortcut, since we may have
                    # escape sequences, which will cause a failure
                    targets = _get_expandables(val)
                    for target in targets:
                        val = val.replace(f"{{{target}}}", str(raw_eval(target)))

                    out = DelayVar(val, skip_format=True)

                    return out

                except (SyntaxError, ValueError):
                    return raw_eval(val)

            # Now, process the values
            if val.startswith("{") and val.endswith("}"):
                # This is the check for wholly evaluable strings. Exluding
                # {value}_string style variables
                # Now, we must count the variables to avoid {int}_{int} style
                try:
                    nvar = count_fstring_variables(val)
                    if nvar <= 1:
                        evaluated = raw_eval(val)
                    else:
                        evaluated = str_eval(val)
                except (SyntaxError, ValueError):
                    # if f-string testing fails, then we have to use "raw" eval
                    evaluated = raw_eval(val)
            else:
                evaluated = str_eval(val)

            # back propagate the new linked value
            setattr(sub, key, evaluated)

        sub._linked = True

    @property
    def template(self) -> str:
        """Returns the template"""
        return self._template

    @template.setter
    def template(self, template: str) -> None:
        """
        Update the template with a new one and regenerate the substitutions

        Args:
            template (str):
                new template to use
        """
        self._template = template
        self._extract_subs()
        self.generate_uuid(self.template)

    @property
    def subs(self) -> List[str]:
        """Returns a list of all substitution names"""
        return list(self._subs.keys())

    @property
    def sub_objects(self) -> List[Substitution]:
        """Returns a list of all substitution objects"""
        return list(self._subs.values())

    @property
    def args(self) -> list:
        """Alias for self.subs"""
        return self.subs

    @property
    def arguments(self):
        """Alias for self.subs"""
        return self.subs

    @property
    def required(self) -> List[str]:
        """
        Returns a list of all required values

        Returns:
            List[str]: a list of all required values
        """
        required = []  # store the required values
        for sub in self.sub_objects:
            # if this sub is not optional, add it
            if not sub.optional:
                required.append(sub.name)
                required += sub.requires  # also add any dependencies

        return list(set(required))

    @property
    def missing(self) -> List[str]:
        """
        Returns a list of all missing required values

        Returns:
            List[str]: a list of all missing required values
        """
        missing = []

        for name in self.required:
            sub = self._subs[name]
            if sub.value is None:
                missing.append(name)

        return missing

    @property
    def valid(self) -> bool:
        """
        Returns True if the script is currently "valid"

        Validation is defined as having no missing required values and all
        required values being present.

        ..note::
            Note that this property only considers values that have been flagged as
            required in the template. This essentially makes it up to the user to
            enable this functionality in their templates.

        Returns:
            bool: True if the script is currently "valid"
        """
        return len(self.missing) == 0

    @property
    def empty_treatment(self) -> Union[str, None]:
        """
        Returns the currently set global behaviour for empty treatment.
        """
        return self._empty_treatment

    @empty_treatment.setter
    def empty_treatment(self, style: Union[str, None]):
        if style is not None and style not in EMPTY_TREATMENT_STYLES:
            raise ValueError(INVALID_EMPTY_TREATMENT.format(style=style))
        self._empty_treatment = style

    @property
    def header_only(self) -> bool:
        """
        Toplevel flag to dictate whether we should return the whole script or
        just the header
        """
        if not hasattr(self, "_header_only"):
            self._header_only = False
        return self._header_only

    @header_only.setter
    def header_only(self, header_only: bool) -> None:
        self._header_only = header_only

    def script(
        self,
        empty_treatment: Union[str, None] = None,
        header_only: Optional[bool] = None,
        **run_args: Any,
    ) -> str:
        """
        Generate the script

        Args:
            empty_treatment (str, None):
                Overrides any local setting of ``empty_treatment`` if not None
            header_only (bool):
                If True, attempt to only return the resource request header

        Returns:
            str: the formatted script
        """
        # check that empty_treatment is valid
        if empty_treatment is None:
            empty_treatment = self.empty_treatment
        if (
            empty_treatment is not None
            and empty_treatment not in EMPTY_TREATMENT_STYLES
        ):
            raise ValueError(INVALID_EMPTY_TREATMENT.format(style=empty_treatment))
        # update header_only
        if header_only is None:
            header_only = self.header_only
        # update the values
        for k, v in self._init_args.items():
            if k in self.subs:
                self._subs[k].temporary_value = v
        for k, v in run_args.items():
            if k in self.subs:
                self._subs[k].temporary_value = v

        # generation section
        self._link_subs()  # ensure values are properly linked

        # check validity, this must be done after linking as it may update requirements
        if not self.valid:
            raise ValueError(f"Missing values for parameters:\n{self.missing}")

        script = copy.deepcopy(self._template)  # do not clobber the internal template

        header_template = ""
        if header_only:
            header_template = self.extract_header()

        for sub in self.sub_objects:
            # get the value in string form
            value = str(sub.value)

            if sub.hidden or value is None or value == "None":
                # no value, triage this argument
                treatment = empty_treatment or sub.empty_treatment
                if treatment == "ignore":
                    continue
                elif treatment == "line":
                    value = DELETION_FLAG_LINE
                elif treatment == "local":
                    value = DELETION_FLAG_LOCAL
            # replace any instance of #name#, capturing args.
            # avoid any whitespace to not get tripped up by comments
            search = re.compile(
                REPLACEMENT_PATTERN.format(name=sub.name), re.IGNORECASE
            )
            if header_only:
                header_template = re.sub(search, EscapeStub(value), header_template)
            else:
                script = re.sub(search, EscapeStub(value), script)
        # replacements complete, generate the output while handling missing values
        if header_only:
            script = header_template
        output = []
        for n, line in enumerate(script.split("\n")):
            if DELETION_FLAG_LINE in line:
                continue

            output.append(line.replace(DELETION_FLAG_LOCAL, ""))

        for sub in self.sub_objects:
            sub.temporary_value = None

        return re.sub(
            ESCAPE_SEQ_PATTERN, "", "\n".join(output)
        )  # remove any escape sequences

    def extract_header(self) -> str:
        """
        Attempt to extract the resource header from the template.

        Here, we assume that the resource header is marked by some #PRAGMA,
        which is either the top of the file or follows a shebang

        We must do this on the template, instead of the output, to make it more
        deterministic. Though we must not modify the template, since that could brick
        the script generation. Best we can do is generate the "header only" template,
        then also perform the same replacements on that before returning that.
        """
        # store the #PRAGMA alongside the number of occurrences and last line
        lastline = 0
        nonpragma_count = 0  # counter for allowing spaces between pragmas
        for n, line in enumerate(self.template.split("\n")):
            pragma = get_pragma(line)

            if pragma == "":
                nonpragma_count += 1

                if nonpragma_count > 2:
                    break

            if pragma != "":
                nonpragma_count = 0
                lastline = n

        return "\n".join(self.template.split("\n")[: lastline + 1])

    def pack(self, values: bool = True, file: str | None = None) -> str:  # type: ignore
        """
        Store the Script

        Args:
            values (bool):
                includes any set values if True
            file (str):
                path to save to, returns the content if None

        Returns:
            str:
                File path if file is not None, else the storage content
        """
        output = copy.deepcopy(self.template)
        if values:
            for sub in self.sub_objects:
                search = re.compile(
                    REPLACEMENT_PATTERN.format(name=sub.name), re.IGNORECASE
                )
                try:
                    value = sub.value

                    if value != try_value(sub.default):
                        value_insert = f"#{sub.target}:value={value}#"
                        output = re.sub(
                            search, EscapeStub(value_insert), output, count=1
                        )
                except ValueError:
                    pass

        if file is not None:
            with open(file, "w+", encoding="utf8") as o:
                o.write(output)
            return os.path.abspath(file)

        return output

    @classmethod
    def unpack(cls, input: str):  # type: ignore
        if os.path.exists(input):
            with open(input, "r", encoding="utf8") as o:
                input = o.read()

        return cls(template=input)
