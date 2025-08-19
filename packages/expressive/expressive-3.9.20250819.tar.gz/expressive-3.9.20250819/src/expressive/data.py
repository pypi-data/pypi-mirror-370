""" Copyright 2025 Russell Fordyce

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import re

import numpy
import sympy

from .config import DTYPES_SUPPORTED, SYMPY_ATOMS_FP, SYMPY_ATOMS_PROMOTE
from .messaging import warn


def data_cleanup(data):
    """ verify the incoming data can be used

        currently this expects a dict of numpy arrays

        FUTURE optional other numpy-backed arrays support (ie. Pandas, Polars, etc.)
          for now, users can use the relevant .to_numpy() methods
          also consider .to_records()
    """
    if not data:
        raise ValueError("no data provided")
    if not isinstance(data, dict):
        raise TypeError(f"data must be a dict of NumPy arrays or scalars, but got {type(data)}")

    data_cleaned = {}
    vector_length = {}
    for name, ref in data.items():
        # check name is sensible
        # NOTE that expr parsing removes spaces, which might mash symbols together
        if not isinstance(name, str):
            raise ValueError(f"data names must be strings, but got {type(name)}: {repr(name)}")
        # NOTE `name.isidentifier()` and "\w+" allow some unsuitable valies like "π" and "_"
        if not name.isidentifier() or name.startswith("_") or name.endswith("_") or not re.match(r"^[a-zA-Z\d_]+$", name):
            raise ValueError(f"data names must be valid Python names (identifiers) and Symbols, but got '{name}'")
        # TODO consider warning for keywords `keyword.iskeyword(name)`, but allow some?.. like "del"
        # coerce single python values to 0-dim numpy values
        if isinstance(ref, (int, float, complex)):
            # NOTE chooses widest, signed type for Python values (int64,float64,complex128)
            #   if users want another type, just choose it (ie. `numpy.uint32(10)`)
            # TODO is there a better way to do automatic typing?
            # TODO config option to prefer min type `numpy.array(ref, numpy.min_scalar_type(ref))`
            ref = numpy.array(ref)[()]
        if not isinstance(ref, (numpy.ndarray, numpy.number)):
            raise TypeError(f"data must be a dict of NumPy arrays or scalars, but has member ({name}:{type(ref)})")
        if ref.dtype not in DTYPES_SUPPORTED:
            raise TypeError(f"unsupported dtype ({name}:{ref.dtype})")
        # NOTE single (ndim==0) values have shape==() and `len(array)` raises `TypeError: len() of unsized object`
        if ref.ndim == 0:
            vector_length[name] = 0
        elif ref.ndim == 1:
            vector_length[name] = len(ref)
        else:
            vector_length[name] = len(ref)  # FUTURE further analysis needed for additional dimensions
        data_cleaned[name] = ref

    # compare shapes and warn for mixed dimensions
    shapes = set(ref.shape for ref in data_cleaned.values()) - {()}  # ignore single values (0-dim)
    if len(shapes) > 1 and any(ref.ndim > 1 for ref in data.values()):
        warn(f"mixed dimensions may not broadcast correctly, got shapes={shapes}")

    # FUTURE consider support for uneven input arrays when indexed [ISSUE 10]
    #   specifically offsets can make it so the data does not need the same lengths or
    #   can be padded to be the correct length automatically
    #   however, this also seems ripe for confusion and errors
    vector_lengths = set(vector_length.values())
    if vector_lengths == {0}:
        raise ValueError("only single values passed (ndim=0), no arrays (at least a result array must be passed to determine length)")
    elif len(vector_lengths - {0}) != 1:
        raise ValueError(f"uneven data lengths (must be all equal or 0 (non-vector)): {vector_lengths}")

    return data_cleaned


def dtype_result_guess(expr, data):
    """ attempt to automatically determine the resulting dtype given an expr and data

        this is a backup where the user has not provided a result dtype
        possibly it could support warning for likely wrong dtype

        this is not expected to be a general solution as the problem is open-ended
        and likely depends on the real data

        WARNING this logic assumes the highest bit-width is 64
          larger widths will require rewriting some logic!
          intermediately a user should specify the type, assuming
          a (future) numba really has support for it

        FUTURE consider  `numpy.dtype.alignment`
    """
    # set of dtypes from given data
    dtypes_expr = {c.dtype for c in data.values()}  # set of NumPy types

    # throw out some obviously bad cases
    if not dtypes_expr:
        raise ValueError("no data provided")
    dtypes_unsupported = dtypes_expr - set(DTYPES_SUPPORTED.keys())
    if dtypes_unsupported:
        raise TypeError(f"unsupported dtypes: {dtypes_unsupported}")

    # always return a complex type if present
    if numpy.dtype("complex128") in dtypes_expr or expr.atoms(sympy.I):
        return numpy.dtype("complex128")
    # complex64 is a pair of 32-bit floats, but some types don't cast nicely
    if numpy.dtype("complex64") in dtypes_expr:
        width_noncomplex = max(DTYPES_SUPPORTED[dt] for dt in dtypes_expr if not dt.kind == "c")
        if not width_noncomplex or width_noncomplex <= 32:
            return numpy.dtype("complex64")
        if numpy.dtype("int64") in dtypes_expr or numpy.dtype("uint64") in dtypes_expr:
            # NOTE the default casting for int64+complex64 is complex64, even though it doesn't have enough bits
            return numpy.dtype("complex128")
        if numpy.dtype("float64") not in dtypes_expr:
            raise RuntimeError(f"BUG: expected float64, but got {dtypes_expr}")
        return numpy.dtype("complex128")

    max_bitwidth = max(DTYPES_SUPPORTED[dt] for dt in dtypes_expr)

    # FUTURE support for float128 (does Numba support this?)
    if max_bitwidth > 64:
        raise RuntimeError(f"BUG: max_bitwidth {max_bitwidth}: only complex types exceeding 64 are supported: {dtypes_expr}")

    # now only
    if numpy.dtype("float64") in dtypes_expr:
        return numpy.dtype("float64")
    # promote 32-bit float to 64-bit when greater types are present
    if numpy.dtype("float32") in dtypes_expr:
        if max_bitwidth > 32:
            return numpy.dtype("float64")
        return numpy.dtype("float32")

    # detect structures that make the result logically floating-point
    # TODO perhaps these should be part of a structured attempt to constrain inputs
    #   in addition to being available for guessing resulting type,
    #   even if the constraints are (initially) warns, not hard errors
    # see https://docs.sympy.org/latest/modules/functions/elementary.html
    if (
        expr.atoms(
            *SYMPY_ATOMS_FP
        ) or (
            # discover simple division
            # direct Integers are Rational, but fractional atoms are not Integer
            # additionally, simple divisions will simplify to Integer
            #   >>> parse_expr("4").atoms(Rational), parse_expr("4").atoms(Integer)
            #   ({4}, {4})
            #   >>> parse_expr("4/2").atoms(Rational), parse_expr("4/2").atoms(Integer)
            #   ({2}, {2})
            #   >>> e = "4/2*x + 1/3*y"
            #   >>> parse_expr(e).atoms(Rational) - parse_expr(e).atoms(Integer)
            #   {1/3}
            expr.atoms(sympy.Rational) - expr.atoms(sympy.Integer)
        ) or (
            # detect N/x constructs
            #   >>> srepr(parse_expr("2/x"))
            #   "Mul(Integer(2), Pow(Symbol('x'), Integer(-1)))"
            expr.match(sympy.Pow(sympy.Wild("", properties=[lambda a: a.is_Symbol or a.is_Function]), sympy.Integer(-1)))
        )
    ):
        if max_bitwidth <= 16:  # TODO is this a good assumption?
            return numpy.dtype("float32")
        return numpy.dtype("float64")

    # now pick the largest useful int
    # NOTE constant coefficients should all be Integer (Rational) if reached here

    w_signed   = 0  # NOTE Falsey
    w_unsigned = 0
    for dtype in dtypes_expr:
        if numpy.issubdtype(dtype, numpy.signedinteger):
            w_signed = max(w_signed, DTYPES_SUPPORTED[dtype])
        elif numpy.issubdtype(dtype, numpy.unsignedinteger):
            w_unsigned = max(w_unsigned, DTYPES_SUPPORTED[dtype])
        else:
            raise RuntimeError(f"BUG: failed to determine if {dtype} is a signed or unsigned int (is it a float?)")
    if w_signed and w_unsigned:
        raise TypeError("won't guess dtype for mixed int and uint, must be provided")

    # NOTE without a result array, Numba often chooses widest int64 even for int8,int16 when promoting
    if w_signed and not w_unsigned:
        return numpy.dtype("int64") if (w_signed > 32 or expr.atoms(*SYMPY_ATOMS_PROMOTE)) else numpy.dtype("int32")
    if not w_signed and w_unsigned:
        return numpy.dtype("uint64") if (w_unsigned > 32 or expr.atoms(*SYMPY_ATOMS_PROMOTE)) else numpy.dtype("uint32")

    raise RuntimeError(f"BUG: couldn't determine a good result dtype for {dtypes_expr}")


def get_result_dtype(expr_sympy, results, data, dtype_result=None):
    """ ensure the result datatype matches what's given if any
        use a reasonable guess when not provided explicitly or via result data array
    """
    if dtype_result is not None:                  # string convert
        dtype_result = numpy.dtype(dtype_result)  # idempotent for NumPy types

    if results:
        name_result = next(iter(results.keys()))  # NOTE dict of 1 value
        try:
            dtype_data_result = data[name_result].dtype
        except KeyError:  # name not in in data (not passed: create array later)
            dtype_data_result = None
        else:  # data array contains result for dtype, if expressly provided too, ensure they match
            if dtype_result is None:
                dtype_result = dtype_data_result
            else:
                if dtype_data_result != dtype_result:
                    raise ValueError(f"passed mismatched result array ({dtype_data_result}) and result dtype ({dtype_result})")

    # if dtype_result is still None, guess or raise
    if dtype_result is None:
        dtype_result = dtype_result_guess(expr_sympy, data)

    if dtype_result not in DTYPES_SUPPORTED:
        raise RuntimeError(f"BUG: dtype_result ({dtype_result}) not in DTYPES_SUPPORTED")

    # definitely a supported NumPy type now
    return dtype_result


def verify_indexed_data_vs_symbols(symbols, result_passed, data):
    """ if this instance is indexed, make sure the data makes sense for it
        for example, with "a + b[i]", `a` must be a single value and `b` must be an array

        TODO consider if this should be merged with `signature_generate()`
    """
    names_symbols = list(symbols.keys())
    if not result_passed:
        names_symbols.pop()  # drop the result name (guaranteed to be last symbol in dict)

    for name in names_symbols:
        symbol = symbols[name]
        dims   = data[name].ndim
        if isinstance(symbol, sympy.IndexedBase) and dims == 0:
            raise ValueError(f"'{name}' is indexed, but is a single (ndim={dims}) value in data")
        if isinstance(symbol, sympy.Symbol) and dims > 0:
            title = {1: "array", 2: "matrix"}.get(dims, "tensor")
            raise ValueError(f"'{name}' is not indexed, but passed {title} (ndim={dims}) value in data")
