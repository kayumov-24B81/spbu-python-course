from typing import Union, List
import math


class Vector:
    """A mathematical vector with basic operations.

    Attributes:
        values: Tuple containing vector components
    """

    values: List[Union[int, float]] = []

    def __init__(self, *values: Union[int, float]):
        """Initializes vector with components.

        Args:
            *values: Variable number of vector components
        """
        self.values = list(values)

    def __mul__(self, vector) -> int | float:
        """Computes dot product of two vectors.

        Args:
            vector: Another vector for dot product

        Returns:
            Dot product value

        Raises:
            ValueError: If vectors have different dimensions
        """
        if len(self.values) != len(vector.values):
            raise ValueError("The dimensions of the vectors do not match")

        product = 0
        for x, y in zip(self.values, vector.values):
            product += x * y

        return product

    def length(self):
        """Calculates vector length.

        Returns:
            Euclidean norm of the vector
        """
        sq_sum = 0
        for x in self.values:
            sq_sum += x**2

        return math.sqrt(sq_sum)

    def angle(self, vector):
        """Calculates angle between two vectors in degrees.

        Args:
            vector: Another vector to calculate angle with

        Returns:
            Angle in degrees between vectors

        Raises:
            ValueError: If vectors have different dimensions or are zero vectors
        """
        numerator = self * vector
        denominator = self.length() * vector.length()

        if denominator == 0:
            raise ValueError("Cannot calculate angle with zero vector")

        return math.acos(numerator / denominator) * 180 / math.pi
