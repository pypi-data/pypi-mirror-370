# Libreflow Launcher

Libreflow Launcher is a startup program for instances of [Libreflow](https://gitlab.com/lfs.coop/libreflow/libreflow).

This application communicates with one or more [Overseer](https://gitlab.com/lfs.coop/overseer) servers and gives users access to the projects (libreflow instances) assigned to them.

Each instance is installed locally by [Poetry](https://python-poetry.org/) and with a custom configuration resolved by Overseer according to the project, site and user.

## Requirements

This version has been primarily tested on Python 3.8 and above. And you need an Overseer server to use the launcher.

## Run

>  `python` `-m libreflow_launcher.gui` `--site sitename`

Arguments :

> -m libreflow_launcher.gui : to call up the launcher with its graphical user interface

> --site sitename : use a specific site