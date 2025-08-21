from typing import assert_type
from numtypes import (
    array,
    Array,
    FloatArray,
    UByteArray,
    Dim1,
    Dim2,
    Dim3,
    D,
    shape,
    Dims,
    shape_of,
)


from tests.dsl import corners_of_3d_box, image_pixels, edges_3d

import numpy as np


def test_that_example_use_cases_work() -> None:
    def translate_box(
        corners: FloatArray[Dims[D[8], D[3]]],
    ) -> FloatArray[Dims[D[8], D[3]]]:
        translation = np.array([1.0, -1.0, 0.0], dtype=corners.dtype)
        result = corners + translation[np.newaxis, :]

        assert shape_of(result, matches=(8, 3))

        return result

    assert_type(
        corners := array(corners_of_3d_box(), shape=(8, 3), dtype=np.float32),
        FloatArray[Dims[D[8], D[3]]],
    )
    assert_type(translate_box(corners), FloatArray[Dims[D[8], D[3]]])

    def flatten_image(image: UByteArray[Dim2]) -> UByteArray[Dim1]:
        return image.reshape(-1)

    assert_type(
        image := array(image_pixels(), shape=(100, 100), dtype=np.uint8),
        UByteArray[Dims[D[100], D[100]]],
    )
    assert_type(flatten_image(image), UByteArray[Dim1])


def test_that_edge_case_with_array_argument_being_of_type_any_works() -> None:
    def normals_for(edges: Array[Dim3]) -> Array[Dim3]:
        L = len(edges)

        assert shape_of(edges, matches=(L, 2, 4), name="edges")

        normals = np.stack([-edges[:, 1], edges[:, 0]], axis=1)
        normals /= np.sqrt(np.sum(normals**2, axis=1, keepdims=True))

        assert shape_of(normals, matches=(L, 2, 4), name="normals")

        return normals

    assert_type(
        edges := array(edges_3d(), shape=shape.Dim3, dtype=np.float64), Array[Dim3]
    )
    assert_type(normals_for(edges), Array[Dim3])
