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

import time

import numpy
import sympy

from .messaging import warn

NS10E9 = 10**9  # factor for nanoseconds to second(s)


def verify_cmp(data, expr_sympy, fn_python, fn_compiled, indexers):
    """ check if the compiled and python (pre-jit) functions have the same results
        this helps catch undefined behavior in Numba space, such as log(0)
    """
    # FIXME many magic numbers should be part of config subsystem [ISSUE 29]
    lengths = {k: (len(ref) if ref.ndim == 1 else 1) for k, ref in data.items()}
    lengths_max = max(lengths.values())
    data_names_containing_nan = []
    for name, ref in data.items():
        if numpy.isnan(ref).any():
            data_names_containing_nan.append(name)
    if data_names_containing_nan:
        warn(f"some data in {','.join(data_names_containing_nan)} is NaN")

    time_start = time.process_time_ns()
    result_py = fn_python(**data)
    time_py = time.process_time_ns() - time_start

    time_start = time.process_time_ns()
    result_nb = fn_compiled(**data)
    time_nb = time.process_time_ns() - time_start

    # hint user that using a lot of data
    if (time_py > 10 * NS10E9) and (lengths_max > 2000):
        warn(f"excessive data may be slowing native verify (python:{time_py / NS10E9:.2f}s, compiled:{time_nb}ns) (data lengths {lengths})")

    # check if either ran more than 30 seconds
    if (time_py >= 30 * NS10E9) or (time_nb >= 30 * NS10E9):
        warn(f"verify took a long time python:{time_py / NS10E9:.2f}s, compiled:{time_nb / NS10E9:.2f}s")

    # hint that just NumPy might actually be faster
    if lengths_max >= 1000:
        if time_nb / time_py > 2:  # NumPy is at least twice as fast
            warn(f"compiled function ({time_nb}ns) may be slower than direct NumPy ({time_py}ns) (data lengths {lengths})")

    # symbolics -> Number -> evalf()
    # FUTURE consider collecting Exceptions into a single warning reporting multiple rows
    result_sp = None
    if not indexers and all(d.ndim <= 1 for d in data.values()):  # no indexed values or tensors
        # NOTE numpy.nan are never equal, while sympy.nan are structurally equal, but not symbolically
        #   >>> numpy.nan == numpy.nan
        #   False
        #   >>> sympy.nan == sympy.nan
        #   True
        #   >>> sympy.Eq(numpy.nan, numpy.nan)
        #   False
        #   >>> sympy.Eq(sympy.nan, sympy.nan)
        #   False
        # NOTE numpy.log() handling of negative/zero values is -inf, not a complex value
        # so `sympy.zoo` is converted to `-numpy.inf`, not something like `numpy.complex64(numpy.inf)`
        # however, it might be worth considering `numpy.emath.log()`, which returns the "principle value"
        #   >>> sympy.log(0)
        #   zoo
        #   >>> numpy.log(0)
        #   -inf
        #   >>> numpy.emath.log(0)
        #   -inf
        #   >>> sympy.log(-1)
        #   I*pi
        #   >>> numpy.log(-1)
        #   nan
        #   >>> numpy.emath.log(-1)
        #   3.141592653589793j
        mapper_incomparable_sympy_results = {
            sympy.oo:   numpy.inf,
            sympy.zoo: -numpy.inf,
            sympy.nan:  numpy.nan,
        }
        result_sp = []
        for ref in data.values():
            if ref.ndim == 1:
                length = len(ref)
                break
        else:  # should have been trapped in `data_cleanup(data)`
            dims = {name: ref.ndim for name, ref in data.items()}  # pragma nocover (helper for impossible path)
            raise RuntimeError(f"BUG: no values with ndim==1 passed somehow all single values or tensors: {dims}")
            # length = 1  # FUTURE if allowing single values
        for index in range(length):
            row = {}
            row_nan = False  # track if the row has nan
            for symbols in data.keys():  # needed to handle single values
                value = data[symbols] if data[symbols].ndim == 0 else data[symbols][index]
                if numpy.isnan(value):
                    row_nan = True
                    break
                row[symbols] = value

            if row_nan:  # row is broken, write nan and continue
                result_sp.append(numpy.nan)  # NOTE sympy.nan are equal
                continue  # next row
            # directly use result as `Eq(LHS,RHS)` when no indexers are passed
            r = expr_sympy.rhs.subs(row).evalf()
            # print(f"row build {expr_sympy.rhs} -> {expr_sympy.rhs.subs(row)} -> {r}")  # debug
            if sympy.I in r.atoms():  # "3 * 1j" -> "3*I" -> "3j"
                r = complex(r)
            else:
                r = mapper_incomparable_sympy_results.get(r) or float(r)  # nan is not Falsey, 0->0.0
            result_sp.append(r)

    if indexers:
        indexer, (start, end) = next(iter(indexers.items()))
        start = -start
        end   = -end or None  # `1` to `-1`, `0` to `None`
        result = numpy.allclose(result_py[start:end], result_nb[start:end], equal_nan=True)
    elif result_sp:  # not indexed and no tensors
        result = []  # collection of bool
        for index in range(length):
            value_np, value_py, value_sp = result_nb[index], result_py[index], result_sp[index]
            r1 = numpy.allclose(value_np, value_py, equal_nan=True)
            r2 = numpy.allclose(value_py, value_sp, equal_nan=True)
            r3 = numpy.allclose(value_sp, value_np, equal_nan=True)
            result.append(r1 and r2 and r3)  # (this is a bool)
        result = all(result)  # compact collection into single bool
    else:  # tensor route
        try:
            length = next(len(ref) for ref in data.values() if ref.ndim > 1)
        except StopIteration:  # pragma nocover (impossible path)
            dims = {name: ref.ndim for name, ref in data.items()}
            raise RuntimeError("BUG: used tensor path, but no data had ndim>1: {dims}")
        result = []  # collection of bool
        for index in range(length):
            result.append(numpy.allclose(result_nb[index], result_py[index], equal_nan=True))
        result = all(result)  # compact collection into single bool

    results = {
        "nb": result_nb,
        "py": result_py,
        "sp": result_sp,
    }
    # print("results:")  # debug
    # print(results)

    if not result:  # FUTURE opportunity to hard fail here (via from config?) [ISSUE 29]
        raise RuntimeError(f"not allclose({result}) when comparing between NumPy and compiled function")
    return result, results
