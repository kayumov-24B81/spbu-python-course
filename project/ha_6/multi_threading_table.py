from collections.abc import MutableMapping
from typing import Any, List, Tuple, Iterator, cast
from multiprocessing import Manager
from multiprocessing.managers import ValueProxy
import threading


class MultiThreadingHashTable(MutableMapping):
    """
    A thread-safe and process-safe hash table implementation using multiprocessing.Manager
    for shared state between processes. Supports dictionary-like interface with separate
    chaining for collision resolution.

    This implementation uses fine-grained locking for high concurrency and multiprocessing
    Manager for inter-process communication.

    Attributes:
        _size (ValueProxy[int]): Shared integer tracking number of key-value pairs
        _table_size (ValueProxy[int]): Shared integer for current internal array size
        _load_factor (float): Maximum load factor before resizing (0.0 to 1.0)
        _buckets (ListProxy[List[Tuple[Any, Any]]]): Shared list of buckets storing key-value pairs
        _bucket_locks (ListProxy[threading.RLock]): Shared list of locks for each bucket
        _resize_lock (threading.RLock): Lock for resize operations to prevent deadlocks

    Example:
        with Manager() as manager:
            ht = MultiThreadingHashTable(manager)
            ht['key1'] = 'value1'
            print(ht['key1'])  # 'value1'
            print(len(ht))     # 1
    """

    def __init__(self, manager: Manager, initial_size: int = 8, load_factor: float = 0.75):  # type: ignore
        """
        Initialize the multi-threading hash table with shared state.

        Args:
            manager: multiprocessing Manager instance for creating shared objects
            initial_size: Initial size of the internal array. Must be positive.
            load_factor: Load factor threshold for triggering resizing (0.0 to 1.0).

        Raises:
            ValueError: If initial_size is less than 1 or load_factor is not between 0 and 1.

        Note:
            The manager parameter is required to enable inter-process communication.
            All internal state is created through the manager to ensure process safety.
        """
        if initial_size < 1:
            raise ValueError("Table size should be positive number")
        if not 0 < load_factor < 1:
            raise ValueError("Load factor should be between 0 and 1")

        self._size: ValueProxy[int] = cast(Any, manager).Value("i", 0)
        self._table_size: ValueProxy[int] = cast(Any, manager).Value("i", initial_size)
        self._load_factor: float = load_factor

        self._buckets = cast(Any, manager).list(
            [cast(Any, manager).list() for _ in range(initial_size)]
        )

        self._bucket_locks = cast(Any, manager).list(
            [cast(Any, manager).RLock() for _ in range(initial_size)]
        )
        self._resize_lock = cast(Any, manager).RLock()

    def _hash(self, key: Any) -> int:
        """
        Compute hash of the key and convert it to table index.
        Args:
            key: Key to hash. Must be hashable.

        Returns:
            Index in the range [0, table_size - 1] for bucket access.
        """
        return abs(hash(key)) % self._table_size.value

    def _resize_needed(self) -> bool:
        """
        Check if the table needs to be resized based on current load factor.

        Returns:
            True if current load factor exceeds threshold, False otherwise.
        """
        current_load: float = self._size.value / self._table_size.value
        return current_load > self._load_factor

    def _resize(self, new_size: int) -> None:
        """
        Resize the table and rehash all elements in a thread-safe and process-safe manner.

        This operation acquires all locks to ensure consistency during the resize process.

        Args:
            new_size: New size for the internal array. Must be larger than current size.

        Note:
            This is a costly operation that blocks all other operations temporarily.
        """
        self._resize_lock.acquire()
        try:
            for lock in self._bucket_locks:
                lock.acquire()

            try:
                old_buckets: List[List[Tuple[int, Any]]] = list(self._buckets)
                old_locks: List[threading.RLock] = list(self._bucket_locks)

                self._table_size.value = new_size
                self._buckets[:] = [
                    self._buckets._manager.list() for _ in range(new_size)
                ]
                self._bucket_locks[:] = [
                    self._bucket_locks._manager.RLock() for _ in range(new_size)
                ]
                self._size.value = 0

                for bucket in old_buckets:
                    for key, value in bucket:
                        self[key] = value
            finally:
                for lock in old_locks:
                    lock.release()
        finally:
            self._resize_lock.release()

    def __setitem__(self, key: Any, value: Any) -> None:
        """
        Set value for key. If key exists, update its value.

        Args:
            key: Key to set or update. Must be hashable.
            value: Value to associate with the key.
        """
        if self._resize_needed():
            self._resize(self._table_size.value * 2)

        index: int = self._hash(key)

        lock = self._bucket_locks[index]
        lock.acquire()

        try:
            bucket: List[Tuple[int, Any]] = self._buckets[index]

            for i, (existing_key, existing_value) in enumerate(bucket):
                if existing_key == key:
                    bucket[i] = (key, value)
                    return

            bucket.append((key, value))
            self._size.value += 1
        finally:
            lock.release()

    def __getitem__(self, key: Any) -> Any:
        """
        Get value for key.

        Args:
            key: Key to search for.

        Returns:
            Value associated with the key.

        Raises:
            KeyError: If the key is not found in the hash table.

        Note:
            This operation uses a shared lock for the specific bucket, allowing
            concurrent reads from different buckets.
        """
        index: int = self._hash(key)

        lock = self._bucket_locks[index]
        lock.acquire()

        try:
            bucket: List[Tuple[int, Any]] = self._buckets[index]

            for (existing_key, value) in bucket:
                if existing_key == key:
                    return value

            raise KeyError(f"Key {key} was not found in hash table!")
        finally:
            lock.release()

    def __delitem__(self, key: Any) -> None:
        """
        Delete key and its associated value.

        Args:
            key: Key to delete.

        Raises:
            KeyError: If the key is not found in the hash table.
        """
        index: int = self._hash(key)

        lock = self._bucket_locks[index]
        lock.acquire()

        try:
            bucket: List[Tuple[int, Any]] = self._buckets[index]

            for i, (existing_key, value) in enumerate(bucket):
                if existing_key == key:
                    del bucket[i]
                    self._size.value -= 1
                    return

            raise KeyError(f"Key {key} was not found in hash table!")
        finally:
            lock.release()

    def __contains__(self, key: Any) -> bool:
        """
        Check if key exists in table.

        Args:
            key: Key to check for existence.

        Returns:
            True if key exists in the table, False otherwise.
        """
        try:
            index: int = self._hash(key)
            with self._bucket_locks[index]:
                bucket: List[Tuple[Any, Any]] = self._buckets[index]
                return any(existing_key == key for (existing_key, value) in bucket)

        except (KeyError, IndexError):
            return False

    def __iter__(self) -> Iterator[Any]:
        """
        Return iterator over all keys in table.

        Creates a consistent snapshot of all keys by acquiring all locks,
        then returns an iterator over the snapshot without holding locks.

        Returns:
            Iterator over all keys in the hash table.

        Note:
            This operation blocks all other operations temporarily while
            creating the snapshot to ensure consistency.
        """
        self._resize_lock.acquire()
        try:
            for lock in self._bucket_locks:
                lock.acquire()

            try:
                keys = []
                for bucket in self._buckets:
                    for (key, value) in bucket:
                        keys.append(key)
                return iter(keys)
            finally:
                for lock in self._bucket_locks:
                    lock.release()
        finally:
            self._resize_lock.release()

    def __len__(self) -> int:
        """
        Return number of elements in table.

        Returns:
            Number of key-value pairs in the hash table.
        """
        return self._size.value

    def __repr__(self) -> str:
        """
        Return string representation of table in dictionary format.

        Returns:
            String representation showing all key-value pairs.

        Note:
            This uses the __iter__ and __getitem__ methods which are thread-safe.
        """
        items: List[str] = []
        for key in self:
            items.append(f"{key}: {self[key]}")
        return "{" + ", ".join(items) + "}"
