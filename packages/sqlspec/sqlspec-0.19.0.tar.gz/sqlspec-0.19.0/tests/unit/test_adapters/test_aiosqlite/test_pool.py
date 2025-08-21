"""Unit tests for aiosqlite async connection pool."""

import asyncio
import time
from collections.abc import AsyncGenerator
from typing import Any, cast
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from sqlspec.adapters.aiosqlite._types import AiosqliteConnection
from sqlspec.adapters.aiosqlite.pool import (
    AiosqliteConnectionPool,
    AiosqliteConnectTimeoutError,
    AiosqlitePoolClosedError,
    AiosqlitePoolConnection,
)


class MockAiosqliteConnection:
    """Mock aiosqlite connection for testing."""

    def __init__(self, database: str = ":memory:"):
        self.database = database
        self.execute_calls: list[str] = []
        self.closed = False
        self.commit_called = False
        self.rollback_called = False

        self.daemon = False
        self.name = f"MockConnection-{id(self)}"

    def __await__(self) -> Any:
        """Make this object awaitable to simulate aiosqlite.connect() behavior."""

        async def _await() -> "MockAiosqliteConnection":
            return self

        return _await().__await__()

    def is_alive(self) -> bool:
        """Mock is_alive method."""
        return not self.closed

    async def execute(self, sql: str) -> None:
        """Mock execute method."""
        if self.closed:
            raise Exception("Connection is closed")
        self.execute_calls.append(sql)

    async def commit(self) -> None:
        """Mock commit method."""
        if self.closed:
            raise Exception("Connection is closed")
        self.commit_called = True

    async def rollback(self) -> None:
        """Mock rollback method."""
        if self.closed:
            raise Exception("Connection is closed")
        self.rollback_called = True

    async def close(self) -> None:
        """Mock close method."""
        self.closed = True


def _cast_mock_connection(mock_conn: MockAiosqliteConnection) -> AiosqliteConnection:
    """Helper to cast mock connection to the proper type."""
    return cast(AiosqliteConnection, mock_conn)


@pytest.fixture
def mock_aiosqlite_connection() -> MockAiosqliteConnection:
    """Create a mock aiosqlite connection."""
    return MockAiosqliteConnection()


@pytest.fixture
def basic_connection_params() -> "dict[str, Any]":
    """Basic connection parameters for testing."""
    return {"database": ":memory:"}


@pytest.fixture
def file_connection_params() -> "dict[str, Any]":
    """File-based connection parameters for testing."""
    return {"database": "test.db"}


@pytest.fixture
def shared_memory_params() -> "dict[str, Any]":
    """Shared memory connection parameters for testing."""
    return {"database": "file::memory:?cache=shared", "uri": True}


@pytest.fixture
async def basic_pool(basic_connection_params: "dict[str, Any]") -> "AsyncGenerator[AiosqliteConnectionPool, None]":
    """Create a basic pool for testing."""
    pool = AiosqliteConnectionPool(basic_connection_params, pool_size=3)
    yield pool
    if not pool.is_closed:
        await pool.close()


