"""DuckDB driver implementation.

This driver provides:
- SQL compilation with single-pass processing
- Memory-efficient design with __slots__
- Statement caching for repeated execution
- Backward compatibility with existing functionality

Features:
- Integration with sqlspec.core modules
- Parameter processing with type coercion
- DuckDB resource management
- Multi-parameter style support
"""

from typing import TYPE_CHECKING, Any, Final, Optional

import duckdb
from sqlglot import exp

from sqlspec.core.cache import get_cache_config
from sqlspec.core.parameters import ParameterStyle, ParameterStyleConfig
from sqlspec.core.statement import SQL, StatementConfig
from sqlspec.driver import SyncDriverAdapterBase
from sqlspec.exceptions import SQLParsingError, SQLSpecError
from sqlspec.utils.logging import get_logger

if TYPE_CHECKING:
    from contextlib import AbstractContextManager

    from sqlspec.adapters.duckdb._types import DuckDBConnection
    from sqlspec.core.result import SQLResult
    from sqlspec.driver import ExecutionResult

__all__ = ("DuckDBCursor", "DuckDBDriver", "DuckDBExceptionHandler", "duckdb_statement_config")

logger = get_logger("adapters.duckdb")


duckdb_statement_config = StatementConfig(
    dialect="duckdb",
    parameter_config=ParameterStyleConfig(
        default_parameter_style=ParameterStyle.QMARK,
        supported_parameter_styles={ParameterStyle.QMARK, ParameterStyle.NUMERIC, ParameterStyle.NAMED_DOLLAR},
        default_execution_parameter_style=ParameterStyle.QMARK,
        supported_execution_parameter_styles={ParameterStyle.QMARK, ParameterStyle.NUMERIC},
        type_coercion_map={},
        has_native_list_expansion=True,
        needs_static_script_compilation=False,
        preserve_parameter_format=True,
        allow_mixed_parameter_styles=False,
    ),
    enable_parsing=True,
    enable_validation=True,
    enable_caching=True,
    enable_parameter_type_wrapping=True,
)


MODIFYING_OPERATIONS: Final[tuple[str, ...]] = ("INSERT", "UPDATE", "DELETE")


class DuckDBCursor:
    """Context manager for DuckDB cursor management."""

    __slots__ = ("connection", "cursor")

    def __init__(self, connection: "DuckDBConnection") -> None:
        self.connection = connection
        self.cursor: Optional[Any] = None

    def __enter__(self) -> Any:
        self.cursor = self.connection.cursor()
        return self.cursor

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        _ = (exc_type, exc_val, exc_tb)
        if self.cursor is not None:
            self.cursor.close()


class DuckDBExceptionHandler:
    """Custom sync context manager for handling DuckDB database exceptions."""

    __slots__ = ()

    def __enter__(self) -> None:
        return None

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        if exc_type is None:
            return

        if issubclass(exc_type, duckdb.IntegrityError):
            e = exc_val
            msg = f"DuckDB integrity constraint violation: {e}"
            raise SQLSpecError(msg) from e
        if issubclass(exc_type, duckdb.OperationalError):
            e = exc_val
            error_msg = str(e).lower()
            if "syntax" in error_msg or "parse" in error_msg:
                msg = f"DuckDB SQL syntax error: {e}"
                raise SQLParsingError(msg) from e
            msg = f"DuckDB operational error: {e}"
            raise SQLSpecError(msg) from e
        if issubclass(exc_type, duckdb.ProgrammingError):
            e = exc_val
            error_msg = str(e).lower()
            if "syntax" in error_msg or "parse" in error_msg:
                msg = f"DuckDB SQL syntax error: {e}"
                raise SQLParsingError(msg) from e
            msg = f"DuckDB programming error: {e}"
            raise SQLSpecError(msg) from e
        if issubclass(exc_type, duckdb.Error):
            e = exc_val
            msg = f"DuckDB error: {e}"
            raise SQLSpecError(msg) from e
        if issubclass(exc_type, Exception):
            e = exc_val
            error_msg = str(e).lower()
            if "parse" in error_msg or "syntax" in error_msg:
                msg = f"SQL parsing failed: {e}"
                raise SQLParsingError(msg) from e
            msg = f"Unexpected database operation error: {e}"
            raise SQLSpecError(msg) from e


