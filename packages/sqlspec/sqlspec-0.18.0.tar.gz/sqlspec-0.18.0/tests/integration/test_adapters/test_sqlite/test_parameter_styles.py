"""Integration tests for SQLite parameter style handling with CORE_ROUND_3 architecture."""

from typing import Any

import pytest

from sqlspec.adapters.sqlite import SqliteDriver
from sqlspec.core.result import SQLResult
from sqlspec.core.statement import SQL


@pytest.mark.xdist_group("sqlite")
def test_qmark_parameter_style(sqlite_session: SqliteDriver) -> None:
    """Test qmark (?) parameter style - SQLite default."""

    sqlite_session.execute("DELETE FROM test_table")
    sqlite_session.commit()

    result = sqlite_session.execute("INSERT INTO test_table (name, value) VALUES (?, ?)", ("qmark_test", 42))
    assert isinstance(result, SQLResult)
    assert result.rows_affected == 1

    select_result = sqlite_session.execute(
        "SELECT name, value FROM test_table WHERE name = ? AND value = ?", ("qmark_test", 42)
    )
    assert isinstance(select_result, SQLResult)
    assert select_result.data is not None
    assert len(select_result.data) == 1
    assert select_result.data[0]["name"] == "qmark_test"
    assert select_result.data[0]["value"] == 42


@pytest.mark.xdist_group("sqlite")
def test_named_colon_parameter_style(sqlite_session: SqliteDriver) -> None:
    """Test named colon (:name) parameter style."""

    sqlite_session.execute("DELETE FROM test_table")
    sqlite_session.commit()

    result = sqlite_session.execute(
        "INSERT INTO test_table (name, value) VALUES (:name, :value)", {"name": "named_test", "value": 123}
    )
    assert isinstance(result, SQLResult)
    assert result.rows_affected == 1

    select_result = sqlite_session.execute(
        "SELECT name, value FROM test_table WHERE name = :target_name", {"target_name": "named_test"}
    )
    assert isinstance(select_result, SQLResult)
    assert select_result.data is not None
    assert len(select_result.data) == 1
    assert select_result.data[0]["name"] == "named_test"
    assert select_result.data[0]["value"] == 123


@pytest.mark.xdist_group("sqlite")
def test_mixed_parameter_scenarios(sqlite_session: SqliteDriver) -> None:
    """Test edge cases and mixed parameter scenarios."""

    sqlite_session.execute("DELETE FROM test_table")
    sqlite_session.commit()

    sql_obj = SQL("INSERT INTO test_table (name, value) VALUES (:name, :value)", name="sql_object_test", value=999)
    result = sqlite_session.execute(sql_obj)
    assert isinstance(result, SQLResult)
    assert result.rows_affected == 1

    verify_result = sqlite_session.execute("SELECT * FROM test_table WHERE name = ?", ("sql_object_test",))
    assert isinstance(verify_result, SQLResult)
    assert verify_result.data is not None
    assert len(verify_result.data) == 1
    assert verify_result.data[0]["name"] == "sql_object_test"
    assert verify_result.data[0]["value"] == 999


@pytest.mark.xdist_group("sqlite")
def test_parameter_type_coercion(sqlite_session: SqliteDriver) -> None:
    """Test parameter type coercion and handling."""

    sqlite_session.execute("DELETE FROM test_table")
    sqlite_session.commit()

    test_cases = [
        ("string_value", "test_string"),
        ("integer_value", 42),
        ("float_value", 3.14),
        ("boolean_value", True),
        ("none_value", None),
    ]

    for name, value in test_cases:
        result = sqlite_session.execute("INSERT INTO test_table (name, value) VALUES (?, ?)", (name, value))
        assert isinstance(result, SQLResult)
        assert result.rows_affected == 1

    select_result = sqlite_session.execute("SELECT name, value FROM test_table ORDER BY name")
    assert isinstance(select_result, SQLResult)
    assert select_result.data is not None
    assert len(select_result.data) == 5

    boolean_row = next(row for row in select_result.data if row["name"] == "boolean_value")
    assert boolean_row["value"] == 1

    none_row = next(row for row in select_result.data if row["name"] == "none_value")
    assert none_row["value"] is None