class TestPoolConnection:
    """Test PoolConnection wrapper class."""

    def test_pool_connection_initialization(self, mock_aiosqlite_connection: MockAiosqliteConnection) -> None:
        """Test PoolConnection initialization."""
        pool_conn = AiosqlitePoolConnection(_cast_mock_connection(mock_aiosqlite_connection))

        assert pool_conn.connection == _cast_mock_connection(mock_aiosqlite_connection)
        assert pool_conn.id is not None
        assert len(pool_conn.id) == 32
        assert pool_conn.idle_since is None
        assert not pool_conn.is_closed

    def test_idle_time_calculation(self, mock_aiosqlite_connection: MockAiosqliteConnection) -> None:
        """Test idle time calculation."""
        pool_conn = AiosqlitePoolConnection(_cast_mock_connection(mock_aiosqlite_connection))

        assert pool_conn.idle_time == 0.0

        time.time()
        pool_conn.mark_as_idle()
        time.sleep(0.1)

        idle_time = pool_conn.idle_time
        assert idle_time > 0.0
        assert idle_time >= 0.1
        assert idle_time < 1.0

    def test_mark_as_in_use(self, mock_aiosqlite_connection: MockAiosqliteConnection) -> None:
        """Test marking connection as in use."""
        pool_conn = AiosqlitePoolConnection(_cast_mock_connection(mock_aiosqlite_connection))

        pool_conn.mark_as_idle()
        assert pool_conn.idle_since is not None

        pool_conn.mark_as_in_use()
        assert pool_conn.idle_since is None
        assert pool_conn.idle_time == 0.0

    async def test_is_alive_healthy_connection(self, mock_aiosqlite_connection: MockAiosqliteConnection) -> None:
        """Test is_alive with healthy connection."""
        pool_conn = AiosqlitePoolConnection(_cast_mock_connection(mock_aiosqlite_connection))

        is_alive = await pool_conn.is_alive()
        assert is_alive is True
        assert "SELECT 1" in mock_aiosqlite_connection.execute_calls

    async def test_is_alive_closed_connection(self, mock_aiosqlite_connection: MockAiosqliteConnection) -> None:
        """Test is_alive with closed connection."""
        pool_conn = AiosqlitePoolConnection(_cast_mock_connection(mock_aiosqlite_connection))
        await pool_conn.close()

        is_alive = await pool_conn.is_alive()
        assert is_alive is False

    async def test_is_alive_failing_connection(self, mock_aiosqlite_connection: MockAiosqliteConnection) -> None:
        """Test is_alive with failing connection."""

        mock_aiosqlite_connection.execute = AsyncMock(side_effect=Exception("Connection error"))

        pool_conn = AiosqlitePoolConnection(_cast_mock_connection(mock_aiosqlite_connection))
        is_alive = await pool_conn.is_alive()
        assert is_alive is False

    async def test_reset_connection(self, mock_aiosqlite_connection: MockAiosqliteConnection) -> None:
        """Test connection reset."""
        pool_conn = AiosqlitePoolConnection(_cast_mock_connection(mock_aiosqlite_connection))

        await pool_conn.reset()
        assert mock_aiosqlite_connection.rollback_called

    async def test_reset_closed_connection(self, mock_aiosqlite_connection: MockAiosqliteConnection) -> None:
        """Test reset on closed connection."""
        pool_conn = AiosqlitePoolConnection(_cast_mock_connection(mock_aiosqlite_connection))
        await pool_conn.close()

        await pool_conn.reset()

    async def test_reset_failing_rollback(self, mock_aiosqlite_connection: MockAiosqliteConnection) -> None:
        """Test reset when rollback fails."""
        mock_aiosqlite_connection.rollback = AsyncMock(side_effect=Exception("Rollback failed"))

        pool_conn = AiosqlitePoolConnection(_cast_mock_connection(mock_aiosqlite_connection))

        await pool_conn.reset()

    async def test_close_connection(self, mock_aiosqlite_connection: MockAiosqliteConnection) -> None:
        """Test closing connection."""
        pool_conn = AiosqlitePoolConnection(_cast_mock_connection(mock_aiosqlite_connection))

        await pool_conn.close()
        assert pool_conn.is_closed
        assert mock_aiosqlite_connection.closed

    async def test_close_already_closed(self, mock_aiosqlite_connection: MockAiosqliteConnection) -> None:
        """Test closing already closed connection."""
        pool_conn = AiosqlitePoolConnection(_cast_mock_connection(mock_aiosqlite_connection))

        await pool_conn.close()
        await pool_conn.close()
        assert pool_conn.is_closed

    async def test_close_failing_connection(self, mock_aiosqlite_connection: MockAiosqliteConnection) -> None:
        """Test closing connection that fails to close."""
        mock_aiosqlite_connection.close = AsyncMock(side_effect=Exception("Close failed"))

        pool_conn = AiosqlitePoolConnection(_cast_mock_connection(mock_aiosqlite_connection))

        await pool_conn.close()

        assert pool_conn.is_closed


