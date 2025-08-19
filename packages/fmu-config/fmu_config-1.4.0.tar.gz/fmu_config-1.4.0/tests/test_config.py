"""Testing fmu-config."""

import json
import os.path
from os.path import join

import pytest

import fmu.config as config
from fmu.config import _oyaml as yaml, utilities as ut

# import fmu.config.fmuconfigrunner as fmurun

JFILE1 = "tests/data/yml/vinstre/global_master_config.yml"
TFILE2 = "tests/data/yml/ogre/global_master_config.yml"
TFILE3 = "tests/data/yml/ogre/global_master_config_with_dupl.yml"
TFILE4 = "tests/data/yml/ogre/global_master_config_with_merge.yml"
RFILE1 = "tests/data/yml/reek/global_variables.yml"

# result may be compared with data stored here
TCMP = "tests/data/yml/test_compare"

fmux = config.etc.Interaction()
logger = fmux.basiclogger(__name__)

# always this statement
if not fmux.testsetup():
    raise SystemExit

TMPD = fmux.tmpdir


def test_vinstre():
    """Test table output behaviour"""

    cfg = config.ConfigParserFMU()
    cfx = config.ConfigParserFMU()

    assert isinstance(cfg, config.ConfigParserFMU)

    cfg.parse(JFILE1)
    cfx.parse(JFILE1, smart_braces=False)

    cfg.to_table(
        rootname="VI",
        destination=fmux.tmpdir,
        template=fmux.tmpdir,
        entry="global.FWL",
        sep="      ",
    )

    cfg.to_ipl(
        rootname="vinstre_global_variables",
        destination=fmux.tmpdir,
        template=fmux.tmpdir,
        tool="rms",
    )

    cfg.to_yaml(
        rootname="vinstre_global_variables_rms",
        destination=fmux.tmpdir,
        template=fmux.tmpdir,
        tool="rms",
    )

    status1 = ut.compare_yaml_files(
        join(TMPD, "vinstre_global_variables_rms.yml"),
        join(TCMP, "vinstre_global_variables_rms.yml"),
    )
    status2 = ut.compare_yaml_files(
        join(TMPD, "vinstre_global_variables_rms.yml.tmpl"),
        join(TCMP, "vinstre_global_variables_rms.yml.tmpl"),
    )
    assert status1 is True
    assert status2 is True

    cfx.to_yaml(
        rootname="vinstre_global_variables_rms_nobraces",
        destination=fmux.tmpdir,
        template=fmux.tmpdir,
        tool="rms",
    )

    assert cfx.config["rms"]["FWL3"][1] == "1236.0 ~ <>"
    assert cfg.config["rms"]["FWL3"][1] == "1236.0 ~ <FWL3_1>"


def test_basic_ogre():
    """Test basic behaviour"""

    cfg = config.ConfigParserFMU()

    assert isinstance(cfg, config.ConfigParserFMU)

    cfg.parse(TFILE2)

    # cfg.show()

    assert len(cfg.config["rms"]["horizons"]) == 6


def test_to_yaml_ogre():
    """Test the output for the YAML files, both templated and normal for rms"""

    cfg = config.ConfigParserFMU()

    assert isinstance(cfg, config.ConfigParserFMU)

    cfg.parse(TFILE2)
    rootn = "ogre_yaml"

    cfg.to_yaml(
        rootname=rootn, destination=fmux.tmpdir, template=fmux.tmpdir, tool="rms"
    )

    # now read the files again to assert tests
    with open(
        os.path.join(fmux.tmpdir, rootn + ".yml"), "r", encoding="utf-8"
    ) as stream:
        cfg_yml = yaml.safe_load(stream)

    with open(
        os.path.join(fmux.tmpdir, rootn + ".yml.tmpl"), "r", encoding="utf-8"
    ) as stream:
        cfg_tmpl = yaml.safe_load(stream)

    assert cfg_yml["KH_MULT_CSAND"] == 1.0
    assert cfg_tmpl["KH_MULT_CSAND"] == "<KH_MULT_CSAND>"

    status1 = ut.compare_yaml_files(
        join(TMPD, rootn + ".yml"),
        join(TCMP, rootn + ".yml"),
    )
    status2 = ut.compare_yaml_files(
        join(TMPD, rootn + ".yml.tmpl"),
        join(TCMP, rootn + ".yml.tmpl"),
    )
    assert status1 is True
    assert status2 is True

    # IPL version
    rootn = "ogre_ipl"
    cfg.to_ipl(
        rootname=rootn, destination=fmux.tmpdir, template=fmux.tmpdir, tool="rms"
    )

    status1 = ut.compare_text_files(
        join(TMPD, rootn + ".ipl"),
        join(TCMP, rootn + ".ipl"),
    )
    status2 = ut.compare_text_files(
        join(TMPD, rootn + ".ipl.tmpl"),
        join(TCMP, rootn + ".ipl.tmpl"),
    )
    assert status1 is True
    assert status2 is True


