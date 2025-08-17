from sqlalchemy import Column, Index, String, Table, UniqueConstraint


def add_slug_column(table: Table, tablename: str | None = None) -> Table:
    """Add a unique, indexed 'slug' column to a Table."""
    slug = Column("slug", String(100), nullable=True, unique=True)
    table.append_column(slug)
    tablename = tablename or table.name
    table.append_constraint(UniqueConstraint("slug", name=f"uq_{tablename}_slug"))
    Index(f"ix_{tablename}_slug_unique", table.c.slug, unique=True)
    return table
