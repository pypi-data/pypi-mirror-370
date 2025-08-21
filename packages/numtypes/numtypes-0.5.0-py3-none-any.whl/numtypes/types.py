from typing import Literal, Any

import numpy as np
from numpy import ndarray, dtype


type Shape = tuple[int, ...]
type ArrayType = np.generic

type AnyShape = tuple[int, ...]
type AnyType = np.generic

type UnknownShape = tuple[Any, ...]

type Float = np.float32
type Double = np.float64
type Byte = np.byte
type UByte = np.ubyte
type Short = np.short
type Int = np.int32
type Long = np.int64
type Bool = np.bool_

type Array[S: Shape = AnyShape, T: ArrayType = Double] = ndarray[S, dtype[T]]
type AnyArray[S: Shape = AnyShape] = Array[S, AnyType]
type FloatArray[S: Shape = AnyShape] = Array[S, Float]
type DoubleArray[S: Shape = AnyShape] = Array[S, Double]
type ByteArray[S: Shape = AnyShape] = Array[S, Byte]
type UByteArray[S: Shape = AnyShape] = Array[S, UByte]
type ShortArray[S: Shape = AnyShape] = Array[S, Short]
type IntArray[S: Shape = AnyShape] = Array[S, Int]
type LongArray[S: Shape = AnyShape] = Array[S, Long]
type BoolArray[S: Shape = AnyShape] = Array[S, Bool]
type IndexArray[S: Shape = AnyShape] = Array[S, np.intp] | Array[S, np.int_]

type NumberArray[S: Shape = AnyShape] = (
    FloatArray[S]
    | DoubleArray[S]
    | ShortArray[S]
    | IntArray[S]
    | LongArray[S]
    | ByteArray[S]
    | UByteArray[S]
)

type Vector[L: int = int, T: ArrayType = Double] = Array[tuple[L], T]
type Matrix[R: int = int, C: int = int, T: ArrayType = Double] = Array[tuple[R, C], T]

type Dim1 = tuple[int]
"""An alias for the shape of a 1D array of any length."""

type Dim2 = tuple[int, int]
"""An alias for the shape of a 2D array with any number of rows and columns."""

type Dim3 = tuple[int, int, int]
"""An alias for the shape of a 3D array."""

type Dim4 = tuple[int, int, int, int]
"""An alias for the shape of a 4D array."""

D = Literal
"""Specifies the size of a single dimensions of an array. This is just slightly less verbose
syntax sugar for `Literal[...]`.
"""

N = D[-1]
"""Specifies a dimension of an array that can have any size."""

Dims = tuple
"""Specifies the dimensions of an array."""


class shape:
    """A namespace for commonly used shapes.

    Example:
        If you're creating a 3D array from some data, but don't really know the dimensions, you
        can do so like this:

        ```python
        from numtypes import array

        data = ...  # some data
        data_array = array(data, shape=(-1, -1, -1), dtype=np.float64)
        ```

        Although that would work, the following option is more readable:

        ```python
        from numtypes import array, shape

        data = ...  # some data
        data_array = array(data, shape=shape.Dim3, dtype=np.float64)
        ```
    """

    Dim1: tuple[int] = (-1,)
    """A predefined shape for any 1D array."""

    Dim2: tuple[int, int] = (-1, -1)
    """A predefined shape for any 2D array."""

    Dim3: tuple[int, int, int] = (-1, -1, -1)
    """A predefined shape for any 3D array."""

    Dim4: tuple[int, int, int, int] = (-1, -1, -1, -1)
    """A predefined shape for any 4D array."""