@pytest.mark.xdist_group("sqlite")
def test_execute_many_parameter_styles(sqlite_session: SqliteDriver) -> None:
    """Test execute_many with different parameter styles."""

    sqlite_session.execute("DELETE FROM test_table")
    sqlite_session.commit()

    tuple_params: list[tuple[str, int]] = [("batch1", 10), ("batch2", 20), ("batch3", 30)]

    result = sqlite_session.execute_many("INSERT INTO test_table (name, value) VALUES (?, ?)", tuple_params)
    assert isinstance(result, SQLResult)
    assert result.rows_affected == 3

    dict_params: list[dict[str, Any]] = [
        {"name": "dict1", "value": 100},
        {"name": "dict2", "value": 200},
        {"name": "dict3", "value": 300},
    ]

    result = sqlite_session.execute_many("INSERT INTO test_table (name, value) VALUES (:name, :value)", dict_params)
    assert isinstance(result, SQLResult)
    assert result.rows_affected == 3

    count_result = sqlite_session.execute("SELECT COUNT(*) as count FROM test_table")
    assert isinstance(count_result, SQLResult)
    assert count_result.data is not None
    assert count_result.data[0]["count"] == 6


@pytest.mark.xdist_group("sqlite")
def test_parameter_edge_cases(sqlite_session: SqliteDriver) -> None:
    """Test parameter handling edge cases."""

    sqlite_session.execute("DELETE FROM test_table")
    sqlite_session.commit()

    result = sqlite_session.execute("SELECT COUNT(*) as count FROM test_table")
    assert isinstance(result, SQLResult)
    assert result.data is not None
    assert result.data[0]["count"] == 0

    result = sqlite_session.execute(
        "INSERT INTO test_table (name, value) VALUES (:param, :param)", {"param": "duplicate_param_test"}
    )
    assert isinstance(result, SQLResult)
    assert result.rows_affected == 1

    select_result = sqlite_session.execute("SELECT * FROM test_table WHERE name = ?", ("duplicate_param_test",))
    assert isinstance(select_result, SQLResult)
    assert select_result.data is not None
    assert len(select_result.data) == 1


@pytest.mark.xdist_group("sqlite")
def test_parameter_escaping_and_sql_injection_protection(sqlite_session: SqliteDriver) -> None:
    """Test that parameters properly prevent SQL injection."""

    sqlite_session.execute("DELETE FROM test_table")
    sqlite_session.commit()

    sqlite_session.execute("INSERT INTO test_table (name, value) VALUES (?, ?)", ("safe_data", 42))

    malicious_input = "'; DROP TABLE test_table; --"

    result = sqlite_session.execute("SELECT * FROM test_table WHERE name = ?", (malicious_input,))
    assert isinstance(result, SQLResult)
    assert result.data is not None
    assert len(result.data) == 0

    count_result = sqlite_session.execute("SELECT COUNT(*) as count FROM test_table")
    assert isinstance(count_result, SQLResult)
    assert count_result.data is not None
    assert count_result.data[0]["count"] == 1


@pytest.mark.parametrize(
    "sql_template,params,expected_count",
    [
        ("SELECT * FROM test_table WHERE value > ?", (25,), 2),
        ("SELECT * FROM test_table WHERE name LIKE ?", ("%test%",), 3),
        ("SELECT * FROM test_table WHERE value > :min_value", {"min_value": 25}, 2),
        ("SELECT * FROM test_table WHERE name = :target", {"target": "test1"}, 1),
    ],
)
@pytest.mark.xdist_group("sqlite")
def test_parameterized_query_patterns(
    sqlite_session: SqliteDriver, sql_template: str, params: Any, expected_count: int
) -> None:
    """Test various parameterized query patterns."""

    sqlite_session.execute("DELETE FROM test_table")
    sqlite_session.commit()

    test_data = [("test1", 10), ("test2", 20), ("test3", 30), ("other", 40)]
    sqlite_session.execute_many("INSERT INTO test_table (name, value) VALUES (?, ?)", test_data)

    result = sqlite_session.execute(sql_template, params)
    assert isinstance(result, SQLResult)
    assert result.data is not None
    assert len(result.data) == expected_count
