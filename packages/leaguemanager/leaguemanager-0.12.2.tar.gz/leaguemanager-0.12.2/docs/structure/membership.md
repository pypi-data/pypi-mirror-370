(membership)=
# Membership

Membership is the third concept encompassing the baseline structure of League Manager.

As seen in the diagram below, this is how individuals are affiliated within their separate entities.

```{image} ../img/basic_competition_participation_membership_wb.png
:alt: League Manager schema showing Competition, Participation, and Membership concepts
:class: bg-primary
:align: center
```

While individual entities (like Team, Athlete, Manager) can be affiliated to a specific event through the Participation objects (i.e., TeamStats, AthleteStats, Managing), they are also linked to a Membership object.

The Membership object makes it so that _individuals_ can be linked to separate entities at the same time, or to establish start and end dates of belonging.

You can see how this is applied below.

# Athlete, Team, Official, Manager

Each of these entities is self-descriptive. These objecs can have Memberships (as seen below), or can be attached to a Participation object (as seen in the previous section). In this way, for example, a single Athlete _could_ have a _membership_ to a different team.

## ManagerMembership

The ManagerMembership has a relationship to a Team object, as well as a Manager object. This membership object can optionally contain start and end dates to dictate a specific point in time in which a manager may have been active with the Team.

This structure allows an individual Manager object to be associated with more than one team at a time, and could contain different roles for different teams (i.e., head coach for one team, assistant for another).

## TeamMembership

An individual Team _could_ be allowed to play in different Seasons at the same time. For example, let's say a League has an open-age division for one Season, and an over-30 division for another Season.

If a Team is eligible for both of those Seasons, they could have separate TeamMembership object attached to each of those Seasons, and that would be used for scheduling and tracking Fixtures.

## IndividualMembership

Similar to Managers (and probably even more so), Athletes might belong to separate Teams across different Leagues and/or Seasons, meaning that they would have separate IndividualMembership objects to track their affiliation to those Teams.

It could track involvement dates, eligibility, or even something like a specific uniform number for that team.
