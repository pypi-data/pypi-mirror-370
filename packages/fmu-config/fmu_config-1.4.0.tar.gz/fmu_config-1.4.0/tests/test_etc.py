"""Testing the classes/functions in in the etc module."""

import os
from pathlib import Path

import pytest
import yaml
from pytest import MonkeyPatch
from yaml.constructor import ConstructorError

import fmu.config as config
from fmu.config import etc, utilities as util
from fmu.config.configparserfmu import ConfigParserFMU

fmux = etc.Interaction()
logger = fmux.basiclogger(__name__)

logger.info("Running tests...")


DROGON = "tests/data/yml/drogon/input/global_master_config.yml"

# always this statement
if not fmux.testsetup():
    raise SystemExit


def test_info_logger_plain():
    """Test basic logger behaviour plain, will capture output to stdin"""
    logger.info("This is a test")
    # no assert is intended


@pytest.fixture(name="mylogger")
def fixture_mylogger():
    """Add logger"""
    # need to do it like this...
    return fmux.basiclogger(__name__, level="DEBUG")


def test_info_logger(mylogger, caplog):
    """Test basic logger behaviour, will capture output to stdin"""

    mylogger.info("This is a test")
    assert "This is a test" in caplog.text

    logger.warning("This is a warning")
    assert "This is a warning" in caplog.text


def test_more_logging_tests(caplog):
    """Testing on the logging levels, see that ENV variable will override
    the basiclogger setting.
    """

    os.environ["FMU_LOGGING_LEVEL"] = "INFO"

    fmumore = etc.Interaction()  # another instance
    locallogger = fmumore.basiclogger(__name__, level="WARNING")
    locallogger.debug("Display debug")
    assert caplog.text == ""  # shall be empty
    locallogger.info("Display info")
    assert "info" in caplog.text  # INFO shall be shown, overrided by ENV!
    locallogger.warning("Display warning")
    assert "warning" in caplog.text
    locallogger.critical("Display critical")
    assert "critical" in caplog.text


def test_timer(capsys):
    """Test the timer function"""

    time1 = fmux.timer()
    for inum in range(100000):
        inum += 1

    fmux.echo(f"Used time was {fmux.timer(time1)}")
    captured = capsys.readouterr()
    assert "Used time was" in captured[0]
    # repeat to see on screen
    fmux.echo("")
    fmux.warn(f"Used time was {fmux.timer(time1)}")


def test_print_fmu_header():
    """Test writing an app header."""
    fmux.print_fmu_header("MYAPP", "0.99", info="Beta release (be careful)")


def test_user_msg():
    """Testing user messages"""

    fmux.echo("")
    fmux.echo("This is a message")
    fmux.warn("This is a warning")
    fmux.warning("This is also a warning")
    fmux.error("This is an error")
    fmux.critical("This is a critical error", sysexit=False)


def test_load_input_extended_yaml():
    """Test loading YAML will extended "fmu" option."""
    cfg = util.yaml_load(DROGON, loader="fmu")

    assert cfg["revision"] == "21.x.0.dev"
    assert (
        cfg["masterdata"]["smda"]["coordinate_system"]["uuid"]
        == "ad214d85-dac7-19da-e053-c918a4889309"
    )


def test_load_input_extended_yaml_shallfail():
    """Test loading non-standard YAML which shall fail when allow_extended is False."""
    with pytest.raises(ConstructorError, match=r"!include"):
        _ = util.yaml_load(DROGON, loader="standard")


def test_load_yaml_compare(tmp_path):
    """Test loading YAML and compare results with/without allow_extended."""

    cfg = util.yaml_load(DROGON, loader="fmu")

    yfile = tmp_path / "drogon.yml"
    with open(yfile, "w", encoding="utf-8") as stream:
        yaml.dump(cfg, stream, allow_unicode=True)

    # read a standard YAML file both with normal and extended option
    cfg1 = util.yaml_load(yfile, loader="fmu")
    cfg2 = util.yaml_load(yfile, loader="standard")

    assert cfg == cfg1 == cfg2


def test_mapping_ordering_maintained(tmp_path: Path) -> None:
    cfg = ConfigParserFMU()
    cfg._config = {"revision": "test", "global": {"c": 1, "b": 2, "a": 3}}

    # Will alphabetically sort mappings
    with open(tmp_path / "bad_cfg.yml", "w", encoding="utf-8") as f:
        yaml.dump(cfg, f, allow_unicode=True)
    # Shouldn't alphabetically sort mappings
    cfg.to_yaml("good_cfg", tmp_path)

    bad_cfg = util.yaml_load(tmp_path / "bad_cfg.yml", loader="fmu")
    good_cfg = util.yaml_load(tmp_path / "good_cfg.yml", loader="fmu")

    assert bad_cfg != cfg._config
    assert good_cfg == cfg._config


def test_mapping_ordering_maintained_during_include(
    tmp_path: Path, monkeypatch: MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    with open("global_config.yml", "w", encoding="utf-8") as f:
        # Can't yaml dump this, puts the !include in quotes
        f.write(
            """
revision: test
global:
  foo: !include _bar.yml
    """.strip()
        )

    _bar_yml = {
        "A_Upper": 11.2,
        "A_Lower_2": 12.3,
        "A_Lower_1": 12.3,
        "C_Fm_3": 13.4,
        "C_Fm_2": 13.4,
        "C_Fm_1": 13.4,
        "B_Upper_2": 14.5,
        "B_Upper_1": 14.5,
        "B_Lower_2": 14.3,
        "B_Lower_1": 14.3,
    }
    with open("_bar.yml", "w", encoding="utf-8") as f:
        f.write(yaml.dump(_bar_yml))

    cfg = config.ConfigParserFMU()
    cfg.parse("global_config.yml")
    cfg.to_yaml(
        rootname="out_config",
        destination=tmp_path,
        template=tmp_path,
    )
    with open("out_config.yml", encoding="utf-8") as f:
        # Strip out added comments
        result = "".join([line for line in f.readlines() if not line.startswith("#")])

    expected = """
revision: test
global:
  foo:
    A_Upper: 11.2
    A_Lower_2: 12.3
    A_Lower_1: 12.3
    C_Fm_3: 13.4
    C_Fm_2: 13.4
    C_Fm_1: 13.4
    B_Upper_2: 14.5
    B_Upper_1: 14.5
    B_Lower_2: 14.3
    B_Lower_1: 14.3
""".strip()
    assert result.strip() == expected.strip()
