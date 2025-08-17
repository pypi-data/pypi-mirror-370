(database-structure)=
# Database Structure

League Manager comes with pre-defined database models that can be used in most instances for a variety of sports competitions. It supports tracking of one or multiple leagues, each with their own corresponding seasons.

The database structure is based loosely on the existing [IPTC Sport Schema](https://sportschema.org). While that spec is meant to be extremely comprehensive and exhaustive, League Manager has borrowed some principles from its ontology, which allows it to be flexible for a wide range of different activities.

(basic-concepts)=
## Basic Concepts

The relationships between database tables can be broken down into three concepts.

- Competition
- Participation
- Membership

Once you get familiar with these concepts, it will become easier to work with the data once you are building your league.
