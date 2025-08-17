from __future__ import annotations

from sqlalchemy import Column, ForeignKey, Table

from leaguemanager.models.base import metadata

group_tag = Table(
    "group_tag",
    metadata,
    Column("group_id", ForeignKey("group.id", ondelete="CASCADE"), primary_key=True),  # pyright: ignore
    Column("tag_id", ForeignKey("tag.id", ondelete="CASCADE"), primary_key=True),  # pyright: ignore
)
