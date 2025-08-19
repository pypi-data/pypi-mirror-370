"""Module for basic interaction with user, including logging for debugging.

This module can and should be used by other FMU modules e.g. fmu.ensemble also.

Logging is enabled by setting a environment variable::

  export FMU_LOGGING_LEVEL=INFO   # if bash; will set logging to INFO level
  setenv FMU_LOGGING_LEVEL INFO   # if tcsh; will set logging to INFO level

Other levels are DEBUG and CRITICAL. CRITICAL is default (cf. Pythons logging)

Usage of logging in scripts::

  from fmu.config import etc
  fmux = etc.Interaction()
  logger = fmux.basiclogger(__name__)
  logger.info('This is logging of %s', something)

Other than logging, there is also a template for user interaction, which shall
be used in client scripts::

  fmux.echo('This is a message')
  fmux.warn('This is a warning')
  fmux.error('This is an error, will continue')
  fmux.critical('This is a big error, will exit')

Ind finally, there is a template for setting up a header for applications, see
the ```print_fmu_header``` method

"""

from __future__ import annotations

import inspect
import logging
import os
import sys
import timeit
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from inspect import FrameInfo
    from types import FrameType

# pylint: disable=protected-access


class _BColors:
    # local class for ANSI term color commands
    # bgcolors:
    # 40=black, 41=red, 42=green, 43=yellow, 44=blue, 45=pink, 46 cyan

    # pylint: disable=too-few-public-methods
    HEADER = "\033[1;96m"
    OKBLUE = "\033[94m"
    OKGREEN = "\033[92m"
    WARN = "\033[93;43m"
    ERROR = "\033[93;41m"
    CRITICAL = "\033[1;91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"

    def __init__(self) -> None:
        pass


