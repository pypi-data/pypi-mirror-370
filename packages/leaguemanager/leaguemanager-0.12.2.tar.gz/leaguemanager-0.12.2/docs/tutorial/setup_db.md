(create-database)=
# Create the Database

Your web application is ready to grow, but first, set up your database so that you have something to interact with.

:::{note}
League Manager comes with some sensible defaults for database management. It uses a [SQLite](https://www.sqlite.org/index.html) database engine, storing data locally in a database file.

Further customizations will be covered in a future, advanced guide.
:::

In your terminal, within the `new-project` directory, use the following command:

```shell
mgr db init
```

This will attempt to create files and directories necessary for your database management (a process called _migrations_).

You should see this prompt:

```text
Are you sure you want initialize migrations for the project? [y/n]:
```
Type `y` and press Enter.

You'll see output letting you know that a few files and directories have been created (referred to as your _migration environment_).

Next, type the following command:

```shell
mgr db make-migrations
```

After running this command, you will get another prompt:

```text
Please enter a message describing this revision:
```

This message is intended to describe what this migration is for. It can be anything you like.

Since you're just getting started, you can type something like "create database tables."

After pressing Enter, you should see a message that confirms all the tables that have been detected.

The command's purpose is to look for the Python models (representing database tables) that have been designed within League Manager, and then to create a _migration file_.

:::{note}
These database commands are a wrapper for common [Alembic](https://alembic.sqlalchemy.org/en/latest/index.html) operations. As you get started, you don't have to worry too much as to what is going on "under the hood."
:::

Lastly, with your _migration file_ in place, you can now run a command that will create the SQLite database tables that were previously detected.

They won't have any data populated in them, but you will now be able to interact with them using League Manager.

```shell
mgr db upgrade
```

This will prompt you with the following message:

```text
Are you sure you want migrate the database to the `head` revision? [y/n]:
```

Type `y` and press Enter.

You should see a message that looks similar to this:

```text
Context impl SQLiteImpl.
Will assume non-transactional DDL.
Running upgrade  -> 86ddfaef179b, create database tables
```

This lets you know that the command was successful.
