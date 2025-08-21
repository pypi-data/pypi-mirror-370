from random import randint
import numpy as np
from numpy.typing import NDArray


def corners_of_3d_box() -> list[list[float]]:
    return [
        [1.0, 1.0, 1.0],
        [1.0, 1.0, -1.0],
        [1.0, -1.0, 1.0],
        [1.0, -1.0, -1.0],
        [-1.0, 1.0, 1.0],
        [-1.0, 1.0, -1.0],
        [-1.0, -1.0, 1.0],
        [-1.0, -1.0, -1.0],
    ]


def image_pixels() -> list[list[int]]:
    return [[0 for _ in range(100)] for _ in range(100)]


def edges_3d() -> list[list[list[float]]]:
    return [
        [[1.0, 1.0, 1.0, 1.0], [1.0, 1.0, 1.0, -1.0]],
        [[1.0, 1.0, 1.0, -1.0], [1.0, 1.0, -1.0, -1.0]],
        [[1.0, 1.0, -1.0, -1.0], [1.0, 1.0, -1.0, 1.0]],
        [[1.0, 1.0, -1.0, 1.0], [1.0, 1.0, 1.0, 1.0]],
    ]


def random_dimensions() -> tuple[int, int]:
    H = randint(1, 100)
    W = randint(1, 100)
    return H, W


def random_array(shape: tuple[int, ...]) -> NDArray[np.float64]:
    return np.random.random(size=shape)
