# NumTypes

[![Python](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![NumPy](https://img.shields.io/badge/numpy-compatible-orange.svg)](https://numpy.org/)
[![Pyright](https://img.shields.io/badge/pyright-compatible-blue.svg)](https://github.com/microsoft/pyright)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](https://gitlab.com/zurabm/numtypes/-/blob/master/LICENSE)

Type hints for NumPy arrays without the hassle! 🎉

## 🎯 Motivation

If you've ever tried to add type hints to code using NumPy, you've probably noticed that the built-in type annotations for arrays are not very useful:

```python
import numpy as np

def translate_box(corners: np.ndarray) -> np.ndarray:
    # What are the dimensions? What's the data type? 🤷
    return corners + ?
```

The NumPy typing module provides an alias `NDArray`, but it doesn't support shape information. Only data types can be specified, like this:

```python
...
from numpy.typing import NDArray

def translate_box(corners: NDArray[np.float32]) -> NDArray[np.float32]:
    # But that's not very helpful, is it? We still don't know how the corners are represented.
    return corners + ?
```

You can be more specific if you use `ndarray` directly, but now it becomes very verbose:

```python
...

def translate_box(corners: np.ndarray[tuple[int, int], np.dtype[np.float32]]) -> np.ndarray[tuple[int, int], np.dtype[np.float32]]:
    # Still, you don't know if a row represents a point, or if the columns represent points. Is it 2D or 3D?
    return corners + ?
```

If you want to specify the exact shape, then it's even worse:

```python
...
from typing import Literal

def translate_box(
    corners: np.ndarray[tuple[Literal[8], Literal[3]], np.dtype[np.float32]]
) -> np.ndarray[tuple[Literal[8], Literal[3]], np.dtype[np.float32]]:
    translation = np.array([1.0, -1.0, 0.0], dtype=corners.dtype)
    return corners + translation[np.newaxis, :]  # NumPy would also lose the type information here
```

**NumTypes** alleviates this issue by providing more concise syntax that:
 - documents the array shapes and data types at the desired specificity,
 - tells your type checker what to expect, and
 - helps it out whenever it gets confused by NumPy.

This library doesn't do any magic, it just provides sensible type aliases and leverages existing typing features (like type guards) in Python to give you better type hints. In fact, it's such a thin wrapper around NumPy's existing types that you could implement it yourself! But doing it every time for every project is tedious, so this library does it for you.

## ✨ Features

- **Precise shape typing** - Specify exact dimensions or use wildcards for flexibility
- **dtype support** - Full support for NumPy data types
- **Runtime shape validation** - Verify array shapes at runtime with `shape_of()`, while helping your type checker in the process
- **Convenient & concise aliases** - `Vector`, `Matrix`, `IntArray`, `BoolArray`, and more
- **Pyright compatible** - Tested and working with Pyright/Pylance
- **Minimal overhead** - Runtime validation is optional, lightweight and can easily be disabled

## 📦 Installation

```bash
pip install numtypes
```

## 🚀 Quick Start

The above use case can be simplified with **NumTypes** like this:

```python
from numtypes import FloatArray, Dims, D

def translate_box(corners: FloatArray[Dims[D[8], D[3]]]) -> FloatArray[Dims[D[8], D[3]]]:
    translation = np.array([1.0, -1.0, 0.0], dtype=corners.dtype)
    result = corners + translation[np.newaxis, :]

    # Simple syntax for validating the shape and helping the type checker.
    assert shape_of(result, matches=(8, 3))

    return result  # The type checker now knows this is a FloatArray with shape (8, 3)
```

Nevertheless, in most cases you will likely use more flexible shapes, like `Dim1`, `Dim2`, etc. This allows you to specify the dimensionality without worrying about the exact size:

```python
from numtypes import UByteArray, Dim1, Dim2

def flatten_image(image: UByteArray[Dim2]) -> UByteArray[Dim1]:
    return image.reshape(-1)  # This actually works with NumPy alone, since it is able to figure out the type.
```

## 📖 Usage

### Basic Array Types

The most common pattern is using `Dim1`, `Dim2`, `Dim3`, etc. for arrays with a known number of dimensions:

```python
from numtypes import Array, Dim1, Dim2, Dim3
import numpy as np

# Some NumPy functions infer type info properly
zeros_1d: Array[Dim1] = np.zeros((5,))
zeros_2d: Array[Dim2] = np.zeros((5, 5))
tensor: Array[Dim3] = np.ones((10, 20, 30))

# The most helpful part is knowing what arrays represent and how they are shaped.
def some_function(array_1: Array[Dim2], array_2: Array[Dim3], *arrays: Array[Dim1]) -> Array[Dim2]:
    ...
```

### Specifying Exact Shapes

When you need to be more specific about dimensions:

```python
from numtypes import FloatArray, IntArray, Dims, D, N

# Exact shape specification
corners: FloatArray[Dims[D[8], D[3]]]  # 8 corners × 3 coordinates
embeddings: FloatArray[Dims[D[1000], D[384]]]  # 1000 embeddings × 384 dimensions

# Using N for flexible dimensions (equivalent to -1)
batch: IntArray[Dims[N, D[224], D[224], D[3]]]  # Any batch size × 224×224 RGB images
sequence: Array[Dims[N, D[768]]]  # Any sequence length × 768 features

# In the following example, it's immediately clear how the vectors are represented.
def operation_on_3d_vectors(vectors: Array[Dims[N, D[3]]]) -> Array[Dims[N, D[3]]]:
    ...
```

### Creating Typed Arrays

NumTypes provides helper functions to create arrays with explicit type information:

```python
from numtypes import array, array_1d, array_2d, Float, Double, Int

# Create with exact shape
arr = array([1, 2, 3], shape=(3,))  # Array[Dims[D[3]]]
mat = array([[1, 2], [3, 4]], shape=(2, 2))  # Array[Dims[D[2], D[2]]]

# Convenience functions for common cases
vec = array_1d([1, 2, 3])  # Vector (alias for Array[Dim1])
mat = array_2d([[1, 2], [3, 4]])  # Matrix (alias for Array[Dim2])

# Specify data types
float_arr = array([1.0, 2.0], shape=(2,), dtype=np.float32)  # Array[Dims[D[2]], Float]
double_arr = array_1d([1.0, 2.0], dtype=np.float64)  # Array[Dim1, Double]
int_arr = array([1, 2], shape=(2,), dtype=np.int32)  # Array[Dims[D[2]], Int]
```

### Runtime Shape Validation

Use `shape_of()` to validate shapes at runtime while providing type information to your type checker:

```python
from numtypes import shape_of, Array, UnknownShape, AnyShape

def process_batch(images: Array) -> Array:
    # Validate the shape
    assert shape_of(images, matches=(32, 224, 224, 3))
    
    # Type checker now knows images has shape (32, 224, 224, 3)
    normalized = images / 255.0
    
    # Validate the output shape if needed
    assert shape_of(normalized, matches=(32, 224, 224, 3))
    return normalized

# Flexible shape validation
assert shape_of(data, matches=(-1, 128))  # Any number of rows, exactly 128 columns
assert shape_of(sequence, matches=(100, -1, -1))  # 100 sequences of any shape
```

### Type Aliases for Common Use Cases

NumTypes provides convenient type aliases for common array types and shapes:

```python
from numtypes import Vector, Matrix, IntArray, BoolArray, FloatArray, IndexArray, Long

# Data type aliases
mask: BoolArray[Dim2]  # 2D boolean array
indices: IntArray[Dim1]  # 1D integer array  
scores: FloatArray[Dims[D[100]]]  # Exactly 100 float scores (float32)
labels: Array[Dims[D[1000]], Long]  # 1000 int64 labels

# Shape aliases
embedding: Vector[D[384]]  # 1D array of 384 elements
rotation: Matrix[D[3], D[3]]  # 3×3 matrix

# Special arrays
sorted_indices: IndexArray[UnknownShape] = np.argsort(scores)  # From argsort
```

You can still use any NumPy data type directly, but these aliases help with readability in common cases.

### Working with NumPy Operations

> ⚠️ **Important**: Many NumPy operations currently lose type information. For example, adding
> two arrays or computing the mean will result in an array with an unknown shape. In general,
> you don't always need to know the exact shape of an array after every operation. As such,
> it makes the most sense to use `shape_of()` to validate the shape of the result only when you need it,
> e.g. when passing an array as an argument to a function, or when returning it from a function. 

Here's how to handle common cases:

```python
# These provide type info correctly.
zeros: Array[Dim2] = np.zeros((5, 5))
ones: Array[Dim3] = np.ones((3, 4, 5))

# Operations that preserve type info
negated: Array[Dim2] = -zeros  # Still an Array[Dim2]

# Operations that lose type info - use shape_of to recover it
data: Array[Dim2] = array_2d([[1.0, 2.0], [3.0, 4.0]])
mean_per_row = data.mean(axis=1)  # Type checker doesn't know the shape
assert shape_of(mean_per_row, matches=(-1,))  # Now it knows it's 1D

# Alternative: use type annotations with `# type: ignore` statements or type casts.
mean_per_row: Array[Dim1] = data.mean(axis=1)  # type: ignore

# For complex operations, validate intermediate results
def matrix_operation(a: Matrix, b: Matrix) -> Vector:
    assert shape_of(a, matches=(10, 20))
    assert shape_of(b, matches=(20, 30))
    
    result = a @ b  # Matrix multiplication
    assert shape_of(result, matches=(10, 30))
    
    flattened = result.reshape(-1)
    assert shape_of(flattened, matches=(300,))
    
    return flattened
```

### Debugging Shape Mismatches

NumTypes supports configuration for debugging shape validation failures:

```python
from numtypes import config
import ipdb

# Configure a debugger to be called on shape mismatch, e.g. ipdb
config.configure(debugger=ipdb.set_trace)

# Configure logging for shape mismatches
config.configure(logger=lambda msg: print(f"Shape mismatch: {msg}"))

array = ...  # Some NumPy array

# Now shape_of will trigger these on failure
assert shape_of(array, matches=(10, 10))  # Will call debugger/logger if shape doesn't match
```

### Removing Runtime Validation

Because the idiomatic usage of `shape_of()` leverages the built in assert statement, you can easily remove runtime validation
by just enabling optimization for your Python interpreter. This is done by running Python with the `-O` flag:

```bash
python -O your_script.py
```

This won't affect the type checking, but will remove whatever overhead the runtime validations introduce.

## ⚙️ Type Checker Compatibility

**Note**: This library is currently only tested with **Pyright** (including Pylance in VS Code). 
Compatibility with mypy and other type checkers is not guaranteed.

## Other Limitations

- **Python Compatibility**: This library requires Python 3.13 or later, due to the latest typing features/syntax used.
- **Structured Arrays**: This library does not support structured arrays (i.e. arrays with named fields).
- **Type Coverage**: The convenience aliases probably don't cover every use case. You can always define your own types using the provided `Array`, `Dims`, and `DimX` types though. If a type feels too common to be missing, please open an issue or PR!
- **Suboptimal Syntax**: The current syntax is not perfect, but it is a trade-off between conciseness and type safety. Even though the ideal
type annotations would look like `Array[8, 3, 2, Float]`, this is currently not possible with the syntax Python supports. Although
one could make `Array[8, 3, 2, Float]` work using `__class_getitem__`, it would not be understandable for type checkers.

## 🤝 Contributing

TODO: Contributing guide coming soon! For now, feel free to open issues and PRs.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](https://gitlab.com/zurabm/numtypes/-/blob/master/LICENSE) file for details.
