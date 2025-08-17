# League Manager

<img src="https://codeberg.org/attachments/ee21b5d5-73b4-4f16-84be-c1c70f414ec3" width="250px">

## Table of Contents

- [About](#about)
    - [Background](#background)
- [Getting Started](#getting_started)
    - [Installing From git](#installing_from_git)
    - [Installing Dependencies](#installing_dependencies)
    - [Installing From pip](#installing_from_pip)
- [CLI Usage](#usage)
    - [Initializing The Database](initializing_database)
- [What Next](#what_next)
- [Contributing](#contributing)


## About 📚 <a name = "about"></a>

**League Manager** allows you to create and manage seasons, leagues, teams, players, and more.

First, define a season that establish when the competition will begin. Next, create one or more leagues (and corresponding teams) to attach to that season.

Then you will be able to auto-generate a weekly schedule based on the number of fixtures/matches within that season.

You can also create one-off fixtures/matches on the schedule. Track results and auto-update a standings table.

### Background 🔍 <a name = "background"></a>

League Manager is built around [Advanced Alchemy](https://docs.advanced-alchemy.litestar.dev/latest/), which itself is a companion library for [SQLAlchemy](https://www.sqlalchemy.org) and [Alembic](https://alembic.sqlalchemy.org/en/latest/).

In also uses the awesome [svcs library](https://svcs.hynek.me/en/stable/) as a way of managing the database services and serving them up as needed, eliminating much of the boilerplate you would have to do on your own.

As such, League Manager is designed to ease the hurdle of setting up database models, migrations, and a multitude of operations/features common to many CRUD applications.


## Getting Started 🚀 <a name = "getting_started"></a>

Keep in mind that League Manager is a work in progress, and some of these instructions might change.

However, you are welcome to check out the license and [contribution guide](https://codeberg.org/pythonbynight/leaguemanager/src/branch/main/CONTRIBUTING.md).

### Installing From git 💻 <a name = "install_from_git"></a>

If you want to work on League Manager or contribute to the project, you can install from the git repository:

```sh
git clone https://git@codeburg.com:pythonbynight/leaguemanager
cd leaguemanager
```


### Installing Dependencies 📦 <a name = "installing_dependencies"></a>

Next, you will need to install the dependencies, and `leaguemanager` itself. I recommend using `uv` for dependency management.

You should be able to download `uv` using a curl command:

```sh
curl -LsSf https://astral.sh/uv/install.sh | sh
```
If you previously installed `uv`, you can upgrade to the latest version.

```sh
uv self update
```

Once `uv` is installed, you can install the project dependencies.

```sh
uv sync
```

This should create a virtual environment and install all the project dependencies.

### Installing From pip 📈 <a name = "installing_from_pip"></a>

If, instead, you want to _use_ League Manager as a dependency for your own project, you can also install the package via pip.

I would recommend starting a new project and creating/activating a virtual environment first.

```sh
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

> Note: You can also use `uv` to install from the repository. The command is:
>
> `uv add leaguemanager`

This allows you to incorporate League Manager into your own application. The CLI can still be used as shown below. You also have access to existing database features and commands (migrations/operations/etc...).

## CLI Usage 🖥️ <a name = "cli_usage"></a>

The CLI command for League Manager is `mgr`

To access the help screen, type in the command as is, or with `--help`

> Note: If you have intstalled `leaguemanager` as a dependency to your project, make sure to create a .py file in your new project, or the CLI command might fail.

```sh
# this accesses the help menu
mgr

# this does as well
mgr --help
```

> Note: Running this command for the first time will create a directory for database data (`data_league_db`). It will stay empty unless you take the following steps.

### Initializing The Database 🔄 <a name = "initializing_database">

Before getting started, you will want to set up your database. League Manager has sqlite support out of the box, and incorporates [Alembic commands](https://alembic.sqlalchemy.org/en/latest/api/commands.html) straight from [Advanced Alchemy](https://docs.advanced-alchemy.litestar.dev/latest/).

You _can_ set a couple of environment variables if you wish to customize where the database file is located, as well as to where the Alembic-related files are created.

However, the CLI will work out of the box with sensible defaults.

All the Alembic commands, managed through Advanced Alchemy, are contained within the `db` subgroup. You can get a list of all those commands by typing:

```sh
mgr db
```

To fire up your database, you will need to type the following commands:

```sh
# This equates to `alembic init` command.
# It creates a "migrations" directory.
# You only need to do this once.
mgr db init migrations

# This builds migration files into the new directory.
# Run this command after making changes to models.
mgr db make-migrations

# This command writes the League Manager tables to the database
# Always run this command after `make-migrations`
mgr db upgrade
```

This sequence of commands will get your database ready to go. Again, they mimic the commands you would ordinarily use with Alembic, but you have no need to install or run Alembic independently (though you can do that too if you wish).

Lastly, although the tables are set up for you, they currently hold no data.

League Manager comes with a small set of synthetic data (in raw json) that can be used to populate the database. (This is a League Manager command, so no need to include the `db` subgroup command):

```sh
# Populate the database with synthetic data
mgr populate
```

If you want to make sure that the tables have been created:

```sh
# Check the "count" of how many rows of data in each table
mgr check --all
```

And lastly, if you want to delete the synthetic data:

```sh
# Delete all the things
mgr delete --all
```

If you actually want to _drop the tables_ from the database, you can once agan refer to the Advanced Alchemy command group (prefaced with `db`) like so:

```sh
mgr db drop-all
```

## What Next 🤔 <a name = "what_next"></a>

League Manager comes with several models, currently skewed toward running _soccer_ leagues, but it can still work with other sports/genres, specifically to generate round-robin style schedules and fixtures/matches.

Under the hood, the library utilizes the [svcs library](https://svcs.hynek.me/en/stable/) to serve up a database session, as well as preconfigured database services offering easy-to-use, preconfigured CRUD operations on each of the provided models.

More documentation on that process will follow. But in short, if you want to access the services:

```python
from leaguemanager import LeagueManager
from leaguemanager.services import SeasonSyncService, TeamSyncService

registry = LeagueManager()
season_service = registry.provide_db_service(SeasonSyncService)
team_service = registry.provide_db_service(TeamSyncService)

# This will return the number of seasons saved in the database
number_of_seasons = season_service.count()

# This will return a list of `Season` objects (models)
seasons = season_service.list()

# Total number of teams in the database
number_of_teams = team_service.count()

# You get the idea
teams = team_service.list()

# Print all the team names
for team in teams:
    print(team.name)
```

The `provide_db_service` is able to look at the `type` of service passed in, and now you have access to many typical CRUD operations and filters for that specific table. Some of the services also include additional business logic specific to League Manager applications.

If you only need the database session (a SQLAlchemy `Session` type) to do your own custom logic using SQLAlchemy, you can also use the registry.

```py
# Using the db session directly

session = registry.provide_db_session

session.execute(delete(SomeModel))
```


## Contributing 🤝 <a name = "contributing"></a>

Hey, you made it down to here! Do you like what you see? Think you can help a bit?

If you would like to contribute, please refer to the [contribution guide](https://codeberg.org/pythonbynight/leaguemanager/src/branch/main/CONTRIBUTING.md) for details on how to help.
