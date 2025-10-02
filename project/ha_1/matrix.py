from typing import Iterable


class Matrix:
    values: Iterable[Iterable[int | float]] = []

    def __init__(self, *rows: Iterable[int | float]):
        if not rows:
            raise ValueError("Matrix cannot be empty")

        lengths = [len(row) for row in rows]
        if len(set(lengths)) != 1:
            raise ValueError("All rows must have the same length")

        self.values = [list(row) for row in rows]

    def __add__(self, matrix: "Matrix") -> "Matrix":
        if (
            len(self.values)
            != len(matrix.values) | len(self.values[0])
            != len(matrix.values[0])
        ):
            raise ValueError("The dimensions of the matrices do not match")

        rows = []
        for i in range(len(self.values)):
            rows.append([])
            for j in range(len(self.values[i])):
                rows[i].append(self.values[i][j] + matrix.values[i][j])

        return Matrix(*rows)

    def __mul__(self, matrix: "Matrix") -> "Matrix":
        if len(self.values[0]) != len(matrix.values):
            raise ValueError(
                "Matrices of given dimensions are not suitable for multiplication"
            )

        rows = []
        for i in range(len(self.values)):
            rows.append([])
            for j in range(len(matrix.values[0])):
                cell = 0
                for r in range(len(self.values[0])):
                    cell += self.values[i][r] * matrix.values[r][j]
                rows[i].append(cell)

        return Matrix(*rows)

    def transpose(self):
        rows = []
        for i in range(len(self.values)):
            rows.append([])
            for j in range(len(self.values[0])):
                rows[i].append(self.values[j][i])

        return Matrix(*rows)

    def __eq__(self, matrix):
        if (
            len(self.values)
            != len(matrix.values) | len(self.values[0])
            != len(matrix.values[0])
        ):
            return False

        for i in range(len(self.values)):
            for j in range(len(self.values[0])):
                if self.values[i][j] != matrix.values[i][j]:
                    return False

        return True
