# Incorporating With Your App

You can also install League Manager as a [dependency](#installing-from-pip) for your project. This allows you to incorporate the League Manager backend into your own application.

:::{warning}
The League Manager backend (database schema) is based loosely on the [IPTC Sports Schema](https://sportschema.org) model, which is designed to describe core elements of competitive sport. For League Manager, it has been adapted to fit typical needs of managing sports and/or other competitive leagues. Further customizations per sport are possible, but documentation is not yet available.

However, the baseline models can be adapted into _most_ competitions. If you have questions on usage, feel free to [leave an issue](https://codeberg.org/issues).
:::

## Accessing Services

Under the hood, League Manager utilizes the [svcs library](https://svcs.hynek.me/en/stable/) to serve up a database session, as well as database services offering easy-to-use, preconfigured CRUD operations on each of the provided models.

The really cool part here ✨ is the inclusion of autocomplete. Once you have retrieved your required service, your IDE will assist you with all the prebuilt database operations.

(You can also look at [Advanced Alchemy's documentation](https://docs.advanced-alchemy.litestar.dev/latest/reference/service.html#advanced_alchemy.service.SQLAlchemySyncRepositoryService) for an idea of what's included.)

Here is an example of how to access those services directly:

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

The `provide_db_service` is able to look at the `type` of service passed in (in this case, both `SeasonSyncService` and `TeamSyncService`), and now you have access to many typical CRUD operations and filters for that specific table.

Some of the services also include additional business logic specific to League Manager applications.

If you only need the database session (a SQLAlchemy `Session` type) to do your own custom logic using SQLAlchemy, you can also use the registry.

```python
# Using the db session directly

session = registry.provide_db_session
session.execute(delete(SomeModel))
```

### Extra

The variable names used above are for illustration. It may be a little more ergonomic to use shorter ones. 😎

```python
from leaguemanager import LeagueManager
from leaguemanager.services import SeasonSyncService, TeamSyncService

lm = LeagueManager()
season_db = lm.provide_db_service(SeasonSyncService)
team_db = lm.provide_db_service(TeamSyncService)

seasons = season_db.list()
```

For the most part, the documentation will generally offer the more verbose naming scheme in order to illustrate what is going on under the hood.
