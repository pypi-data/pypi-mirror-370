# Using The CLI

If you [clone League Manager locally](#installing-from-git) and update the dependencies, you can use the CLI directly without any modifications.

:::{tip}
Make sure to activate your virtual environment
:::

The CLI command for League Manager is `mgr`.

To access the help screen, type in the command as is, or with `--help`.


```shell
# this accesses the help menu
mgr

# this does as well
mgr --help
```

:::{note}
Running this command for the first time will create a directory for database data (`data_league_db`). It will stay empty unless you take the following steps.
:::

(initializing-database)=
## Initializing The Database

Before getting started, you will want to set up your database. League Manager has sqlite support out of the box, and incorporates [Alembic commands](https://alembic.sqlalchemy.org/en/latest/api/commands.html) straight from [Advanced Alchemy](https://docs.advanced-alchemy.litestar.dev/latest/).

You _can_ set a couple of environment variables if you wish to customize where the database file is located, as well as to where the Alembic-related files are created.

However, the CLI will work out of the box with sensible defaults.

The default database used is `sqlite`, and it creates a data directory within your project root called `data_league_db`. The name of the database is `lmgr_data.db`

:::{tip}
:class: dropdown

Because Alembic is used for migrations, the _migration environment_ is needed for proper database management. This typically includes an `alembic.ini` file, a `migrations` directory, an `env.py` file, and so on. This is all managed for you under the hood, but you _can_ configure these yourself if you want to customize it.
:::

All the Alembic commands, managed through Advanced Alchemy, are contained within the `db` subgroup. You can get a list of all those commands by typing:

```shell
mgr db
```
And you should see something like this:

```text
Commands
show-current-revision   Shows the current revision for the database.
downgrade               Downgrade database to a specific revision.
upgrade                 Upgrade database to a specific revision.
stamp                   Stamp the revision table with the given revision
init                    Initialize migrations for the project
make-migrations         Create a new migration revision.
drop-all                Drop all tables from the database.
dump-data               Dump specified tables from the database to JSON files.
```

***

Now, to fire up your database, you will need to type the following commands:

```shell
# Equates to `alembic init` command.
# By default, creates a "migrations" directory.
mgr db init

# Builds migration files into the new directory.
# Run this command after making changes to models.
mgr db make-migrations

# Writes the League Manager tables to the database
# Run after `make-migrations` for changes to take effect
mgr db upgrade
```

This sequence of commands will get your database ready to go. Again, they mimic the commands you would ordinarily use with Alembic, but you have no need to install or run Alembic independently (though you can do that too if you wish).

When running the `init` command, you will be asked to confirm if you want to initialize the project in a default `migrations` directory. Select `y` for yes.

You will also be asked to enter a message when running the `make-migrations` command. It typically describes what the migration is for. In this case, you can type something like "add tables" or "initialize database."



:::{tip}
You only run the `init` command once when setting up the database (or if you want to _nuke_ everything and start over). Ordinarily, you will only need to run `make-migrations` when your table schema changes (i.e., updates to your models), and `upgrade` for the changes to be applied.
:::

Lastly, after typing the `upgrade` command, you will be asked to confirm if you want to apply the migrations. Select `y` for yes.

After these three commands, your database is ready!

(populating-data)=
## Populating Data

Although the tables are set up for you, they currently hold no data.

League Manager comes with a small set of synthetic data (in raw json) that can be used to populate the database. (This is a League Manager command, so no need to include the `db` subgroup command):

```shell
# Populate the database with synthetic data
mgr populate
```

```text
✨ Successfully created data! ✨
Created 3 Seasons
Created 3 Leagues
Created 10 Teams
Created 1 Organization
```

If you want to make sure that the tables have been created:

```shell
# Check the "count" of how many rows of data in each table
mgr check --all
```
```text
✨ These are the counts of data in each table ✨
3 Seasons
3 Leagues
10 Teams
1 Organization
```

And lastly, if you want to delete the synthetic data:

```shell
# Delete all the things
mgr delete --all
```

```text
⛔ Removed all Seasons, Leagues, Teams, and Organizations.⛔
```