class TestAiosqliteConnectionPool:
    """Test AiosqliteConnectionPool class."""

    def test_pool_initialization(self, basic_connection_params: "dict[str, Any]") -> None:
        """Test pool initialization with default parameters."""
        pool = AiosqliteConnectionPool(basic_connection_params)

        assert pool._connection_parameters == basic_connection_params
        assert pool._pool_size == 5
        assert pool._connect_timeout == 30.0
        assert pool._idle_timeout == 24 * 60 * 60
        assert pool._operation_timeout == 10.0
        assert pool.size() == 0
        assert pool.checked_out() == 0
        assert not pool.is_closed

    def test_pool_initialization_custom_params(self, basic_connection_params: "dict[str, Any]") -> None:
        """Test pool initialization with custom parameters."""
        pool = AiosqliteConnectionPool(
            basic_connection_params, pool_size=10, connect_timeout=60.0, idle_timeout=3600.0, operation_timeout=5.0
        )

        assert pool._pool_size == 10
        assert pool._connect_timeout == 60.0
        assert pool._idle_timeout == 3600.0
        assert pool._operation_timeout == 5.0

    def test_pool_properties(self, basic_connection_params: "dict[str, Any]") -> None:
        """Test pool property methods."""
        pool = AiosqliteConnectionPool(basic_connection_params, pool_size=3)

        assert pool.size() == 0
        assert pool.checked_out() == 0
        assert not pool.is_closed

    @patch("sqlspec.adapters.aiosqlite.pool.aiosqlite.connect")
    async def test_create_connection_memory_database(
        self, mock_connect: MagicMock, basic_connection_params: "dict[str, Any]"
    ) -> None:
        """Test connection creation for memory database."""
        mock_connection = MockAiosqliteConnection(":memory:")
        mock_connect.return_value = mock_connection

        pool = AiosqliteConnectionPool(basic_connection_params)
        pool_conn = await pool._create_connection()

        mock_connect.assert_called_once_with(**basic_connection_params)
        assert pool_conn.connection == _cast_mock_connection(mock_connection)
        assert pool_conn.idle_since is not None

        expected_pragmas = [
            "PRAGMA journal_mode = MEMORY",
            "PRAGMA synchronous = OFF",
            "PRAGMA temp_store = MEMORY",
            "PRAGMA cache_size = -16000",
            "PRAGMA foreign_keys = ON",
            "PRAGMA busy_timeout = 30000",
        ]

        for pragma in expected_pragmas:
            assert pragma in mock_connection.execute_calls

        assert mock_connection.commit_called

    @patch("sqlspec.adapters.aiosqlite.pool.aiosqlite.connect")
    async def test_create_connection_file_database(
        self, mock_connect: MagicMock, file_connection_params: "dict[str, Any]"
    ) -> None:
        """Test connection creation for file database."""
        mock_connection = MockAiosqliteConnection("test.db")
        mock_connect.return_value = mock_connection

        pool = AiosqliteConnectionPool(file_connection_params)
        await pool._create_connection()

        expected_pragmas = [
            "PRAGMA journal_mode = WAL",
            "PRAGMA synchronous = NORMAL",
            "PRAGMA foreign_keys = ON",
            "PRAGMA busy_timeout = 30000",
        ]

        for pragma in expected_pragmas:
            assert pragma in mock_connection.execute_calls

    @patch("sqlspec.adapters.aiosqlite.pool.aiosqlite.connect")
    async def test_create_connection_shared_cache(
        self, mock_connect: MagicMock, shared_memory_params: "dict[str, Any]"
    ) -> None:
        """Test connection creation for shared cache database."""
        mock_connection = MockAiosqliteConnection("file::memory:?cache=shared")
        mock_connect.return_value = mock_connection

        pool = AiosqliteConnectionPool(shared_memory_params)
        await pool._create_connection()

        expected_pragmas = ["PRAGMA journal_mode = MEMORY", "PRAGMA read_uncommitted = ON"]

        for pragma in expected_pragmas:
            assert pragma in mock_connection.execute_calls

        assert pool._wal_initialized

    @patch("sqlspec.adapters.aiosqlite.pool.aiosqlite.connect")
    async def test_create_connection_optimization_failure(
        self, mock_connect: MagicMock, file_connection_params: "dict[str, Any]"
    ) -> None:
        """Test connection creation when optimization fails."""
        mock_connection = MockAiosqliteConnection("test.db")

        original_execute = mock_connection.execute

        async def failing_execute(sql: str) -> None:
            if "journal_mode" in sql:
                raise Exception("PRAGMA failed")
            await original_execute(sql)

        mock_connection.execute = failing_execute
        mock_connect.return_value = mock_connection

        pool = AiosqliteConnectionPool(file_connection_params)

        pool_conn = await pool._create_connection()

        assert pool_conn.connection == _cast_mock_connection(mock_connection)

        assert "PRAGMA foreign_keys = ON" in mock_connection.execute_calls
        assert "PRAGMA busy_timeout = 30000" in mock_connection.execute_calls

    @patch("sqlspec.adapters.aiosqlite.pool.aiosqlite.connect")
    async def test_claim_if_healthy_success(
        self, mock_connect: MagicMock, basic_connection_params: "dict[str, Any]"
    ) -> None:
        """Test successful healthy connection claim."""
        mock_connection = MockAiosqliteConnection()
        mock_connect.return_value = mock_connection

        pool = AiosqliteConnectionPool(basic_connection_params)
        pool_conn = await pool._create_connection()

        claimed = await pool._claim_if_healthy(pool_conn)
        assert claimed is True
        assert pool_conn.idle_since is None

    @patch("sqlspec.adapters.aiosqlite.pool.aiosqlite.connect")
    async def test_claim_if_healthy_idle_timeout(
        self, mock_connect: MagicMock, basic_connection_params: "dict[str, Any]"
    ) -> None:
        """Test claiming connection that exceeds idle timeout."""
        mock_connection = MockAiosqliteConnection()
        mock_connect.return_value = mock_connection

        pool = AiosqliteConnectionPool(basic_connection_params, idle_timeout=0.1)
        pool_conn = await pool._create_connection()

        await asyncio.sleep(0.2)

        claimed = await pool._claim_if_healthy(pool_conn)
        assert claimed is False
        assert pool_conn.id not in pool._connection_registry

    @patch("sqlspec.adapters.aiosqlite.pool.aiosqlite.connect")
    async def test_claim_if_healthy_health_check_timeout(
        self, mock_connect: MagicMock, basic_connection_params: "dict[str, Any]"
    ) -> None:
        """Test claiming connection with health check timeout."""
        mock_connection = MockAiosqliteConnection()

        async def slow_execute(sql: str) -> None:
            await asyncio.sleep(1.0)

        mock_connection.execute = slow_execute
        mock_connect.return_value = mock_connection

        pool = AiosqliteConnectionPool(basic_connection_params, operation_timeout=0.1)
        pool_conn = await pool._create_connection()

        claimed = await pool._claim_if_healthy(pool_conn)
        assert claimed is False
        assert pool_conn.id not in pool._connection_registry

    @patch("sqlspec.adapters.aiosqlite.pool.aiosqlite.connect")
    async def test_try_provision_new_connection_success(
        self, mock_connect: MagicMock, basic_connection_params: "dict[str, Any]"
    ) -> None:
        """Test successful new connection provisioning."""
        mock_connection = MockAiosqliteConnection()
        mock_connect.return_value = mock_connection

        pool = AiosqliteConnectionPool(basic_connection_params, pool_size=5)

        new_conn = await pool._try_provision_new_connection()
        assert new_conn is not None
        assert new_conn.connection == _cast_mock_connection(mock_connection)
        assert new_conn.idle_since is None
        assert pool.size() == 1

    @patch("sqlspec.adapters.aiosqlite.pool.aiosqlite.connect")
    async def test_try_provision_new_connection_at_capacity(
        self, mock_connect: MagicMock, basic_connection_params: "dict[str, Any]"
    ) -> None:
        """Test provisioning when at capacity."""
        mock_connect.return_value = MockAiosqliteConnection()

        pool = AiosqliteConnectionPool(basic_connection_params, pool_size=1)

        await pool._create_connection()

        new_conn = await pool._try_provision_new_connection()
        assert new_conn is None

    @patch("sqlspec.adapters.aiosqlite.pool.aiosqlite.connect")
    async def test_try_provision_new_connection_failure(
        self, mock_connect: MagicMock, basic_connection_params: "dict[str, Any]"
    ) -> None:
        """Test provisioning when connection creation fails."""
        mock_connect.side_effect = Exception("Connection failed")

        pool = AiosqliteConnectionPool(basic_connection_params)

        new_conn = await pool._try_provision_new_connection()

        assert new_conn is None

    @patch("sqlspec.adapters.aiosqlite.pool.aiosqlite.connect")
    async def test_acquire_from_queue(self, mock_connect: MagicMock, basic_connection_params: "dict[str, Any]") -> None:
        """Test acquiring connection from queue."""
        mock_connection = MockAiosqliteConnection()
        mock_connect.return_value = mock_connection

        pool = AiosqliteConnectionPool(basic_connection_params)

        pool_conn = await pool._create_connection()
        pool_conn.mark_as_idle()
        pool._queue.put_nowait(pool_conn)

        acquired = await pool.acquire()
        assert acquired == pool_conn
        assert acquired.idle_since is None

    @patch("sqlspec.adapters.aiosqlite.pool.aiosqlite.connect")
    async def test_acquire_create_new(self, mock_connect: MagicMock, basic_connection_params: "dict[str, Any]") -> None:
        """Test acquiring connection by creating new one."""
        mock_connection = MockAiosqliteConnection()
        mock_connect.return_value = mock_connection

        pool = AiosqliteConnectionPool(basic_connection_params)

        acquired = await pool.acquire()
        assert acquired.connection == _cast_mock_connection(mock_connection)
        assert acquired.idle_since is None
        assert pool.size() == 1

    async def test_acquire_timeout(self, basic_connection_params: "dict[str, Any]") -> None:
        """Test acquisition timeout."""
        pool = AiosqliteConnectionPool(basic_connection_params, connect_timeout=0.1, pool_size=1)

        dummy_conn = AiosqlitePoolConnection(_cast_mock_connection(MockAiosqliteConnection()))
        pool._connection_registry[dummy_conn.id] = dummy_conn

        with pytest.raises(AiosqliteConnectTimeoutError, match="Connection acquisition timed out"):
            await pool.acquire()

    async def test_acquire_from_closed_pool(self, basic_connection_params: "dict[str, Any]") -> None:
        """Test acquiring from closed pool."""
        pool = AiosqliteConnectionPool(basic_connection_params)
        await pool.close()

        with pytest.raises(AiosqlitePoolClosedError, match="Cannot acquire connection from closed pool"):
            await pool.acquire()

    @patch("sqlspec.adapters.aiosqlite.pool.aiosqlite.connect")
    async def test_release_success(self, mock_connect: MagicMock, basic_connection_params: "dict[str, Any]") -> None:
        """Test successful connection release."""
        mock_connection = MockAiosqliteConnection()
        mock_connect.return_value = mock_connection

        pool = AiosqliteConnectionPool(basic_connection_params)
        pool_conn = await pool._create_connection()
        pool_conn.mark_as_in_use()

        await pool.release(pool_conn)

        assert pool_conn.idle_since is not None
        assert mock_connection.rollback_called
        assert pool._queue.qsize() == 1

    @patch("sqlspec.adapters.aiosqlite.pool.aiosqlite.connect")
    async def test_release_reset_failure(
        self, mock_connect: MagicMock, basic_connection_params: "dict[str, Any]"
    ) -> None:
        """Test release when reset fails."""
        mock_connection = MockAiosqliteConnection()

        async def hanging_rollback() -> None:
            await asyncio.sleep(1.0)

        mock_connection.rollback = hanging_rollback
        mock_connect.return_value = mock_connection

        pool = AiosqliteConnectionPool(basic_connection_params, operation_timeout=0.1)
        pool_conn = await pool._create_connection()

        await pool.release(pool_conn)

        assert pool_conn.id not in pool._connection_registry

    async def test_release_to_closed_pool(self, basic_connection_params: "dict[str, Any]") -> None:
        """Test releasing to closed pool."""
        pool = AiosqliteConnectionPool(basic_connection_params)
        pool_conn = AiosqlitePoolConnection(_cast_mock_connection(MockAiosqliteConnection()))
        pool._connection_registry[pool_conn.id] = pool_conn

        await pool.close()
        await pool.release(pool_conn)

        assert pool_conn.id not in pool._connection_registry

    async def test_release_unknown_connection(self, basic_connection_params: "dict[str, Any]") -> None:
        """Test releasing unknown connection."""
        pool = AiosqliteConnectionPool(basic_connection_params)
        unknown_conn = AiosqlitePoolConnection(_cast_mock_connection(MockAiosqliteConnection()))

        await pool.release(unknown_conn)

        assert not pool.is_closed

    @patch("sqlspec.adapters.aiosqlite.pool.aiosqlite.connect")
    async def test_get_connection_context_manager(
        self, mock_connect: MagicMock, basic_connection_params: "dict[str, Any]"
    ) -> None:
        """Test get_connection context manager."""
        mock_connection = MockAiosqliteConnection()
        mock_connect.return_value = mock_connection

        pool = AiosqliteConnectionPool(basic_connection_params)

        async with pool.get_connection() as conn:
            assert conn == _cast_mock_connection(mock_connection)

        assert pool._queue.qsize() == 1

    @patch("sqlspec.adapters.aiosqlite.pool.aiosqlite.connect")
    async def test_get_connection_exception_handling(
        self, mock_connect: MagicMock, basic_connection_params: "dict[str, Any]"
    ) -> None:
        """Test get_connection context manager with exception."""
        mock_connection = MockAiosqliteConnection()
        mock_connect.return_value = mock_connection

        pool = AiosqliteConnectionPool(basic_connection_params)

        try:
            async with pool.get_connection() as conn:
                assert conn == _cast_mock_connection(mock_connection)
                raise ValueError("Test exception")
        except ValueError:
            pass

        assert pool._queue.qsize() == 1

    @patch("sqlspec.adapters.aiosqlite.pool.aiosqlite.connect")
    async def test_pool_close(self, mock_connect: MagicMock, basic_connection_params: "dict[str, Any]") -> None:
        """Test pool closure."""
        mock_connections = [MockAiosqliteConnection() for _ in range(3)]
        mock_connect.side_effect = mock_connections

        pool = AiosqliteConnectionPool(basic_connection_params, pool_size=5)

        conns = []
        for _ in range(3):
            conn = await pool._create_connection()
            conns.append(conn)
            pool._queue.put_nowait(conn)

        await pool.close()

        assert pool.is_closed
        assert pool._queue.qsize() == 0
        assert len(pool._connection_registry) == 0

        for mock_conn in mock_connections:
            assert mock_conn.closed

    async def test_close_already_closed_pool(self, basic_connection_params: "dict[str, Any]") -> None:
        """Test closing already closed pool."""
        pool = AiosqliteConnectionPool(basic_connection_params)

        await pool.close()
        await pool.close()

        assert pool.is_closed

    @patch("sqlspec.adapters.aiosqlite.pool.aiosqlite.connect")
    async def test_wait_for_healthy_connection_pool_closed(
        self, mock_connect: MagicMock, basic_connection_params: "dict[str, Any]"
    ) -> None:
        """Test waiting for connection when pool gets closed."""
        pool = AiosqliteConnectionPool(basic_connection_params)

        async def close_pool_after_delay() -> None:
            await asyncio.sleep(0.1)
            await pool.close()

        close_task = asyncio.create_task(close_pool_after_delay())

        with pytest.raises(AiosqlitePoolClosedError, match="Pool closed during connection acquisition"):
            await pool._wait_for_healthy_connection()

        await close_task

    @patch("sqlspec.adapters.aiosqlite.pool.aiosqlite.connect")
    async def test_concurrent_access(self, mock_connect: MagicMock, basic_connection_params: "dict[str, Any]") -> None:
        """Test concurrent pool access."""

        mock_connections = [MockAiosqliteConnection(f"conn_{i}") for i in range(10)]
        mock_connect.side_effect = mock_connections

        pool = AiosqliteConnectionPool(basic_connection_params, pool_size=5)

        async def worker(worker_id: int) -> str:
            """Worker that acquires and releases a connection."""
            async with pool.get_connection():
                await asyncio.sleep(0.01)
                return f"worker_{worker_id}_done"

        tasks = [worker(i) for i in range(10)]
        results = await asyncio.gather(*tasks)

        assert len(results) == 10
        assert all("done" in result for result in results)

        assert not pool.is_closed
        await pool.close()

    @patch("sqlspec.adapters.aiosqlite.pool.aiosqlite.connect")
    async def test_acquire_with_shared_cache_delay(
        self, mock_connect: MagicMock, shared_memory_params: "dict[str, Any]"
    ) -> None:
        """Test acquire with shared cache initialization delay."""
        mock_connection = MockAiosqliteConnection()
        mock_connect.return_value = mock_connection

        pool = AiosqliteConnectionPool(shared_memory_params)

        pool._wal_initialized = False

        conn = await pool.acquire()

        assert conn.connection == _cast_mock_connection(mock_connection)

        await pool.release(conn)
        await pool.close()

    async def test_pool_size_tracking(self, basic_connection_params: "dict[str, Any]") -> None:
        """Test pool size and checked out tracking."""
        pool = AiosqliteConnectionPool(basic_connection_params, pool_size=3)

        assert pool.size() == 0
        assert pool.checked_out() == 0

        conn = AiosqlitePoolConnection(_cast_mock_connection(MockAiosqliteConnection()))
        pool._connection_registry[conn.id] = conn

        assert pool.size() == 1
        assert pool.checked_out() == 1

        pool._queue.put_nowait(conn)

        assert pool.size() == 1
        assert pool.checked_out() == 0


