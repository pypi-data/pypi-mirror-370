"""Testing fmu-config tools."""

import pytest

import fmu.config as config
from fmu.config import utilities as utils

# import fmu.config.fmuconfigrunner as fmurun

fmux = config.etc.Interaction()
logger = fmux.basiclogger(__name__)

REEK = "tests/data/yml/reek/global_variables.yml"

# always this statement
if not fmux.testsetup():
    raise SystemExit


def test_basic_tools():
    """Test basic tools behaviour"""

    cfg = utils.yaml_load(REEK)

    assert cfg["global"]["name"] == "Reek"

    with pytest.raises(FileNotFoundError):
        utils.yaml_load("not_a_file.xyz")
