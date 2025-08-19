"""Testing fmu-config, here focus on individual private functions"""

import datetime
from collections import OrderedDict

import fmu.config as config
from fmu.config._configparserfmu_ipl import (
    _cast_value,
    _freeform_handle_entry,
    _guess_dtype,
)

FMUX = config.etc.Interaction()
logger = FMUX.basiclogger(__name__)

# always this statement
if not FMUX.testsetup():
    raise SystemExit


def test_ipl_guess_dtype():
    """Test IPL guess dtype output behaviour"""

    # int; single var
    var = "TESTVAR"
    entry = {var: 1}
    usekey = _guess_dtype(var, entry)
    assert isinstance(usekey, OrderedDict)
    ndict = usekey[var]
    assert isinstance(ndict, OrderedDict)
    assert ndict["dtype"] == "int"
    assert ndict["value"] == 1

    # float; single var
    var = "TESTVAR"
    entry = {var: 1.0}
    usekey = _guess_dtype(var, entry)
    assert isinstance(usekey, OrderedDict)
    ndict = usekey[var]
    assert isinstance(ndict, OrderedDict)
    assert ndict["dtype"] == "float"
    assert ndict["value"] == 1.0

    # string; single var
    var = "TESTVAR"
    entry = {var: "someword"}
    usekey = _guess_dtype(var, entry)
    assert isinstance(usekey, OrderedDict)
    ndict = usekey[var]
    assert isinstance(ndict, OrderedDict)
    assert ndict["dtype"] == "str"
    assert ndict["value"] == "someword"

    # date; single var
    var = "TESTVAR"
    entry = {var: datetime.date(1999, 11, 1)}
    usekey = _guess_dtype(var, entry)
    assert isinstance(usekey, OrderedDict)
    ndict = usekey[var]
    assert isinstance(ndict, OrderedDict)
    assert ndict["dtype"] == "date"
    assert ndict["value"] == datetime.date(1999, 11, 1)

    # int; list of
    var = "TESTVAR"
    entry = {var: [2, 1, 3, 2]}
    usekey = _guess_dtype(var, entry)
    assert isinstance(usekey, OrderedDict)
    ndict = usekey[var]
    assert isinstance(ndict, OrderedDict)
    assert ndict["dtype"] == "int"
    assert ndict["values"] == [2, 1, 3, 2]


def test_ipl_cast_value():
    """Test IPL guess dtype output behaviour"""

    value = _cast_value("233")
    assert isinstance(value, int)

    value = _cast_value("233.0")
    assert isinstance(value, float)


def test_free_form_handle_entry():
    decl, expr = _freeform_handle_entry("MYVAR", 2, None, "int", False)
    assert decl == "Int MYVAR\n"
    assert expr == "MYVAR = 2\n"

    decl, expr = _freeform_handle_entry("MYVAR", 2.0, None, "float", False)
    assert decl == "Float MYVAR\n"
    assert expr == "MYVAR = 2.0\n"
