"""
Migration runner for applying numbered SQL migrations per backend dialect.

Tracks applied migrations in a schema_migrations table and executes
pending .sql files in order.
"""

import logging
import os
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from getting_started.storage.base import StorageBackend

LOG = logging.getLogger(__name__)

SCHEMA_MIGRATIONS_TABLE = "schema_migrations"


def run_migrations(backend: "StorageBackend", dialect: str) -> None:
    """Apply all pending migrations for the given backend.

    Args:
        backend: An initialized StorageBackend instance (connected, ready).
        dialect: Dialect name ("postgres" or "sqlite").

    Raises:
        FileNotFoundError: If migration files directory not found.
    """
    migrations_dir = Path(__file__).parent / dialect
    if not migrations_dir.exists():
        raise FileNotFoundError(f"Migrations directory not found: {migrations_dir}")

    LOG.info("Running migrations for %s from %s", dialect, migrations_dir)

    migration_files = sorted(migrations_dir.glob("*.sql"))
    if not migration_files:
        LOG.warning("No migration files found in %s", migrations_dir)
        return

    if dialect == "postgres":
        _run_postgres_migrations(backend, migration_files)
    elif dialect == "sqlite":
        _run_sqlite_migrations(backend, migration_files)
    else:
        raise ValueError(f"Unknown dialect: {dialect}")


def _run_postgres_migrations(backend: "StorageBackend", files: list[Path]) -> None:
    """Run migrations against PostgreSQL."""
    import psycopg

    host = os.environ.get("POSTGRES_HOST", "localhost")
    dbname = os.environ.get("POSTGRES_DB", "getting_started")
    user = os.environ.get("POSTGRES_USER", "postgres")
    password = os.environ.get("POSTGRES_PASSWORD", "postgres")

    conn = psycopg.connect(host=host, dbname=dbname, user=user, password=password)
    try:
        with conn.cursor() as cur:
            cur.execute(
                f"""
                CREATE TABLE IF NOT EXISTS {SCHEMA_MIGRATIONS_TABLE} (
                    version TEXT PRIMARY KEY,
                    applied_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                )
            """
            )

            for migration_file in files:
                version = migration_file.stem
                cur.execute(
                    f"SELECT 1 FROM {SCHEMA_MIGRATIONS_TABLE} WHERE version = %s",
                    (version,),
                )
                if cur.fetchone():
                    LOG.debug("Migration %s already applied, skipping", version)
                    continue

                LOG.info("Applying migration: %s", version)
                sql = migration_file.read_text()
                cur.execute(sql)
                cur.execute(
                    f"INSERT INTO {SCHEMA_MIGRATIONS_TABLE} (version) VALUES (%s)",
                    (version,),
                )

        conn.commit()
        LOG.info("All migrations applied successfully")
    finally:
        conn.close()


def _run_sqlite_migrations(backend: "StorageBackend", files: list[Path]) -> None:
    """Run migrations against SQLite."""
    import sqlite3

    from getting_started.storage.sqlite_backend import DEFAULT_DB_PATH

    db_path = os.environ.get("SQLITE_DB_PATH", str(DEFAULT_DB_PATH))
    conn = sqlite3.connect(db_path)
    try:
        cur = conn.cursor()
        cur.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {SCHEMA_MIGRATIONS_TABLE} (
                version TEXT PRIMARY KEY,
                applied_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        for migration_file in files:
            version = migration_file.stem
            cur.execute(
                f"SELECT 1 FROM {SCHEMA_MIGRATIONS_TABLE} WHERE version = ?",
                (version,),
            )
            if cur.fetchone():
                LOG.debug("Migration %s already applied, skipping", version)
                continue

            LOG.info("Applying migration: %s", version)
            sql = migration_file.read_text()
            cur.executescript(sql)
            cur.execute(
                f"INSERT INTO {SCHEMA_MIGRATIONS_TABLE} (version) VALUES (?)",
                (version,),
            )

        conn.commit()
        LOG.info("All migrations applied successfully")
    finally:
        conn.close()
