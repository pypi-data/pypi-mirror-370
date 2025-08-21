# clickpy

Automated mouse clicker script using [PyAutoGUI][1] and [Typer][2].

This app will randomly click your mouse between 1 second and 3 minutes, to prevent your screen and apps from sleeping or displaying an `away` status.

The rational behind the random interval is: if the mouse contiually clicked every second or millisecond, it could easily be detected as an automated process.

The random interval provides a sembalance of feasability, although the interval could be reduced and extended as needed, or move the cursor after a couple consecutive clicks. (Possibe future feature?)

PyAutoGUI provides a simple interface to the mouse, and Typer provides simple cli parsing. You can find out more about these libraries with the links provided above.

## Installation

This package supports Python 3.6 through 3.9. It does not support any version of Python 2, nor any version of 3 lower than 3.6. Please upgrade our Python version, if possible.

I highly recommend using [pipx][3] for installing standalone packages, as it adds a layer of isolation to your installation. But pip will also work.

```bash
pipx install clickpy
# -- or --
pip install clickpy
```

If you're using macOS or Linux, you may have to install additional dependencies for PyAutoGUI to work properly. Please review their [docs][4] for additional information.

Windows users don't have to install any additional software.

To uninstall, type in your terminal:

```bash
pipx uninstall clickpy
# -- or --
pip uninstall clickpy
```

## Running

Once this package is installed, and any additional dependencies too, run the app like so:

```bash
clickpy
```

To stop it, press `ctrl+c`.

There are 3 flags you can use; `-d` will display debug information, `-f` will speed the app up to 1 click every second, and `--help` will display the help menu.

## For Developers

Please read [contributing.md](./CONTRIBUTING.md) for more information about this repo, how it's maintained and developed. And feel free to make PRs.

[1]: https://github.com/asweigart/pyautogui
[2]: https://github.com/tiangolo/typer
[3]: https://github.com/pypa/pipx
[4]: https://github.com/asweigart/pyautogui/blob/master/docs/install.rst
