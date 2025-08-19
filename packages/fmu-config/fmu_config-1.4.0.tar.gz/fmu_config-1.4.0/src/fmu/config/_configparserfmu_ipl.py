"""Addon to configparser.py. Focus on IPL handling"""

from __future__ import annotations

import datetime
import os
from collections import OrderedDict
from copy import deepcopy
from typing import TYPE_CHECKING

from fmu.config import etc

if TYPE_CHECKING:
    from typing import Any

    from .configparserfmu import ConfigParserFMU

XFMU = etc.Interaction()
logger = XFMU.functionlogger(__name__)

# pylint: disable=protected-access
# pylint: disable=too-many-branches


class ConfigError(ValueError):
    """Exception used for config error, derived from ValueError"""


def to_ipl(
    config_parser: ConfigParserFMU,
    rootname: str = "global_variables",
    destination: str | None = None,
    template: str | None = None,
    tool: str = "rms",
) -> None:
    """Export the config as a global variables IPL and/or template
    form of the IPL.

    Args:
        rootname: Root file name without extension. An extension
            .ipl will be added for destination, and .ipl.tmpl
            for template output.
        destination (str): The output file destination (folder)
        template (str): The folder for the templated version of the
            IPL (for ERT).
        tool (str): Which section in the master to use (default is 'rms')
    """

    if not destination and not template:
        raise ConfigError("Both destination and template for IPL cannot be None.")

    if destination and not os.path.isdir(destination):
        raise ConfigError(
            'Given "destination" {} is not a directory'.format(destination)
        )
    if template and not os.path.isdir(template):
        raise ConfigError('Given "template" {} is not a directory'.format(template))

    declarations = []
    expressions_dest: list[str] = []
    expressions_tmpl: list[str] = []

    metadata = config_parser._get_sysinfo(commentmarker="//")
    declarations.extend(metadata)

    hdecl, hlist = _ipl_stringlist_format(config_parser, "horizons", tool=tool)
    if hdecl is not None:
        declarations.extend(hdecl)
        assert hlist is not None
        expressions_dest.extend(hlist)
        expressions_tmpl.extend(hlist)

    hdecl, hlist = _ipl_stringlist_format(config_parser, "zones", tool=tool)
    if hdecl is not None:
        declarations.extend(hdecl)
        assert hlist is not None
        expressions_dest.extend(hlist)
        expressions_tmpl.extend(hlist)

    hdecl, hlist = _ipl_kwlists_format(config_parser, tool=tool)
    if hdecl is not None:
        declarations.extend(hdecl)
        assert hlist is not None
        expressions_dest.extend(hlist)
        expressions_tmpl.extend(hlist)

    # freeform formats (most complex to handle)
    if destination:
        hdecl, hlist = _ipl_freeform_format(config_parser)
        if hdecl is not None:
            declarations.extend(hdecl)
            assert hlist is not None
            expressions_dest.extend(hlist)

        destfile = os.path.join(destination, rootname + ".ipl")
        with open(destfile, "w", encoding="utf-8") as stream:
            for line in declarations:
                stream.write(line)

            for line in expressions_dest:
                stream.write(line)

    if template:
        hdecl, hlist = _ipl_freeform_format(config_parser, template=True)
        if hdecl is not None:
            if not destination:
                declarations.extend(hdecl)

            assert hlist is not None
            expressions_tmpl.extend(hlist)

        tmplfile = os.path.join(template, rootname + ".ipl.tmpl")
        with open(tmplfile, "w", encoding="utf-8") as stream:
            for line in declarations:
                stream.write(line)

            for line in expressions_tmpl:
                stream.write(line)


