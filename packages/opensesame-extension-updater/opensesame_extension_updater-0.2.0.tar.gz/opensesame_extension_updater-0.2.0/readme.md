# Updater extension for OpenSesame/ Rapunzel

Copyright 2023-2025 Sebastiaan Mathôt (@smathot)


## About

An extension that automatically checks for updates to extensions and plugins for OpenSesame and Rapunzel.

The extension first collects all packages that need to be checked by inspecting all implicit namespace packages within `opensesame_extensions` and `opensesame_plugins`, which can define a `package` list in `__init__.py` (see also `opensesame_extensions\updater\__init__.py`).

Next, the current version and the latest version of each of these packages is checked. By default, `conda` is used to check packages installed by both `conda` and `pip`; this is the primary update method on the Windows and Mac OS packages of OpenSesame/ Rapunzel, which are built using `conda`. If `conda` is not available, then `pip` is used to check packages for user-installed pip-packages ; this is the primary update method on Ubuntu, on which updates are generally handled through `apt` except for optional pip-installed packages.

## License

This code is distributed under the terms of the GNU General Public License 3. The full license should be included in the file COPYING, or can be obtained from:

- <http://www.gnu.org/licenses/gpl.txt>
