from typing import assert_type
from numtypes import (
    array,
    array_1d,
    array_2d,
    Array,
    Int,
    Long,
    Float,
    Double,
    FloatArray,
    IntArray,
    BoolArray,
    IndexArray,
    NumberArray,
    Dim1,
    Dim2,
    Dim3,
    Dim4,
    D,
    N,
    Dims,
    Shape,
    UnknownShape,
    Vector,
    Matrix,
    shape_of,
    vector,
    matrix,
)

import pytest
from pytest import mark

from dsl import random_dimensions, random_array

import numpy as np


def test_that_array_shape_is_as_specified_during_creation() -> None:
    # The shape must match exactly.
    assert_type(array([], shape=(0,)), Array[Dims[D[0]]])
    assert_type(array([1, 2, 3], shape=(3,)), Array[Dims[D[3]]])
    assert_type(array([[1, 2], [3, 4]], shape=(2, 2)), Array[Dims[D[2], D[2]]])
    assert_type(array([[1, 2, 3], [4, 5, 6]], shape=(2, 3)), Array[Dims[D[2], D[3]]])

    # The expected shape in some dimensions can be less specific.
    assert_type(array([1, 2, 3], shape=(-1,)), Array[Dims[N]])
    assert_type(array([[1, 2], [3, 4]], shape=(-1, 2)), Array[Dims[N, D[2]]])
    assert_type(array([[1], [2]], shape=(-1, -1)), Array[Dims[N, N]])

    # For common shapes, different versions of `array` can be used.
    # These don't check exact dimensions, but rather the number of dimensions.
    assert_type(array_1d([1, 2, 3]), Array[Dim1])
    assert_type(array_1d([1, 2, 3, 4, 5]), Array[Dim1])
    assert_type(array_2d([[1, 2], [3, 4]]), Array[Dim2])
    assert_type(array_2d([[], [], []]), Array[Dim2])

    # 1D and 2D arrays can also be typed as `Vector` and `Matrix`.
    assert_type(array_1d([1, 2, 3]), Vector)
    assert_type(array_1d([1, 2], length=(2,)), Vector[D[2]])
    assert_type(array([1, 2, 3], shape=(3,)), Vector[D[3]])

    assert_type(array_2d([[1, 2], [3, 4]]), Matrix)
    assert_type(array_2d([[1, 2], [3, 4]], shape=(2, 2)), Matrix[D[2], D[2]])
    assert_type(array([[1, 2], [3, 4]], shape=(2, 2)), Matrix[D[2], D[2]])

    # Some regular numpy functions also provide type information.
    assert_type(np.zeros((3,)), Array[Dim1])
    assert_type(np.zeros((2, 3)), Array[Dim2])
    assert_type(np.zeros((2, 3, 4)), Array[Dim3])
    assert_type(np.zeros((0, 2, 3, 4)), Array[Dim4])


def test_that_array_data_type_is_as_specified_during_creation() -> None:
    # The data type can be specified using the `dtype` argument.
    assert_type(array([1], shape=(1,), dtype=np.float32), Array[Dims[D[1]], Float])
    assert_type(array_1d([1, 2, 3], dtype=np.float64), Array[Dim1, Double])
    assert_type(array_1d([1], dtype=np.int32, length=(1,)), Array[Dims[D[1]], Int])
    assert_type(array_2d([[1, 2], [3, 4]], dtype=np.int32), Array[Dim2, Int])
    assert_type(
        array_2d([[], []], dtype=np.int64, shape=(2, 0)),
        Array[Dims[D[2], D[0]], Long],
    )

    # For convenience, arrays of different data types have their own type aliases.
    assert_type(array([1], shape=(1,), dtype=np.float32), FloatArray[Dims[D[1]]])
    assert_type(array([1], shape=(1,), dtype=np.int32), IntArray[Dims[D[1]]])
    assert_type(array([True], shape=(1,), dtype=np.bool_), BoolArray[Dims[D[1]]])
    assert_type(np.argsort(array_1d([1, 2, 3])), IndexArray[UnknownShape])


def test_that_checking_array_shape_gives_type_information() -> None:
    # The shape of the array can be checked using the `shape_of` function.
    assert shape_of(
        array := np.array([[1, 2], [3, 4]], dtype=np.float64), matches=(2, 2)
    )

    # Afterwards, the type checker will also have this type information.
    assert_type(array, Array[Dims[D[2], D[2]]])

    # You don't need to check every dimension.
    assert shape_of(
        another_array := np.array([[1, 2], [3, 4]], dtype=np.float64),
        matches=(2, -1),
    )

    # The type checker will then know that the second dimension can be anything.
    assert_type(another_array, Array[Dims[D[2], N]])

    # The dimensions also do not need to be literals.
    H, W = random_dimensions()
    assert shape_of(yet_another_array := random_array((H, W, 8)), matches=(H, W, 8))

    # But in this case, the type checker will only know the sizes of the literal dimensions.
    assert_type(yet_another_array, Array[Dims[int, int, D[8]]])


def test_that_number_arrays_work_for_all_number_types() -> None:
    def test_function(number_array: NumberArray[Dim1]) -> None:
        assert_type(number_array, NumberArray[Dim1])

    # The type checker will know that the array can be of any number type.
    test_function(np.zeros((3,), dtype=np.float32))
    test_function(np.zeros((3,), dtype=np.float64))
    test_function(np.zeros((3,), dtype=np.short))
    test_function(np.zeros((3,), dtype=np.int32))
    test_function(np.zeros((3,), dtype=np.int64))
    test_function(np.zeros((3,), dtype=np.byte))
    test_function(np.zeros((3,), dtype=np.ubyte))


def test_that_vector_and_matrix_aliases_work() -> None:
    # The `vector` and `matrix` aliases are just more meaningful names for `array_1d` and `array_2d`.
    assert_type(vector([1, 2, 3, 4, 5, 6]), Vector)
    assert_type(vector([1, 2, 3, 4, 5, 6], length=(6,)), Vector[D[6]])
    assert_type(matrix([[1, 2], [3, 4]]), Matrix)
    assert_type(matrix([[1, 2], [3, 4]], shape=(2, 2)), Matrix[D[2], D[2]])

    # The size for the `vector` can be inferred automatically for common sizes.
    assert_type(vector((1,)), Vector[D[1]])
    assert_type(vector((1, 2)), Vector[D[2]])
    assert_type(vector((1, 2, 3)), Vector[D[3]])
    assert_type(vector((1, 2, 3, 4)), Vector[D[4]])


@mark.parametrize(
    ["array", "shape"],
    [
        (np.array([[1, 2], [3, 4]], dtype=np.float64), (2, 3)),
        (np.array([1, 2, 3], dtype=np.float64), (4,)),
        (np.array([[1, 2], [3, 4]], dtype=np.float64), (3, 2)),
        (np.array([[[1], [2]], [[3], [4]]], dtype=np.float64), (2, -1, 2)),
    ],
)
def test_that_an_assert_error_is_raised_if_shape_does_not_match(
    array: Array, shape: Shape
) -> None:
    with pytest.raises(AssertionError):
        assert shape_of(array, matches=shape)