def _ipl_stringlist_format(
    config_parser: ConfigParserFMU, subtype: str, tool: str = "rms"
) -> tuple[list[str] | None, list[str] | None]:
    """Process the rms horizons etc, and return declarations and values."""

    cfg = config_parser.config[tool].get(subtype)
    if cfg is None:
        return None, None

    decl = []
    expr = []
    for variable in cfg:
        mydecl = "String {}[]\n".format(variable)
        decl.append(mydecl)

        array = cfg[variable]
        for inum, element in enumerate(array):
            mylist = '{}[{}] = "{}"\n'.format(variable, inum + 1, element)
            expr.append(mylist)

    expr.append("\n")

    return decl, expr


def _ipl_kwlists_format(
    config_parser: ConfigParserFMU, tool: str = "rms"
) -> tuple[list[str] | None, list[str] | None]:
    """Process the rms 'kwlists', and return declarations and values.

    This format is on the form::

      rms:
        kwlists:

          FACIESNAMES:
            OFFSHORE_VI_C: [1, "Offshore mudstones, Viking Gp."]
            MUDDY_SPIC_C: [2, "Muddy spiculites"]
            BIOSTROME_REEF_C: [3, "Biostrome reef"]
            SANDY_SPIC_C: [4, "Sandy spiculites"]
            TSS_Z1_C: [5, "Transgressive sands, Draupne Fm 2"]

    It should then give::

       Int OFFSHORE_VI_C = 1
       Int MUDDY_SPIC_C = 2
       etc...

       String FACIESNAMES[]

       FACIESNAMES[OFFSHORE_VI_C] = "Offshore mudstones, Viking Gp."
       etc
    """

    cfg = config_parser.config[tool].get("kwlists")
    if cfg is None:
        return None, None

    decl = []
    expr = []
    for key, var in cfg.items():
        mydecl = "String {}[]\n".format(key)
        decl.append(mydecl)

        for subkey, (code, fullname) in var.items():
            # logger.info(subkey, code, fullname)
            mydecl = "Int {} = {}\n".format(subkey, code)
            decl.append(mydecl)

            mylist = '{}[{}] = "{}"\n'.format(key, subkey, fullname)
            expr.append(mylist)

        expr.append("\n")

    return decl, expr


def _cast_value(value: Any) -> Any:
    """Convert data type when a number is represented as a string,
    e.g. '1' or '34.33'
    """

    logger.info("Value is of type %s", type(value))
    result = value
    if isinstance(value, str):
        if "." in value:
            try:
                result = float(value)
            except ValueError:
                result = value
        elif value.lower() in ("yes", "true"):
            result = True
        elif value.lower() in ("no", "false"):
            result = False
        else:
            try:
                result = int(value)
            except ValueError:
                result = value
    else:
        result = value

    return result


def _guess_dtype(var: str, entry: dict[str, Any]) -> dict[str, Any]:
    """Guess the IPL dtype from value or values if dtype is missing.

    The entry itself will then be a scalar or a list, which need to be
    analysed. If a list, only the first value is analysed for data
    type; then it is ASSUMED it is the type...

    Returns a dict (OrderedDict) as usekey[keyword]['dtype'] and
    usekey[keyword]['value'] or usekey[keyword]['values']
    """

    values = entry[var]
    keyword = var
    logger.info("Guess dtype and value(s) for %s %s", var, values)

    usekey: OrderedDict = OrderedDict()
    usekey[keyword] = OrderedDict()
    usekey[keyword]["dtype"] = None
    usekey[keyword]["value"] = None  # Keep "value" if singel entry
    usekey[keyword]["values"] = None  # Keep "values", if list

    if isinstance(values, list):
        checkval = values[0]
        scheckval = str(checkval)
        if "~" in scheckval:
            val, _xtmp = scheckval.split("~")
            checkval = val.strip()
            checkval = _cast_value(checkval)

        usekey[keyword]["values"] = values
        del usekey[keyword]["value"]
    else:
        checkval = values
        scheckval = str(checkval)
        if "~" in scheckval:
            val, _xtmp = scheckval.split("~")
            checkval = val.strip()
            checkval = _cast_value(checkval)
        usekey[keyword]["value"] = values
        del usekey[keyword]["values"]

    for alt in ("int", "str", "float", "bool"):
        if alt in str(type(checkval)):
            usekey[keyword]["dtype"] = alt
            break

    if not usekey[keyword]["dtype"]:
        # dtype is still None; evaluate for date or datepair:
        if isinstance(checkval, list):
            checkval = checkval[0]
            if isinstance(checkval, datetime.date):
                usekey[keyword]["dtype"] = "datepair"
        else:
            if isinstance(checkval, datetime.date):
                usekey[keyword]["dtype"] = "date"

    # final check
    if not usekey[keyword]["dtype"]:
        raise RuntimeError("Cannot find dtype")

    logger.info("Updated key XX dtype is %s", usekey[keyword]["dtype"])
    logger.info("Updated key XX is %s", usekey)
    return usekey