class DuckDBDriver(SyncDriverAdapterBase):
    """DuckDB driver implementation.

    This driver uses the core module system for SQL processing:

    Features:
    - SQL compilation with single-pass processing
    - Memory-efficient design with __slots__
    - Statement caching for repeated execution
    - Parameter processing with type coercion
    - DuckDB resource management

    Core Integration:
    - sqlspec.core.statement for SQL processing
    - sqlspec.core.parameters for parameter handling
    - sqlspec.core.cache for statement caching
    - sqlspec.core.config for configuration management

    DuckDB Support:
    - Multi-parameter style support (QMARK, NUMERIC, NAMED_DOLLAR)
    - Script execution with statement splitting
    - Batch operations with row counting
    - DuckDB-specific exception handling

    Compatibility:
    - Backward compatibility with existing DuckDB driver interface
    - StatementConfig API compatibility
    - Transaction management patterns
    """

    __slots__ = ()
    dialect = "duckdb"

    def __init__(
        self,
        connection: "DuckDBConnection",
        statement_config: "Optional[StatementConfig]" = None,
        driver_features: "Optional[dict[str, Any]]" = None,
    ) -> None:
        if statement_config is None:
            cache_config = get_cache_config()
            updated_config = duckdb_statement_config.replace(
                enable_caching=cache_config.compiled_cache_enabled,
                enable_parsing=True,
                enable_validation=True,
                dialect="duckdb",
            )
            statement_config = updated_config

        super().__init__(connection=connection, statement_config=statement_config, driver_features=driver_features)

    def with_cursor(self, connection: "DuckDBConnection") -> "DuckDBCursor":
        """Create context manager for DuckDB cursor."""
        return DuckDBCursor(connection)

    def handle_database_exceptions(self) -> "AbstractContextManager[None]":
        """Handle database-specific exceptions and wrap them appropriately."""
        return DuckDBExceptionHandler()

    def _try_special_handling(self, cursor: Any, statement: SQL) -> "Optional[SQLResult]":
        """Handle DuckDB-specific special operations.

        DuckDB doesn't have special operations like PostgreSQL COPY,
        so this always returns None to proceed with standard execution.

        Args:
            cursor: DuckDB cursor object
            statement: SQL statement to analyze

        Returns:
            None for standard execution (no special operations)
        """
        _ = (cursor, statement)
        return None

    def _is_modifying_operation(self, statement: SQL) -> bool:
        """Check if the SQL statement is a modifying operation.

        Uses both AST-based detection (when available) and SQL text analysis
        to identify operation type.

        Args:
            statement: SQL statement to analyze

        Returns:
            True if the operation modifies data (INSERT/UPDATE/DELETE)
        """

        expression = statement.expression
        if expression and isinstance(expression, (exp.Insert, exp.Update, exp.Delete)):
            return True

        sql_upper = statement.sql.strip().upper()
        return any(sql_upper.startswith(op) for op in MODIFYING_OPERATIONS)

    def _execute_script(self, cursor: Any, statement: SQL) -> "ExecutionResult":
        """Execute SQL script with statement splitting and parameter handling.

        Uses core module for statement parsing and parameter processing.
        Handles DuckDB script execution requirements with parameter support.

        Args:
            cursor: DuckDB cursor object
            statement: SQL statement with script content

        Returns:
            ExecutionResult with script execution metadata
        """
        sql, prepared_parameters = self._get_compiled_sql(statement, self.statement_config)
        statements = self.split_script_statements(sql, statement.statement_config, strip_trailing_semicolon=True)

        successful_count = 0
        last_result = None

        for stmt in statements:
            last_result = cursor.execute(stmt, prepared_parameters or ())
            successful_count += 1

        return self.create_execution_result(
            last_result, statement_count=len(statements), successful_statements=successful_count, is_script_result=True
        )

    def _execute_many(self, cursor: Any, statement: SQL) -> "ExecutionResult":
        """Execute SQL with multiple parameter sets using batch processing.

        Uses DuckDB's executemany for batch operations with
        row counting for both modifying and non-modifying operations.

        Args:
            cursor: DuckDB cursor object
            statement: SQL statement with multiple parameter sets

        Returns:
            ExecutionResult with batch execution metadata
        """
        sql, prepared_parameters = self._get_compiled_sql(statement, self.statement_config)

        if prepared_parameters:
            cursor.executemany(sql, prepared_parameters)

            if self._is_modifying_operation(statement):
                row_count = len(prepared_parameters)
            else:
                try:
                    result = cursor.fetchone()
                    row_count = int(result[0]) if result and isinstance(result, tuple) and len(result) == 1 else 0
                except Exception:
                    row_count = max(cursor.rowcount, 0) if hasattr(cursor, "rowcount") else 0
        else:
            row_count = 0

        return self.create_execution_result(cursor, rowcount_override=row_count, is_many_result=True)

    def _execute_statement(self, cursor: Any, statement: SQL) -> "ExecutionResult":
        """Execute single SQL statement with data handling.

        Uses core processing for parameter handling and result processing.
        Handles both SELECT queries and non-SELECT operations.

        Args:
            cursor: DuckDB cursor object
            statement: SQL statement to execute

        Returns:
            ExecutionResult with execution metadata
        """
        sql, prepared_parameters = self._get_compiled_sql(statement, self.statement_config)
        cursor.execute(sql, prepared_parameters or ())

        if statement.returns_rows():
            fetched_data = cursor.fetchall()
            column_names = [col[0] for col in cursor.description or []]

            if fetched_data and isinstance(fetched_data[0], tuple):
                dict_data = [dict(zip(column_names, row)) for row in fetched_data]
            else:
                dict_data = fetched_data

            return self.create_execution_result(
                cursor,
                selected_data=dict_data,
                column_names=column_names,
                data_row_count=len(dict_data),
                is_select_result=True,
            )

        try:
            result = cursor.fetchone()
            row_count = int(result[0]) if result and isinstance(result, tuple) and len(result) == 1 else 0
        except Exception:
            row_count = max(cursor.rowcount, 0) if hasattr(cursor, "rowcount") else 0

        return self.create_execution_result(cursor, rowcount_override=row_count)

    def begin(self) -> None:
        """Begin a database transaction."""
        try:
            self.connection.execute("BEGIN TRANSACTION")
        except duckdb.Error as e:
            msg = f"Failed to begin DuckDB transaction: {e}"
            raise SQLSpecError(msg) from e

    def rollback(self) -> None:
        """Rollback the current transaction."""
        try:
            self.connection.rollback()
        except duckdb.Error as e:
            msg = f"Failed to rollback DuckDB transaction: {e}"
            raise SQLSpecError(msg) from e

    def commit(self) -> None:
        """Commit the current transaction."""
        try:
            self.connection.commit()
        except duckdb.Error as e:
            msg = f"Failed to commit DuckDB transaction: {e}"
            raise SQLSpecError(msg) from e
