import pytest
from project.ha_1.vector import Vector
from project.ha_1.matrix import Matrix


def test_vector_init():
    vector = Vector(1, 4, 6)
    assert vector.values[0] == 1
    assert vector.values[1] == 4
    assert vector.values[2] == 6


def test_vector_mult():
    vector1 = Vector(1, 4, 3)
    vector2 = Vector(1, 5, 6)
    assert vector1 * vector2 == 39


def test_vector_mult_error():
    vector1 = Vector(1, 4, 3)
    vector2 = Vector(1, 5, 6, 7)
    with pytest.raises(ValueError):
        vector1 * vector2


def test_vector_length():
    vector = Vector(4, 3, 0)
    assert vector.length() == 5


def test_vector_angle():
    vector1 = Vector(1, 2, 3)
    vector2 = Vector(-2, 1, 0)
    assert vector1.angle(vector2) == 90


def test_vector_angle_error():
    vector1 = Vector(0, 0, 0)
    vector2 = Vector(0, 0, 0)
    with pytest.raises(ValueError):
        vector1.angle(vector2)


def test_matrix_init():
    matrix = Matrix([1, 2], [3, 4])
    assert matrix.values[0][0] == 1
    assert matrix.values[0][1] == 2
    assert matrix.values[1][0] == 3
    assert matrix.values[1][1] == 4


def test_matrix_init_error():
    with pytest.raises(ValueError):
        Matrix()

    with pytest.raises(ValueError):
        Matrix([1, 2], [4, 3, 2])


def test_matrix_eq():
    matrix1 = Matrix([1, 2], [3, 4])
    matrix2 = Matrix([1, 2], [3, 4])
    assert matrix1 == matrix2


def test_matrix_add():
    matrix1 = Matrix([2, 3], [-1, 5])
    matrix2 = Matrix([-6, 1], [1, 0])
    matrix = Matrix([-4, 4], [0, 5])
    assert matrix1 + matrix2 == matrix


def test_matrix_add_error():
    matrix1 = Matrix([2, 3], [-1, 5])
    matrix2 = Matrix([-6, 1], [1, 0], [2, 1])
    with pytest.raises(ValueError):
        matrix1 + matrix2


def test_matrix_mult():
    matrix1 = Matrix([1, 2], [4, 1])
    matrix2 = Matrix([-1, 3], [5, -2])
    matrix = Matrix([9, -1], [1, 10])
    assert matrix1 * matrix2 == matrix


def test_matrix_mult_error():
    matrix1 = Matrix([1, 2], [4, 1])
    matrix2 = Matrix([-1, 3], [5, -2], [2, 1])
    with pytest.raises(ValueError):
        matrix1 * matrix2


def test_matrix_transpose():
    matrix = Matrix([5, 3], [2, -1])
    matrix_t = Matrix([5, 2], [3, -1])
    assert matrix.transpose() == matrix_t
