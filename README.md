# systemd multi-process manager

[![Build Status](https://travis-ci.org/anlutro/systemd-multi-process-manager.svg?branch=master)](https://travis-ci.org/anlutro/systemd-multi-process-manager)
[![Latest version on PyPI](https://img.shields.io/pypi/v/sdmpm?maxAge=2592000)](https://pypi.python.org/pypi/sdmpm)
![License](https://img.shields.io/github/license/anlutro/systemd-multi-process-manager.svg)

`systemd` supports multiple processes of the exact same type using templating. However, it's very tedious to scale the number of processes up or down. This script aims to simplify that.

## Installation

The script is published on PyPI under the name `sdmpm`.

1. Use a tool like [pipx](https://github.com/pipxproject/pipx) or [psm](https://github.com/anlutro/psm) to install this script into a dedicated virtualenv: `psm install sdmpm`
2. Install using pip: `pip install sdmpm` (preferably with `--user` or in a virtualenv)

You can also just download the script directly from Github, it has no external dependencies and is tested on Python 3.5 and higher.

```bash
wget https://github.com/anlutro/systemd-multi-process-manager/raw/master/src/sdmpm.py -o /usr/local/bin/sdmpm
```

## Usage

Assuming you have a templated service already configured (i.e. there is an `/etc/systemd/system/example@.service`), you can use this to determine how many of this process should be running:

```
$ sdmpm scale example 4
```

You can also use the standard `systemctl` commands such as `status`, `start`, `stop`, `restart`, `enable` and `disable`.

You can pass `--user` which will work just like `systemctl --user`.

## License

The contents of this repository are released under the [GPL v3 license](https://opensource.org/licenses/GPL-3.0). See the [LICENSE](LICENSE) file included for more information.
