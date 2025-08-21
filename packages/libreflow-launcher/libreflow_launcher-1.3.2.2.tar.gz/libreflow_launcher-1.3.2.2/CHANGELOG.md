# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html)[^1].

<!---
Types of changes

- Added for new features.
- Changed for changes in existing functionality.
- Deprecated for soon-to-be removed features.
- Removed for now removed features.
- Fixed for any bug fixes.
- Security in case of vulnerabilities.

-->

## [Unreleased]

## [1.3.2.1] - 2025-08-04

### Fixed
* Fixed a bug where the launcher was stuck in offline mode on the first startup

## [1.3.2] - 2025-08-01

### Fixed

* Any error with the api request will set the launcher to offline

## [1.3.1] - 2025-07-31

### Fixed

* uv cache clean on start project and when updating, which basically automatically triggers an update
* renamed `SHOW_PROCESS_VIEW` to `LIBREFLOW_SHOW_PROCESS_VIEW` to follow Libreflow's latest update

## [1.3.0] - 2025-07-30

### BREAKING CHANGES

* Pyside6 module is now being used.
* Virtual environments are now handled by `uv`.
  * It speeds up the creation and updating of Libreflow instances, while also providing greater stability.
  * `poetry` remains in the requirements, in order to allow everyone to migrate any Libreflow instance with the new package manager.
    * Support for `poetry` will be removed at the end of August.

### Added

* An option to skip updates in a Libreflow instance.
* When there is only one project assigned to the user, the autostart command-line argument will skip the launcher GUI and start the Libreflow instance instead.
* The launcher can now be used in offline mode when Overseer servers are unreachable.

### Changed

* Projects list loading time has been improved when switching servers and exiting the settings page.

## [1.2.7] - 2025-03-26

### Changed

* Improve HTTPS redirection by handling 308 error code.

## [1.2.6] - 2025-03-21

### Added

* HTTPS redirect to Overseer server on initial login.

## [1.2.5] - 2024-12-19

### Fixed

* Sync session was broken since 1.2.0 update.

## [1.2.4] - 2024-12-18

### Fixed

* Handle french accents in paths, in bat executable files.

## [1.2.3] - 2024-12-17

### Changed

* The jobs session launch script asks the user for custom pool name(s). If the input pool(s) are left blank, the session is run in the pools defined in the Overseer project configuration (`KABARET_JOBS_POOL_NAME` variable), or `compositing` if the latter are undefined.

## [1.2.2] - 2024-12-13

### Fixed

* Double quote has been added to the python path to handle any whitespace.

## [1.2.1] - 2024-12-12

### Fixed

* Context menu for project was broken if `file_manager.synchronisation` libreflow extension is used.

## [1.2.0] - 2024-12-11

### Added

* A new environment variable `PYTHON_MIN_VERSION` is handled in the project configuration to specify a minimum python version requirement for a project.
* A request session is created when a project has the `file_manager.synchronisation` libreflow extension installed.
* A placeholder file with the project name is now created in project folders.
* A project environment variable `LF_PROJECT_NAME` can now be used in a sync and request session, to specify the project name used in libreflow.

### Changed

* `KABARET_FLOW_EXT_INSTALLERS` environment variable is no longer used if there is no extensions assigned to a project.
* The launcher now uses the direct path for python. Especially for using the correct version selected in the settings.
* Poetry path is no longer used. Instead, it calls the Python module to ensure that the correct one is used according to the Python version.
* In the settings, the Python path parameter is now a list and you can add a custom path.
* Checking the Poetry environment of a project has been improved.
  * It makes sure it uses the correct Python version selected in the settings, and that all dependencies are installed.

### Fixed

* Python versions are now fetched correctly on Linux distributions.
* In the wizard, the default port of an Overseer server is now adjusted according to the address type.
  * `80` for a public address or `5500` for a local one.
* When switching servers, the project list showed only one.

### Removed

* The environment variable `LF_LAUNCHER_POETRY_PATH` is no longer used.

## [1.1.6.1] - 2024-10-23

### Fixed

* Typo error for check the extension category about the latest release fix.

## [1.1.6] - 2024-10-23

### Fixed

* Using a git version of an extension broke the usage of a libreflow instance.

## [1.1.5] - 2024-10-23

### Fixed

* The resolved extensions are now enabled for the jobs session. The generated script provides them in the `KABARET_FLOW_EXT_INSTALLERS` environment variable.

## [1.1.4] - 2024-08-06

### Fixed

