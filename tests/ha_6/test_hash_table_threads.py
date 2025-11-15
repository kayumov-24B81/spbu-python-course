import pytest
import threading
import time
import random
from multiprocessing import Manager
from project.ha_6.multi_threading_table import MultiThreadingHashTable


class TestMultiThreadingHashTable:
    """Comprehensive tests for MultiThreadingHashTable in multi-threaded environment."""

    @pytest.fixture
    def manager(self):
        """Return multiprocessing Manager instance."""
        with Manager() as manager:
            yield manager

    @pytest.fixture
    def table(self, manager):
        """Return empty MultiThreadingHashTable instance."""
        return MultiThreadingHashTable(manager)

    def test_concurrent_inserts_no_data_loss(self, table):
        """Test that no data is lost during concurrent insertions."""
        num_threads = 10
        inserts_per_thread = 100
        total_operations = num_threads * inserts_per_thread

        inserted_keys = set()
        insertion_errors = []
        lock = threading.Lock()

        def insert_worker(thread_id):
            for i in range(inserts_per_thread):
                key = f"thread_{thread_id}_key_{i}"
                value = f"value_{thread_id}_{i}"
                try:
                    table[key] = value
                    with lock:
                        inserted_keys.add(key)
                except Exception as e:
                    insertion_errors.append(str(e))

        threads = []

        for i in range(num_threads):
            thread = threading.Thread(target=insert_worker, args=(i,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        assert len(insertion_errors) == 0
        assert len(table) == total_operations

        for thread_id in range(num_threads):
            for i in range(inserts_per_thread):
                key = f"thread_{thread_id}_key_{i}"
                expected_value = f"value_{thread_id}_{i}"
                assert table[key] == expected_value

    def test_concurrent_updates_consistency(self, table):
        """Test that concurrent updates maintain consistency."""
        initial_data = {f"key_{i}": f"initial_{i}" for i in range(50)}
        for key, value in initial_data.items():
            table[key] = value

        num_threads = 5
        updates_per_thread = 15
        update_errors = []

        def update_worker(thread_id):
            for i in range(updates_per_thread):
                key = f"key_{i % 50}"
                new_value = f"updated_by_{thread_id}_{i}"
                try:
                    table[key] = new_value
                    current_value = table[key]
                    if not current_value.startswith("updated_by_"):
                        update_errors.append(
                            f"Unexpected value: {key} : {current_value}"
                        )

                except Exception as e:
                    update_errors.append(str(e))

        threads = []
        for i in range(num_threads):
            thread = threading.Thread(target=update_worker, args=(i,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        assert len(update_errors) == 0

        for i in range(50):
            key = f"key_{i}"
            assert key in table

    def test_concurrent_reads_and_writes(self, table):
        """Test mixed read and write operations concurrently."""
        num_threads = 8
        operations_per_thread = 50

        read_errors = []
        write_errors = []
        read_count = [0]
        write_count = [0]
        read_lock = threading.Lock()
        write_lock = threading.Lock()

        def read_write_worker(thread_id):
            for i in range(operations_per_thread):
                operation = random.choice(["read", "write"])
                key = f"key_{i % 20}"

                if operation == "write":
                    value = f"value_{thread_id}_{i}"
                    try:
                        table[key] = value
                        with write_lock:
                            write_count[0] += 1
                    except Exception as e:
                        write_errors.append(str(e))
                else:
                    try:
                        value = table.get(key, "default")
                        with read_lock:
                            read_count[0] += 1
                        if value != "default" and not isinstance(value, str):
                            read_errors.append(
                                f"Invalid value type: {key} : {type(value)}"
                            )
                    except Exception as e:
                        read_errors.append(str(e))

        threads = []
        for i in range(num_threads):
            thread = threading.Thread(target=read_write_worker, args=(i,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        assert len(read_errors) == 0
        assert len(write_errors) == 0

        assert read_count[0] > 0
        assert write_count[0] > 0

    def test_lock_contention_atomic_operations(self, table):
        """Test that locks prevent race conditions in atomic operations."""
        num_threads = 10
        increments_per_thread = 100

        table["counter"] = 0

        def increment_worker():
            for _ in range(increments_per_thread):
                with table._resize_lock:
                    current = table["counter"]
                    table["counter"] = current + 1

        threads = []

        for _ in range(num_threads):
            thread = threading.Thread(target=increment_worker)
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        expected_count = num_threads * increments_per_thread
        actual_count = table["counter"]

        assert actual_count == expected_count

    def test_concurrent_deletions(self, table):
        """Test that concurrent deletions work correctly."""
        num_keys = 100

        initial_keys = [f"key_{i}" for i in range(num_keys)]
        for key in initial_keys:
            table[key] = f"value_{key}"

        num_threads = 4
        deletion_errors = []
        deleted_keys = []
        deletion_lock = threading.Lock()

        def delete_worker(thread_id):
            keys_per_thread = num_keys // num_threads
            start_index = thread_id * keys_per_thread
            end_index = start_index + keys_per_thread

            for i in range(start_index, end_index):
                key = initial_keys[i]
                try:
                    del table[key]
                    with deletion_lock:
                        deleted_keys.append(key)
                except KeyError:
                    pass
                except Exception as e:
                    deletion_errors.append(str(e))

        threads = []
        for i in range(num_threads):
            thread = threading.Thread(target=delete_worker, args=(i,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        assert len(deletion_errors) == 0

        for key in initial_keys:
            assert key not in table

    def test_iteration_thread_safety(self, table):
        """Test that iteration works correctly in multi-threaded environment."""
        for i in range(50):
            table[f"key_{i}"] = f"value_{i}"

        iteration_errors = []
        modification_errors = []
        iterations_completed = [0]

        def iteration_worker():
            try:
                snapshot = list(table.items())

                keys_from_items = [item[0] for item in snapshot]
                values_from_items = [item[1] for item in snapshot]

                if len(keys_from_items) != len(values_from_items):
                    iteration_errors.append(
                        "Keys and values length mismatch in items snapshot"
                    )

                count = 0
                for key in table:
                    count += 1
                    if count > 1000:
                        break

                iterations_completed[0] += 1

            except Exception as e:
                iteration_errors.append(f"Iteration errors: {str(e)}")

        def modification_worker():
            try:
                for i in range(20):
                    table[f"mod_key_{i}"] = f"mod_value_{i}"
                    if i % 3 == 0 and f"mod_key_{i}" in table:
                        try:
                            del table[f"mod_key_{i}"]
                        except KeyError:
                            pass
            except Exception as e:
                modification_errors.append(f"Modification error: {str(e)}")

        iter_threads = []
        for _ in range(3):
            thread = threading.Thread(target=iteration_worker)
            iter_threads.append(thread)
            thread.start()

        mod_threads = []
        for _ in range(3):
            thread = threading.Thread(target=modification_worker)
            mod_threads.append(thread)
            thread.start()

        for thread in iter_threads + mod_threads:
            thread.join()

        assert len(iteration_errors) == 0
        assert len(modification_errors) == 0
        assert iterations_completed[0] > 0

    def test_resize_during_concurrent_operations(self, manager):
        """Test  that resize operations work correctly during concurrent acess"""
        table = MultiThreadingHashTable(manager, initial_size=4, load_factor=0.5)

        num_threads = 6
        operations_per_thread = 30
        resize_errors = []

        def worker(thread_id):
            for i in range(operations_per_thread):
                try:
                    key = f"key_{thread_id}_{i}"
                    table[key] = f"value_{thread_id}_{i}"

                    if i % 5 == 0:
                        _ = table.get(key, None)

                    if i % 7 == 0 and i > 0:
                        del_key = f"key_{thread_id}_{i - 1}"
                        if del_key in table:
                            del table[del_key]

                except Exception as e:
                    resize_errors.append(f"Thread {thread_id} error: {str(e)}")

        threads = []
        for i in range(num_threads):
            thread = threading.Thread(target=worker, args=(i,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        total_expected = num_threads * operations_per_thread

        assert len(resize_errors) == 0
        assert len(table) > 0
        assert len(table) <= total_expected

    def test_deadlock_prevention(self, table):
        """Test that the implementation is free from deadlocks"""
        for i in range(20):
            table[f"key_{i}"] = f"value_{i}"

        num_threads = 5
        operations_per_thread = 40
        completed_operations = [0]
        deadlock_detected = [False]

        def complex_worker(thread_id):
            for i in range(operations_per_thread):
                try:
                    key1 = f"key{(thread_id + i) % 20}"
                    key2 = f"key{(thread_id + i + 1) % 20}"

                    table[key1] = f"new_value_{thread_id}_{i}"
                    _ = table[key2]

                    if i % 5 == 0:
                        del_key = f"key_{(thread_id + i + 2) % 20}"
                        if del_key in table:
                            del table[del_key]

                    completed_operations[0] += 1

                except Exception as e:
                    if "deadlock" in str(e).lower():
                        deadlock_detected[0] = True
                    completed_operations[0] += 1

        threads = []
        for i in range(num_threads):
            thread = threading.Thread(target=complex_worker, args=(i,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join(timeout=10.0)
            if thread.is_alive():
                deadlock_detected[0] = True

        expected_min_operations = (
            num_threads * operations_per_thread * 0.8
        )  # 80% success rate

        assert not deadlock_detected[0]
        assert completed_operations[0] >= expected_min_operations


@pytest.fixture
def manager():
    """Return multiprocessing Manager instance."""
    with Manager() as manager:
        yield manager


@pytest.fixture
def table(manager):
    """Return empty MultiThreadingHashTable instance."""
    return MultiThreadingHashTable(manager)


def test_all_operations_concurrently(table):
    """Test demonstrating real parallel execution by measuring performance
    under high thread contention with minimal keys."""
    num_threads = 15
    operations_per_thread = 200
    errors = []
    execution_times = []
    error_lock = threading.Lock()
    time_lock = threading.Lock()

    keys = ["key_1", "key_2", "key_3"]

    def worker(thread_id):
        local_errors = []
        start_time = time.time()
        try:
            for i in range(operations_per_thread):
                key = keys[i % len(keys)]
                operation_type = (thread_id + i) % 5

                if operation_type == 0:
                    table[key] = f"writer_{thread_id}_{i}"
                elif operation_type == 1:
                    try:
                        value = table[key]
                        assert isinstance(value, str)
                    except KeyError:
                        pass
                elif operation_type == 2:
                    try:
                        del table[key]
                    except KeyError:
                        pass
                elif operation_type == 3:
                    _ = key in table
                else:
                    table[key] = f"mixed_{thread_id}_{i}"
                    try:
                        value = table[key]
                    except KeyError:
                        pass

        except Exception as e:
            local_errors.append(f"Thread {thread_id}: {e}")

        end_time = time.time()

        with error_lock:
            errors.extend(local_errors)
        with time_lock:
            execution_times.append(end_time - start_time)

    start_total = time.time()

    threads = []
    for i in range(num_threads):
        thread = threading.Thread(target=worker, args=(i,))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    total_time = time.time() - start_total
    avg_thread_time = sum(execution_times) / len(execution_times)

    is_parallel = total_time < avg_thread_time * num_threads * 0.8

    assert len(errors) == 0
    assert is_parallel
    assert total_time > 0.001


def test_sneaky_pie_recipe():
    def print_black(text):
        BLACK = "\033[30m"
        RESET = "\033[0m"
        print(f"{BLACK}{text}{RESET}")

    print_black(
        "3 яйца, 1 ст муки, 1 не полный стакан сахара. "
        "Все смешать. 0.5 ч. ложки разрыхлителя. "
        "На форму положить пероаментную бумагу если есть. Можно и без. "
        "Форму смазать сливочным маслом. "
        "Положить яблоки, сверху налить тесто. Дать постоять 10 мин. "
        "Выпекать в разогретой духовке 150 гр. 30-40 мин."
    )
    pie_is_yummy = True
    assert pie_is_yummy
