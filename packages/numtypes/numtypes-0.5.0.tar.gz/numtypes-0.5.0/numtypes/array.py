from typing import Sequence, Type, TypeGuard, overload, Any, runtime_checkable, Protocol

from numtypes.types import Shape, UnknownShape, ArrayType, Array, Dim1, Dim2, Vector, D
from numtypes.debug import verify

import numpy as np


@runtime_checkable
class Shaped(Protocol):
    """A protocol that defines an object that has a shape."""

    @property
    def shape(self) -> tuple[int, ...]:
        """The shape of the object."""
        ...


def array[S: Shape, T: ArrayType](
    elements: Sequence, *, dtype: Type[T] = np.float64, shape: S
) -> Array[S, T]:
    """Creates a numpy array with the given shape and type.

    Args:
        elements: The elements to create the array from.
        dtype: The type of the array. Defaults to np.float64.
        shape: The shape of the array. Use -1 if you don't want to check the size of a specific dimension.

    Returns:
        A numpy array with the given shape and type. The advantage of this function is that it
        tells the type checker what the shape of the array is.
    """

    result = np.array(elements, dtype=dtype)

    assert shape_of(result, matches=shape)

    return result


@overload
def array_1d(elements: tuple[float]) -> Vector[D[1]]:
    """Creates a 1D numpy array (vector) with a single element."""
    ...


@overload
def array_1d(elements: tuple[float, float]) -> Vector[D[2]]:
    """Creates a 1D numpy array (vector) with two elements."""
    ...


@overload
def array_1d(elements: tuple[float, float, float]) -> Vector[D[3]]:
    """Creates a 1D numpy array (vector) with three elements."""
    ...


@overload
def array_1d(elements: tuple[float, float, float, float]) -> Vector[D[4]]:
    """Creates a 1D numpy array (vector) with four elements."""
    ...


@overload
def array_1d[T: ArrayType](
    elements: Sequence, *, dtype: Type[T] = np.float64
) -> Array[Dim1, T]:
    """Creates a 1D numpy array with the given elements and type.

    Args:
        elements: The elements to create the array from.
        dtype: The type of the array. Defaults to np.float64.

    Returns:
        A 1D numpy array with the given elements and type. The advantage of this function is that
        it tells the type checker what the shape of the array is.
    """
    ...


@overload
def array_1d[T: ArrayType, L: tuple[int]](
    elements: Sequence, *, dtype: Type[T] = np.float64, length: L
) -> Array[L, T]:
    """Creates a 1D numpy array with the given elements and type.

    Args:
        elements: The elements to create the array from.
        dtype: The type of the array. Defaults to np.float64.
        length: The length of the array (as a tuple of one integer). This is used to specify the exact
            length of the array.

    Returns:
        A 1D numpy array with the given elements and type. The advantage of this function is that
        it tells the type checker what the shape of the array is.
    """
    ...


def array_1d[T: ArrayType, L: tuple[int]](
    elements: Sequence, *, dtype: Type[T] = np.float64, length: L | None = None
) -> Array[Dim1 | L, T]:
    result = np.array(elements, dtype=dtype)

    assert shape_of(result, matches=(len(elements),) if length is None else length)

    return result


vector = array_1d
"""A more meaningful alias for `array_1d` in some contexts."""


@overload
def array_2d[T: ArrayType](
    elements: Sequence[Sequence], *, dtype: Type[T] = np.float64
) -> Array[Dim2, T]:
    """Creates a 2D numpy array with the given elements and type.

    Args:
        elements: The elements to create the array from. Each element should be a sequence
            representing a row of the 2D array.
        dtype: The type of the array. Defaults to np.float64.

    Returns:
        A 2D numpy array with the given elements and type. The advantage of this function is that
        it tells the type checker what the shape of the array is.
    """


@overload
def array_2d[T: ArrayType, S: tuple[int, int]](
    elements: Sequence[Sequence], *, dtype: Type[T] = np.float64, shape: S
) -> Array[S, T]:
    """Creates a 2D numpy array with the given elements and type.

    Args:
        elements: The elements to create the array from. Each element should be a sequence
            representing a row of the 2D array.
        dtype: The type of the array. Defaults to np.float64.
        shape: The shape of the array (as a tuple of two integers). This is used to specify the exact
            shape of the array.

    Returns:
        A 2D numpy array with the given elements and type. The advantage of this function is that
        it tells the type checker what the shape of the array is.
    """


def array_2d[T: ArrayType, S: tuple[int, int]](
    elements: Sequence[Sequence], *, dtype: Type[T] = np.float64, shape: S | None = None
) -> Array[Dim2 | S, T]:
    result = np.array(elements, dtype=dtype)

    assert shape_of(
        result, matches=(len(elements), len(elements[0])) if shape is None else shape
    )

    return result


matrix = array_2d
"""A more meaningful alias for `array_2d` in some contexts."""


def shape_of[ShapeT: Shape, DataT: ArrayType](
    array: Any | Array[UnknownShape, DataT],
    /,
    *,
    matches: ShapeT,
    name: str = "array",
) -> TypeGuard[Array[ShapeT, DataT]]:
    """Verifies that the shape of the given array matches the expected shape.

    Args:
        array: The array to check. If used together with an assert, the type of the
            array will be inferred by the type checker.
        matches: The expected shape. Use -1 if you don't want to check the size of a
            specific dimension.
        name: The name of the array. Used in the error message.

    Returns:
        True, which indicates that the shape of the array match the expected shape. If
        the shape does not match, an AssertionError is raised instead.
    """
    ...

    assert isinstance(array, Shaped), (
        f"The {name} must be an array-like object that has a shape. "
        f"Got {type(array)} instead."
    )

    verify(
        all(
            actual == expected
            for actual, expected in zip(array.shape, matches)
            if expected != -1
        )
        and len(array.shape) == len(matches),
        f"Expected the {name} to have shape {matches}, but got {array.shape}.",
    )

    return True
