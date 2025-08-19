"""Module for parsing global configuration for FMU.

This module will normally be ran from the `fmuconfig` script,
which is the front-end script for the user.
"""

from __future__ import annotations

import datetime
import errno
import getpass
import json
import os
import re
import socket
import sys
from collections import Counter, OrderedDict
from copy import deepcopy
from os.path import join as ojoin
from typing import TYPE_CHECKING

from fmu.config import _configparserfmu_ipl, _oyaml as yaml, etc
from fmu.config._loader import ConstructorError, FmuLoader

try:
    from fmu.config.version import __version__
except ImportError:
    __version__ = "0.0.0"

if TYPE_CHECKING:
    from typing import Any, Literal

xfmu = etc.Interaction()
logger = xfmu.functionlogger(__name__)


class ConfigParserFMU:
    """Class for parsing global config files for FMU."""

    def __init__(self) -> None:
        self._config: dict[str, Any] = {}
        self._yamlfile: str | None = None
        self._runsilent = True
        logger.debug("Ran __init__")

    @property
    def config(self) -> dict[str, Any]:
        """Get the current config as a Python dictionary (read only)."""
        return self._config

    @property
    def yamlfile(self) -> str | None:
        """The name of the input master YAML formatted file (read only)."""
        return self._yamlfile

    def parse(self, yfile: str, smart_braces: bool = True) -> None:
        """Parsing the YAML file (reading it)."""

        with open(yfile, encoding="utf-8") as stream:
            try:
                self._config = yaml.load(stream, Loader=FmuLoader)
            except ConstructorError as errmsg:
                xfmu.error(str(errmsg))
                raise SystemExit from errmsg

        self._yamlfile = yfile

        if smart_braces:
            res = self._fill_empty_braces(deepcopy(self._config), "X")
            assert isinstance(res, dict)
            self._config = res

        self._cleanify_doubleunderscores()
        self._validate_unique_tmplkeys()

    def show(self, style: Literal["yaml", "yml", "json", "jason"] = "yaml") -> None:
        """Show (print) the current configuration to STDOUT.

        Args:
            style: Choose between 'yaml' (default), or 'json'"""

        xfmu.echo("Output of configuration:")
        if style in ("yaml", "yml"):
            yaml.dump(
                self.config,
                default_flow_style=False,
                sort_keys=False,
                stream=sys.stdout,
            )
        elif style in ("json", "jason"):
            stream = json.dumps(self.config, indent=4, default=str)
            print(stream)

    def to_table(
        self,
        rootname: str = "myconfig",
        destination: str | None = None,
        template: str | None = None,
        entry: str | None = None,
        createfolders: bool = False,
        sep: str = ",",
    ) -> None:
        # pylint: disable=too-many-arguments
        # pylint: disable=too-many-branches

        """Export a particular entry in config as text table files;
        one with true values and one with templated variables.

        Args:
            rootname: Root file name without extension. An extension
                .txt will be added for destination, and .txt.tmpl
                for template output.
            destination: The directory path for the destination
                file. If None, then no output will be given
            template: The directory path for the templated
                file. If None, then no templated output will be given.
            entry (str): Using one of the specified key/entry sections in the
                master config that holds a table, e.g. 'global.FWL'.
            createfolders (bool): If True then folders will be created if they
                do not exist (default is False).
            sep (str): Table separator, e.g. ' ', default is ','

        Raises:
            ValueError: If both destination and template output is None,
                or folder does not exist in advance, if createfolder=False,
                or entry is not spesified.

        Example:

            >>> config.to_table('fwl', destination='../',
                                entry='global.FWL')
        """

        if not destination and not template:
            raise ValueError(
                "Both destination and template are None."
                "At least one of them has to be set!."
            )

        if entry is None:
            raise ValueError('The entry is None; need a value, e.g. "global.FWL"')

        if createfolders:
            self._force_create_folders([destination, template])
        else:
            self._check_folders([destination, template])

        keys = entry.split(".")

        if len(keys) == 1:
            cfg = self.config[keys[0]]
        elif len(keys) == 2:
            cfg = self.config[keys[0]][keys[1]]
        elif len(keys) == 3:
            cfg = self.config[keys[0]][keys[1]][keys[2]]
        elif len(keys) == 4:
            cfg = self.config[keys[0]][keys[1]][keys[2]][keys[3]]
        else:
            raise ValueError("Entry with more that 4 sublevels, not supported")

        if destination:
            with open(
                ojoin(destination, rootname + ".txt"), "w", encoding="utf-8"
            ) as dest:
                for row in cfg:
                    for col in row:
                        stream = self._get_required_form(str(col), template=False)
                        print(str(stream) + sep, file=dest, end="")
                    print("", file=dest)
        if template:
            with open(
                ojoin(template, rootname + ".txt.tmpl"), "w", encoding="utf-8"
            ) as tmpl:
                for row in cfg:
                    for col in row:
                        stream = self._get_required_form(str(col), template=True)
                        print(str(stream) + sep, file=tmpl, end="")
                    print("", file=tmpl)

    def to_yaml(
        self,
        rootname: str = "myconfig",
        destination: str | None = None,
        template: str | None = None,
        tool: str | None = None,
        createfolders: bool = False,
    ) -> None:
        # pylint: disable=too-many-arguments

        """Export the config as YAML files; one with true values and
        one with templated variables.

        Args:
            rootname: Root file name without extension. An extension
                .yml will be added for destination, and .yml.tmpl
                for template output.
            destination: The directory path for the destination
                file. If None, then no output will be given
            template: The directory path for the templated
                file. If None, then no templated output will be given.
            tool (str): Using one of the specified tool sections in the
                master config, e.g. 'rms'. Default is None which means all.
            createfolders (bool): If True then folders will be created if they
                do not exist (default is False).

        Raises:
            ValueError: If both destination and template output is None,
                or folder does not exist in advance, if createfolder=False.

        Example:

            >>> config.to_yaml('global_variables', destination='../')
        """
        logger.info("To YAML")
        if not destination and not template:
            raise ValueError(
                "Both destination and template are None."
                "At least one of them has to be set!."
            )

        if createfolders:
            self._force_create_folders([destination, template])
        else:
            self._check_folders([destination, template])

        # remove dtype, value(s) from RMS/IPL freeform entries
        newcfg = self._strip_rmsdtype()

        if tool is not None:
            mystream = yaml.dump(
                newcfg[tool],
                default_flow_style=False,
                sort_keys=False,
                allow_unicode=True,
            )
        else:
            mystream = yaml.dump(
                newcfg, default_flow_style=False, sort_keys=False, allow_unicode=True
            )

        mystream = "".join(self._get_sysinfo()) + mystream

        mystream = re.sub(r"\s+~", "~", mystream)
        mystream = re.sub(r"~\s+", "~", mystream)

        cfg1 = self._get_dest_form(mystream)
        cfg2 = self._get_tmpl_form(mystream)
        assert isinstance(cfg1, str)  # Above can also return list
        assert isinstance(cfg2, str)

        if destination:
            out = os.path.join(destination, rootname + ".yml")
            with open(out, "w", encoding="utf-8") as stream:
                stream.write(cfg1)

        if template:
            out = os.path.join(template, rootname + ".yml.tmpl")
            with open(out, "w", encoding="utf-8") as stream:
                stream.write(cfg2)

    def to_json(
        self,
        rootname: str,
        destination: str | None = None,
        template: str | None = None,
        createfolders: bool = False,
        tool: str | None = None,
    ) -> None:
        """Export the config as JSON files; one with true values and
        one with templated variables.

        Args:
            rootname: Root file name without extension. An extension
                .json will be added for destination, and .json.tmpl
                for template output.
            destination: The directory path for the destination
                file. If None, then no output will be given
            template: The directory path for the templated
                file. If None, then no output will be given
            tool (str): Using one of the specified tool sections in the
                master config, e.g. 'rms'. Default is None which means all.
            createfolders: If True then folders will be created if they
                do not exist.

        Raises:
            ValueError: If both destination and template output is None,
                or folder does not exist in advance, if createfolder=False.

        Example:

            >>> config.to_json('global_variables', destination='../')
        """

        if not destination and not template:
            raise ValueError(
                "Both destionation and template are None."
                "At least one of them has to be set!."
            )

        if createfolders:
            self._force_create_folders([destination, template])
        else:
            self._check_folders([destination, template])

        # remove dtype, value(s) from RMS/IPL freeform entries
        newcfg = self._strip_rmsdtype()

        mycfg = newcfg[tool] if tool is not None else newcfg

        mystream = json.dumps(mycfg, indent=4, default=str, ensure_ascii=False)

        mystream = re.sub(r"\s+~", "~", mystream)
        mystream = re.sub(r"~\s+", "~", mystream)

        if destination:
            cfg1 = self._get_dest_form(mystream)
            assert isinstance(cfg1, str)  # Above can also return list
            out = os.path.join(destination, rootname + ".json")
            with open(out, "w", encoding="utf-8") as stream:
                stream.write(cfg1)

        if template:
            cfg2 = self._get_tmpl_form(mystream)
            assert isinstance(cfg2, str)  # Above can also return list
            out = os.path.join(template, rootname + ".json.tmpl")
            with open(out, "w", encoding="utf-8") as stream:
                stream.write(cfg2)

    def to_ipl(
        self,
        rootname: str = "global_variables",
        destination: str | None = None,
        template: str | None = None,
        createfolders: bool = False,
        tool: str = "rms",
    ) -> None:
        """Export the config as a global variables IPL and/or template.

        Args:
            rootname (str): Root file name without extension. An extension
                `.ipl` will be added for destination, and `.ipl.tmpl`
                for template output.
            destination (str): The output file destination (folder).
            template (str): The folder for the templated version of the
                IPL (for ERT).
            createfolders: If True then folders will be created if they
                do not exist.
            tool (str): Which section in the master to use (default is 'rms').

        """

        if createfolders:
            self._force_create_folders([destination, template])
        else:
            self._check_folders([destination, template])

        # keep most code in separate file ( a bit lengthy)
        _configparserfmu_ipl.to_ipl(
            self,
            rootname=rootname,
            destination=destination,
            template=template,
            tool=tool,
        )

    def to_eclipse(self) -> None:
        """Export the config templates and actuals under `eclipse`"""

        cfg = self.config

        for deck in cfg["eclipse"]:
            logger.info("Deck is %s", deck)
            edeck = cfg["eclipse"][deck]

            content = edeck["content"]
            content_dest = self._get_dest_form(content)
            content_tmpl = self._get_tmpl_form(content)
            assert isinstance(content_dest, str)  # Above can return list
            assert isinstance(content_tmpl, str)

            with open(edeck["destfile"], "w", encoding="utf-8") as dest:
                dest.write(content_dest)

            with open(edeck["tmplfile"], "w", encoding="utf-8") as tmpl:
                tmpl.write(content_tmpl)

    # =========================================================================
    # Private methods
    # =========================================================================

    def _cleanify_doubleunderscores(self) -> None:
        """Remove keys with double underscore in level 2, and
        move data up one level.

        This is done in order to allow anonymous include, e.g.::

           rms:
              __tmp1: !include facies.yml

        The input in facies.yaml will then be relocated to the key 'rms',
        up one level.

        .. versionchanged:: 1.0.1 secure same order of __xxx keys

        """

        # pylint: disable=too-many-nested-blocks
        newcfg = deepcopy(self._config)

        for key, val in self._config.items():
            if isinstance(val, dict):
                subkeyorder = []
                _tmps = {}

                for subkey, subval in val.items():
                    if subkey.startswith("__"):
                        if isinstance(subval, dict):
                            for subsubkey, subsubval in subval.items():
                                _tmps[subsubkey] = deepcopy(subsubval)
                                subkeyorder.append(subsubkey)
                        del newcfg[key][subkey]
                    else:
                        subkeyorder.append(subkey)
                        _tmps[subkey] = subval

                # order
                ordered = OrderedDict()
                for keyw in subkeyorder:
                    ordered[keyw] = _tmps[keyw]
                newcfg[key] = ordered

        self._config = newcfg

    def _validate_unique_tmplkeys(self) -> None:
        """Collect all <...> and check that they are unique and uppercase.

        Note that duplicate <xxx> may be OK, and a print should only be issued
        if required, as information.

        """

        mystream = yaml.dump(self._config, default_flow_style=False, sort_keys=False)
        tlist = []
        tmpl = re.findall(r"<\w+>", mystream)
        for item in tmpl:
            tlist.append(item)

        for item in tlist:
            wasitem = item
            item = item.rstrip(">")
            item = item.lstrip("<")
            if any(char.islower() for char in item):
                xfmu.error(
                    "Your template key contains lowercase letter: {}".format(wasitem)
                )

        if len(tlist) != len(set(tlist)) and not self._runsilent:
            xfmu.echo("Note, there are duplicates in <...> keywords")
            counter = Counter(tlist)
            for item, cnt in counter.items():
                if cnt > 1:
                    xfmu.echo("{0:30s} occurs {1:3d} times".format(item, cnt))

    def _fill_empty_braces(
        self, stream: str | list | dict, key: str
    ) -> str | list | dict[str, Any]:
        """If an empty variable is given, this shall be replaced with
        key name.

        For example::

              FLW1: 2000~<>

        shall be::

              FLW1: 2000~<FWL1>

        This function uses recursion

        Args:
            stream: a dict or string or...
            key: To use as <KEY>

        """
        if isinstance(stream, str):
            if key in ("value", "values") and "<>" in stream:
                xfmu.warn(
                    'Empty template "<>" is not supported in "value" or '
                    '"values" fields: {}'.format(stream)
                )
            else:
                return stream.replace("<>", "<" + str(key) + ">")
        elif isinstance(stream, list):
            return [
                self._fill_empty_braces(item, str(key) + "_" + str(num))
                for num, item in enumerate(stream)
            ]
        elif isinstance(stream, dict):
            return OrderedDict(
                [
                    (xkey, self._fill_empty_braces(item, xkey))
                    for xkey, item in stream.items()
                ]
            )
        return stream

    @staticmethod
    def _get_sysinfo(commentmarker: str = "#") -> list[str]:
        """Return a text string that serves as info for the outpyt styles
        that support comments."""

        host = socket.gethostname()
        user = getpass.getuser()
        now = str(datetime.datetime.now())
        ver = __version__
        cmt = commentmarker

        return [
            "{} Autogenerated from global configuration.\n".format(cmt),
            "{} DO NOT EDIT THIS FILE MANUALLY!\n".format(cmt),
            "{} Machine {} by user {}, at {}, using fmu.config ver. {}\n".format(
                cmt, host, user, now, ver
            ),
        ]

    @staticmethod
    def _force_create_folders(folderlist: list[str | None]) -> None:
        for folder in folderlist:
            if folder is None:
                continue
            try:
                os.makedirs(folder)
            except OSError as errmsg:
                if errmsg.errno != errno.EEXIST:
                    raise

    @staticmethod
    def _check_folders(folderlist: list[str | None]) -> None:
        for folder in folderlist:
            if folder is None:
                continue

            if not os.path.exists(folder):
                raise ValueError(
                    "Folder {} does not exist. It must either "
                    "exist in advance, or the createfolders key"
                    "must be True.".format(folder)
                )

    def _strip_rmsdtype(self) -> dict[str, Any]:
        """Returns a copy of the _config dictionary so that the (e.g.)
        FREEFORM['dtype'] and FREEFORM['value'] = x or FREEFORM['values'] = x
        becomes simplified to FREEFORM = x
        """

        newcfg = deepcopy(self._config)

        if "rms" in self._config:
            cfgrms = self._config["rms"]
        else:
            return newcfg

        for key, val in cfgrms.items():
            logger.debug(key, val)
            if isinstance(val, dict):
                logger.debug(val.keys())
                if "dtype" and "value" in val:
                    newcfg["rms"][key] = deepcopy(val["value"])
                elif "dtype" and "values" in val:
                    newcfg["rms"][key] = deepcopy(val["values"])
                elif "dtype" in val:
                    raise RuntimeError(
                        'Wrong input YAML?. It seems that "{}" has '
                        '"dtype" but no "value" or "values" ({})'.format(
                            key, val.keys()
                        )
                    )

        return newcfg

    @staticmethod
    def _get_required_form(
        stream: str | list, template: bool = False, ipl: bool = False
    ) -> list | str | None:
        """Given a variable on form 1.0 ~ <SOME>, return the required form.

        For single values, it should be flexible how it looks like, e.g.::

            19.0~<SOME>
            19.0 ~ <SOME>

        If ipl is True and template is false, it should return::

            19.0  // <SOME>

        If ipl is True and template is True, it should return::

            <SOME>  // 19.0

        Args:
            stream (:obj:`str` or :obj:`list` of :obj:`str`): Input string
                or list of strings to break up
            template (bool): If template mode
            ipl (bool): If IPL mode
        """

        if "~" not in stream:
            return stream

        result = None

        if isinstance(stream, list):
            pass
        elif isinstance(stream, str):
            if "~" in stream:
                value, tvalue = stream.split("~")
                value = value.strip()
                tvalue = tvalue.strip()

                if ipl:
                    if template:
                        result = tvalue + "  // " + value
                    else:
                        result = value + "  // " + tvalue
                else:
                    result = tvalue if template else value

        else:
            raise ValueError("Input for templateconversion neither string or list")

        return result

    @staticmethod
    def _get_tmpl_form(stream: list | str) -> list | str:
        """Get template form (<...> if present, not numbers)."""

        pattern = "\\-*[\\-a-zA-Z0-9._/]+~"

        if isinstance(stream, list):
            logger.info("STREAM is a list object")
            result = []
            for item in stream:
                moditem = re.sub(pattern, "", item)
                moditem = re.sub('"', "", moditem)
                moditem = " " + moditem.strip()
                result.append(moditem)
            return result

        if isinstance(stream, str):
            logger.info("STREAM is a str object - get tmpl form")
            res = re.sub(pattern, "", stream)
            res = re.sub('"', "", res)
            return res.strip() + "\n"

        raise ValueError("Input for templateconversion neither string or list")

    @staticmethod
    def _get_dest_form(stream: list | str) -> list | str:
        """Get destination form (numbers, not <...>)"""

        logger.info("TRY DEST %s", stream)
        pattern = "~.*<.+?>"

        if isinstance(stream, list):
            logger.info("STREAM is a list object")
            result = []
            for item in stream:
                moditem = re.sub(pattern, "", item)
                moditem = " " + moditem.strip()
                result.append(moditem)
            return result

        if isinstance(stream, str):
            logger.info("STREAM is a str object - get dest form")
            res = re.sub(pattern, "", stream)
            return res.strip() + "\n"

        raise ValueError("Input for templateconversion neither string or list")
