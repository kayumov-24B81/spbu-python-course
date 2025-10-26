from collections.abc import MutableMapping
from typing import Any, List, Tuple, Iterator


class HashTable(MutableMapping):
    """
    Hash table implementation with separate chaining for collision resolution.
    Inherits from MutableMapping to get dictionary-like interface.

    Attributes:
        _size: number of key-value pairs in the table
        _table_size: current size of the internal array
        _load_factor: maximum load factor before resizing
        _buckets: array of buckets (lists) storing key-value pairs
    """

    def __init__(self, initial_size: int = 8, load_factor: float = 0.75):
        """
        Initialize the hash table.

        Args:
            initial_size: initial size of the internal array
            load_factor: load factor threshold for triggering resizing

        Raises:
            ValueError: if initial_size < 1 or load_factor not between 0 and 1
        """
        if initial_size < 1:
            raise ValueError("Table size should be positive number")
        if not 0 < load_factor < 1:
            raise ValueError("Load factor should be between 0 and 1")

        self._size = 0
        self._table_size = initial_size
        self._load_factor = load_factor
        self._buckets = [[] for _ in range(self._table_size)]

    def _hash(self, key: Any) -> int:
        """
        Compute hash of the key and convert it to table index.

        Args:
            key: key to hash

        Returns:
            index in range [0, table_size - 1]
        """
        return abs(hash(key)) % self._table_size

    def _resize_needed(self) -> bool:
        """
        Check if table needs to be resized.

        Returns:
            True if current load factor exceeds threshold, False otherwise
        """
        current_load: float = self._size / self._table_size
        return current_load > self._load_factor

    def _resize(self, new_size: int) -> None:
        """
        Resize the table and rehash all elements.

        Args:
            new_size: new size for the table
        """
        old_buckets: List[Tuple[int, Any]] = self._buckets

        self._table_size = new_size
        self._buckets = [[] for _ in range(self._table_size)]
        self._size = 0

        for bucket in old_buckets:
            for key, value in bucket:
                self[key] = value

    def __setitem__(self, key: Any, value: Any) -> None:
        """
        Set value for key. If key exists, update its value.

        Args:
            key: key to set
            value: value to associate with key
        """
        if self._resize_needed():
            self._resize(self._table_size * 2)

        index: int = self._hash(key)
        bucket: List[Tuple[int, Any]] = self._buckets[index]

        for i, (existing_key, existing_value) in enumerate(bucket):
            if existing_key == key:
                bucket[i] = (key, value)
                return

        bucket.append((key, value))
        self._size += 1

    def __getitem__(self, key: Any) -> Any:
        """
        Get value for key.

        Args:
            key: key to search for

        Returns:
            value associated with key

        Raises:
            KeyError: if key is not found
        """
        index: int = self._hash(key)
        bucket: List[Tuple[int, Any]] = self._buckets[index]

        for existing_key, value in bucket:
            if existing_key == key:
                return value

        raise KeyError(f"Key {key} was not found in hash table!")

    def __delitem__(self, key: Any) -> None:
        """
        Delete key and its associated value.

        Args:
            key: key to delete

        Raises:
            KeyError: if key is not found
        """
        index: int = self._hash(key)
        bucket: List[Tuple[int, Any]] = self._buckets[index]

        for i, (existing_key, value) in enumerate(bucket):
            if existing_key == key:
                del bucket[i]
                self._size -= 1
                return

        raise KeyError(f"Key {key} was not found in hash table!")

    def __contains__(self, key: Any) -> bool:
        """
        Check if key exists in table.

        Args:
            key: key to check

        Returns:
            True if key exists, False otherwise
        """
        try:
            _: Any = self[key]
            return True
        except KeyError:
            return False

    def __iter__(self) -> Iterator[Any]:
        """
        Return iterator over all keys in table.

        Returns:
            iterator of keys
        """
        for bucket in self._buckets:
            for key, value in bucket:
                yield key

    def __len__(self) -> int:
        """
        Return number of elements in table.

        Returns:
            number of key-value pairs
        """
        return self._size

    def __repr__(self) -> str:
        """
        Return string representation of table.

        Returns:
            string representation in dictionary format
        """
        items: List[str] = []
        for bucket in self._buckets:
            for key, value in bucket:
                items.append(f"{key}: {value}")
        return "{" + ", ".join(items) + "}"