class Interaction:
    """System for handling interaction; dialogues and messages in FMU.

    This module cooperates with the standard Python logging module.
    """

    def __init__(self) -> None:
        self._callclass: str | None = None
        self._caller: str | None = None
        self._lformat: str | None = None
        self._lformatlevel = 1
        self._logginglevel = "CRITICAL"
        self._logginglevel_fromenv: str | None = None
        self._loggingname = ""
        self._syslevel = 1
        self._test_env = True
        self._tmpdir = "TMP"
        self._testpath: str | None = None

        # a string, for Python logging:
        self._logginglevel_fromenv = os.environ.get("FMU_LOGGING_LEVEL", None)

        # a number, for format, 1 is simple, 2 is more info etc
        loggingformat = os.environ.get("FMU_LOGGING_FORMAT")

        if self._logginglevel_fromenv:
            self.logginglevel = self._logginglevel_fromenv

        if loggingformat is not None:
            self._lformatlevel = int(loggingformat)

    @property
    def logginglevel(self) -> str:
        """Set or return a logging level property, e.g. logging.CRITICAL"""

        return self._logginglevel

    @logginglevel.setter
    def logginglevel(self, level: str) -> None:
        # pylint: disable=pointless-statement

        validlevels = ("INFO", "WARNING", "DEBUG", "CRITICAL")
        if level in validlevels:
            self._logginglevel = level
        else:
            raise ValueError("Invalid level given, must be in {}".format(validlevels))

    @property
    def numericallogginglevel(self) -> int:
        """Return a numerical logging level (read only)"""
        llo = logging.CRITICAL
        if self._logginglevel == "INFO":
            llo = logging.INFO
        elif self._logginglevel == "WARNING":
            llo = logging.WARNING
        elif self._logginglevel == "DEBUG":
            llo = logging.DEBUG

        return llo

    @property
    def loggingformatlevel(self) -> int:
        """Set logging format (for future use)"""
        return self._lformatlevel

    @property
    def loggingformat(self) -> str:
        """Returns the format string to be used in logging"""

        if self._lformatlevel <= 1:
            self._lformat = "%(levelname)8s: \t%(message)s"
        else:
            self._lformat = (
                "%(asctime)s Line: %(lineno)4d %(name)44s "
                + "[%(funcName)40s()]"
                + "%(levelname)8s:"
                + "\t%(message)s"
            )

        return self._lformat

    @property
    def tmpdir(self) -> str:
        """Get and set tmpdir for testing"""
        return self._tmpdir

    @tmpdir.setter
    def tmpdir(self, value: str) -> None:
        self._tmpdir = value

    @staticmethod
    def print_fmu_header(
        appname: str, appversion: str, info: str | None = None
    ) -> None:
        """Prints a banner for a FMU app to STDOUT.

        Args:
            appname (str): Name of application.
            appversion (str): Version of application on form '3.2.1'
            info (str, optional): More info, e.g. if beta release

        Example::

            fmux.print_fmu_header('fmuconfig', '0.2.1', info='Beta release!')
        """
        cur_version = "Python " + str(sys.version_info[0]) + "."
        cur_version += str(sys.version_info[1]) + "." + str(sys.version_info[2])

        app = "This is " + appname + ", v. " + str(appversion)
        if info:
            app = app + " (" + info + ")"

        print("")
        print(_BColors.HEADER)
        print("#" * 79)
        print("#{}#".format(app.center(77)))
        print("#{}#".format(cur_version.center(77)))
        print("#" * 79)
        print(_BColors.ENDC)
        print("")

    def basiclogger(self, name: str, level: str | None = None) -> logging.Logger:
        """Initiate the logger by some default settings."""

        if level is not None and self._logginglevel_fromenv is None:
            self.logginglevel = level

        fmt = self.loggingformat
        self._loggingname = name
        logging.basicConfig(format=fmt, stream=sys.stdout)
        logging.getLogger().setLevel(self.numericallogginglevel)  # root logger
        logging.captureWarnings(True)

        return logging.getLogger(name)

    @staticmethod
    def functionlogger(name: str) -> logging.Logger:
        """Get the logger for functions (not top level)."""

        logger = logging.getLogger(name)
        logger.addHandler(logging.NullHandler())
        return logger

    def testsetup(self, path: str = "TMP") -> bool:
        """Basic setup for FMU testing (developer only; relevant for tests)"""

        try:
            os.makedirs(path)
        except OSError:
            if not os.path.isdir(path):
                raise

        self._test_env = True
        self._tmpdir = path
        self._testpath = None

        return True

    @staticmethod
    def timer(*args: dict) -> float:
        """Without args; return the time, with a time as arg return the
        difference.

        Example::

            time1 = timer()
            for i in range(10000):
                i = i + 1
            time2 = timer(time1)
            print('Execution took {} seconds'.format(time2)

        """
        time1 = timeit.default_timer()

        if args:
            return time1 - args[0]  # type: ignore

        return time1

    def echo(self, string: str) -> None:
        """Show info at runtime (for user scripts)"""
        level = -5
        idx = 3

        caller = sys._getframe(1).f_code.co_name
        frame = inspect.stack()[1][0]
        self.get_callerinfo(caller, frame)

        self._output(idx, level, string)

    def warn(self, string: str) -> None:
        """Show warnings at Runtime (pure user info/warns)."""
        level = 0
        idx = 6

        caller = sys._getframe(1).f_code.co_name
        frame = inspect.stack()[1][0]
        self.get_callerinfo(caller, frame)

        self._output(idx, level, string)

    warning = warn

    def error(self, string: str) -> None:
        """Issue an error, will not exit system by default"""
        level = -8
        idx = 8

        caller = sys._getframe(1).f_code.co_name
        frame = inspect.stack()[1][0]
        self.get_callerinfo(caller, frame)

        self._output(idx, level, string)

    def critical(self, string: str, sysexit: bool = True) -> None:
        """Issue a critical error, default is SystemExit."""
        level = -9
        idx = 9

        caller = sys._getframe(1).f_code.co_name
        frame = inspect.stack()[1][0]
        self.get_callerinfo(caller, frame)

        self._output(idx, level, string)
        if sysexit:
            raise SystemExit("STOP!")

    def get_callerinfo(self, caller: str, frame: FrameType) -> tuple[str, str]:
        """Get caller info for logging (developer stuff)"""
        # just keep the last class element
        xname = str(self._get_class_from_frame(frame))
        the_class = xname.split(".")[-1]

        self._caller = caller
        self._callclass = the_class

        return (self._caller, self._callclass)

    # =========================================================================
    # Private routines
    # =========================================================================

    @staticmethod
    def _get_class_from_frame(frame: FrameType) -> FrameInfo:
        # python3 is incomplete (need more coffee)
        current = inspect.currentframe()
        outer = inspect.getouterframes(current)
        return outer[0]

    def _output(self, idx: int, level: int, string: str) -> None:
        # pylint: disable=too-many-branches

        prefix = ""
        endfix = ""

        if idx == 0:
            prefix = "++"
        elif idx == 1:
            prefix = "**"
        elif idx == 3:
            prefix = ">>"
        elif idx == 6:
            prefix = _BColors.WARN + "##"
            endfix = _BColors.ENDC
        elif idx == 8:
            prefix = _BColors.ERROR + "!#"
            endfix = _BColors.ENDC
        elif idx == 9:
            prefix = _BColors.CRITICAL + "!!"
            endfix = _BColors.ENDC

        prompt = False
        if level <= self._syslevel:
            prompt = True

        if prompt:
            if self._syslevel <= 1:
                print("{} {}{}".format(prefix, string, endfix))
            else:
                ulevel = str(level)
                if level == -5:
                    ulevel = "M"
                if level == -8:
                    ulevel = "E"
                if level == -9:
                    ulevel = "W"
                print(
                    "{0} <{1}> [{2:23s}->{3:>33s}] {4}{5}".format(
                        prefix, ulevel, self._callclass, self._caller, string, endfix
                    )
                )
