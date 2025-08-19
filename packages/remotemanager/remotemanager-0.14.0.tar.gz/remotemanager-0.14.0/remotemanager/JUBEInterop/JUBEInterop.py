import logging
import os.path
import re
import xml.etree.ElementTree as ET
from typing import Union

from remotemanager.connection.computer import Computer
from remotemanager.script.substitution import Substitution

logger = logging.getLogger(__name__)


class JUBETemplate(Computer):
    """Extends BaseComputer to provide compatibility with JUBE platforms"""

    def __init__(self, template: str, platform: str, **kwargs):
        if os.path.exists(template):
            with open(template) as o:
                template = o.read()

        self._platform_path = ""
        self.platform_path = platform

        super().__init__(template=template, **kwargs)

    @classmethod
    def from_repo(
        cls,
        path: str,
        branch: str = "develop",
        repo: str = "https://gitlab.com/max-centre/JUBE4MaX",
        platform_name: str = "platform.xml",
        template_name: str = "submit.job",
        local_dir: Union[None, str] = None,
        **kwargs,
    ):
        """
        Pulls a platform and template from a gitlab repository

        Files will be pulled from a combination of repo, branch and name

        e.g.
        from_repo(
            repo="https://gitlab.com/l_sim/remotemanager",
            branch="devel",
            name="tests/standard/foo"
        )

        This will look for the two links:
        https://gitlab.com/l_sim/remotemanager/-/raw/devel/tests/standard/foo/platform.xml
        https://gitlab.com/l_sim/remotemanager/-/raw/devel/tests/standard/foo/submit.job

        A general form of the links are:
        {repo}/-/raw/{branch}/{name}/{platform_name}
        {repo}/-/raw/{branch}/{name}/{template_name}
        """
        url = os.path.join("/", branch, path)
        url = f"{repo}/-/raw" + url

        if local_dir is None:
            local_dir = os.path.split(path.strip("/"))[-1]

            if local_dir == "" or local_dir is None:
                local_dir = os.getcwd()

        print(f"searching for {platform_name} & {template_name} at {url}")

        platform_path = os.path.join(local_dir, platform_name)
        cls.download_file(os.path.join(url, platform_name), platform_path)
        template_path = os.path.join(local_dir, template_name)
        cls.download_file(os.path.join(url, template_name), template_path)

        return cls(template=template_path, platform=platform_path, **kwargs)

    @property
    def platform_path(self) -> str:
        """Path to the platform file"""
        return self._platform_path

    @platform_path.setter
    def platform_path(self, path: str):
        if not os.path.exists(path):
            raise ValueError(f"Platform file {path} not found")

        self._platform_path = path

    def _extract_subs(self, link: bool = True) -> None:
        """
        Overrides BaseComputer sub extraction to instead parse from platform.xml
        """
        logger.debug("generating subs specified in platform.xml")
        tree = ET.parse(self.platform_path)
        root = tree.getroot()
        # platform.xml specifies "substitutesets" which translate what's
        # in the template to the actual parameter name. Apply these changes here.
        cache = {}
        for subsituteset in root.findall("substituteset"):
            for change in subsituteset.iter():
                if change.tag != "sub":
                    logger.debug("skip row %s", change)
                    continue
                target = change.attrib["source"]
                name = change.attrib["dest"].strip("$")

                cache[name] = {"target": target}

        for parameterset in root.findall("parameterset"):
            for parameter in parameterset.iter():
                if parameter.tag != "parameter":
                    continue

                name = parameter.attrib["name"]
                mode = parameter.attrib.get("mode", None)

                default = parameter.text

                if isinstance(default, str):
                    for tmp in cache:
                        if f"${tmp}" in default:
                            mode = "python"
                    default = default.strip()

                data = {"mode": mode, "default": default}
                if name in cache:
                    cache[name].update(data)
                else:
                    cache[name] = data
                # Subs require a target, create one if it does not exist
                target = cache[name].get("target", None)
                if target is None or target == "":
                    cache[name]["target"] = f"{name}"

        for name, args in cache.items():
            sub = Substitution(name=name, **args)
            self._subs[name] = sub

    def get_unevaluated_links(self, sub: Substitution) -> list:
        """
        Performs a regex search for unlinked JUBE $parameters within a value

        Args:
            sub: Substitution object to check
        """
        # only strings are valid targets
        if not isinstance(sub.value, str):
            return []
        # can lazily ignore any value not containing a $ char
        if "$" not in sub.value:
            return []
        # need to check for exact links using regex
        # this avoids bash $evaluations raising false positives
        cache = []
        for name in self.arguments:
            search = r"\$" + name + r"\b"
            if re.search(search, sub.value) is not None:
                cache.append(name)
        return cache

    def link_sub(self, sub: Substitution) -> None:
        """Performs recursive linking for target sub"""
        links = self.get_unevaluated_links(sub)

        # if the sub is fully linked, attempt an evaluation and return
        if len(links) == 0:
            logger.debug("%s has no children, evaluating and completing", sub.name)
            # set the temporary value, so these links do not permanently update values
            sub.temporary_value = attempt_eval(sub.value)
            return

        logger.debug("Performing recursive linking for sub %s", sub.name)
        # otherwise, we need to recursively continue
        value = sub.value  # store the value for treatment
        for name in links:
            logger.debug("\tevaluating child %s", name)
            obj = self._subs[name]  # get the actual associated object
            # if this sub child object has children of itself, recurse the call
            sub_links = self.get_unevaluated_links(obj)  # search for any children
            if len(sub_links) != 0:
                logger.debug("\tlinked to: %s, recursing...", sub_links)
                self.link_sub(obj)
            # recursion ensures that this child has a valid value, collect it
            update = str(obj.value)
            # search and replace an exact match
            search = r"\$" + name + r"\b"
            # search for the exact string, continuing if not found
            # this prevents $tasks matching $taskspernode, for example
            if re.search(search, value) is None:
                continue
            value = re.sub(search, update, value)
        # set the temporary value
        sub.temporary_value = attempt_eval(value)

    def _link_subs(self) -> None:
        """Ensures proper linking of JUBE substitutions"""
        for sub in self.sub_objects:
            self.link_sub(sub)


def attempt_eval(value: str):
    """Attempt to evaluate `value`"""
    try:
        return eval(value)
    except Exception:
        return value
