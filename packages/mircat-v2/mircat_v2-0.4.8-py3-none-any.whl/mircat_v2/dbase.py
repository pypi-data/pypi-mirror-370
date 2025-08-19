import json
import sqlite3
from pathlib import Path

from loguru import logger
from mircat_v2.configs import write_config, dbase_schema_file


def add_dbase_subparser(subparsers):
    # Add subcommands
    dbase_parser = subparsers.add_parser(
        "dbase",
        help="Database management commands",
        description="mircat-v2 database management commands.",
    )
    dbase_subparsers = dbase_parser.add_subparsers(
        dest="dbase_command", description="Database operations:"
    )

    # Add subcommand for creating a new database
    create_parser = dbase_subparsers.add_parser("create", help="Create a new database")
    create_parser.add_argument(
        "dbase_path",
        type=Path,
        help="Path to the database file",
    )
    create_parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite the database if it already exists",
    )

    set_parser = dbase_subparsers.add_parser(
        "set", help="Set an existing sqlite database file to be used in mircat-v2"
    )
    set_parser.add_argument(
        "dbase_path", type=Path, help="Path to the existing database file."
    )
    dbase_subparsers.add_parser(
        "update", help="Update the database schema to the newest version."
    )

    # add subcommand for querying the database
    query_parser = dbase_subparsers.add_parser("query", help="Query the database")
    query_parser.add_argument(
        "query",
        type=str,
        help="SQL query to execute",
    )


def run_dbase_command(args) -> None:
    """Run the appropriate function depending on the given dbase command
    Parameters:
        args: The arguments passed to the CLI
    """
    match args.dbase_command:
        case "create":
            create_database(args.dbase_path, args.overwrite)
        case "set":
            set_database(args.dbase_path)
        case "update":
            logger.error("update command not functional yet")
        case "query":
            logger.error("query command not functional yet.")


def create_database(dbase_path: Path, overwrite: bool = False) -> None:
    """
    Create a new SQLite database at the specified path.

    Parameters:
        dbase_path (Path): Path to the database file.
        overwrite (bool): If True, overwrite the database if it already exists.
    """
    # Raise an error if the database exists and we don't want to overwrite
    if dbase_path.exists() and not overwrite:
        raise FileExistsError(
            f"Database file {dbase_path} already exists. Use `mircat-v2 dbase set` to use it or `--overwrite` to completely overwrite."
        )
    # Confirm that you want to delete the previous database
    elif dbase_path.exists() and overwrite:
        response = input(
            "Are you sure you want to overwrite the existing database? This will not copy data to the new one. (y/n): "
        )
        if response.lower() != "y":
            logger.info(f"Left existing database at {dbase_path} intact.")
            return
        logger.info(f"Overwriting existing database at {dbase_path}")
        dbase_path.unlink()
    # Create the database
    with sqlite3.connect(dbase_path) as conn:
        create_tables_from_schema(conn)
    logger.success(f"Database created at {dbase_path}")
    conn.close()
    save_dbase_path(dbase_path)


def set_database(dbase_path: Path) -> None:
    """Set the database at the given path to be used for database operations"""
    if not dbase_path.exists():
        raise FileNotFoundError(
            f"The sqlite database at {dbase_path} was not found. If you want to create one here, please use `mircat-v2 dbase create {dbase_path}`"
        )
    # The sql create script only makes tables if they do not exist - so it's safe to run this
    with sqlite3.connect(dbase_path) as conn:
        create_tables_from_schema(conn)
    conn.close()
    save_dbase_path(dbase_path)
    logger.success("Set {} as the database for mircat-v2.", dbase_path)


# TODO - write the update option using the default dbase schema that we store to the config.
def save_dbase_path(dbase_path: Path) -> None:
    dbase_config = str(dbase_path.resolve())
    write_config(dbase_config, "dbase", "dbase_path")


def create_tables_from_schema(conn: sqlite3.Connection) -> None:
    cursor = conn.cursor()
    # Run the creation script
    with dbase_schema_file.open("r") as f:
        schema_script = f.read()
    cursor.executescript(schema_script)
    conn.commit()


def insert_data_batch(dbase_config: dict, table: str, data_records: list[dict]):
    """Insert a batch of data into the database for a specific table."""
    if not data_records:
        return
    dbase_path = Path(dbase_config["dbase_path"])
    conn = sqlite3.connect(dbase_path)
    cursor = conn.cursor()
    try:
        # Get the columns that exist in the table
        table_schema = dbase_config["tables"].get(table)
        if not table_schema:
            raise ValueError(
                f"Table {table} does not exist in the standard MirCAT database schema."
            )
        # Check if the table exists
        cursor.execute(
            f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'"
        )
        if not cursor.fetchone():
            logger.info(f"Table {table} does not exist. Creating it.")
            create_tables_from_schema(conn)
            logger.info(f"Table {table} created successfully.")
        table_columns = list(table_schema.keys())

        # Process each record in the batch
        insert_data = []
        for metadata in data_records:
            # Filter metadata to only include columns that exist in the table and
            # put in correct order. We use get to insert null values for missing columns
            insert_data.append(
                {
                    col: metadata.get(col)
                    for col in table_columns
                    if col != "PRIMARY KEY"
                }
            )
        logger.debug("Insert data: {}", insert_data)

        if insert_data:
            # Use the first record to determine column order
            columns = list(insert_data[0].keys())
            placeholders = ", ".join(["?" for _ in columns])
            insert_sql = (
                f"REPLACE INTO {table} ({', '.join(columns)}) VALUES ({placeholders})"
            )

            # Prepare values for batch insert
            values_list = []
            for metadata in insert_data:
                values = [metadata.get(col) for col in columns]
                values_list.append(values)

            # Execute batch insert
            cursor.executemany(insert_sql, values_list)
            conn.commit()
            logger.success(f"DBase: Inserted {len(values_list)} records into {table} table")
    except Exception as e:
        conn.rollback()
        logger.error(f"Error inserting batch: {e}")
        raise
    finally:
        conn.close()
