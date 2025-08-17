(set-up-your-environment)=
# Set Up Your Environment

To begin using League Manager, you will need to have a current version of Python installed (Python 3.12 is recommended).

:::{hint}
If you're already comfortable with basic Python setup, you can skip to the next page.
:::

(install-python)=
## Install Python

:::{note}
This tutorial assumes some basic knowledge of using Python, but here are a few items to get started.
:::

There are several ways to install Python on your system (and some systems come with Python installed).

For this tutorial, I recommend installing Python directly from [python.org](https://www.python.org). (If it is not already installed.)

Go to their [latest release page](https://www.python.org/downloads/latest/) and download the version for your system.

(create-project-directory)=
## Create A Project Directory

Open up your terminal and  create a project.

```shell
# create a new directory
mkdir new-project

# change into that directory
cd new-project
```
(using-virtual-environment)=
## Using A Virtual Environment

```shell
python -m venv .venv
```

:::{hint}
-   `python` uses the currently active Python interpreter
-   `-m` refers to a module that contains a script
-   `venv` is the name of the module installed with Python
-   `.venv` is name of the virtual environment we create in this directory
:::

Once you have create the virtual environment (a `.venv` in your `new-project` directory), you need to activate it:

```powershell
# on Linux/macOS
source .venv/bin/activate

# on Windows
.venv\Scripts\Activate.ps1
```

To install packages, you can do this directly in your terminal by using the `pip` command. Before using it, update it to the latest version.

```shell
python -m pip install --upgrade pip
```

(install-league-manager)=
## Install League Manager

Now you can install League Manager from PyPI (a packaging index) by running the following command:

```shell
python -m pip install leaguemanager
```
(ready-to-go)=
## Ready To Go

This should more or less get you ready to start building a League Manager project.

:::{seealso}
If you are curious as to what all these things mean, the popular web framework [FastAPI](https://fastapi.tiangolo.com) has a [great writeup on these steps and what they do](https://fastapi.tiangolo.com/virtual-environments/).
:::
