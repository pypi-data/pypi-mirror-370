(competition)=
# Competition

The first of these concepts, Competition, can be understood as any data that relates to the _properties_ of the competition itself. These can be considered a series of events which culminate in a competitive goal (winning a league, championship, or tournament).

As mentioned, this paradigm is borrowed from the IPTC Sport Schema Ontology, but the model names have been modified to better fit the structure of many competitive leagues.

Bellow is a basic schema diagram with the model names used within League Manager to represent facets of the Competition.

```{image} ../img/basic_competition_wb.png
:alt: League Manager Competition schema showing Competition concept
:class: bg-primary
:align: center
```

(organization)=
## Organization

At the top level of each instance of League Manager, there should be an Organization. This will typically be an individual, group, or (you guessed it) organization responsible for running the league or leagues.

This Organization can be associated to a Site, which can optionally contain an address and contact information.

(league)=
## League

What would League Manager be without the concept of a _League_? In this context, it represents a top level "competition" that could span several seasons. (It's usually a recurring competition, but can also be configured as a one-time tournament.)

For example, an Organization might run a year round Youth Soccer League, with Spring, Summer, and Winter seasons. Or, an Organization might run _multiple_ youth leagues, each with their own set Seasons. How you set up your structure is up to you.

(season)=
## Season

As mentioned above, a single League can have multiple Seasons. A Season is a type of "competition" that has a defined beginning and end, and expects there to be a winner at the end.

(phase)=
## Phase

Each Season will have a specific "phase" on any give day of play. This can sometimes be thought of as a "Match Day" or "Game Week", depending on how the League is structured.

It could also represent specific phases in a _tournament_ type of setting, for example "Quarterfinals" or "Semifinals."

(fixture)=
## Fixture

A Fixture represents a specific _event_ within a competition. This is considered the _smallest_ occurrence of a competition that has a winner.

A Fixture typically has a time and date for the event, which itself can be linked to a Site (especially if it is different than the one linked to the Organization itself). It also defines who will be competing in the event.

A single Phase can have multiple Fixtures.
