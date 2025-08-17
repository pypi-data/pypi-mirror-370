(getting-started)=
# Getting Started

Keep in mind that League Manager is a work in progress, and some of these instructions might change.

However, you are welcome to check out the [license](project:../license.md) and [contribution guide](project:../contrib.md).

(installing-from-git)=
## Installing From git

If you want to work on League Manager or contribute to the project, you can install from the git repository:

```shell
git clone https://git@codeburg.com:pythonbynight/leaguemanager
cd leaguemanager
```
(updating-dependencies)=
### Updating Dependencies

Next, you will need to install the dependencies, and `leaguemanager` itself. I recommend using `uv` for dependency management.

You should be able to download `uv` using a curl command:

```shell
curl -LsSf https://astral.sh/uv/install.sh | sh
```
If you previously installed `uv`, you can upgrade to the latest version.

```shell
uv self update
```

Once `uv` is installed, you can install the project dependencies.

```shell
uv sync
```

This should create a virtual environment and install all the project dependencies.

(installing-from-pip)=
## Installing From pip

If, instead, you want to _use_ League Manager as a dependency for your own project, you can also install the package via pip.

I would recommend starting a new project and creating/activating a virtual environment first.

```shell
# Create a new project and virtual environment

mkdir my-project
cd my-project
python -m venv .venv

# On Linux/MacOS
source .venv/bin/activate

# Or Windows
.venv/Scripts/activate
```

Then install with pip:

```shell
python -m pip install leaguemanager
```

:::{note}
You can also use `uv` to install from the repository. The corresponding command is:

`uv add leaguemanager`
:::

This allows you to incorporate League Manager into your own application. The CLI can still be used as shown in the next page. You also have access to existing database features and commands (migrations/operations/etc...).
