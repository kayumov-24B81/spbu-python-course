from project.ha_6.multi_threading_table import HashTableManager, MultiThreadingHashTable
from multiprocessing import Manager, Process


def worker_insert(process_id, table, count):
    """Insert count key-value pairs into the table from a worker process."""
    for i in range(count):
        key = f"key_{process_id}_{i}"
        value = f"value_{process_id}_{i}"
        table[key] = value


def worker_update(process_id, table, count):
    """Update existing keys in the table from a worker process."""
    for i in range(count):
        key = f"key_{process_id}_{i}"
        if key in table:
            table[key] = f"updated_{process_id}_{i}"


def worker_delete(process_id, table, count):
    """Delete keys from the table from a worker process."""
    deleted_count = 0
    for i in range(count):
        key = f"key_{process_id}_{i}"
        try:
            if key in table:
                del table[key]
                deleted_count += 1
        except KeyError:
            pass
        except Exception as e:
            print(f"Delete error for {key}: {e}")


def mixed_worker(pid, table, count):
    """Mixed worker."""
    for i in range(count):
        key = f"mixed_{pid}_{i}"

        if i % 5 == 0:
            table[key] = f"data_{pid}_{i}"

        elif i % 5 == 1:
            try:
                _ = table[key]
            except KeyError:
                pass

        elif i % 5 == 2:
            if key in table:
                table[key] = f"updated_{pid}_{i}"

        elif i % 5 == 3:
            other_key = f"mixed_{pid}_{(i + 1) % count}"
            try:
                _ = table[other_key]
            except KeyError:
                pass

        else:
            if i % 25 == 0:
                try:
                    del table[key]
                except KeyError:
                    pass


def verify_data_integrity(table, expected_data):
    """Verify that table contains exactly the expected data."""
    assert len(table) == len(expected_data)

    for key, expected_value in expected_data.items():
        assert key in table
        assert table[key] == expected_value

    for key in table:
        assert key in expected_data


class TestTableProcesses:
    """Test suite for multiprocess hash table operations."""

    def test_multiprocess_basic_insert(self):
        """Test concurrent insert operations from multiple processes."""
        with HashTableManager() as manager:
            ht = manager.MultiThreadingHashTable()

            processes = []
            for i in range(4):
                p = Process(target=worker_insert, args=(i, ht, 25))
                processes.append(p)
                p.start()

            for p in processes:
                p.join()

            expected_data = {}
            for i in range(4):
                for j in range(25):
                    key = f"key_{i}_{j}"
                    expected_data[key] = f"value_{i}_{j}"

            verify_data_integrity(ht, expected_data)

    def test_multiprocess_concurrent_updates(self):
        """Test concurrent update operations from multiple processes."""
        with HashTableManager() as manager:
            ht = manager.MultiThreadingHashTable()

            initial_data = {}
            for i in range(4):
                for j in range(25):
                    key = f"key_{i}_{j}"
                    value = f"initial_{i}_{j}"
                    ht[key] = value
                    initial_data[key] = value

            verify_data_integrity(ht, initial_data)

            processes = []
            for i in range(4):
                p = Process(target=worker_update, args=(i, ht, 25))
                processes.append(p)
                p.start()

            for p in processes:
                p.join()

            updated_data = {}
            for i in range(4):
                for j in range(25):
                    key = f"key_{i}_{j}"
                    updated_data[key] = f"updated_{i}_{j}"

            verify_data_integrity(ht, updated_data)

    def test_multiprocess_deletion_integrity(self):
        """Test concurrent delete operations and data integrity."""
        with HashTableManager() as manager:
            ht = manager.MultiThreadingHashTable()

            initial_data = {}
            for i in range(4):
                for j in range(25):
                    key = f"key_{i}_{j}"
                    value = f"value_{i}_{j}"
                    ht[key] = value
                    initial_data[key] = value

            verify_data_integrity(ht, initial_data)

            processes = []
            for i in range(2):
                p = Process(target=worker_delete, args=(i, ht, 25))
                processes.append(p)
                p.start()

            for p in processes:
                p.join()

            remaining_data = {}
            for i in range(2, 4):
                for j in range(25):
                    key = f"key_{i}_{j}"
                    remaining_data[key] = f"value_{i}_{j}"

            verify_data_integrity(ht, remaining_data)

    def test_multiprocess_mixed_operations(self):
        """Test mixed operations (insert, read, update, delete) from multiple processes."""
        with HashTableManager() as manager:
            ht = manager.MultiThreadingHashTable()

            processes = []
            for i in range(3):
                p = Process(target=mixed_worker, args=(i, ht, 40))
                processes.append(p)
                p.start()

            for p in processes:
                p.join()

            final_data = {}
            operations_count = 40

            for i in range(3):
                for j in range(operations_count):
                    key = f"mixed_{i}_{j}"

                    if j % 5 == 0:
                        final_data[key] = f"data_{i}_{j}"

                    elif j % 5 == 2:
                        if key in final_data:
                            final_data[key] = f"updated_{i}_{j}"

                    elif j % 5 == 4:
                        if j % 25 == 0 and key in final_data:
                            del final_data[key]

            assert len(ht) == len(final_data)

            for key, expected_value in final_data.items():
                assert key in ht
                assert ht[key] == expected_value

            for key in ht:
                assert key in final_data
