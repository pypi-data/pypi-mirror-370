# fmu-config

![fmu-config](https://github.com/equinor/fmu-config/workflows/fmu-config/badge.svg)
![Python Version](https://img.shields.io/badge/python-3.11%20|%203.12%20|%203.13-blue.svg)
[![License: LGPL v3](https://img.shields.io/github/license/equinor/fmu-tools)](https://www.gnu.org/licenses/lgpl-3.0)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![PyPI](https://img.shields.io/pypi/v/fmu-config.svg)](https://pypi.org/project/fmu-config/)

FMU config is a small Python library to facilitate configuration of global
variables in Equinor's Fast Model Update (FMU) setup.

## Installation

```sh
    pip install fmu-config
```

## Usage

```sh
    fmuconfig global_config.yml
```

The idea is that there is one global config file that will be the "mother"
of all other files, such as:

- `global_variables.ipl`: IPL file to run from RMS
- `global_variables.ipl.tmpl`: Templated IPL version where
  [ERT](https://github.com/equinor/ert) will fill in `<>` variables
- `global_variables.yml`: working YAML file, with numbers
- `global_variables.yml.tmpl`: templated YAML file, with `<...>` instead of
   numbers; for ERT to process
- Various eclipse file stubs (both "working" and template versions)
- Working and templated files for other tools/scripts

The global_config file shall be in YAML format, with extension `.yml`

To run this package against the global configuration file, just run

## Documentation

The documentation is location at
https://equinor.github.io/fmu-config/

## Contributing

See the [Contributing](CONTRIBUTING.md) document.

## License

This software is released under LGPLv3.
