from project.ha_6.multi_threading_table import MultiThreadingHashTable, HashTableManager
from multiprocessing import Manager
import pytest


class TestHashTable:
    """Comprehensive tests for HashTable."""

    @pytest.fixture
    def manager(self):
        """Return HashTableManager instance."""
        with HashTableManager() as manager:
            yield manager

    @pytest.fixture
    def table(self, manager):
        """Return empty HashTable instance."""
        return manager.MultiThreadingHashTable()

    @pytest.fixture
    def no_resize_table(self, manager):
        """Return HashTable with resize disabled."""
        table = manager.MultiThreadingHashTable()
        table._load_factor = 100.0
        return table

    @pytest.mark.parametrize(
        "key, value",
        [
            ("string_key", "string_value"),
            (123, 456),
            (45.67, 99.99),
            ((1, 2), "tuple_value"),
            (None, "none_key"),
            ("", "empty_string"),
            (True, "boolean_key"),
        ],
    )
    def test_set_get_different_key_types(self, table, key, value):
        """Test setting and getting with various key types."""
        table[key] = value
        assert table[key] == value
        assert key in table

    @pytest.mark.parametrize(
        "key",
        [
            "nonexistent_key",
            "missing",
            "unknown",
            999,
            "",
        ],
    )
    def test_key_error_cases(self, table, key):
        """Test KeyError for missing keys."""
        with pytest.raises(KeyError):
            _ = table[key]

        with pytest.raises(KeyError):
            del table[key]

    @pytest.mark.parametrize(
        "initial_value, updated_value",
        [
            (1, 100),
            ("old", "new"),
            ([1, 2], [3, 4, 5]),
            (None, "not_none"),
            ("value", None),
        ],
    )
    def test_update_existing_key(self, table, initial_value, updated_value):
        """Test updating value for existing key."""
        table["test_key"] = initial_value
        assert table["test_key"] == initial_value

        table["test_key"] = updated_value
        assert table["test_key"] == updated_value
        assert len(table) == 1

    # Remove collision tests since they access internal attributes through proxy

    @pytest.mark.parametrize(
        "initial_size, load_factor, elements_to_add",
        [(4, 0.75, 4), (8, 0.5, 5), (10, 0.8, 9), (16, 0.9, 15)],
    )
    def test_auto_resize_scenarios(
        self, manager, initial_size, load_factor, elements_to_add
    ):
        """Test automatic resizing in different scenarios."""
        table = manager.MultiThreadingHashTable(
            initial_size=initial_size, load_factor=load_factor
        )

        for i in range(elements_to_add):
            table[f"key_{i}"] = i

        # Trigger resize by adding one more element
        table["resize_trigger"] = "resize!!!"

        # Verify all data is still accessible after resize
        for i in range(elements_to_add):
            assert table[f"key_{i}"] == i
        assert table["resize_trigger"] == "resize!!!"

    @pytest.mark.parametrize(
        "test_data",
        [
            {"a": 1, "b": 2, "c": 3},
            {"x": "hello", "y": "world", "z": "test"},
            {1: "one", 2: "two", 3: "three"},
        ],
    )
    def test_mutable_mapping_interface(self, table, test_data):
        """Test MutableMapping interface with different data."""
        for key, value in test_data.items():
            table[key] = value

        # Test iteration and data retrieval
        retrieved_data = {}
        for key in table:
            retrieved_data[key] = table[key]

        assert retrieved_data == test_data

    @pytest.mark.parametrize(
        "test_data, key_to_remove",
        [
            ({"a": 1, "b": 2, "c": 3}, "b"),
            ({"x": 10, "y": 20, "z": 30}, "x"),
            ({"first": "1st", "second": "2nd", "third": "3rd"}, "second"),
        ],
    )
    def test_delete_operation(self, table, test_data, key_to_remove):
        """Test delete operation with different data."""
        for key, value in test_data.items():
            table[key] = value

        del table[key_to_remove]
        assert key_to_remove not in table
        assert len(table) == len(test_data) - 1

        # Verify remaining data
        for key, value in test_data.items():
            if key != key_to_remove:
                assert table[key] == value

    @pytest.mark.parametrize(
        "initial_size, expected_error",
        [
            (0, "Table size should be positive number"),
            (-1, "Table size should be positive number"),
        ],
    )
    def test_invalid_initial_size(self, initial_size, expected_error):
        """Test invalid initial size parameters."""
        with pytest.raises(ValueError, match=expected_error):
            MultiThreadingHashTable(initial_size=initial_size)

    @pytest.mark.parametrize(
        "load_factor, expected_error",
        [
            (0, "Load factor should be between 0 and 1"),
            (1, "Load factor should be between 0 and 1"),
        ],
    )
    def test_invalid_load_factor(self, load_factor, expected_error):
        """Test invalid load factor parameters."""
        with pytest.raises(ValueError, match=expected_error):
            MultiThreadingHashTable(load_factor=load_factor)


@pytest.fixture
def manager():
    """Return HashTableManager instance."""
    with HashTableManager() as manager:
        yield manager


@pytest.mark.parametrize(
    "operations, expected_final_state",
    [
        (
            [
                ("insert", "a", 1),
                ("insert", "b", 2),
                ("update", "a", 10),
                ("delete", "b", None),
            ],
            {"a": 10},
        ),
        (
            [
                ("insert", "x", 100),
                ("insert", "y", 200),
                ("insert", "z", 300),
                ("delete", "y", None),
                ("insert", "w", 400),
            ],
            {"x": 100, "z": 300, "w": 400},
        ),
        (
            [
                ("insert", "k1", "v1"),
                ("update", "k1", "v1_updated"),
                ("insert", "k2", "v2"),
                ("delete", "k1", None),
            ],
            {"k2": "v2"},
        ),
    ],
)
def test_mixed_operations_sequences(manager, operations, expected_final_state):
    """Test complex sequences of operations."""
    table = manager.MultiThreadingHashTable()

    for operation, key, value in operations:
        if operation == "insert":
            table[key] = value
        elif operation == "update":
            table[key] = value
        elif operation == "delete":
            del table[key]

    assert len(table) == len(expected_final_state)
    for key, expected_value in expected_final_state.items():
        assert table[key] == expected_value
