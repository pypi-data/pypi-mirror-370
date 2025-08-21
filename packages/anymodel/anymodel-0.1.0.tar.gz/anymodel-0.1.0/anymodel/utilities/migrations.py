"""Database migration utilities.

This module provides utilities for automatic database schema migrations
using Alembic.
"""


def automigrate(engine, metadata):
    """Automatically migrate database schema to match metadata.

    Detects differences between the current database schema and the
    provided metadata, then applies the necessary migrations.

    Args:
        engine: SQLAlchemy engine connected to the database
        metadata: SQLAlchemy metadata describing the desired schema

    See: https://alembic.sqlalchemy.org/en/latest/cookbook.html#run-alembic-operation-objects-directly-as-in-from-autogenerate
    """
    from alembic.autogenerate import produce_migrations
    from alembic.migration import MigrationContext
    from alembic.operations import Operations
    from alembic.operations.ops import ModifyTableOps

    with engine.connect() as connection:
        context = MigrationContext.configure(connection)
        migrations = produce_migrations(context, metadata)
        operations = Operations(context)

        if not len(migrations.upgrade_ops.ops):
            # No database schema changes detected
            return

        stack = [migrations.upgrade_ops]
        use_batch = engine.name == "sqlite"
        while stack:
            elem = stack.pop(0)

            if use_batch and isinstance(elem, ModifyTableOps):
                with operations.batch_alter_table(elem.table_name, schema=elem.schema) as batch_ops:
                    for table_elem in elem.ops:
                        batch_ops.invoke(table_elem)

            elif hasattr(elem, "ops"):
                stack.extend(elem.ops)
            else:
                operations.invoke(elem)
        connection.commit()
