from typing import (
    Optional, 
    Union, 
    Any
)

from ...typing import (
    TensorLike, 
    DTypeLike, 
    Casting,
    Order, 
    ArrayLikeBool,
    ArrayLike
)

from ..exceptions import (
    DeviceMismatch, DEVICE_MISMATCH_MSG,
    CuPyNotFound, CUPY_NOT_FOUND_MSG
)

import numpy as np
try:
    import cupy as cp
except (ImportError, ModuleNotFoundError):
    cp = None

###
### Arithmetics
###

def add(
    x1: TensorLike, 
    x2: TensorLike, 
    /,
    out: Optional[Union[np.ndarray, Any]] = None,
    *,
    in_place: bool = False,
    where: Union[ArrayLikeBool, bool] = True,
    casting: Casting = 'same_kind',
    order: Order = 'K',
    dtype: Optional[DTypeLike] = None,
    subok: bool = True
) -> TensorLike:
    if not x1.is_device(x2.device): raise DeviceMismatch(DEVICE_MISMATCH_MSG)
    from ...tensor import Tensor
    if x1.is_cpu():
        y = np.add(x1.data, x2.data, out=out, dtype=dtype, where=where, casting=casting, order=order, subok=subok)
    else:
        if cp is None: raise CuPyNotFound(CUPY_NOT_FOUND_MSG)
        y = cp.add(x1.data, x2.data, out=out, dtype=dtype, casting=casting)
    if in_place:
        x1.data = y
        return x1
    return Tensor(y, device=x1.device, prev=(x1, x2), requires_grad=x1.requires_grad or x2.requires_grad)

def subtract(
    x1: TensorLike, 
    x2: TensorLike, 
    /,
    out: Optional[Union[np.ndarray, Any]] = None,
    *,
    in_place: bool = False,
    where: Union[ArrayLikeBool, bool] = True,
    casting: Casting = 'same_kind',
    order: Order = 'K',
    dtype: Optional[DTypeLike] = None,
    subok: bool = True
) -> TensorLike:
    if not x1.is_device(x2.device): raise DeviceMismatch(DEVICE_MISMATCH_MSG)
    from ...tensor import Tensor
    if x1.is_cpu():
        y = np.subtract(x1.data, x2.data, out=out, dtype=dtype, where=where, casting=casting, order=order, subok=subok)
    else:
        if cp is None: raise CuPyNotFound(CUPY_NOT_FOUND_MSG)
        y = cp.subtract(x1.data, x2.data, out=out, dtype=dtype, casting=casting)
    if in_place:
        x1.data = y
        return x1
    return Tensor(y, device=x1.device, prev=(x1, x2), requires_grad=x1.requires_grad or x2.requires_grad)

def multiply(
    x1: TensorLike, 
    x2: TensorLike, 
    /,
    out: Optional[Union[np.ndarray, Any]] = None,
    *,
    in_place: bool = False,
    where: Union[ArrayLikeBool, bool] = True,
    casting: Casting = 'same_kind',
    order: Order = 'K',
    dtype: Optional[DTypeLike] = None,
    subok: bool = True
) -> TensorLike:
    if not x1.is_device(x2.device): raise DeviceMismatch(DEVICE_MISMATCH_MSG)
    from ...tensor import Tensor
    if x1.is_cpu():
        y = np.multiply(x1.data, x2.data, out=out, dtype=dtype, where=where, casting=casting, order=order, subok=subok)
    else:
        if cp is None: raise CuPyNotFound(CUPY_NOT_FOUND_MSG)
        y = cp.multiply(x1.data, x2.data, out=out, dtype=dtype, casting=casting)
    if in_place:
        x1.data = y
        return x1
    return Tensor(y, device=x1.device, prev=(x1, x2), requires_grad=x1.requires_grad or x2.requires_grad)

def matmul(
    x1: TensorLike, 
    x2: TensorLike, 
    /,
    out: Optional[Union[np.ndarray, Any]] = None,
    *,
    in_place: bool = False,
    casting: Casting = 'same_kind',
    order: Order = 'K',
    dtype: Optional[DTypeLike] = None,
    subok: bool = True
) -> TensorLike:
    if not x1.is_device(x2.device): raise DeviceMismatch(DEVICE_MISMATCH_MSG)
    from ...tensor import Tensor
    if x1.is_cpu():
        y = np.matmul(x1.data, x2.data, out=out, casting=casting, order=order, dtype=dtype, subok=subok)
    else:
        if cp is None: raise CuPyNotFound(CUPY_NOT_FOUND_MSG)
        y = cp.matmul(x1.data, x2.data, out=out, dtype=dtype, casting=casting)
    if in_place:
        x1.data = y
        return x1
    return Tensor(y, device=x1.device, prev=(x1, x2), requires_grad=x1.requires_grad or x2.requires_grad)