* Error raising when fetching available python versions while Python 2.7 is installed on the system. The version simply won't appear in the list.
* Only Python versions having a valid interpreter path are available in the global settings.
* Missing `shutil` import and undefined method preventing the launcher from starting when the user settings were not created yet.

## [1.1.3] - 2024-07-31

### Fixed

* Exception for invalid poetry path. Redirect the user to specify a correct one in the global settings.

## [1.1.2] - 2024-07-26

### Added

* A new environment variable `KABARET_JOBS_POOL_NAME` is handled in the project configuration to specify which pools the libreflow jobs session should be use.

### Fixed

* Libreflow jobs session now uses the correct module.

## [1.1.1] - 2024-07-25

### Fixed

* Libreflow extension coming from a git repo did not have the correct name format on the poetry config.

## [1.1.0] - 2024-07-18

### Added

* An advanced mode for power users that can be enabled in the global settings
  * Includes actions for reinstalling or uninstalling a libreflow instance, starting non-gui sessions and shortcuts for debugging.
* User has a new option in the global settings, to show the process view when starting a libreflow instance.
  * This parameter only works if it's not defined in the project configuration. Overseer remote config remains in priority.
* Disabled or archived projects will no longer be loaded. The same applies to those where the user or site is not assigned.
* User can now add a new server from the server list.
* Sites are handled better during the login process. If there is a problem (e.g. undefined or unassigned), a new warning page will be displayed informing the user of the issue.
  * If other sites are assigned to the user, he can select one and try to use it.
* When hovering over a server in the list, there is now a refresh button.
* Project configuration resolve now ensures that all the major dependencies (e.g. kabaret, libreflow) are present.
* Every project flow of Libreflow now can be used.

### Changed

* Poetry path and site name can now be set in the global settings.
  * The environment variable `LF_LAUNCHER_POETRY_PATH` will be used when the user preferences are initialised.
  * The same applies to the `LF_LAUNCHER_SITE_NAME` environment variable. It remains prioritised if the variable is still in use.
* Logging module is now used to harmonise log messages and set levels.
* The virtual environement of a libreflow instance is better checked to ensure the installation is valid and can be used.

### Fixed

* About page
  * Now shows the correct current version.
  * PyPi button redirects to the correct package page.
* Issue #21
  * Buttons for deleting a server in the settings were hidden when updating a libreflow instance.

## [1.0.12] - 2024-06-20

### Added

* Support for a read replica of a redis cluster. You need to set `KABARET_READ_REPLICA_HOST` and `KABARET_READ_REPLICA_PORT` in your project environment variables.

## [1.0.11] - 2024-06-20

### Fixed

* Issue #19
  * All version specifiers of [PEP 440](https://peps.python.org/pep-0440/#version-specifiers) can be used for extensions.

## [1.0.10] - 2024-05-31

### Added

* Handle specific version number for extensions from pypi.

## [1.0.9] - 2024-05-22

### Added

* MacOS support to manage installation and execution of Libreflow instances

## [1.0.8] - 2024-05-16

### Added

* Support project environment variables
* Issue #9
  * Indentation on user settings json files
* Issue #15
  * If the login is an email address, only the username part is kept.

## [1.0.7] - 2024-05-15

### Fixed

* Issue #11
  * Added a exception for `HTTPError` and `RequestException` to avoid crashes when connection or authentification error has occured.
  * Handle recent changes of Overseer API error codes for user token.
  * Current user cache is now cleared when user token is invalid or expired.
* Issue #7
  * Current user is now properly setted when user settings folder do not exist.
* Issue #14
  * Append libreflow extensions with the correct pattern in the environment variable.

* Connection status to a server is updated when hovering a server.

## [1.0.6] - 2024-05-07

### Added

* Shell script to start a Libreflow instance on Linux.

## [1.0.5] - 2024-04-29

### Fixed

* Site name is now correctly defined on libreflow starting script (`bat` or `sh` file)
* Install dir is now correctly used for installing libreflow instance

## [1.0.4] - 2024-04-29

### Added

* An environment variable `LF_LAUNCHER_POETRY_PATH` can be used to define a specific path for poetry.

## [1.0.3] - 2024-04-29

### Fixed

* Host address for a server can now be a domain name instead of a direct IP address.
  * The default port is `5500` if you don't specify it in the wizard.

## [1.0.0-1.0.2] - 2024-04-25

Initial public commit and pypi setup. This is an early version of Libreflow Launcher.
It includes management of Overseer servers, access to projects (instances of Libreflow) that have been assigned to the user, and can be installed locally on the machine by Poetry.

The user interface is likely to change in the future.