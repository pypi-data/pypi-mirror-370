import sqlglot

from sqlalchemy.types import TypeDecorator, JSON
from sqlalchemy.dialects.postgresql import JSONB

from dxtrx.utils import json
from dxtrx.utils.logging import get_logger

logger = get_logger(__name__)

def format_sql_statement(sql: sqlglot.expressions.Expression) -> str:
    """Formats a SQL statement by removing comments and cleaning whitespace.

    Args:
        sql (sqlglot.expressions.Expression): The SQL expression to format.

    Returns:
        str: The formatted SQL statement, or None if the input is empty or None.
    """
    if sql is None or not sql.sql().strip() or sql.sql().strip() == "":
        return None
    
    sql.comments = None # Remove comments

    return sql

def format_sql_multistatement(sql: str, read_dialect: str = "postgres", write_dialect: str = "postgres") -> str:
    """Formats multiple SQL statements by parsing and formatting each statement individually.

    Args:
        sql (str): The SQL string containing multiple statements.
        read_dialect (str, optional): The dialect to use for parsing. Defaults to "postgres".
        write_dialect (str, optional): The dialect to use for writing. Defaults to "postgres".

    Returns:
        str: List of formatted SQL statements.
    """
    # Tokenize and parse all statements
    logger.info(f"Formatting SQL multistatement: {sql}")
    parsed_statements = sqlglot.parse(sql, read=read_dialect)

    final_statements = []
    for stmt in parsed_statements:
        stmt = format_sql_statement(stmt)
        if stmt is None:
            continue
        final_statements.append(stmt.sql(dialect=write_dialect))

    # Remove empty queries
    final_statements = [q for q in final_statements if q is not None and q.strip() != ""]

    return final_statements

class ORJSONType(TypeDecorator):
    """Platform-independent JSON type using orjson and PostgreSQL JSONB when available.
    
    This class extends SQLAlchemy's TypeDecorator to provide JSON type support that works
    across different database platforms. It uses orjson for JSON serialization/deserialization
    and PostgreSQL's JSONB type when available.
    """
    
    impl = JSON  # Default impl for non-Postgres
    cache_ok = True

    def load_dialect_impl(self, dialect):
        """Loads the appropriate type implementation based on the database dialect.

        Args:
            dialect: The SQLAlchemy dialect being used.

        Returns:
            The appropriate type descriptor for the given dialect.
        """
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(JSONB())
        return dialect.type_descriptor(JSON())

    def process_bind_param(self, value, dialect):
        """Processes the value before binding it to a parameter.

        Args:
            value: The value to be bound.
            dialect: The SQLAlchemy dialect being used.

        Returns:
            The processed value ready for binding, or None if the input is None.
        """
        if value is None:
            return None
        
        # TODO: Check if this is the best way to handle this
        # Right now it serdes the value to a string and then back to a dict
        # This is not the most efficient way to handle this, but it's the only way to ensure that the value is a dict
        return json.loads(json.dumps(value))

    def process_result_value(self, value, dialect):
        """Processes the value after retrieving it from the database.

        Args:
            value: The value retrieved from the database.
            dialect: The SQLAlchemy dialect being used.

        Returns:
            The processed value, or None if the input is None.
        """
        if value is None:
            return None
        return json.loads(value)