def divide(
    x1: TensorLike, 
    x2: TensorLike, 
    /,
    out: Optional[Union[np.ndarray, Any]] = None,
    *,
    in_place: bool = False,
    where: Union[ArrayLikeBool, bool] = True,
    casting: Casting = 'same_kind',
    order: Order = 'K',
    dtype: Optional[DTypeLike] = None,
    subok: bool = True
) -> TensorLike:
    if not x1.is_device(x2.device): raise DeviceMismatch(DEVICE_MISMATCH_MSG)
    from ...tensor import Tensor
    if x1.is_cpu():
        y = np.divide(x1.data, x2.data, out=out, dtype=dtype, where=where, casting=casting, order=order, subok=subok)
    else:
        if cp is None: raise CuPyNotFound(CUPY_NOT_FOUND_MSG)
        y = cp.divide(x1.data, x2.data, out=out, dtype=dtype, casting=casting)
    if in_place:
        x1.data = y
        return x1
    return Tensor(y, device=x1.device, prev=(x1, x2), requires_grad=x1.requires_grad or x2.requires_grad)

def negative(
    x: TensorLike,
    /,
    out: Optional[Union[np.ndarray, Any]] = None, 
    *,
    in_place: bool = False,
    where: Union[ArrayLikeBool, bool] = True,
    casting: Casting = 'same_kind',
    order: Order = 'K',
    dtype: Optional[DTypeLike] = None,
    subok: bool = True
) -> TensorLike:
    from ...tensor import Tensor
    if x.is_cpu():
        y = np.negative(x.data, out=out, dtype=dtype, where=where, casting=casting, order=order, subok=subok)
    else:
        if cp is None: raise CuPyNotFound(CUPY_NOT_FOUND_MSG)
        y = cp.negative(x.data, out=out, dtype=dtype, casting=casting)
    if in_place:
        x.data = y
        return x
    return Tensor(y, device=x.device, prev=(x,), requires_grad=x.requires_grad)

def sign(
    x: TensorLike,
    /,
    out: Optional[Union[np.ndarray, Any]] = None, 
    *,
    in_place: bool = False,
    where: Union[ArrayLikeBool, bool] = True,
    casting: Casting = 'same_kind',
    order: Order = 'K',
    dtype: Optional[DTypeLike] = None,
    subok: bool = True
) -> TensorLike:
    from ...tensor import Tensor
    if x.is_cpu():
        y = np.sign(x.data, out=out, dtype=dtype, where=where, casting=casting, order=order, subok=subok)
    else:
        if cp is None: raise CuPyNotFound(CUPY_NOT_FOUND_MSG)
        y = cp.sign(x.data, out=out, dtype=dtype, casting=casting)
    if in_place:
        x.data = y
        return x
    return Tensor(y, device=x.device, prev=(x,), requires_grad=x.requires_grad)

def abs(
    x: TensorLike,
    /,
    out: Optional[Union[np.ndarray, Any]] = None, 
    *,
    in_place: bool = False,
    where: Union[ArrayLikeBool, bool] = True,
    casting: Casting = 'same_kind',
    order: Order = 'K',
    dtype: Optional[DTypeLike] = None,
    subok: bool = True
) -> TensorLike:
    from ...tensor import Tensor
    if x.is_cpu():
        y = np.abs(x.data, out=out, dtype=dtype, where=where, casting=casting, order=order, subok=subok)
    else:
        if cp is None: raise CuPyNotFound(CUPY_NOT_FOUND_MSG)
        y = cp.abs(x.data, out=out, dtype=dtype, casting=casting)
    if in_place:
        x.data = y
        return x
    return Tensor(y, device=x.device, prev=(x,), requires_grad=x.requires_grad)

