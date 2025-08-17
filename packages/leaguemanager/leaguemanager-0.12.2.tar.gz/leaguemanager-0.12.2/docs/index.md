---
sd_hide_title: true
---

# Overview

```{rubric} League Manager
:heading-level: 1
```

**League Manager** is a python package for running a League or Leagues. You can manage Seasons, Schedules, Teams, and more.

Install it locally and use the included CLI tool for streamlined database management.

```{image} ./img/demo.gif
:alt: leaguemanager cli
:class: bg-primary
:align: center
```

Or install it as a dependency for your own application and use the tightly coupled services for a robust League management backend.

````{div} sd-d-flex-row
```{button-ref} documentation/installing
:ref-type: doc
:color: primary
:class: sd-rounded-pill sd-mr-3

Get Started
```
````

***

```{rubric} Overview
:heading-level: 2
```
Define one or more Seasons to establish when competitions will begin, and then create one or more Leagues to attach to a Season. You can then create Teams that will compete in each League.

Based on a few options (such as how many games per season, or how many concurrent games are played per matchday), you will then be able to auto-generate a weekly Schedule based on the number of Fixtures (or matches) within that season.

You can also create one-off Fixtures on the Schedule. Track results and auto-update a Standings table.



```{toctree}
:hidden:
:caption: Documentation
:maxdepth: 2
documentation/installing.md
documentation/using_cli.md
documentation/using_with_app.md
```

```{toctree}
:caption: Tutorial
:hidden:
:maxdepth: 3
tutorial/overview.md
tutorial/environment.md
tutorial/web_framework.md
tutorial/setup_db.md
tutorial/interact_with_db.md
```

```{toctree}
:caption: Concepts
:hidden:
:maxdepth: 3
structure/db_structure.md
structure/competition.md
structure/participation.md
structure/membership.md
```

```{toctree}
:hidden:
:caption: Reference
:maxdepth: 1
apidocs/index.rst
```


```{toctree}
:hidden:
:caption: Contributing
:maxdepth: 2

contrib
license
```
