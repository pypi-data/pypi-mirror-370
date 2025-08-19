"""Module with some simple functions, e.g. for parsing for YAML into RMS"""

from __future__ import annotations

from yaml.loader import Loader

from fmu.config import _oyaml as yaml
from fmu.config._loader import ConstructorError, FmuLoader


def yaml_load(
    filename: str, safe: bool = True, tool: str | None = None, loader: str = "standard"
) -> dict | None:
    """Load as YAML file, return a dictionary of type OrderedDict which is the config.

    Returning an ordered dictionary is a main feature of this loader. It makes it much
    easier to compare the dictionaries returned. In addition, it allows for reading the
    input (extended) YAML format, if key ``allow_extended`` is True.

    Args:
        filename (str): Name of file (YAML formatted)
        safe (bool): If True (default), then use `safe_load` when allow_extended is
            set to False. Not applied if loader is "fmu".
        tool (str): Refers to a particular main section in the config.
            Default is None, which means 'all'.
        loader (str): If "fmu", the in-house FMU extended YAML loader that allows
            use of e.g. `!include` is applied; otherwise the default is "standard" YAML.

    Example::
        >>> import fmu.config.utilities as utils
        >>> cfg = utils.yaml_load('somefile.yml')

    """

    useloader = FmuLoader if loader.lower() == "fmu" else Loader

    with open(filename, "r", encoding="utf-8") as stream:
        try:
            if safe and loader.lower() != "fmu":
                cfg = yaml.safe_load(stream)
            else:
                cfg = yaml.load(stream, Loader=useloader)
        except ConstructorError as cerr:
            if "!include" in str(cerr):
                print(
                    "\n*** Consider setting loader='fmu' to read fmu.config "
                    "input style ***\n"
                )
            raise

    if tool is not None:
        try:
            newcfg = cfg[tool]
            cfg = newcfg
        except Exception as exc:  # pylint: disable=broad-except
            print(f"Cannot import: {exc}")
            return None

    return cfg


def compare_yaml_files(file1: str, file2: str) -> bool:
    """Compare two YAML files and return True if they are equal

    Args:
        file1 (str): Path to file1
        file2 (str): Path to file2
    """

    cfg1 = yaml_load(file1)
    cfg2 = yaml_load(file2)

    cfg1txt = yaml.dump(cfg1, default_flow_style=False, sort_keys=False)
    cfg2txt = yaml.dump(cfg2, default_flow_style=False, sort_keys=False)

    return cfg1txt == cfg2txt


def compare_text_files(file1: str, file2: str, comments: str = "//") -> bool:
    """Compare two text files, e.g. IPL and return True if they are equal

    Lines starting with comments indicator will be discarded

    Args:
        file1 (str): Path to file1
        file2 (str): Path to file2
        comments (str): How comment lines are indicated, e.g. "//" for IPL
    """

    text1 = ""
    text2 = ""

    with open(file1, "r", encoding="utf-8") as fil1:
        for line in fil1:
            if not line.startswith(comments):
                text1 += line

    with open(file2, "r", encoding="utf-8") as fil2:
        for line in fil2:
            if not line.startswith(comments):
                text2 += line

    return text1 == text2
