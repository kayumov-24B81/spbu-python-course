from project.ha_6.multi_threading_table import MultiThreadingHashTable
from multiprocessing import Manager
import pytest


class TestHashTable:
    """Comprehensive tests for HashTable."""

    @pytest.fixture
    def manager(self):
        """Return multiprocessing Manager instance."""
        with Manager() as manager:
            yield manager

    @pytest.fixture
    def table(self, manager):
        """Return empty HashTable instance."""
        return MultiThreadingHashTable(manager)

    @pytest.fixture
    def no_resize_table(self, manager):
        """Return HashTable with resize disabled."""
        table = MultiThreadingHashTable(manager)
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

    @pytest.mark.parametrize(
        "table_size, keys",
        [
            (2, ["a", "b", "c"]),
            (3, ["a", "b", "c", "d", "e"]),
            (5, ["a", "b", "c"]),
            (1, ["a", "b"]),
            (4, list("abcdefgh")),
        ],
    )
    def test_collision_distribution_basic(
        self, manager, no_resize_table, table_size, keys
    ):
        """Test that all keys are stored correctly despite collisions."""
        no_resize_table._table_size.value = table_size
        no_resize_table._buckets[:] = [manager.list() for _ in range(table_size)]

        for key in keys:
            no_resize_table[key] = f"value_{key}"

        bucket_sizes = []

        for bucket in no_resize_table._buckets:
            bucket_sizes.append(len(bucket))

        assert len(bucket_sizes) == table_size
        assert sum(bucket_sizes) == len(keys)

        for key in keys:
            assert no_resize_table[key] == f"value_{key}"

    @pytest.mark.parametrize(
        "table_size, keys, expected_conditions",
        [
            # (table_size, keys, [(min_buckets_with_data, max_bucket_size)])
            (2, ["a", "b", "c"], (1, 3)),
            (3, ["a", "b", "c", "d", "e"], (1, 5)),
            (5, ["a", "b", "c"], (1, 3)),
            (1, ["a", "b"], (1, 2)),
        ],
    )
    def test_collision_distribution_advanced(
        self, manager, no_resize_table, table_size, keys, expected_conditions
    ):
        """Test collision distribution with realistic expectations."""
        no_resize_table._table_size.value = table_size
        no_resize_table._buckets[:] = [manager.list() for _ in range(table_size)]

        for key in keys:
            no_resize_table[key] = f"value_{key}"

        bucket_sizes = []

        for bucket in no_resize_table._buckets:
            bucket_sizes.append(len(bucket))

        non_empty_buckets = sum(1 for size in bucket_sizes if size > 0)
        max_bucket_size = max(bucket_sizes)

        min_expected_buckets, max_expected_single_bucket = expected_conditions

        assert non_empty_buckets >= min_expected_buckets
        assert max_bucket_size <= max_expected_single_bucket
        assert sum(bucket_sizes) == len(keys)

    @pytest.mark.parametrize(
        "initial_size, load_factor, elements_to_add",
        [(4, 0.75, 4), (8, 0.5, 5), (10, 0.8, 9), (16, 0.9, 15)],
    )
    def test_auto_resize_scenarios(
        self, manager, initial_size, load_factor, elements_to_add
    ):
        """Test automatic resizing in different scenarios."""
        table = MultiThreadingHashTable(
            manager, initial_size=initial_size, load_factor=load_factor
        )
        original_size = table._table_size.value

        for i in range(elements_to_add):
            table[f"key_{i}"] = i

        assert table._table_size.value == original_size

        table["resize_trigger"] = "resize!!!"

        assert table._table_size.value == 2 * original_size

        for i in range(elements_to_add):
            assert table[f"key_{i}"] == i

    @pytest.mark.parametrize(
        "initial_size, load_factor, elements_to_add",
        [
            (8, 0.75, 5),  # No resize (5/8 = 0.625 < 0.75)
            (10, 0.8, 7),  # No resize (7/10 = 0.7 < 0.8)
            (16, 0.9, 14),  # No resize (14/16 = 0.875 < 0.9)
            (20, 0.75, 14),  # No resize (14/20 = 0.7 < 0.75)
        ],
    )
    def test_no_resize_scenarios(
        self, manager, initial_size, load_factor, elements_to_add
    ):
        """Test that resize doesn't happen when not needed."""
        table = MultiThreadingHashTable(
            manager, initial_size=initial_size, load_factor=load_factor
        )
        original_size = table._table_size.value
        for i in range(elements_to_add):
            table[f"key_{i}"] = i

        assert table._table_size.value == original_size

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

        assert set(table.keys()) == set(test_data.keys())
        assert set(table.values()) == set(test_data.values())
        assert set(table.items()) == set(test_data.items())

        for key, value in test_data.items():
            assert table.get(key) == value

        assert table.get("missing_key") is None
        assert table.get("missing_key", "default") == "default"

    @pytest.mark.parametrize(
        "test_data, key_to_remove",
        [
            ({"a": 1, "b": 2, "c": 3}, "b"),
            ({"x": 10, "y": 20, "z": 30}, "x"),
            ({"first": "1st", "second": "2nd", "third": "3rd"}, "second"),
        ],
    )
    def test_pop_method(self, table, test_data, key_to_remove):
        """Test pop method with different data."""
        for key, value in test_data.items():
            table[key] = value

        expected_value = test_data[key_to_remove]
        popped_value = table.pop(key_to_remove)

        assert popped_value == expected_value
        assert key_to_remove not in table
        assert len(table) == len(test_data) - 1

    @pytest.mark.parametrize(
        "initial_size, expected_error",
        [
            (0, "Table size should be positive number"),
            (-1, "Table size should be positive number"),
        ],
    )
    def test_invalid_initial_size(self, manager, initial_size, expected_error):
        """Test invalid initial size parameters."""
        with pytest.raises(ValueError, match=expected_error):
            MultiThreadingHashTable(manager, initial_size=initial_size)

    @pytest.mark.parametrize(
        "load_factor, expected_error",
        [
            (0, "Load factor should be between 0 and 1"),
            (1, "Load factor should be between 0 and 1"),
        ],
    )
    def test_invalid_load_factor(self, manager, load_factor, expected_error):
        """Test invalid load factor parameters."""
        with pytest.raises(ValueError, match=expected_error):
            MultiThreadingHashTable(manager, load_factor=load_factor)


@pytest.fixture
def manager():
    """Return multiprocessing Manager instance."""
    with Manager() as manager:
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
    table = MultiThreadingHashTable(manager)

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