def _ipl_freeform_format(
    config_parser: ConfigParserFMU, template: bool = False
) -> tuple[list[str] | None, list[str] | None]:
    """Process the RMS IPL YAML config freeform types.

    The freeform types are e.g. like this::

        rms:
          KH_MULT_MTR:
            dtype: float
            value: 1.0 ~ <KH_MULT_MTR>  # <..> be used in ERT template

          GOC:
            dtype: float
            values:
              - 2010.0
              - 2016.0

    I.e. they are defined as *UPPERCASE_LETTER* keys within
    the RMS section, in contrast to 'horizons' and 'zones'

    Args:
        template (bool): If True, then the tvalue* are returned, if present

    """

    decl = ["\n// Declare free form:\n"]
    expr = ["\n// Free form expressions:\n"]

    cfg = config_parser.config["rms"]

    # collect uppercase keys in 'rms'
    freeform_keys = []
    for key in cfg:
        if all(word[0].isupper() for word in key if word.isalpha()):
            freeform_keys.append(key)

    if not freeform_keys:
        return None, None

    for variable in freeform_keys:
        logger.info("Variable to process is %s", variable)
        expr.append("\n")

        if variable.startswith("_IPL_CODE"):
            logger.info("IPL code stub: %s \n%s", variable, cfg[variable])
            expr.append(cfg[variable])
            continue

        if variable.startswith("_IPL_DECLARE"):
            logger.info("IPL declare only: %s \n%s", variable, cfg[variable])
            decl.append(cfg[variable])
            continue

        if not isinstance(cfg[variable], dict):
            guesscfg = _guess_dtype(variable, cfg)

            usecfg = guesscfg[variable]
        else:
            usecfg = deepcopy(cfg[variable])

        mydtype = usecfg["dtype"]
        myvalue = usecfg.get("value")
        myvalues = usecfg.get("values")

        if mydtype in ("date", "datepair"):
            if myvalue is not None:
                raise RuntimeError(
                    '<{}>: Treating <date> as "value" is not '
                    'possible, rather make into list "values" '
                    "with one entry instead!".format(myvalue)
                )
            myvalues = _fix_date_format(variable, mydtype, myvalues, aslist=True)
            mydtype = "str"

        if myvalue is None and myvalues is None:
            raise ConfigError(
                "'value' or 'values' is missing for RMS variable {}".format(variable)
            )

        adecl, aexpr = _freeform_handle_entry(
            variable, myvalue, myvalues, mydtype, template
        )

        logger.info("Append %s", adecl)
        decl.append(adecl)
        expr.append(aexpr)

    decl.append("//{} {}\n\n".format("-*- END IPL DECLARATIONS -*-", "-" * 48))

    return decl, expr


