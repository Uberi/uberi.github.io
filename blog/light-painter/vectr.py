#!/usr/bin/env python3

"""Vector mathematics library for Python 3."""

__author__ = "Anthony Zhang (Uberi)"
__version__ = "1.0.0"
__license__ = "BSD"

import math, numbers

class Vector:
    """"""
    def __init__(self, *components):
        """Returns a new `Vector` instance with components `components`."""
        for component in components: float(component) # ensure all the components are valid numbers

        self.values = list(components)

    def magnitude(self):
        """Returns the vector's magnitude"""
        return math.sqrt(sum(component ** 2 for component in self))

    def magnitude_squared(self):
        """Returns the square of the vector's magnitude. This is more efficient than using `self.magnitude() ** 2`"""
        return sum(component ** 2 for component in self)

    def extended(self, dimensions, component_value = 0):
        """Returns the vector extended into `dimensions` dimensions, where additional components are `component_value`."""
        if dimensions % 1 != 0: raise ValueError("`dimensions` must be an integer; `dimensions` is actually \"{}\"".format(dimensions))
        if len(self) > dimensions: raise ValueError("Vector extension can only extend the vector into higher dimensions; \"{}\" cannot be extended into an {} dimensional vector.".format(self, dimensions))

        return Vector(*(self.values + [component_value] * (dimensions - len(self))))

    def normalized(self):
        """Returns the vector scaled to have magnitude 1."""
        magnitude = self.magnitude()
        if magnitude == 0: raise ValueError("\"{}\" is a zero vector, which cannot be normalized.".format(self))
        return self / magnitude
    
    def cross(self, value):
        """Returns the vector cross product of the vector and another vector `value`"""
        if len(self) != 3 and len(self) != 7: raise ValueError("Vector cross product can only be applied in 3 or 7 dimensions; \"{}\" is {} dimensional".format(self, len(self)))
        if len(value) != 3 and len(value) != 7: raise ValueError("Vector cross product can only be applied in 3 or 7 dimensions; \"{}\" is {} dimensional".format(value, len(value)))
        if len(self) != len(value): raise ValueError("Both vectors must be the same dimension; \"{}\" is {} dimensional while \"{}\" is {} dimensional".format(self, len(self), value, len(value)))

        if len(self) == 3:
            # 3D vector cross product, see https://en.wikipedia.org/wiki/Cross_product#Coordinate_notation
            return Vector(
                self[1] * value[2] - self[2] * value[1],
                self[2] * value[0] - self[0] * value[2],
                self[0] * value[1] - self[1] * value[0]
            )
        
        # 7D vector cross product, see https://en.wikipedia.org/wiki/Seven-dimensional_cross_product#Coordinate_expressions
        return Vector(
            self[1] * value[3] - self[3] * value[1] + self[2] * value[6] - self[6] * value[2] + self[4] * value[5] - self[5] * value[4],
            self[2] * value[4] - self[4] * value[2] + self[3] * value[0] - self[0] * value[3] + self[5] * value[6] - self[6] * value[5],
            self[3] * value[5] - self[5] * value[3] + self[4] * value[1] - self[1] * value[4] + self[6] * value[0] - self[0] * value[6],
            self[4] * value[6] - self[6] * value[4] + self[5] * value[2] - self[2] * value[5] + self[0] * value[1] - self[1] * value[0],
            self[5] * value[0] - self[0] * value[5] + self[6] * value[3] - self[3] * value[6] + self[1] * value[2] - self[2] * value[1],
            self[6] * value[1] - self[1] * value[6] + self[0] * value[4] - self[4] * value[0] + self[2] * value[3] - self[3] * value[2],
            self[0] * value[2] - self[2] * value[0] + self[1] * value[5] - self[5] * value[1] + self[3] * value[4] - self[4] * value[3]
        )

    def rotated2D(self, theta):
        """Returns the vector (2D only) rotated clockwise by `theta` radians."""
        if len(self) != 2: raise ValueError("2D rotation can only be applied in 2 dimensions; \"{}\" is {} dimensional.".format(self, len(self)))

        cosine, sine = math.cos(theta), math.sin(theta)
        return Vector(cosine * self[0] + sine * self[1], -sine * self[0] + cosine * self[1])

    def rotated3D(self, theta, axis):
        """Returns the vector (3D only) rotated clockwise (viewed when facing in the direction of the vector `axis`; right hand rule) around the vector axis `axis` by `theta` radians."""
        if len(self) != 3: raise ValueError("3D rotation can only be applied in 3 dimensions; \"{}\" is {} dimensional.".format(self, len(self)))

        # apply 3D rotation matrix, see https://en.wikipedia.org/wiki/Rotation_matrix#Rotation_matrix_from_axis_and_angle
        x, y, z = axis.normalized()
        cosine, sine = math.cos(theta), math.sin(theta)
        opposite_cosine = 1 - cosine
        return Vector(
            (cosine + x ** 2 * opposite_cosine)  * self[0] + (x * y * opposite_cosine - z * sine) * self[1] + (x * z * opposite_cosine + y * sine) * self[2],
            (y * x * opposite_cosine + z * sine) * self[0] + (cosine + y ** 2 * opposite_cosine)  * self[1] + (y * z * opposite_cosine - x * sine) * self[2],
            (z * x * opposite_cosine - y * sine) * self[0] + (z * y * opposite_cosine + x * sine) * self[1] + (cosine + z ** 2 * opposite_cosine)  * self[2]
        )

    def angle_between(self, value):
        """Returns the smallest angle between the vector and another vector `value`."""
        if not isinstance(value, Vector): raise ValueError("Value \"{}\" must be a vector".format(value))

        return math.acos(self * value / self.magnitude() / value.magnitude())

    def multiply_matrix(self, matrix):
        """Multiply the vector by matrix `matrix`, a list of lists where inner lists represent rows (accessed via `matrix[ROW_INDEX][COLUMN_INDEX]`)."""
        for i, row in enumerate(matrix):
            if len(row) != len(self): raise ValueError("Invalid matrix dimensions; row {} is {} dimensional, while the vector is {} dimensional.".format(i, len(row), len(self)))
            for cell in row: float(cell) # ensure the entries in the row are all valid numbers

        return Vector(*(sum(cell * component for cell, component in zip(row, self)) for row in matrix))

    def __repr__(self): return "<Vector {}>".format(" ".join(str(value) for value in self.values))
    def __str__(self): return str(self.values)
    def __iter__(self): return iter(self.values)
    def __reversed__(self): return reversed(self.values)
    def __len__(self): return len(self.values)
    def __contains__(self, value): return value in self.values
    def __getitem__(self, index):
        if isinstance(index, slice):
            return Vector(*self.values[index])
        return self.values[index]
    def __setitem__(self, index, value):
        float(value) # ensure that the component is a valid number
        self.values[index] = value
    def __add__(self, value):
        """Returns the vector addition of the vector and `value`."""
        if not isinstance(value, Vector): raise ValueError("`value` must be a `Vector` instance; `value` is actually \"{}\".".format(value))
        return Vector(*(component1 + component2 for component1, component2 in zip(self, value)))
    def __sub__(self, value):
        """Returns the vector difference of the vector and `value`."""
        if not isinstance(value, Vector): raise ValueError("`value` must be a `Vector` instance; `value` is actually \"{}\".".format(value))
        return Vector(*(component1 - component2 for component1, component2 in zip(self, value)))
    def __rmul__(self, value): return self * value
    def __mul__(self, value):
        """Returns the vector dot product of the vector and `value` if `value` is also a `Vector`, otherwise multiplies the vector by `value` component-wise."""
        if isinstance(value, Vector): # another vector, compute the dot product
            return sum(component1 * component2 for component1, component2 in zip(self, value))
        float(value) # ensure the multiplicand is a valid number
        return Vector(*(component * value for component in self))
    def __truediv__(self, value):
        """Returns the vector divided component-wise by `value`."""
        float(value) # ensure the multiplicand is a valid number
        return Vector(*(component / value for component in self))
    def __floordiv__(self, value):
        """Returns the vector floor divided component-wise by `value`."""
        float(value) # ensure the multiplicand is a valid number
        return Vector(*(component // value for component in self))
    def __mod__(self, value):
        """Returns the vector modulo `value` component-wise."""
        float(value) # ensure the multiplicand is a valid number
        return Vector(*(component % value for component in self))
    def __divmod__(self, value):
        """Returns the vector floor divided component-wise by `value`, and the vector modulo `value` component-wise."""
        float(value) # ensure the multiplicand is a valid number
        return self // value, self % value
    def __neg__(self): return Vector(*(-component for component in self))
    def __pos__(self): return Vector(*self)
    def __abs__(self): return Vector(*(abs(component) for component in self))
    def __round__(self, places = 0): return Vector(*(round(component, places) for component in self))
    def __ceil__(self): return Vector(*(math.ceil(component) for component in self))
    def __floor__(self): return Vector(*(math.floor(component) for component in self))
    def __trunc__(self): return Vector(*(math.trunc(component) for component in self))
    def __eq__(self, value): return self.values == list(value)
    def __bool__(self): return bool(self.values)
    def __hash__(self): return hash(self.values)
    __slots__ = ["values"] # list the attributes of this class
