import pytest
from project.ha_3.currying import curry_explicit, uncurry_explicit


class TestCurryExplicit:
    def test_spec_currying(self):
        func = curry_explicit((lambda x, y, z: f"<{x},{y},{z}>"), 3)

        assert func(1)(2)(3) == "<1,2,3>"

    def test_basic_currying(self):
        f = lambda x, y, z: x + y + z
        curried = curry_explicit(f, 3)

        assert curried(1)(2)(3) == 6

    def test_partial_application(self):
        f = lambda x, y, z: x * y * z
        curried = curry_explicit(f, 3)

        double = curried(2)
        triple_double = double(3)
        assert triple_double(4) == 24
        assert triple_double(5) == 30

    def test_zero_arity(self):
        f = lambda: "hello"
        curried = curry_explicit(f, 0)

        assert curried() == "hello"

    def test_single_argument(self):
        f = lambda x: x
        curried = curry_explicit(f, 1)

        assert curried(5) == 5
        assert curried("hel o") == "hel o"

    def test_error_negative_arity(self):
        f = lambda x, y: x + y

        with pytest.raises(ValueError, match="Arity should not be negative"):
            curry_explicit(f, -1)

    def test_error_too_many_arguments(self):
        f = lambda x, y: x + y
        curried = curry_explicit(f, 2)

        with pytest.raises(ValueError, match="Too many arguments"):
            curried(1, 2, 3)

    def test_error_single_argument_required(self):
        f = lambda x, y, z: x + y + z
        curried = curry_explicit(f, 3)
        partial = curried(1)

        with pytest.raises(ValueError, match="Must provide exactly one argument"):
            partial(2, 3)


@pytest.fixture
def curried():
    def f1(x):
        def f2(y):
            def f3(z):
                return x + y + z

            return f3

        return f2

    return f1


class TestUncurryExplicit:
    def test_spec_uncurrying(self):
        def g(x):
            def g1(y):
                def g2(z):
                    return f"<{x},{y},{z}>"

                return g2

            return g1

        uncurried = uncurry_explicit(g, 3)
        assert uncurried(1, 2, 3) == "<1,2,3>"

    def test_basic_uncurrying(self, curried):
        uncurried = uncurry_explicit(curried, 3)
        assert uncurried(1, 2, 3) == 6

    def test_zero_arity_uncurry(self):
        def const_curried():
            return "helo"

        uncurried = uncurry_explicit(const_curried, 0)
        assert uncurried() == "helo"

    def test_single_argument_uncurry(self):
        def single_curried(x):
            return x

        uncurried = uncurry_explicit(single_curried, 1)
        assert uncurried(11) == 11

    def test_error_wrong_argument_count(self):
        uncurried = uncurry_explicit(curried, 3)

        with pytest.raises(TypeError, match="Expected 3 arguments, got 2"):
            uncurried(1, 2)

        with pytest.raises(TypeError, match="Expected 3 arguments, got 4"):
            uncurried(1, 2, 3, 4)

    def test_error_negative_arity_uncurry(self):
        with pytest.raises(ValueError, match="Arity should not be negative"):
            uncurry_explicit(curried, -1)


def test_spec_full_cycle():
    f2 = curry_explicit((lambda x, y, z: f"<{x},{y},{z}>"), 3)
    g2 = uncurry_explicit(f2, 3)

    assert f2(123)(456)(562) == "<123,456,562>"
    assert g2(123, 456, 562) == f2(123)(456)(562)
