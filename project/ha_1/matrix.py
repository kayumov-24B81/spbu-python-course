from typing import List, Union


class Matrix:
    """A mathematical matrix with basic linear algebra operations.

    Attributes:
        values: 2D list containing matrix elements

    """

    values: List[List[Union[int, float]]] = []

    def __init__(self, *rows: List[Union[int, float]]) -> None:
        """Initializes a matrix from rows.

        Args:
            *rows: Variable number of rows, each row is an iterable of numbers

        Raises:
            ValueError: If matrix is empty or rows have different lengths
        """
        if not rows:
            raise ValueError("Matrix cannot be empty")

        lengths = [len(row) for row in rows]
        if len(set(lengths)) != 1:
            raise ValueError("All rows must have the same length")

        self.values = [list(row) for row in rows]

    def __add__(self, matrix: "Matrix") -> "Matrix":
        """Adds two matrices element-wise.

        Args:
            matrix: Another matrix to add

        Returns:
            Matrix: New matrix containing the sum

        Raises:
            ValueError: If matrices have different dimensions
        """
        if len(self.values) != len(matrix.values) or len(self.values[0]) != len(
            matrix.values[0]
        ):
            raise ValueError("The dimensions of the matrices do not match")

        rows: List[List[Union[int, float]]] = []
        for i in range(len(self.values)):
            row: List[Union[int, float]] = []
            rows.append(row)
            for j in range(len(self.values[i])):
                rows[i].append(self.values[i][j] + matrix.values[i][j])

        return Matrix(*rows)

    def __mul__(self, matrix: "Matrix") -> "Matrix":
        """Multiplies two matrices.

        Args:
            matrix: Another matrix to multiply with

        Returns:
            Matrix: Result of matrix multiplication

        Raises:
            ValueError: If matrices cannot be multiplied
        """
        if len(self.values[0]) != len(matrix.values):
            raise ValueError(
                "Matrices of given dimensions are not suitable for multiplication"
            )

        rows: List[List[Union[int, float]]] = []
        for i in range(len(self.values)):
            row: List[Union[int, float]] = []
            rows.append(row)
            for j in range(len(matrix.values[0])):
                cell: Union[int, float] = 0
                for r in range(len(self.values[0])):
                    cell += self.values[i][r] * matrix.values[r][j]
                rows[i].append(cell)

        return Matrix(*rows)

    def transpose(self) -> "Matrix":
        """Returns transposed matrix.

        Returns:
            Matrix: Transposed matrix where rows become columns
        """
        rows: List[List[Union[int, float]]] = []
        for i in range(len(self.values)):
            row: List[Union[int, float]] = []
            rows.append(row)
            for j in range(len(self.values[0])):
                rows[i].append(self.values[j][i])

        return Matrix(*rows)

    def __eq__(self, matrix: object) -> bool:
        """Checks if two matrices are equal.

        Args:
            matrix: Another matrix to compare with

        Returns:
            bool: True if matrices have same dimensions and elements
        """
        if not isinstance(matrix, Matrix):
            return NotImplemented

        if len(self.values) != len(matrix.values) or len(self.values[0]) != len(
            matrix.values[0]
        ):
            return False

        for i in range(len(self.values)):
            for j in range(len(self.values[0])):
                if self.values[i][j] != matrix.values[i][j]:
                    return False

        return True
