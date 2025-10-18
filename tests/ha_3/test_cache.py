import pytest
from project.ha_3.currying import cache
from collections import OrderedDict


class TestCacheBasic:
    def test_cache_basic_usage(self):
        call_counter = 0

        @cache(limit=3)
        def function(x):
            nonlocal call_counter
            call_counter += 1
            return 2 * x

        assert function(1) == 2
        assert call_counter == 1

        assert function(1) == 2
        assert call_counter == 1

    def test_cache_different_args(self):
        call_counter = 0

        @cache(limit=3)
        def function(x, y):
            nonlocal call_counter
            call_counter += 1
            return x * y

        assert function(1, 2) == 2
        assert call_counter == 1

        assert function(3, 1) == 3
        assert call_counter == 2

        assert function(1, 2) == 2
        assert call_counter == 2

    def test_cache_disabled(self):
        call_counter = 0

        @cache()
        def function(x):
            nonlocal call_counter
            call_counter += 1
            return x - 1

        assert function(1) == 0
        assert call_counter == 1

        assert function(1) == 0
        assert call_counter == 2

    def test_cache_LRU_eviction(self):
        call_counter = 0

        @cache(limit=2)
        def function(x):
            nonlocal call_counter
            call_counter += 1
            return x

        function(1)  # computes
        function(2)  # computes
        function(1)  # takes from cache and moves to first position in list
        function(3)  # computes and evicts 2

        function(2)  # computes

        assert call_counter == 4

    def test_cache_with_kwargs(self):
        call_counter = 0

        @cache(limit=3)
        def function(a, b=0):
            nonlocal call_counter
            call_counter += 1
            return a + b

        assert function(1) == 1
        assert function(1, b=2) == 3
        assert function(1, b=0) == 1
        assert call_counter == 2

    def test_cache_with_unhashable(self):
        call_counter = 0

        @cache(limit=2)
        def function(data):
            nonlocal call_counter
            call_counter += 1
            return len(data)

        assert function([1, 2, 3]) == 3
        assert function([1, 2, 3]) == 3
        assert call_counter == 1

        assert function({"a": 1}) == 1
        assert call_counter == 2

    def test_cache_with_class(self):
        call_counter = 0

        class Dummy:
            def __init__(self, name):
                self.name = name

        @cache(limit=2)
        def function(object):
            nonlocal call_counter
            call_counter += 1
            return object.name

        bob = Dummy("bob")

        assert function(bob) == "bob"
        assert function(bob) == "bob"

        assert call_counter == 1

    def test_cache_metadata_preservation(self):
        @cache(limit=1)
        def example(x):
            """Function for tests"""
            return x

        assert example.__name__ == "example"
        assert example.__doc__ == "Function for tests"