class TestPoolExceptionClasses:
    """Test custom exception classes."""

    def test_pool_closed_error(self) -> None:
        """Test AiosqlitePoolClosedError exception."""
        error = AiosqlitePoolClosedError("Pool is closed")
        assert str(error) == "Pool is closed"
        assert isinstance(error, Exception)

    def test_pool_connect_timeout_error(self) -> None:
        """Test AiosqliteConnectTimeoutError exception."""
        error = AiosqliteConnectTimeoutError("Acquisition timed out")
        assert str(error) == "Acquisition timed out"
        assert isinstance(error, Exception)


@pytest.mark.asyncio
async def test_pool_stress_test(basic_connection_params: "dict[str, Any]") -> None:
    """Stress test the pool with many concurrent operations."""
    with patch("sqlspec.adapters.aiosqlite.pool.aiosqlite.connect") as mock_connect:
        mock_connections = [MockAiosqliteConnection(f"stress_{i}") for i in range(20)]
        mock_connect.side_effect = mock_connections

        pool = AiosqliteConnectionPool(basic_connection_params, pool_size=5, connect_timeout=1.0)

        async def stress_worker(worker_id: int) -> int:
            """Worker that performs multiple operations."""
            operations = 0
            for _ in range(5):
                try:
                    async with pool.get_connection():
                        await asyncio.sleep(0.001)
                        operations += 1
                except Exception:
                    pass
            return operations

        tasks = [stress_worker(i) for i in range(20)]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        total_operations = sum(r for r in results if isinstance(r, int))
        assert total_operations > 0

        await pool.close()


@pytest.mark.asyncio
async def test_memory_usage_pattern(basic_connection_params: "dict[str, Any]") -> None:
    """Test that pool doesn't cause memory leaks with rapid acquire/release cycles."""
    with patch("sqlspec.adapters.aiosqlite.pool.aiosqlite.connect") as mock_connect:
        mock_connect.return_value = MockAiosqliteConnection()

        pool = AiosqliteConnectionPool(basic_connection_params, pool_size=2)

        for _ in range(100):
            async with pool.get_connection():
                pass

        assert pool.size() <= 2
        assert not pool.is_closed

        await pool.close()
        assert pool.is_closed
        assert pool.size() == 0