def test_to_yaml_ogre_selfread():
    """Test the output for the YAML files, and convert OUTPUT yaml to ipl"""

    cfg = config.ConfigParserFMU()

    cfg.parse(TFILE2)
    rootn = "ogre_yaml"

    cfg.to_yaml(rootname=rootn, destination=fmux.tmpdir, template=fmux.tmpdir)

    newinput = os.path.join(fmux.tmpdir, rootn + ".yml")
    newrootn = "ogre_yaml_selfread"

    cfx = config.ConfigParserFMU()
    cfx.parse(newinput)

    cfx.to_ipl(
        rootname=newrootn, destination=fmux.tmpdir, template=fmux.tmpdir, tool="rms"
    )


def test_ogre_to_yaml_merge():
    """Test the output for the YAML files, and convert OUTPUT yaml to ipl"""

    cfg = config.ConfigParserFMU()

    cfg.parse(TFILE4)
    rootn = "ogre_yaml"

    cfg.to_yaml(rootname=rootn, destination=fmux.tmpdir, template=fmux.tmpdir)

    newinput = os.path.join(fmux.tmpdir, rootn + ".yml")
    newrootn = "ogre_yaml_selfread"

    cfx = config.ConfigParserFMU()
    cfx.parse(newinput)

    cfx.to_ipl(
        rootname=newrootn, destination=fmux.tmpdir, template=fmux.tmpdir, tool="rms"
    )


def test_yaml_has_duplicates_ogre():
    """The YAML file has duplicates; should raise error"""

    cfg = config.ConfigParserFMU()

    with pytest.raises(SystemExit):
        cfg.parse(TFILE3)


def test_to_json_ogre():
    """Test the output for the JSON files, both templated and normal for
    rms section.
    """

    cfg = config.ConfigParserFMU()

    assert isinstance(cfg, config.ConfigParserFMU)

    cfg.parse(TFILE2)
    rootn = "ogre_json"

    cfg.to_json(
        rootname=rootn, destination=fmux.tmpdir, template=fmux.tmpdir, tool="rms"
    )

    with open(
        os.path.join(fmux.tmpdir, rootn + ".json"), "r", encoding="utf-8"
    ) as myfile:
        cfg_json = json.load(myfile)

    assert cfg_json["KH_MULT_CSAND"] == str(1.0)


def test_ipl_ogre():
    """Test basic behaviour"""

    cfg = config.ConfigParserFMU()

    assert isinstance(cfg, config.ConfigParserFMU)

    cfg.parse(TFILE2)

    # cfg.show()
    # cfg.show(style='json')

    # export the config as a global variables IPL
    logger.info("Test dir is %s", fmux.tmpdir)
    cfg.to_ipl(
        destination=os.path.join(fmux.tmpdir), template=os.path.join(fmux.tmpdir)
    )


def test_special_chars():
    """Test that special characters are carried through to produced files.

    When using non-ascii in source global_variables or include files, they shall not be
    converted to hex.
    """

    cfg = config.ConfigParserFMU()
    cfg.parse(JFILE1)
    cfg.to_yaml(
        rootname="special_chars_global_variables",
        destination=fmux.tmpdir,
        template=fmux.tmpdir,
    )
    cfg.to_json(
        rootname="special_chars_global_variables",
        destination=fmux.tmpdir,
    )

    # test assumption
    assert cfg.config["_special_chars"]["norwegian_letters"] == "æøåÆØÅ"

    # YAML
    outpath_yml = join(TMPD, "special_chars_global_variables.yml")
    assert os.path.isfile(outpath_yml)

    # open with yaml reader (which handles ÆØÅ)
    with open(outpath_yml, "r", encoding="utf-8") as stream:
        outcontent = yaml.safe_load(stream)
    assert outcontent["_special_chars"]["norwegian_letters"] == "æøåÆØÅ"

    # confirm correct encoding in raw txt
    with open(outpath_yml, "r", encoding="utf-8") as stream:
        outcontent_yaml_raw = stream.read()
    assert "_special_chars:" in outcontent_yaml_raw  # test assumption
    assert "æøåÆØÅ" in outcontent_yaml_raw

    # JSON
    outpath_json = join(TMPD, "special_chars_global_variables.json")
    assert os.path.isfile(outpath_json)

    # confirm correct encoding in raw txt
    with open(outpath_json, "r", encoding="utf-8") as stream:
        outcontent_json_raw = stream.read()
    assert "æøåÆØÅ" in outcontent_json_raw


# def test_basic_reek():
#     """Test basic behaviour, Reek setup"""

#     cfg = config.ConfigParserFMU()

#     assert isinstance(cfg, config.ConfigParserFMU)

#     cfg.parse(RFILE1)

#     cfg.show()

#     # will write the eclipse files
#     cfg.to_eclipse()
#     cfg.to_ipl()
#     cfg.to_yaml('myyaml', destination='TMP')
#     cfg.to_json('myjson', destination='TMP')

#     # assert len(cfg.config['horizons']) == 6

#     # # export the config as a global variables IPL
#     # cfg.to_ipl('myfile')


# def test_command_make_ipls():
#     """Make IPL both global_variable.ipl and global_variables.tmpl, Reek."""
#     fmurun.main(['--input', RFILE1, '--mode', 'ipl'])  # noqa


# def test_command_make_yamls():
#     """Make IPL both global_variables_rms.yml and global_variables_tmpl.yml,
#     Reek.
#     """

#     fmurun.main(['--input', RFILE1, '--mode', 'yaml', --tool, 'rms'])  # noqa
