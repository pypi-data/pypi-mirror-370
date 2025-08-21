![Greenbone Logo](https://www.greenbone.net/wp-content/uploads/gb_new-logo_horizontal_rgb_small.png)

# Pontos - Greenbone Python Utilities and Tools <!-- omit in toc -->

[![GitHub releases](https://img.shields.io/github/release/greenbone/pontos.svg)](https://github.com/greenbone/pontos/releases)
[![PyPI release](https://img.shields.io/pypi/v/pontos.svg)](https://pypi.org/project/pontos/)
[![code test coverage](https://codecov.io/gh/greenbone/pontos/branch/main/graph/badge.svg)](https://codecov.io/gh/greenbone/pontos)
[![Build and test](https://github.com/greenbone/pontos/actions/workflows/ci-python.yml/badge.svg)](https://github.com/greenbone/pontos/actions/workflows/ci-python.yml)

The **pontos** Python package is a collection of utilities, tools, classes and
functions maintained by [Greenbone].

Pontos is the German name of the Greek titan [Pontus](https://en.wikipedia.org/wiki/Pontus_(mythology)),
the titan of the sea.

## Table of Contents <!-- omit in toc -->

- [Documentation](#documentation)
- [Installation](#installation)
  - [Requirements](#requirements)
  - [Install using pipx](#install-using-pipx)
  - [Install using pip](#install-using-pip)
  - [Install using poetry](#install-using-poetry)
- [Command Completion](#command-completion)
  - [Setup for bash](#setup-for-bash)
  - [Setup for zsh](#setup-for-zsh)
- [Development](#development)
- [Maintainer](#maintainer)
- [Contributing](#contributing)
- [License](#license)

## Documentation

The documentation for pontos can be found at https://greenbone.github.io/pontos/. Please refer to the documentation for more details as this README just gives a short overview.

## Installation

### Requirements

Python 3.9 and later is supported.

### Install using pipx

You can install the latest stable release of **pontos** from the Python
Package Index (pypi) using [pipx]

    python3 -m pipx install pontos

### Install using pip

> [!NOTE]
> The `pip install` command does no longer work out-of-the-box in newer
> distributions like Ubuntu 23.04 because of [PEP 668](https://peps.python.org/pep-0668).
> Please use the [installation via pipx](#install-using-pipx) instead.

You can install the latest stable release of **pontos** from the Python
Package Index (pypi) using [pip]

    python3 -m pip install --user pontos

### Install using poetry

Because **pontos** is a Python library you most likely need a tool to
handle Python package dependencies and Python environments. Therefore we
strongly recommend using [poetry].

You can install the latest stable release of **pontos** and add it as
a dependency for your current project using [poetry]

    poetry add pontos

## Command Completion

`pontos` comes with support for command line completion in bash and zsh. All
pontos CLI commands support shell completion. As examples the following sections
explain how to set up the completion for `pontos-release` with bash and zsh.

### Setup for bash

```bash
echo "source ~/.pontos-release-complete.bash" >> ~/.bashrc
pontos-release --print-completion bash > ~/.pontos-release-complete.bash
```

Alternatively, you can use the result of the completion command directly with
the eval function of your bash shell:

```bash
eval "$(pontos-release --print-completion bash)"
```

### Setup for zsh

```zsh
echo 'fpath=("$HOME/.zsh.d" $fpath)' >> ~/.zsh
mkdir -p ~/.zsh.d/
pontos-release --print-completion zsh > ~/.zsh.d/_pontos_release
```

Alternatively, you can use the result of the completion command directly with
the eval function of your zsh shell:

```bash
eval "$(pontos-release --print-completion zsh)"
```


## Development

**pontos** uses [poetry] for its own dependency management and build
process.

First install poetry via [pipx]

    python3 -m pipx install poetry

Afterwards run

    poetry install

in the checkout directory of **pontos** (the directory containing the
`pyproject.toml` file) to install all dependencies including the packages only
required for development.

Afterwards activate the git hooks for auto-formatting and linting via
[autohooks].

    poetry run autohooks activate

Validate the activated git hooks by running

    poetry run autohooks check

## Maintainer

This project is maintained by [Greenbone AG][Greenbone]

## Contributing

Your contributions are highly appreciated. Please
[create a pull request](https://github.com/greenbone/pontos/pulls)
on GitHub. Bigger changes need to be discussed with the development team via the
[issues section at GitHub](https://github.com/greenbone/pontos/issues)
first.

## License

Copyright (C) 2020-2024 [Greenbone AG][Greenbone]

Licensed under the [GNU General Public License v3.0 or later](LICENSE).

[Greenbone]: https://www.greenbone.net/
[poetry]: https://python-poetry.org/
[pip]: https://pip.pypa.io/
[pipx]: https://pypa.github.io/pipx/
[autohooks]: https://github.com/greenbone/autohooks
