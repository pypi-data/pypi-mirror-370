(interacting-with-db)=
# Interacting With the Database

At this point in time, you have a database with pre-made tables that are ready to be used. But empty tables are boring!

(populate-tables-fake-data)=
## Populate Tables With Fake Data

They are empty until you fill them with _something_.

For now, go ahead and populate some of the tables with _synthetic data_ (fake stuff) so that you can interact with it through your web app.

Make sure you are in the `new-project` directory and type the following command:

```shell
mgr populate
```

You should see a confirmation message like this:

```text
✨ Successfully created data! ✨
3 Seasons
3 Leagues
10 Teams
1 Organization
```

(league-manager-object)=
## The `LeagueManager` Object

In order to interact with the data, your web application will need to create a `LeagueManager` object.

This object contains a _registry_ of all the "services" you can perform on the database objects. In other words, each table in your database has a Python _model_ representing the table. In addition, each table has its own "service" that handles all operations on that particular table.

:::{tip}
:class: dropdown
In addition, each model has its own "repository" as well. Most of the functionality between a "repository" and a "service" is the same, with some minor differences. See the [Advanced Alchemy documentation](https://docs.advanced-alchemy.litestar.dev/latest/usage/repositories.html) for clarification.
:::

(models-services)=
## Models and Services

In the database, there is a `season` table with a corresponding `Season` model.

A simplified version of the database table looks something like this:

|id|name|description|active|start_date|end_date|
|-|-|-|-|-|-|
||||||

The corresponding League Manager model looks something like this:

```python
@define(slots=False)
class Season(UUIDAuditBase):
    """A season defines an overall period of time in which
    a league or leagues are active.
    """

    organization_id: str | None = field(default=None)
    name: str | None = field(default=None, validator=validators.max_len(80))
    description: str | None = field(default=None, validator=validators.optional(validators.max_len(120)))
    active: bool = field(default=True)
    projected_start_date: str | None = field(default=None)
    projected_end_date: str | None = field(default=None)
    actual_start_date: datetime | None = field(default=None)
    actual_end_date: datetime | None = field(default=None)
```

And as explained above, there is a `SeasonSyncService` (service for short) that defines all the operations we can perform on the `season` table, by utilizing the `Season` model.

To recap:
-   The `LeagueManager` object provides access to "services" that define operations on database tables
-   There is a specific "service" that corresponds to the specific database table (i.e., `SeasonSyncService`)
-   The "service" uses a Python model that is linked to the database table (i.e., `Season`)

Because all the operations to a specific table are contained within the service, you rarely will have to refer to the model directly.

(using-leaguemanager-in-app)=
## Using `LeagueManager` In Your App

Now that you have two seasons created in the database (_synthetic data_!), you can interact with the data with League Manager`s corresponding service.


```python
from leaguemanager import LeagueManager
from leaguemanager.services import SeasonSyncService
from litestar import Litestar, get

lm = LeagueManager()
season_service = lm.provide_db_service(SeasonSyncService)

seasons = season_service.list()

@get("/")
async def hello_world() -> str:
    return f"There are {len(seasons)} seasons in the database!"

app = Litestar([hello_world])
```

While in the `new-project` directory in the terminal, type:

```shell
litestar run --reload
```
:::{tip}
The `--reload` flag refreshes the server every time you save a change to your Python files. Instead of having to stop and restart the server, you can just refresh your browser to see any changes you've made.
:::

This should show up like this on your browser:

```text
There are 2 seasons in the database!
```

If you want to see a more detail, Litestar can turn your `Season` object into a dictionary.

Change the return type of the `hello_world` route to `dict` and return the first object in `seasons`:

```python
from leaguemanager import LeagueManager
from leaguemanager.services import SeasonSyncService
from litestar import Litestar, get

lm = LeagueManager()
season_service = lm.provide_db_service(SeasonSyncService)

seasons = season_service.list()

@get("/")
async def hello_world() -> dict:
    return seasons[0]

app = Litestar([hello_world])
```
Refresh your browser, and you should see something like this:

```text
{
  "description": "For all leagues participating in the Spring Season 2025",
  "projected_start_date": "2025-04-06",
  "created_at": "2025-01-30T07:43:52.853379",
  "id": "e0622643-2e7a-4f3e-bbd6-0b7f286a8f74",
  "name": "Spring Season 2025 - Sundays",
  "active": true,
  "projected_end_date": null,
  "updated_at": "2025-01-30T07:43:52.853393",
  "leagues": []
}
```

:::{note}
Your browser may render this as one line, but the data should be similar to this.
:::

This should give you an idea of how to access the League Manager services and interact with them from within your app.

You can see what services are included by looking at the API documentation, but a more in depth tutorial will be written in the future.