def clip(
    a: TensorLike,
    a_min: TensorLike,
    a_max: TensorLike,
    /,
    out: Optional[ArrayLike] = None,
    *,
    where: Union[bool, ArrayLikeBool] = True,
    casting: Casting = 'same_kind',
    order: Order = 'K',
    dtype: Optional[DTypeLike] = None,
    subok: bool = True
) -> TensorLike:
    from ...tensor import Tensor
    if not (a.device == a_min.device == a_max.device): raise DeviceMismatch(DEVICE_MISMATCH_MSG)
    if a.is_cpu():
        if out is None:
            y = np.clip(a.data, a_min.data, a_max.data, where=where, casting=casting, order=order, dtype=dtype, subok=subok)
        else:
            y = np.clip(a.data, a_min.data, a_max.data, out=out, where=where, casting=casting, order=order, dtype=dtype, subok=subok)
    else:
        if cp is None: raise CuPyNotFound(CUPY_NOT_FOUND_MSG)
        y = cp.clip(a.data, a_min.data, a_max.data, out=out)
    return Tensor(y)

###
### Exponents/Logarithms
###

def exp(
    x: TensorLike, 
    /, 
    out: Optional[Union[np.ndarray, Any]] = None,
    *,
    in_place: bool = False,
    where: Union[bool, ArrayLikeBool] = True, 
    casting: Casting = 'same_kind',
    order: Order = 'K', 
    dtype: Optional[DTypeLike] = None, 
    subok: bool = True
) -> TensorLike:
    from ...tensor import Tensor
    if x.is_cpu():
        y = np.exp(x.data, out=out, where=where, casting=casting, order=order, dtype=dtype, subok=subok)
    else:
        if cp is None: raise CuPyNotFound(CUPY_NOT_FOUND_MSG)
        y = cp.exp(x.data, out=out, casting=casting, dtype=dtype)
    if in_place:
        x.data = y
        return x
    return Tensor(y, device=x.device, prev=(x,), requires_grad=x.requires_grad)

def sqrt(
    x: TensorLike, 
    /, 
    out: Optional[Union[np.ndarray, Any]] = None,
    *,
    in_place: bool = False,
    where: Union[bool, ArrayLikeBool] = True, 
    casting: Casting = 'same_kind',
    order: Order = 'K', 
    dtype: Optional[DTypeLike] = None, 
    subok: bool = True
) -> TensorLike:
    from ...tensor import Tensor
    if x.is_cpu():
        y = np.sqrt(x.data, out=out, where=where, casting=casting, order=order, dtype=dtype, subok=subok)
    else:
        if cp is None: raise CuPyNotFound(CUPY_NOT_FOUND_MSG)
        y = cp.sqrt(x.data, out=out, casting=casting, dtype=dtype)
    if in_place:
        x.data = y
        return x
    return Tensor(y, device=x.device, prev=(x,), requires_grad=x.requires_grad)

def log(
    x: TensorLike, 
    /, 
    out: Optional[Union[np.ndarray, Any]] = None,
    *,
    in_place: bool = False,
    where: Union[bool, ArrayLikeBool] = True, 
    casting: Casting = 'same_kind',
    order: Order = 'K', 
    dtype: Optional[DTypeLike] = None, 
    subok: bool = True
) -> TensorLike:
    from ...tensor import Tensor
    if x.is_cpu():
        y = np.log(x.data, out=out, where=where, casting=casting, order=order, dtype=dtype, subok=subok)
    else:
        if cp is None: raise CuPyNotFound(CUPY_NOT_FOUND_MSG)
        y = cp.log(x.data, out=out, casting=casting, dtype=dtype)
    if in_place:
        x.data = y
        return x
    return Tensor(y, device=x.device, prev=(x,), requires_grad=x.requires_grad)

def square(
    x: TensorLike, 
    /, 
    out: Optional[Union[np.ndarray, Any]] = None,
    *,
    in_place: bool = False,
    where: Union[bool, ArrayLikeBool] = True, 
    casting: Casting = 'same_kind',
    order: Order = 'K', 
    dtype: Optional[DTypeLike] = None, 
    subok: bool = True
) -> TensorLike:
    from ...tensor import Tensor
    if x.is_cpu():
        y = np.square(x.data, out=out, where=where, casting=casting, order=order, dtype=dtype, subok=subok)
    else:
        if cp is None: raise CuPyNotFound(CUPY_NOT_FOUND_MSG)
        y = cp.square(x.data, out=out, casting=casting, dtype=dtype)
    if in_place:
        x.data = y
        return x
    return Tensor(y, device=x.device, prev=(x,), requires_grad=x.requires_grad)

###
###
###

__all__ = [
    'add', 'subtract', 'multiply', 'matmul', 'divide',
    'negative', 'sign', 'abs',

    'exp', 'sqrt', 'log', 'square',

    'clip'
]