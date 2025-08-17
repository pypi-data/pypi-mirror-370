(participation)=
# Participation

Participation refers to the actions that can be associated specifically to a given Fixture.

These objects are where you can find the scores and stats for a competitive event.

```{image} ../img/basic_competition_participation_wb.png
:alt: League Manager schema showing Competition and Participation concepts
:class: bg-primary
:align: center
```

You'll notice that a Team or Athlete is not linked directly to a Fixture object. Instead, there exists a layer of Participation objects.

This makes it possible for an Athlete (or Team) to compete in different events or fixtures. These objects are where all scores and statistics are attached, making them query-able by any specific Fixture.

## Managing

The Managing object captures the participation of a Manager (whether a single coach, or a coaching staff, that could include assistant coaches and/or other coaching roles).

An object like this could be used to track actions taken by a Manager during a Fixture, or infractions earned.

## Officiating

The Officiating object captures the participation of an Official (or a team of officials and/or referees). This object serves as a way to track which officials have been assigned to any given Fixture throughout the Leagues/Seasons.

## TeamStats

This is likely the most prominent of the Participation objects, as it is where scores and stats are expressed for a single Team.

This includes the outcome of the competition (i.e., win, loss, tie), the points scored for and against, as well as how many points are added, kept, or removed in the standings based on the result.

## AthleteStats

In addition, League Manager also allows stats tracking for individual Athletes. Since the default tables are meant to encompass many different sports or activities, this table tracks general statistics, such as points scored, saves, cautions, and ejections.