def _freeform_handle_entry(
    variable: str,
    myvalue: str | bool | None,
    myvalues: list[str] | None,
    dtype: str,
    template: bool,
) -> tuple[str, str]:  # pylint: disable=too-many-statements
    """Handling of any entry as single value or list in IPL.

    Either myvalue or myvalues shall be None!

    Args:
        variable (str): Name of variable
        myvalue (str or bool): Single value case
        myvalues (): List of values
        dtype (str): Type of variable on python form: "str", "float", "int", ...

    Returns:
        (decl, expr): Declaration string and expression string
    """

    decl = ""
    expr = ""

    subtype = None
    if dtype is not None:
        subtype = dtype.capitalize()
    if "Str" in subtype:
        subtype = "String"

    logger.info(
        "Subtype for %s is %s (myvalue is %s, dtype is %s)",
        variable,
        subtype,
        myvalue,
        dtype,
    )

    # inner function
    def _fixtheentry(
        variable: str,
        myval: str | bool,
        subtype: str,
        count: int | None = None,
        template: bool = False,
    ) -> tuple[str, str]:
        logger.info("Fix freeform entry %s (subtype %s)", variable, subtype)
        tmpvalue = str(myval)
        if "~" in tmpvalue:
            val, var = tmpvalue.split("~")
            val = val.strip()
            var = var.strip()
        else:
            val = tmpvalue.strip()
            var = None

        if subtype == "Bool":
            if val in ("True", "yes", "YES", "Yes", "true", "TRUE"):
                val = "TRUE"
            if val in ("False", "no", "NO", "No", "false", "FALSE"):
                val = "FALSE"

        if subtype == "Float":
            logger.info("Input float value is %s (%s)", val, variable)
            if "e" in str(val).lower():
                val = "{0:E}".format(float(val))

            logger.info("Updated float value is %s (%s)", val, variable)

        if subtype == "String":
            val = '"{}"'.format(val)
            if var:
                var = '"{}"'.format(var)

        myvalue = val
        if var:
            myvalue = val + "  // " + var

        if var and template:
            myvalue = var + "  // " + val

        counter = ""
        if count:
            counter = "[" + str(count) + "]"
        expr = variable + counter + " = " + myvalue + "\n"

        decltype = ""
        if count:
            decltype = "[]"  # e.g. Bool SOMEBOOL[]

        decl = subtype + " " + variable + decltype + "\n"

        return decl, expr

    # single entry
    if myvalue is not None:
        decl, expr = _fixtheentry(variable, myvalue, subtype, template=template)

    # list entry
    elif myvalues is not None:
        expr = ""
        for icount, myval in enumerate(myvalues):
            decl, subexpr = _fixtheentry(
                variable, myval, subtype, count=icount + 1, template=template
            )
            expr += subexpr

    return decl, expr


def _fix_date_format(
    var: str, dtype: str, value: str | None, aslist: bool = False
) -> str | list[str] | None:
    """Make dateformat to acceptable RMS IPL format."""

    logger.info("Fix dates for %s", var)
    if value is None:
        returnv = None

    logger.info("Fix dates... dtype is %s", dtype)
    if dtype not in ("date", "datepair"):
        logger.info("Fix dates... dtype is %s RETURN", dtype)
        return value

    values: list[tuple[datetime.datetime, datetime.datetime]] | str | None = None
    if aslist:
        logger.debug("Dates is a list")
        values = value
        value = ""

    if dtype == "date":
        logger.info("Process date ...")
        if values:
            mynewvalues: list[str] = []
            logger.info("Process date as values")
            for val in values:
                if isinstance(val, (datetime.datetime, datetime.date)):
                    val = str(val)
                    val = val.replace("-", "")
                    mynewvalues.append(val)
            returnv = mynewvalues

    if dtype == "datepair" and values:
        mynewvalues = []
        for val in values:
            date1, date2 = val  # type: ignore
            # -- might be iterable, list, tuple
            if isinstance(date1, (datetime.datetime, datetime.date)):
                date1 = str(date1)
                date1 = date1.replace("-", "")
            if isinstance(date2, (datetime.datetime, datetime.date)):
                date2 = str(date2)
                date2 = date2.replace("-", "")
            mynewvalues.append(date1 + "_" + date2)

        returnv = mynewvalues

    return returnv
