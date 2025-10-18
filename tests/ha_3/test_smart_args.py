import pytest
from project.ha_3.smart_args import smart_args, Evaluated, Isolated
import random


class TestSpecs:
    """Specification examples tests."""

    def test_spec_isolated(self):
        """Isolated should copy mutable args, preserving originals."""

        @smart_args()
        def check_isolation(*, d=Isolated):
            d["a"] = 0
            return d

        no_mutable = {"a": 10}

        assert check_isolation(d=no_mutable) == {"a": 0}
        assert no_mutable == {"a": 10}

    def test_spec_evaluated(self):
        """Evaluated should recompute values, normal defaults should not."""
        random.seed(11)
        call_counter = 0

        def get_random_number():
            nonlocal call_counter
            call_counter += 1
            return random.randint(0, 100)

        results = []

        @smart_args()
        def check_evaluation(*, x=get_random_number(), y=Evaluated(get_random_number)):
            results.append((x, y))

        check_evaluation()
        check_evaluation()
        check_evaluation(y=150)

        assert call_counter == 3
        assert results[0][0] == results[1][0] == results[2][0]
        assert results[0][1] != results[1][1]
        assert results[2][1] == 150


class TestEvaluated:
    """Evaluated functionality tests."""

    def test_evaluated_basic(self):
        """Evaluated should compute new value each call."""
        call_counter = 0

        def get_value():
            nonlocal call_counter
            call_counter += 1
            return call_counter * 10

        @smart_args()
        def function(*, value=Evaluated(get_value)):
            return value

        assert function() == 10
        assert function() == 20
        assert call_counter == 2

    def test_evaluated_with_provided_arg(self):
        """Provided arguments should skip Evaluated computation."""
        call_counter = 0

        def get_value():
            nonlocal call_counter
            call_counter += 1
            return 11

        @smart_args()
        def function(*, value=Evaluated(get_value)):
            return value

        assert function(value=2) == 2
        assert call_counter == 0

    def test_evaluated_multiple(self):
        """Multiple Evaluated params should work independently."""
        call_counter_a = 0
        call_counter_b = 0

        def get_a():
            nonlocal call_counter_a
            call_counter_a += 1
            return call_counter_a

        def get_b():
            nonlocal call_counter_b
            call_counter_b += 1
            return call_counter_b + 5

        @smart_args()
        def function(*, a=Evaluated(get_a), b=Evaluated(get_b)):
            return a + b

        assert function() == 7
        assert function() == 9
        assert function(a=100) == 108
        assert call_counter_a == 2
        assert call_counter_b == 3


class TestIsolated:
    """Isolated functionality tests."""

    def test_isolated_basic(self):
        """Isolated should protect original mutable objects."""
        original_list = [1, 2, 3]

        @smart_args()
        def function(*, data=Isolated):
            data.append(100)
            return data

        result = function(data=original_list)

        assert result == [1, 2, 3, 100]
        assert original_list == [1, 2, 3]

    def test_isolated_with_nested(self):
        """Isolated should work with nested mutable structures."""
        original_dict = {"a": [1, 2], "b": {"x": 10}}

        @smart_args()
        def function(*, data=Isolated):
            data["a"].append(3)
            data["b"]["x"] = 20
            data["c"] = "new"
            return data

        result = function(data=original_dict)

        assert result == {"a": [1, 2, 3], "b": {"x": 20}, "c": "new"}
        assert original_dict == {"a": [1, 2], "b": {"x": 10}}


class TestSmartArgsPositional:
    """Positional arguments handling tests."""

    def test_positional_isolated(self):
        """Isolated should work with positional args when allowed."""
        original_list = [1, 2]

        @smart_args(check_positional=True)
        def function(data=Isolated):
            data.append(3)
            return data

        result_data = function(original_list)

        assert result_data == [1, 2, 3]
        assert original_list == [1, 2]

    def test_positional_evaluated(self):
        """Evaluated should work with positional args when allowed."""
        call_counter = 0

        def get_value():
            nonlocal call_counter
            call_counter += 1
            return call_counter * 10

        @smart_args(check_positional=True)
        def function(data=Evaluated(get_value)):
            return data

        assert function() == 10
        assert function(5) == 5
        assert call_counter == 1

    def test_positional_not_allowed_error(self):
        """Should raise error for positional args when not allowed."""
        with pytest.raises(AssertionError, match="Positional arguments"):

            @smart_args()
            def function(data=Isolated):
                return data


class TestErrors:
    """Error handling tests."""

    def test_mix_classes_error(self):
        """Should raise error when mixing Evaluated and Isolated."""
        with pytest.raises(AssertionError, match="Cannot mix"):

            @smart_args()
            def function(*, a=Evaluated(lambda: 1), b=Isolated):
                return a, b

    def test_evaluated_not_callable_error(self):
        """Should raise error if Evaluated gets non-callable."""
        with pytest.raises(ValueError, match="callable"):

            @smart_args()
            def function(*, a=Evaluated("hello")):
                return a
