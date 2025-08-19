# Contributing

Contributions are welcome, and they are greatly appreciated! Every
little bit helps, and credit will always be given.

You can contribute in many ways:

## Types of Contributions

### Report Bugs

Report issues and bugs at [fmu-config/issues](https://github.com/equinor/fmu-config/issues)

If you are reporting a bug, please include:

- Your operating system name and version.
- Any details about your local setup that might be helpful in troubleshooting.
- Detailed steps to reproduce the bug.

### Fix Bugs

Look through the Git issues for bugs. Anything tagged with "bug"
and "help wanted" is open to whoever wants to implement it.

### Implement Features

Look through the Git issues for features. Anything tagged with "enhancement"
and "help wanted" is open to whoever wants to implement it.

### Write Documentation

fmu-config could always use more documentation, whether as part of the
official fmu-config docs, in docstrings, or even on the web in blog posts,
articles, and such.

### Submit Feedback

The best way to send feedback is to file an issue at [fmu-config/issues](https://github.com/equinor/fmu-config/issues)

If you are proposing a feature:

- Explain in detail how it would work.
- Keep the scope as narrow as possible, to make it easier to implement.
- Remember that this is a volunteer-driven project, and that contributions
  are welcome :)

## Code standards

It is very important to be complient to code standards. fmu-config uses
[ruff](https://pypi.org/project/ruff/),
[mypy](https://mypy.readthedocs.io/en/stable/) to format and lint all code.

### In addition

- Start with documentation and tests. Think and communicate first!
- Docstrings shall start and end with """ and use Google style.
- Use pytest as testing engine
- Code shall be be Python 3.9+ compliant

### Linting

```sh
  ruff check . && ruff format . --check
```

The pylint is rather strict and sometimes excpetions are needed... , but anyway quite useful!

```sh
  python -m pylint mycode.py
```

## Get Started

Ready to contribute? Here's how to set up `fmu-config` for local development.

1. Fork the `fmu-config` repo in web browser to a personal fork
2. Clone your fork locally:

    ```sh
        git clone git@github.com:<your-user>/fmu-config.git
        cd fmu-config
        git remote add upstream git@github.com:equinor/fmu-config.git
    ```

   This means your `origin` is now your personal fork, while the actual master
   is at `upstream`.
3. Then create a virtual environment and install

    ```sh
        python -m venv <your-venv>
        source <your-venv>/bin/activate
        pip install ".[dev]"
    ```
