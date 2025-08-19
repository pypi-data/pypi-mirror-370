#!/usr/bin/env python3

""" Copyright 2024-2025 Russell Fordyce

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

import unittest
import unittest.mock

import contextlib
import itertools
import json
import os
import re
import subprocess
import sys
import time
import warnings
from collections import UserDict
from copy import deepcopy
from shlex import split as shlex_split
from textwrap import dedent as text_dedent
from textwrap import indent as text_indent
from queue import Empty as EmptyQueueException

import numba
import numpy
import sympy

import expressive
from expressive import Expressive


VERSION_SYMPY = tuple(map(int, sympy.__version__.split('.')))[:2]

# pass-through some version-dependent warnings
WARNS_PASSTHROUGH = [
    # https://numpy.org/doc/stable/release/1.22.0-notes.html#the-np-machar-class-has-been-deprecated
    r"`np\.(core\.)?MachAr` (module )?is (deprecated|considered private)",
]


@contextlib.contextmanager
def must_warn_re(warning_regexes, ordered=False, multimatch=False, warns_passthrough=None):
    """ helper similar to pytest's .warns() which implements more advanced
        warning catch-match functionality than unittest natively supports
        however, it doesn't bother matching the warning type and assumes
        the message is sufficient to be a match

        specifically unittest's .assertWarns() doesn't work nicely with
        multiple expected warnings and consumes all warnings within its context

        pytest .warns() doc
            https://docs.pytest.org/en/stable/how-to/capture-warnings.html#warns
    """
    if isinstance(warning_regexes, str):
        warning_regexes = [warning_regexes]
    if not isinstance(warning_regexes, (list, set, tuple)):  # pragma nocover
        raise ValueError(f"warning_regexes must be one of [str,list,set,tuple], but got {type(warning_regexes)}")
    if ordered and isinstance(warning_regexes, set):  # pragma nocover
        raise ValueError("warning_regexes passed as a set which is unordered, but ordered=True")

    if warns_passthrough is None:
        warns_passthrough = WARNS_PASSTHROUGH

    # TODO make exact string vs regex easier/more obvious, assumes re for now
    with warnings.catch_warnings(record=True) as warning_collection:
        yield
        warning_messages = []  # collect warnings to compare with warning_regexes
        warnings_rewarn  = []  # collect known-spurious warnings to re-warn them
        for warning in warning_collection:
            warn_msg = str(warning.message)
            for warn_re in warns_passthrough:
                if re.match(warn_re, warn_msg):  # pragma nocover (not a guaranteed path)
                    warnings_rewarn.append(warning)
                    break  # discovered a warning to re-warn
            else:  # no warns_passthrough matched
                warning_messages.append(warn_msg)

    # re-warn outside of the .catch_warnings() context
    # this also attempts to discover which test the warning came from by inspecting the stack
    # https://stackoverflow.com/questions/76314792/python-catching-and-then-re-throw-warnings-from-my-code
    # https://stackoverflow.com/questions/2654113/how-to-get-the-callers-method-name-in-the-called-method
    if warnings_rewarn:  # pragma nocover (not a guaranteed path)
        call_frame = None
        try:
            import inspect
            for frame in inspect.stack()[1:]:  # here, __exit__, caller, ?..
                if frame.filename.endswith(("test.py", "test.pyc")):
                    call_frame = frame
                    break
            else:  # didn't find and break
                raise RuntimeError("BUG: failed to find any matching frame for warning(s)")
        except Exception as ex:
            warnings.warn(f"failed to determine caller for warnings: {repr(ex)}", RuntimeWarning)
        else:  # successfully determined caller, tell user which test it came from so they can investigate
            warnings.warn(f"in '{call_frame.function}:L{call_frame.lineno}' {len(warnings_rewarn)} warning(s) caught, now re-warning", RuntimeWarning)
        for warning in warnings_rewarn:
            warnings.warn_explicit(
                message=warning.message,
                category=warning.category,
                filename=warning.filename,
                lineno=warning.lineno,
                source=warning.source,
            )
        if call_frame is None:  # something went wrong with discovering the caller
            raise Exception("BUG: failed to get caller via inspect, raising an Exception to highlight it")

    if ordered:
        for index, (warn_re, warn_msg) in enumerate(itertools.zip_longest(
            warning_regexes,
            warning_messages,
        )):
            if warn_re is None:  # pragma nocover
                raise AssertionError(f"unmatched warning (warning {index}): '{warn_msg}'")
            if not re.match(warn_re, warn_msg):  # pragma nocover
                raise AssertionError(f"message doesn't match regex (warning {index}): '{warn_re}' '{warn_msg}'")
        return  # completed ordered path

    # unordered warnings
    count_total_warnings = len(warning_messages)
    warning_regexes = list(set((warning_regexes)))  # drop duplicates, becomes unordered
    completed = set()
    for warn_re in warning_regexes:
        index_matched = []
        for index, warn_msg in enumerate(warning_messages):
            if re.match(warn_re, warn_msg):
                index_matched.append(index)
                if not multimatch:  # only match one warning (raise for additional warnings which are the same)
                    break  # next warn_re
        if not index_matched:  # pragma nocover NOTE can't use else clause due to multimatch
            if warning_messages:
                warnings.warn("failed to match some messages\n" + "\n".join(warning_messages), RuntimeWarning)
            raise AssertionError(f"failed to match regex to any warning ({count_total_warnings} total): {warn_re}")
        # drop messages backwards by-index so the earlier ones are unaffected by mutation
        for index in index_matched[::-1]:
            completed.add(warning_messages[index])
            del warning_messages[index]

    # in the successful case, every message is deleted
    if warning_messages:  # pragma nocover
        warns_block = "\n  ".join(warning_messages)
        msg = f"failed to match some warnings ({len(warning_messages)}/{count_total_warnings}):\n  {warns_block}"
        if not multimatch:  # needlessly complex
            for message in warning_messages:
                if message in warns_block:
                    msg += "\nset multimatch=True when calling must_warn_re() if duplicates are expected"
                    break
        raise AssertionError(msg)


@contextlib.contextmanager
def modify_config_global():
    if not isinstance(expressive.CONFIG, UserDict):
        raise RuntimeError(f"BUG: CONFIG must inherit from UserDict: {type(expressive.CONFIG).mro()}")
    if expressive.CONFIG._setup is not False:
        raise RuntimeError(f"BUG: CONFIG._setup must be False, but got {expressive.CONFIG._setup}")
    # freeze a copy of CONFIG's essential properties
    _config = deepcopy(expressive.CONFIG.data)
    keys = set(expressive.CONFIG.keys())
    id_pre = id(expressive.CONFIG)
    try:
        yield
    finally:  # always restore data for later tests
        id_post = id(expressive.CONFIG)
        if id_pre != id_post:
            raise RuntimeError(f"BUG: CONFIG replaced during context: {id_pre}!={id_post}")
        if expressive.CONFIG._setup is not False:
            raise RuntimeError(f"BUG: CONFIG._setup must be False, but got {expressive.CONFIG._setup}")
        keys_final = set(expressive.CONFIG.keys())
        keys_differ = keys.symmetric_difference(keys_final)
        if keys_differ:  # removed or added keys detected
            raise RuntimeError(f"BUG: CONFIG keys {keys_differ} remain mutated after restore: {expressive.CONFIG}")
        expressive.CONFIG.update(_config)  # all values clobbered
        # must be the same
        if expressive.CONFIG is not expressive.CONFIG:
            raise RuntimeError(f"BUG: expressive.CONFIG({id_post}) is not expressive.config.CONFIG({id(expressive.config.CONFIG)})")


class TestMeta(unittest.TestCase):

    def test_basic_import(self):
        """ make sure the simplest import+use form works """
        for cmd in [
            """python3 -c 'from expressive import Expressive ; print(Expressive("a + b"))'""",  # preferred
            """python3 -c 'import expressive ; print(expressive.Expressive("a + b"))'""",
            """python3 -c 'import expressive ; print(expressive.expressive.Expressive("a + b"))'""",
        ]:
            p = subprocess.Popen(
                shlex_split(cmd),
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                text=True,
            )
            out, err = p.communicate()
            if p.returncode != 0:
                raise AssertionError(f"BUG: failed (rc={p.returncode}): {out + err}")
            self.assertEqual(out.strip(), "Expressive(Eq(result, a + b))")

    def test_assumptions(self):
        """ assert features of packages here
            this is not for SymPy .assumptions0
        """
        # some NaN cases
        # numpy.nan are never equal, while sympy.nan are structurally equal, but not symbolically
        self.assertFalse(numpy.nan == numpy.nan)
        self.assertTrue(sympy.nan == sympy.nan)
        self.assertFalse(sympy.Eq(sympy.nan, sympy.nan))

        # log(0) handling
        self.assertTrue(sympy.log(0) ==  sympy.zoo)
        with must_warn_re("divide by zero encountered in log"):  # won't warn in numba
            self.assertTrue(numpy.log(0) == -numpy.inf)

        # TODO should this be its own test?
        # some SymPy decompositions
        for exponent, exprs in {
            2: [
                sympy.parse_expr("sqrt(x + 2)"),
                sympy.parse_expr("(x + 2)**(1/2)"),
                sympy.parse_expr("Pow(x + 2, Rational(1,2))")
            ],
            3: [
                sympy.parse_expr("cbrt(x + 2)"),
                sympy.parse_expr("(x + 2)**(1/3)"),
                sympy.parse_expr("Pow(x + 2, Rational(1,3))")
            ]
        }.items():
            # blocks should all be represented the same way
            #   "Pow(Add(Symbol('x'), Integer(2)), Rational(1, 2))"
            for expr in exprs:
                self.assertTrue(f"Rational(1, {exponent})" in sympy.srepr(expr))
                self.assertTrue("Pow(Add(" in sympy.srepr(expr))
            # get each pair and verify they're equal
            for e1, e2 in itertools.combinations(exprs, 2):
                self.assertTrue(e1 == e2)

    def test_piecewise_fold_behavior(self):
        """ show `piecewise_fold()` distributes `Eq` in all tested SymPy versions """
        expr = sympy.parse_expr("Eq(result, Piecewise((a, a > 3), (b, a < 1), (c, True)))")
        self.assertEqual(str(expr).count("Eq"), 1)
        expr = sympy.piecewise_fold(expr)
        self.assertEqual(str(expr).count("Eq"), 3)

    def test_modify_global_config(self):
        """ ensure global CONFIG can be modified for tests and is otherwise sufficiently immutable """
        key_test = "translate_simplify.build.sum.threaded_timeout_warn"
        id_pre = id(expressive.CONFIG)
        value_default = expressive.CONFIG[key_test]
        self.assertEqual(value_default, expressive.config._CONFIG_DEFAULTS[key_test])
        with modify_config_global():
            id_inner = id(expressive.CONFIG)
            expressive.CONFIG[key_test] = 100
            # error for nonexistent key
            with self.assertRaisesRegex(KeyError, re.escape("unknown key 'some.fake.key', ")):
                expressive.CONFIG["some.fake.key"] = True
        id_post = id(expressive.CONFIG)
        # CONFIG is still the same object
        self.assertTrue(id_pre == id_inner == id_post)
        self.assertEqual(expressive.CONFIG[key_test], value_default)

        # keys cannot be removed by any normal method
        keys_pre = set(expressive.CONFIG.keys())
        key_test = "data.runtime.unused_data_callback"
        msg_err = "ConfigWrapper keys cannot be removed"
        with modify_config_global():
            with self.assertRaisesRegex(KeyError, msg_err):
                del expressive.CONFIG[key_test]
            with self.assertRaisesRegex(KeyError, msg_err):
                expressive.CONFIG.pop(key_test)
            with self.assertRaisesRegex(KeyError, msg_err):
                expressive.CONFIG.clear()
        # despite attempts, keys are the same
        self.assertEqual(keys_pre, set(expressive.CONFIG.keys()))

        # further show `modify_config_global()` helper internally asserts keys are not modified
        _data = deepcopy(expressive.CONFIG.data)
        with self.assertRaisesRegex(RuntimeError, r"BUG: CONFIG keys \{"):  # set of changed keys
            with modify_config_global():  # raises on ctx exit when restoring keys
                expressive.CONFIG.data.clear()  # bypass __delitem__ by changing internal data
                self.assertTrue(len(expressive.CONFIG.keys()) == 0)  # did clear the keys
        # meta restore keys after .clear() bypass above
        self.assertTrue(len(expressive.CONFIG.keys()) == 0)  # bypassed checks
        expressive.CONFIG.data.update(_data)
        # keys were properly restored
        self.assertEqual(keys_pre, set(expressive.CONFIG.keys()))
        self.assertTrue(set(expressive.CONFIG.keys()) == set(expressive.config._CONFIG_DEFAULTS.keys()))

        # finally, CONFIG is still the same object
        self.assertTrue(id_pre == id(expressive.CONFIG))


class TestEqualityExtract(unittest.TestCase):
    """ test coercing inputs into a form like `Eq(result, expr)`
            "expr" -> RHS -> Eq(result, RHS)
            "LHS = RHS" -> Eq(LHS, RHS)

        additionally tests naming of LHS result value

        also tests indexed offsets (FUTURE move to distinct test or rename)
    """

    def test_equality_extract(self):
        data = {
            "x": numpy.arange(100, dtype="int64"),
        }
        E = Expressive("r = x**2")
        E.build(data)

        # give it a spin
        data = {
            "x": numpy.arange(1000, dtype="int64"),
        }
        result = E(data)

        self.assertTrue(numpy.array_equal(
            numpy.arange(1000)**2,
            result,
        ))

    def test_pass_name_result(self):
        E = Expressive("x**2", name_result="some_result")
        self.assertTrue(len(E._results) == 1)
        self.assertTrue("some_result" in E._results)

        # mismatch case
        expr_str = "a = x**2"
        msg = re.escape("mismatch between name_result (b) and parsed symbol name (a)")
        with self.assertRaisesRegex(ValueError, msg):
            Expressive(expr_str, name_result="b")

        # not a string
        for name_result in [
            # None is the default for no work!
            False,
            1,
            (),
        ]:
            with self.assertRaisesRegex(ValueError, r"name_result must be None or a str, but got"):
                expressive.parsers.parse_inputs("x**2", None, name_result, None, None)  # FUTURE fix config [ISSUE 204]

    def test_indexed(self):
        data = {
            "x": numpy.arange(1000, dtype="int64"),
        }

        # lhs and rhs are indexed
        E = Expressive("r[i] = x[i]**2")
        E.build(data)

        # indexed and named everywhere
        E = Expressive("r[i] = x[i]**2", name_result="r")
        E.build(data)

        self.assertTrue(len(E._results) == 1)
        self.assertTrue("r" in E._results)
        # the symbol should be an IndexedBase
        self.assertTrue(E._results["r"].atoms(sympy.IndexedBase))

        E = Expressive("r[i] = x**2")
        with self.assertRaisesRegex(ValueError, re.escape("'x' is not indexed, but passed array (ndim=1) value in data")):
            E.build(data)

        # mismatched LHS,RHS indexers
        with self.assertRaisesRegex(ValueError, r"^only a single Idx is supported, but got: \{[ni]: \[0, 0\], [ni]: \[0, 0\]\}$"):
            E = Expressive("r[i] = a[n]**2")

    def test_indexed_offset(self):
        """ check offset range detection """
        for expr_string, offset_values in {
            # single offset
            "r[i] = x[i-1]**2": ("i", -1, 0),
            "r[i] = x[i+1]**2": ("i",  0, 1),
            "r[i+1] = x[i]**2": ("i",  0, 1),
            "r[i-1] = x[i]**2": ("i", -1, 0),
            # double offset
            "r[i-5] = x[i+10]**2": ("i", -5, 10),
            "r[i-2] = x[i-2]**2":  ("i", -2, 0),
            # mixed offsets
            "r[i-2] = log(x) + y[i-2]*z + w[i+1]":  ("i", -2, 1),
            # wide offsets
            "r[i+1000] = x[i-1000]**2":  ("i", -1000, 1000),
        }.items():
            E = Expressive(expr_string)
            self.assertEqual(len(E._indexers), 1)
            indexer, (start, end) = next(iter(E._indexers.items()))
            self.assertEqual((indexer.name, start, end), offset_values)

    def test_bad_equalities(self):
        with self.assertRaisesRegex(ValueError, "multiple possible result values"):
            E = Expressive("a + b = x")
        with self.assertRaisesRegex(ValueError, "multiple or no possible result values"):
            E = Expressive("a + b + c = x")
        with self.assertRaisesRegex(ValueError, "multiple or no possible result values"):
            E = Expressive("a[i] + b = x")
        # FUTURE consider this or a similar case of multiple assignment
        #   for example `(a, b) == c` might be a useful construct and be Pythonic, despite
        #   making little sense mathematically
        with self.assertRaisesRegex(ValueError, "multiple or no possible result values"):
            E = Expressive("a[i] + b[i] = x")

    def test_data_sensible(self):
        data = {
            "a": numpy.arange(1000, dtype="int64"),
        }

        E = Expressive("r = a**2 + b")

        # passed data doesn't match the signature
        with self.assertRaisesRegex(KeyError, r"b"):
            E.build(data)

        # works when the full data is available
        data["b"] = numpy.arange(1000, dtype="int64")
        E.build(data)
        self.assertEqual(len(E.signatures_mapper), 1)

        # passing r is optional and doesn't create a new signature
        # FUTURE show rebuild warning after [ISSUE 194]
        data["r"] = numpy.zeros(1000, dtype="int64")
        E.build(data)
        self.assertEqual(len(E.signatures_mapper), 1)

        # however, a different result dtype results in a rebuild and new signature
        data["r"] = numpy.zeros(1000, dtype="int32")
        E.build(data)
        self.assertEqual(len(E.signatures_mapper), 2)

    def test_name_and_data_only(self):
        E = Expressive("a**2 + b", name_result="r")

        data = {
            "a": numpy.arange(1000, dtype="int64"),
            "b": numpy.arange(1000, dtype="int64"),
            "r": numpy.zeros(1000, dtype="int64"),
        }
        E.build(data)
        E(data)

    def test_name_and_not_data(self):
        """ fail when missing details about the result array """
        E = Expressive("a**2 + b", name_result="r")

        data = {
            "a": numpy.arange(1000, dtype="int64"),
            "b": numpy.arange(1000, dtype="int64"),
        }
        E.build(data)
        result = E(data)

        self.assertTrue(numpy.array_equal(
            numpy.arange(1000)**2 + numpy.arange(1000),
            result,
        ))

    def test_mismatched_dtypes(self):
        """ fail when missing details about the result array """
        E = Expressive("a**2 + b", name_result="r")

        data = {
            "a": numpy.arange(1000, dtype="int64"),
            "b": numpy.arange(1000, dtype="int64"),
            "r": numpy.zeros(1000, dtype="int64"),
        }
        with self.assertRaisesRegex(ValueError, r"mismatched.*int64.*float64"):
            E.build(data, dtype_result="float64")
        with self.assertRaisesRegex(ValueError, r"mismatched.*int64.*int32"):
            E.build(data, dtype_result="int32")

    def test_indxed_rhs(self):
        E = Expressive("a[i]**2", name_result="r")
        data = {
            "a": numpy.arange(1000, dtype="int64"),
        }
        E.build(data)

    def test_result_array_fill(self):
        """ should fill, not re-create result array """
        E = Expressive("a[i]**2 + b[i]", name_result="r")
        data = {
            "a": numpy.arange(100, dtype="int64"),
            "b": numpy.arange(100, dtype="int64"),
            "r": numpy.zeros(100, dtype="int64")
        }

        E.build(data)

        # now create new data and build with it, passing result
        data = {
            "a": numpy.arange(1000, dtype="int64"),
            "b": numpy.arange(1000, dtype="int64"),
            "r": numpy.zeros(1000, dtype="int64")
        }
        ref = data["r"]

        result = E(data)
        # reference hasn't been swapped out
        self.assertTrue(ref is result)
        self.assertTrue(data["r"] is ref)
        # check the contents too
        self.assertEqual(data["r"][0], 0)
        self.assertEqual(data["r"][1], 2)
        self.assertEqual(data["r"][2], 6)
        self.assertEqual(data["r"][999], 999**2 + 999)

    def test_self_reference(self):
        """ passing result with data works without explicitly naming it
            however, the user should be warned when they might not mean to do so
        """

        # warn only when the name (symbol) literally 'result' is
        #  - not in LHS, but given in RHS
        #  - not indexed (IndexedBase)
        #  - not named as name_result

        # equivalent instances to compare
        Expressive("result ** 2", name_result="result")
        Expressive("result = result ** 2")
        Expressive("result[i] ** 2")  # functionally equivalent (results), but internally uses the indexed path
        Expressive("result[i+1] ** 2")  # actually offset by 1 too, but shouldn't raise!
        # ensure warn occurs and then try it!
        with must_warn_re(r"^symbol 'result' in RHS refers to result array, but not indexed or passed as name_result$"):
            E = Expressive("result ** 2")

        data = {
            "result": numpy.arange(1000, dtype="int64"),
        }
        ref = data["result"]
        E.build(data)
        result = E(data)

        # reference hasn't been swapped out
        self.assertTrue(ref is result)
        self.assertTrue(data["result"] is ref)
        # check the contents too
        self.assertEqual(data["result"][0], 0)
        self.assertEqual(data["result"][1], 1)
        self.assertEqual(data["result"][2], 4)
        self.assertEqual(data["result"][999], 999**2)

    def test_complex_dtype(self):
        length = 1000
        data = {
            "a": numpy.full(length, 1j),
        }
        E = Expressive("E**(a * pi)")  # famous e^(i*pi)=-1
        E.build(data)
        result = E(data)
        self.assertTrue(numpy.allclose(result, numpy.full(length, -1)))


class TestSymPyExprInput(unittest.TestCase):
    """ test passing a SymPy expr rather than a simple string """

    def test_sympy_input_basic(self):
        x, y = sympy.symbols("x y")
        expr = x**2 + y**3
        E = Expressive(expr)

    def test_invalid_args(self):
        for expr in [
            b"x**2 + y",
            None,
            object(),
        ]:
            with self.assertRaisesRegex(ValueError, r"unexpected expr type"):
                E = Expressive(expr)

    def test_complex_dtype(self):
        # directly include I (1j)
        a, b = sympy.symbols("a b")
        expr = a + b*sympy.I
        E = Expressive(expr)

        data = {
            "a": numpy.arange(1000, dtype="int32"),
            "b": numpy.arange(1000, dtype="int32"),
        }
        E.build(data)
        result = E(data)
        self.assertEqual(result.dtype, numpy.dtype("complex128"))

        # simple multiplication
        a, b = sympy.symbols("a b")
        expr = a*b
        E = Expressive(expr)

        data = {
            "a": numpy.arange(1000, dtype="complex64"),
            "b": numpy.arange(1000, dtype="int32"),
        }
        E.build(data)
        result = E(data)
        self.assertEqual(result.dtype, numpy.dtype("complex64"))

        # simple addition
        a, b = sympy.symbols("a b")
        expr = a+b
        E = Expressive(expr)

        # NOTE the default numba casting of complex64+float64 is complex128
        #   but complex64++int64 is only cast to complex64, which doesn't have enough bits
        #   this is fixed in [ISSUE 192] by creating and passing the array outside of Numba
        data = {
            "a": numpy.array([1, 2**60], dtype="complex64"),
            "b": numpy.array([1, 2**60], dtype="float64"),
        }
        E.build(data)
        result = E(data)
        self.assertEqual(result.dtype, numpy.dtype("complex128"))
        data = {
            "a": numpy.array([1, 2**60], dtype="complex64"),
            "b": numpy.array([1, 2**60], dtype="int64"),
        }
        E.build(data)
        result = E(data)
        self.assertEqual(result.dtype, numpy.dtype("complex128"))  # previously complex64

    def test_indexed_offset(self):
        a = sympy.IndexedBase("a")
        i = sympy.Idx("i")
        expr = a[i-1]**2
        E = Expressive(expr)

        # equality version
        r = sympy.IndexedBase("r")
        expr = sympy.Eq(r[i], a[i-1]**2)
        E = Expressive(expr)

    def test_indexed_bad(self):
        a, b = sympy.symbols("a b", cls=sympy.IndexedBase)  # create some useful symbols
        i, n = sympy.symbols("i n", cls=sympy.Idx)

        # multiple indexers
        with self.assertRaisesRegex(ValueError, "only a single Idx is supported, but got"):
            Expressive(a[i]**2 + b[n])

        # multiple indexers in a single block
        with self.assertRaisesRegex(ValueError, r"^indexer must be a single Idx, but got a\[[i\+n\-1\s]{9}\]$"):
            Expressive(a[i+n-1]**2)  # a[i + n - 1]

        # wacky non-integer indexing
        with self.assertRaisesRegex(ValueError, "^" + re.escape("expected a single Integer (or nothing: 0) as the offset, but parsed")):
            E = Expressive(a[i+1/2]**2)

        # nested indexing
        with self.assertRaisesRegex(ValueError, "^" + re.escape("multiple or nested IndexedBase: a[b[i]]")):
            E = Expressive(a[b[i]]**2)

    def test_symbols_mismatches(self):
        x, y = sympy.symbols("x y")

        # y never used in expr
        with self.assertRaisesRegex(ValueError, "^some symbols not present in expr: " + re.escape(r"{y}")):
            Expressive(x**2, symbols={"y": y})

        # LHS doesn't match result "resultname"
        with self.assertRaisesRegex(ValueError, re.escape("mismatched name between name_result(resultname) and LHS(x)")):
            Expressive(sympy.Eq(x, y), name_result="resultname")

        # a Symbol name literally "result" used, but not expressly named as name_result
        result = sympy.Symbol("result")
        with must_warn_re("symbol 'result' in RHS refers to result array, but not indexed or passed as name_result"):
            # Expressive(x + result**3, symbols={"result": result})
            Expressive(x + result**3)

    def test_multiple_equality(self):
        a, b, c = sympy.symbols("a b c")
        expr = sympy.Eq(a, sympy.Eq(b, c))
        with self.assertRaisesRegex(ValueError, "^only a single equality can exist, but got"):
            Expressive(expr)


class TestGuess_dtype(unittest.TestCase):

    def test_simple(self):
        data = {
            "a": numpy.array([1,2,3], dtype="uint8"),
        }
        E = Expressive("2*a")
        dt = expressive.data.dtype_result_guess(E._expr_sympy, data)
        self.assertEqual(dt, "uint32")

        # exclusively float32
        data = {
            "a": numpy.array([1,2,3], dtype="float32"),
            "b": numpy.array([1,2,3], dtype="float32"),
        }
        E = Expressive("a * b")
        dt = expressive.data.dtype_result_guess(E._expr_sympy, data)
        self.assertEqual(dt, "float32")

        # choose wider when present
        data = {
            "a": numpy.array([1,2,3], dtype="float32"),
            "b": numpy.array([1,2,3], dtype="float64"),
        }
        E = Expressive("a * b")
        dt = expressive.data.dtype_result_guess(E._expr_sympy, data)
        self.assertEqual(dt, "float64")

    def test_empty_inputs(self):
        E = Expressive("2*a")
        with self.assertRaisesRegex(ValueError, r"no data"):
            expressive.data.dtype_result_guess(E._expr_sympy, data={})

    def test_floating_point_operators(self):
        # most floating point math results in float64
        data = {
            "a": numpy.array([1,2,3], dtype="int32"),
        }
        E = Expressive("log(a)")
        dt = expressive.data.dtype_result_guess(E._expr_sympy, data)
        self.assertEqual(dt, "float64")

    def test_float_promote(self):
        # presence of a wider value causes promotion to float64
        data = {
            "a": numpy.array([1,2,3], dtype="int64"),
            "b": numpy.array([1,2,3], dtype="float32"),
        }
        E = Expressive("a * b")
        dt = expressive.data.dtype_result_guess(E._expr_sympy, data)
        self.assertEqual(dt, "float64")

        # most values are promoted to float64 regardless of width
        data = {
            "a": numpy.array([1,2,3], dtype="int32"),
        }
        E = Expressive("log(a)")
        dt = expressive.data.dtype_result_guess(E._expr_sympy, data)
        self.assertEqual(dt, "float64")

        # while small values are promoted to float32
        data = {
            "a": numpy.array([1,2,3], dtype="int8"),
            "b": numpy.array([1,2,3], dtype="int8"),
        }
        E = Expressive("log(a) + b")
        dt = expressive.data.dtype_result_guess(E._expr_sympy, data)
        self.assertEqual(dt, "float32")

    def test_bad(self):
        # boolean is currently unsupported
        data = {
            "a": numpy.array([1,2,3], dtype="bool"),
            "b": numpy.array([1,2,3], dtype="bool"),
        }
        E = Expressive("a * b")
        with self.assertRaisesRegex(TypeError, r"unsupported.*bool"):
            expressive.data.dtype_result_guess(E._expr_sympy, data=data)

        # mixed integer signs
        data = {
            "a": numpy.array([1,2,3], dtype="int32"),
            "b": numpy.array([1,2,3], dtype="uint32"),
        }
        E = Expressive("a * b")
        with self.assertRaisesRegex(TypeError, r"mixed int and uint"):
            expressive.data.dtype_result_guess(E._expr_sympy, data=data)

    def test_complex_dtype(self):
        # complex dtype
        data = {
            "a": numpy.array([1,2,3], dtype="complex64"),
            "b": numpy.array([1,2,3], dtype="float32"),
        }
        E = Expressive("a * b")
        dt = expressive.data.dtype_result_guess(E._expr_sympy, data)
        self.assertEqual(dt, "complex64")

        # various dtypes
        data = {
            "a": numpy.array([1,2,3], dtype="complex64"),
            "b": numpy.array([1,2,3], dtype="float64"),
            "c": numpy.array([1,2,3], dtype="complex128"),
        }
        E = Expressive("a * b * c")
        dt = expressive.data.dtype_result_guess(E._expr_sympy, data)
        self.assertEqual(dt, "complex128")

        # warns for problematic cast int64+complex64 -> complex64
        data = {
            "a": numpy.array([1,2,3], dtype="complex64"),
            "b": numpy.array([1,2,3], dtype="float32"),
            "c": numpy.array([1,2,3], dtype="int64"),
        }
        E = Expressive("a * b * c")
        dt = expressive.data.dtype_result_guess(E._expr_sympy, data)
        self.assertEqual(dt, "complex128")

    def test_pow_int32_int64_bug(self):
        data = {
            "a": numpy.arange(100, dtype="int32"),
        }

        # promote type when Pow is used
        E = Expressive("a**2")
        for dtype in (None, "int16", "int32", "int64"):
            # NOTE setting int32 would raise due to Numba casting before [ISSUE 192]
            E.build(data, dtype_result=dtype)
            result = E(data)
            self.assertEqual(result.dtype, numpy.dtype("int64"))  # type is promoted

        data["b"] = numpy.arange(100, dtype="int32")

        # don't promote int32 for addition
        E = Expressive("a + b")
        E.build(data)
        result = E(data)
        self.assertEqual(result.dtype, numpy.dtype("int32"))  # type is not promoted

        # fractional powers always become floating-point
        for powstr in ("1/2", "3/2", "1/5", "10/3"):
            E = Expressive(f"a + b**({powstr})")
            E.build(data)
            result = E(data)
            self.assertEqual(result.dtype, numpy.dtype("float64"))

    def test_additional_low_bit_int_promote(self):
        data = {
            "a": numpy.arange(100, dtype="int8"),
            "b": numpy.arange(100, dtype="int16"),
        }
        E = Expressive("a**2 + b**2")
        E.build(data)
        result = E(data)
        self.assertTrue(len(E.signatures_mapper) == 1)
        self.assertEqual(result.dtype, numpy.dtype("int64"))  # dtype is always promoted

        # passing a custom result array, however avoids promotion
        data["result"] = numpy.zeros(100, dtype="int16")
        E.build(data)
        result = E(data)
        self.assertTrue(len(E.signatures_mapper) == 2)
        self.assertEqual(result.dtype, numpy.dtype("int16"))
        self.assertEqual(result[10], 200)  # gives the right result

        del data["result"]  # drop to prevent re-use

        # the error this originally validated [ISSUE 165] is now avoided with [ISSUE 192]
        #     Exception triggered for small types when a result array is not passed
        #       numba.core.errors.TypingError: Failed in nopython mode pipeline (step: nopython frontend)
        #       No conversion from array(int64, 1d, C) to array(int16, 1d, C) for '$20return_value.8', defined at None
        #     with self.assertRaisesRegex(Exception, re.escape("No conversion from array(int64, 1d, C) to array(int16, 1d, C)")):
        #         with must_warn_re("don't use dtype_result and prefer passing a result array if you see this "):
        E.build(data, dtype_result="int16")
        result = E(data, dtype_result="int16")
        self.assertTrue(result.dtype == numpy.dtype("int16"))

        # however, simple operations won't trigger promotion in Numba
        E = Expressive("a + b")
        E.build(data, dtype_result="int16")
        result = E(data, dtype_result="int16")  # NOTE actually setting this repeatedly is a little annoying..
        self.assertEqual(result.dtype, numpy.dtype("int16"))
        self.assertEqual(result[10], 20)

    # FUTURE additional overflowing test(s) [ISSUE 46]
    #   specifically this should (probably) collaborate with the builder to expressly create a result array


class Testdata_cleanup(unittest.TestCase):

    def test_bad_keys(self):
        # check that dict keys are acceptable
        # NOTE that the expr parsing will throw out spaces too
        data = {True: numpy.array([1,2,3], dtype="int32")}
        with self.assertRaisesRegex(ValueError, r"^data names must be strings, but got .*True"):
            expressive.data.data_cleanup(data)

        for key in [
            "has space",
            "2test",
            "a\n",
            ":",
            "a:",
            ":a",
            "_",  # exactly start or end with _ is not allowed
            "_foo_",
            "π",  # FUTURE consider allowing π and similar (valid identifier) or coerce to `sympy.pi` expr
            "∂",
        ]:
            data = {key: numpy.array([1,2,3], dtype="int32")}
            msg = f"data names must be valid Python names (identifiers) and Symbols, but got '{key}'"
            with self.assertRaisesRegex(ValueError, "^" + re.escape(msg) + "$"):
                expressive.data.data_cleanup(data)

        # some keys which are allowed
        for key in [
            "has_underscore",
            "test2",
            "a",
        ]:
            data = {key: numpy.array([1,2,3], dtype="int32")}
            result = expressive.data.data_cleanup(data)
            self.assertTrue(data[key] is result[key])  # same object

        # TODO consider warning for valid Python keywords
        #   https://docs.python.org/3/library/keyword.html

    def test_bad_data(self):
        with self.assertRaisesRegex(ValueError, r"no data"):
            expressive.data.data_cleanup({})

        data = ["a"]
        with self.assertRaisesRegex(TypeError, r"data must be a dict of NumPy arrays or scalars.*list"):
            expressive.data.data_cleanup(data)

        data = {"a": [1]}
        with self.assertRaisesRegex(TypeError, r"data must be a dict of NumPy arrays or scalars.*list"):
            expressive.data.data_cleanup(data)

        data = {"a": numpy.array([1,2,3], dtype="bool")}
        with self.assertRaisesRegex(TypeError, r"unsupported dtype .*bool"):
            expressive.data.data_cleanup(data)

    def test_uneven_arrays(self):
        # see also TestSingleValues for non-vector data
        data = {
            "a": numpy.arange(100, dtype="int64"),
            "b": numpy.arange( 99, dtype="int64"),
        }
        with self.assertRaisesRegex(ValueError, r"uneven data lengths .*99"):
            expressive.data.data_cleanup(data)

    def test_complex_dtype(self):
        data = {
            "aj": numpy.array([1j for _ in range(1000)], dtype="complex64"),
        }
        data = expressive.data.data_cleanup(data)
        self.assertEqual(data["aj"].dtype, numpy.dtype("complex64"))  # no change

        data = {
            "a": 1j,
            "b": numpy.arange(1000, dtype="complex64"),
            "c": numpy.arange(1000),
        }
        data = expressive.data.data_cleanup(data)
        self.assertEqual(data["a"].dtype, numpy.dtype("complex128"))  # automatic coerce
        self.assertEqual(data["b"].dtype, numpy.dtype("complex64"))


class TestUnusedData(unittest.TestCase):

    def test_unused_data_simple(self):
        # default behavior warns
        data = {
            "a": numpy.arange(100, dtype="int64"),
            "b": numpy.arange(100, dtype="int64"),
        }
        expr = "a**2"
        msg_err = re.escape("some passed data was not used [b]")
        E = Expressive(expr)
        E.build(data)
        self.assertTrue(E._config["data.runtime.unused_data_callback"] == "warn")
        with must_warn_re(msg_err):
            r1 = E(data)

        # set to raise
        E = Expressive(expr, config={"data.runtime.unused_data_callback": "raise"})
        E.build(data)
        with self.assertRaisesRegex(TypeError, msg_err):
            E(data)

        # ignore bypasses the warning
        E = Expressive(expr, config={"data.runtime.unused_data_callback": "ignore"})
        E.build(data)
        r2 = E(data)

        result_expected = numpy.arange(100) ** 2
        self.assertTrue(numpy.array_equal(result_expected, r1))
        self.assertTrue(numpy.array_equal(result_expected, r2))


    def test_unused_data_TypeError_pass(self):
        """ TypeErrors unrelated to the data args are still raised """

        def fn_mock(**kwargs):
            raise TypeError(f"mocked Exception, got kwargs={sorted(kwargs)}")

        data = {
            "a": numpy.arange(100, dtype="int64"),
            "b": numpy.arange(100, dtype="int64"),
        }

        E = Expressive("a + b")
        E.build(data)

        # clobber the built function
        key = next(iter(E.signatures_mapper.keys()))
        fn_original = E.signatures_mapper[key]
        E.signatures_mapper[key] = fn_mock

        with self.assertRaisesRegex(TypeError, re.escape("mocked Exception, got kwargs=['a', 'b']")):
            E(data)

        # restored instance still works
        E.signatures_mapper[key] = fn_original
        result = E(data)
        self.assertTrue(numpy.array_equal(result, data["a"] + data["b"]))

        # FUTURE consider another function with data["c"] and unused_data_callback=="raise"

    def test_unused_data_result(self):
        data = {
            "a": numpy.arange(100, dtype="int64"),
            "b": numpy.arange(100, dtype="int64"),
            "result": numpy.zeros(100),
        }
        expr = "log(a)"
        E = Expressive(expr, name_result="result")
        E.build(data)
        with must_warn_re(re.escape("some passed data was not used [b]")):
            r1 = E(data)

        self.assertTrue(numpy.array_equal(r1, data["result"]))
        self.assertTrue(r1 is data["result"])  # should always be the case

        # switching out the result array name causes "result" member to become unused
        E = Expressive(expr, name_result="other")
        E.build(data)
        with must_warn_re(re.escape("some passed data was not used [b,result]")):
            r2 = E(data)

        self.assertTrue(numpy.array_equal(r2, data["result"]))
        self.assertTrue(r2 is not data["result"])  # creates a new result array

    def test_unused_data_chaining(self):
        data = {
            "a": numpy.arange(100, dtype="int64"),
            "b": numpy.arange(100, dtype="int64"),
            "result": numpy.zeros(100),
        }

        # check config default value is right
        self.assertTrue(expressive.CONFIG["data.runtime.unused_data_callback"] != "ignore")
        with modify_config_global():
            expressive.CONFIG["data.runtime.unused_data_callback"] = "ignore"
            E1 = Expressive("log(a + 1)", name_result="result")  # lazy avoid log(0)->nan warning from NumPy result_expected
            E2 = Expressive("b**result", name_result="result")
            E1.build(data)
            E2.build(data)
            E1(data)
            result_expected = numpy.log(numpy.arange(100) + 1)
            self.assertTrue(numpy.array_equal(result_expected, data["result"]))
            E2(data)  # relies on result from E1
        # original is restored, see also `TestMeta.test_modify_global_config()`
        self.assertTrue(expressive.CONFIG["data.runtime.unused_data_callback"] != "ignore")

        result_expected = numpy.arange(100) ** numpy.log(numpy.arange(100) + 1)
        self.assertTrue(numpy.array_equal(result_expected, data["result"]))


class TestParallelizationModel(unittest.TestCase):

    # TODO consider mocking env dict contents during setup/teardown and/or inherit TestCase
    #   to ease issues with unusual user environments where PYTHON_CPU_COUNT is set
    #   (and NUMBA_NUM_THREADS to a lesser degree, or even error for it)

    def test_parallel_model_parse(self):
        """ trivial test to get coverage on the parser """

        # try all the acceptable values
        for arg in (None, "prange", "disabled"):
            d = expressive.parsers.parse_parallel_model(arg)
            self.assertTrue(isinstance(d, dict))

        d = expressive.parsers.parse_parallel_model("disabled")
        self.assertTrue(all(v == False for v in d.values()))  # every value is False (alt set compare)

        # ValueError for other values
        with self.assertRaisesRegex(ValueError, r"parallel_model must be.*got 'bad'"):
            expressive.parsers.parse_parallel_model("bad")
        with self.assertRaisesRegex(ValueError, r"parallel_model must be.*got ''"):
            expressive.parsers.parse_parallel_model("")
        with self.assertRaisesRegex(ValueError, r"parallel_model must be.*got 'PRANGE'"):
            expressive.parsers.parse_parallel_model("PRANGE")  # TODO consider some fuzzy fixing

    def test_prange_ndim_guess(self):
        """ prange seems especially troublesome because its internal threading can swallow errors
            however.. the multicore speedups are not to be ignored
            allow users to enable it by setting `parallel_model="prange"`
            or disable automatic parallelization with `parallel_model="disabled"`
        """
        data_ndim1 = {                        # .ndim
            "a": numpy.array([1,2,3]),        # 1
            "b": numpy.array([1,2,3]),        # 1
            "c": 10,                          # 0
        }
        data_ndim2 = {                        # .ndim
            "a": numpy.array([[1,2],[3,4]]),  # 2
            "b": numpy.array([1,2]),          # 1
            "c": 10,                          # 0
        }
        # fix scalars
        data_ndim1 = expressive.data.data_cleanup(data_ndim1)
        with must_warn_re(r"mixed dimensions may not broadcast correctly"):
            data_ndim2 = expressive.data.data_cleanup(data_ndim2)
        self.assertTrue(isinstance(data_ndim1["c"], numpy.number))
        self.assertTrue(isinstance(data_ndim2["c"], numpy.number))
        self.assertTrue(data_ndim1["c"].ndim == 0)
        self.assertTrue(data_ndim2["c"].ndim == 0)

        # unset (None) -> max .ndim 1 -> True
        E = Expressive("a + log(b) * c")
        allow_prange, use_native_threadpool = expressive.codegen.discover_parallelization(data_ndim1, E._config)
        self.assertEqual(allow_prange, True)

        # expressly disabled
        E = Expressive("a + log(b) * c", parallel_model="disabled")
        allow_prange, use_native_threadpool = expressive.codegen.discover_parallelization(data_ndim1, E._config)
        self.assertEqual(allow_prange, False)  # never enabled

        # expressly set
        E = Expressive("a + log(b) * c", parallel_model="prange")
        allow_prange, use_native_threadpool = expressive.codegen.discover_parallelization(data_ndim1, E._config)
        self.assertEqual(allow_prange, True)

        # now try with more dimensions

        # unset (None) -> max .ndim 2 -> False
        E = Expressive("a + log(b) * c")
        # opportunity to expect a warning about result dimensions
        with must_warn_re(r"mixed dimensions may not broadcast correctly"):
            with self.assertRaisesRegex(ValueError, r"couldn't determine result dimensions.*provide a result array"):
                E._prepare(data_ndim2, dtype_result=None)

        data_ndim2["result"] = numpy.zeros_like(data_ndim2["a"], dtype="float32")  # create a result array to avoid error
        with must_warn_re(r"mixed dimensions may not broadcast correctly"):
            data, _, _, _ = E._prepare(data_ndim2, dtype_result=None)
        allow_prange, use_native_threadpool = expressive.codegen.discover_parallelization(data_ndim2, E._config)
        self.assertEqual(allow_prange, False)
        self.assertTrue(isinstance(data["c"], numpy.number))  # free conversion validate..

        # expressly set the parallel model to prange
        # NOTE this may result in errors
        E = Expressive("a + log(b) * c", parallel_model="prange")
        with must_warn_re(r"mixed dimensions may not broadcast correctly"):
            E._prepare(data_ndim2, dtype_result=None)
        allow_prange, use_native_threadpool = expressive.codegen.discover_parallelization(data_ndim2, E._config)
        self.assertEqual(allow_prange, True)

        # builds (and verifies) without error with prange set
        with must_warn_re(r"mixed dimensions may not broadcast correctly", multimatch=True):
            E.build(data_ndim2, verify=True)
            E(data_ndim2)

        # make sure the calculation actually worked
        self.assertTrue(numpy.allclose(
            data_ndim2["result"],
            numpy.array([[1, 8.931472], [ 3, 10.931472]])
        ))
        # NOTE attempting to use lower-dim array raises an exception from Numba parfors `assert target_ndim >= n`
        # data_ndim2["result"] = numpy.zeros_like(data_ndim2["b"], dtype="float32")

        # TODO integrate with verify_cmp
        # TODO assert multiple builds (==2) [ISSUE 154]

    # FUTURE good case for pytest's parameterization
    def test_ParallelRunner_basics(self):
        # FUTURE consider inheriting unittest.TestCase to .stop() during each setup

        # create instance for the rest of the testcase
        PR = expressive.parallel.ParallelRunner()

        # initial Queue always empty, so it's nicer to have a value than rely on `.empty()` or `.qsize()`
        try:
            value = PR._Q_jobs.get_nowait()
        except EmptyQueueException:  # queue.Empty
            pass # empty: successful case
        else:    # pragma nocover (failed case)
            raise AssertionError(f"BUG: Queue should be empty, but .get() found {value}")
        p1 = PR.start()
        p2 = PR.start()  # show idempotent
        PR.stop()
        PR.stop()        # show idempotent

        # same object is always returned by `.start()` and updating
        self.assertTrue((p1 is p2) and (PR is p1) and (PR is p2))
        for threadcount in range(1, 4):
            pN = PR.update(threadcount=threadcount)  # calls start internally
            self.assertTrue(p1 is pN)
            self.assertTrue(len(PR.threads) == threadcount)

    def test_worker_count_from_cores(self):
        # FIXME ugly Python-version dependent test for now..
        pynew = bool(sys.version_info[:2] >= (3, 13))

        # try some bad threadcount args
        for threadcount in [0, -1, -2, False, "", 1.1]:
            msg = re.escape(f"threadcount must be int>=1, but got {repr(threadcount)}")
            with self.assertRaisesRegex(ValueError, msg):
                expressive.parallel.ParallelRunner(threadcount=threadcount)

        # experiment with threadcount set or detect as 1
        expressive.parallel.ParallelRunner(threadcount=1)  # doesn't warn

        # warn user if threadcount is detected as 1
        with unittest.mock.patch.dict(os.environ, clear=True):  # force missing os.environ["PYTHON_CPU_COUNT"] behavior
            with must_warn_re(f"possibly a bad environment: cores_system={os.cpu_count()} cores_process=1"):
                with unittest.mock.patch("os.process_cpu_count" if pynew else "os.sched_getaffinity") as mock:
                    mock.return_value = 1 if pynew else [0]  # direct `mock()` vs `len(mock())`
                    threadcount = expressive.parallel.worker_count_from_cores()
        self.assertEqual(threadcount, 1)
        with must_warn_re("^possibly a bad environment: cores_system=1 cores_process="):
            with unittest.mock.patch("os.cpu_count") as mock:
                mock.return_value = 1
                threadcount = expressive.parallel.worker_count_from_cores()
        self.assertEqual(threadcount, 1)

        # TODO it might be worth testing more, such as setting cpu_count() == 2, etc.
        # but no real system will behave this way .. it might be worth considering some CI/CD systems
        # which could only be provided 2 cores, but ideally a contrived system could skip this whole
        # test suite and just test on a representative system if at all

        # further manipulation
        with unittest.mock.patch.dict(os.environ, clear=True):  # force missing os.environ["PYTHON_CPU_COUNT"] behavior
            with unittest.mock.patch("os.cpu_count") as mock_s:
                mock_s.return_value = 10
                with unittest.mock.patch("os.process_cpu_count" if pynew else "os.sched_getaffinity") as mock_p:
                    mock_p.return_value = 8 if pynew else list(range(8))  # direct `mock()` vs `len(mock())`
                    threadcount = expressive.parallel.worker_count_from_cores()
        self.assertEqual(threadcount, 8)  # lower threadcount is chosen (without warning)

        # exploit custom short-circuiting behavior
        with unittest.mock.patch("os.cpu_count") as mock_s:
            mock_s.return_value = 10
            for count_p in range(2, 5):
                for key in ["NUMBA_NUM_THREADS", "PYTHON_CPU_COUNT"]:
                    with unittest.mock.patch.dict(os.environ, {key: f"{count_p}"}):
                        threadcount = expressive.parallel.worker_count_from_cores()
                    self.assertEqual(threadcount, count_p)  # lower threadcount is chosen (without warning)

        # force newer behavior even under older Python
        with unittest.mock.patch("os.cpu_count") as mock_s:
            mock_s.return_value = 10
            with unittest.mock.patch.dict(os.environ, clear=True):
                with unittest.mock.patch.object(sys, "version_info", (3, 100, 1)):
                    with unittest.mock.patch("os.process_cpu_count", create=True) as mock_p:
                        mock_p.return_value = 8
                        threadcount = expressive.parallel.worker_count_from_cores()
                        mock_p.assert_called_once()
            mock_s.assert_called()
        self.assertEqual(threadcount, 8)  # lower threadcount is chosen (without warning)

        # force older behavior when user set PYTHON_CPU_COUNT=0 for some reason
        with unittest.mock.patch.dict(os.environ, {"PYTHON_CPU_COUNT": "0"}):
            with self.assertRaisesRegex(OSError, "impossible worker count detected: 0"):
                threadcount = expressive.parallel.worker_count_from_cores()
        # and again with NUMBA_NUM_THREADS which is even more direct
        for count_p in [0, -1]:
            with unittest.mock.patch.dict(os.environ, {"NUMBA_NUM_THREADS": f"{count_p}"}):
                with self.assertRaisesRegex(OSError, f"NUMBA_NUM_THREADS must be int>=1 if set, but got {count_p}"):
                    threadcount = expressive.parallel.worker_count_from_cores()

    def test_ParallelRunner_ends(self):
        # test only exists for one line of coverage for non-indexed value(s)
        data_simple = {
            "a": 5,
            "b": numpy.arange(10),
        }
        data = {
            "a": 5,
            "b": numpy.arange(10**6),
        }
        E = Expressive("a + b[i]", parallel_model="native_threadpool")
        E.build(data_simple, verify=False)
        result_1 = E(data)

        # FUTURE this shouldn't raise and can be handled nicely..
        #   however, referring to an offset result is illegal!
        #   and should be disallowed .. for example
        #     a[i] + b[i+1] + result[i]    # acceptable as result only consumes its own index
        #     a[i] + b[i+1] + result[i+1]  # can't be parallelized nicely as it depends on ordering
        E = Expressive("a + b[i+1]", parallel_model="native_threadpool")
        E.build(data_simple, verify=False)
        with self.assertRaisesRegex(NotImplementedError, re.escape("non-zero indexers are disallowed (for now)")):
            E(data)

        # TODO split into another test, this just gets coverage on array_passed codepath
        data_simple["result"] = numpy.zeros(10)
        data["result"] = numpy.zeros(10**6)
        E = Expressive("a + b[i]", parallel_model="native_threadpool")
        E.build(data_simple, verify=False)
        result_2 = E(data)

        self.assertTrue(numpy.allclose(result_1, result_2))
        self.assertTrue(result_2 is data["result"])

    def test_ParallelRunner_active(self):
        # TODO move out to integration side along with TestMany as easily the longest-running test

        # TODO consider wrapping/replacing main instance here
        #   even mocking just for features like call count

        PR = expressive.parallel.parallel_runner

        # run once, creating an initial function used in later builds
        data = {
            "a": numpy.arange(10),
            "b": numpy.arange(10),
        }
        E = Expressive("a[i] + b[i]", parallel_model="native_threadpool")
        self.assertEqual(E._config["builder.parallel_model.native_threadpool"], True)
        self.assertTrue(PR._started == False)
        self.assertTrue(len(PR.threads) == 0)
        E.build(data, verify=False)
        self.assertTrue(PR._started == True)

        with must_warn_re(r"very little data passed datalen=\d+, using buckets=\d+", multimatch=True):
            E(data)  # triggers warn
            # extract signature to pack into later builds
            self.assertTrue(len(E.signatures_mapper) == 1)
            sig_outer, fn_outer = next(iter(E.signatures_mapper.items()))

            # sweep through lots of options
            # especially show no combinations breaks in data_slices or any thread
            for threadcount in range(1, 16):
                for size in range(2, 35):  # 1 raises, 35 chosen as (3*(10+1)+1)+1
                    try:
                        value = PR._Q_jobs.get_nowait()
                    except EmptyQueueException:  # queue.Empty
                        pass # successful case: Q should never have any content here
                    else:
                        raise AssertionError(f"BUG: Q should be empty, but .get() found {value}")
                    p1 = PR.start()
                    p2 = PR.start()  # should also be idempotent
                    PR.stop()
                    PR.stop()  # should be idempotent

                    # same object is always returned by `.start()`
                    self.assertTrue((p1 is p2) and (PR is p1) and (PR is p2))

                    # E = Expressive("a + b", parallel_model="native_threadpool")  # FIXME handle simple case too
                    E = Expressive("a[i] + b[i]", parallel_model="native_threadpool")

                    self.assertEqual(E._config["builder.parallel_model.native_threadpool"], True)
                    self.assertTrue(PR._started == False)
                    self.assertTrue(len(PR.threads) == 0)

                    data = {
                        "a": numpy.arange(size),  # 1 is rejected "BUG: failed to discover data length during chunking"
                        "b": numpy.arange(size),
                    }
                    # skip build to avoid massive overhead time
                    #   E.build(data, verify=False)
                    #   self.assertTrue(PR._started == True)
                    # following `PR.update()` starts instance
                    E.signatures_mapper[sig_outer] = fn_outer

                    # change threadcount on instance]
                    PN = PR.update(threadcount=threadcount)
                    self.assertTrue(PN is PR)
                    self.assertTrue(PR._started == True)
                    self.assertTrue(len(PR.threads) == threadcount)

                    # TODO wrap with mock side effect to prove run
                    result = E(data)

                    # prove soft reference worked
                    self.assertTrue(len(data) == 2)
                    self.assertTrue("result" not in data)

                    self.assertTrue(numpy.allclose(result, data["a"] + data["b"]))

        PR.update(threadcount="auto")  # reset threadcount to system default

    def test_bad_broadcasting_indexed_threaded(self):
        """ show that native_threadpool can trap and report Exceptions correctly, unlike prange
            see also TestTensorsMultidim.test_bad_broadcasting_indexed
        """
        exit_warn = None  # allow re-warning outside `must_warn_re()` context for [ISSUE 179]
        with must_warn_re([
            "mixed dimensions may not broadcast correctly",
            "very little data passed datalen=2, using buckets=1",
            ], multimatch=True,
        ):
            data = {
                "a": numpy.array([[1,2],[3,4]]),
                "b": numpy.array([[1,2],[3,4]]),
                "result": numpy.array([[0,0,0],[0,0,0]]),  # wrong shape results in warns and then error
            }
            # using prange covers up that this does not work!
            # FUTURE experiment more with boundscheck=True (does not catch the error)
            E = Expressive("a[i]+b[i]", parallel_model="prange")
            E.build(data, verify=False)
            try:
                E(data)  # most instantiations do not raise despite issue
            except Exception as ex:  # pragma nocover only ubuntu 24.10 container fails here!
                # FIXME why does this only happen under the 24.10 container? [ISSUE 179]
                #  - should be understood
                #  - consider tighter check beyond lsb-release too
                try:
                    with open("/etc/lsb-release") as fh:
                        is_2410_container = bool("DISTRIB_RELEASE=24.10" in fh.read())
                except Exception:
                    is_2410_container = False
                if not is_2410_container:  # unexpected path: this is a real error: re-raise outer `E(data)` Exception
                    raise RuntimeError(f"BUG: unexpected Exception calling E(data) with prange: {repr(ex)}") from ex
                # success path for 24.04 container [ISSUE 179]
                exit_warn = f"[ISSUE 179] caught Exception from prange instance: {repr(ex)}"
            else:
                # BEWARE the array is actually unfilled despite reporting success!
                self.assertTrue(numpy.array_equal(data["result"], numpy.array([[0,0,0],[0,0,0]])))

            # however, using native_threadpool the Exception can be detected
            data = {
                "a": numpy.array([[1,2],[3,4]]),
                "b": numpy.array([[1,2],[3,4]]),
                "result": numpy.array([[0,0,0],[0,0,0]]),  # wrong shape results in warns and then error
            }
            E = Expressive("a[i]+b[i]", parallel_model="native_threadpool")
            E.build(data, verify=False)
            msg = re.escape("caught (1) Exception(s) in threads: ValueError('cannot assign slice")
            with self.assertRaisesRegex(RuntimeError, msg):
                E(data)

        if exit_warn is not None:  # pragma nocover [ISSUE 179]
            warnings.warn(exit_warn, RuntimeWarning)


class TestExternalSymbols(unittest.TestCase):

    def test_symbols_basic(self):
        a, b = sympy.symbols("a b")
        symbols = {"a": a, "b": b}
        E = Expressive("a + b", symbols=symbols)
        self.assertTrue(E._symbols["a"] is a)  # same references
        self.assertTrue(E._symbols["b"] is b)

    def test_symbols_collection_types(self):
        a, b = sympy.symbols("a b")
        for collection_type in (tuple, list, set):
            symbols = collection_type([a, b])
            E = Expressive("a + b", symbols=symbols)
            self.assertTrue(E._symbols["a"] is a)  # same references
            self.assertTrue(E._symbols["b"] is b)

    def test_symbols_partial(self):
        a, b = sympy.symbols("a b")
        E = Expressive("a + b + c", symbols=(a, b))
        self.assertTrue("c" in E._symbols)     # created symbol
        self.assertTrue(E._symbols["a"] is a)  # same reference

    def test_symbols_indexed(self):
        # correctly uses IndexedBase
        a, b = sympy.symbols("a b", cls=sympy.IndexedBase)
        E = Expressive("a[i] + b[i+1]", symbols=(a, b))
        self.assertTrue(E._symbols["a"] is a)  # same references
        self.assertTrue(E._symbols["b"] is b)
        indexer = next(iter(E._indexers))
        self.assertEqual(indexer.name, "i")
        self.assertTrue("i" not in E._symbols)  # still correctly generates Idx
        self.assertTrue(E._indexers[indexer] == [0, 1])

        # correctly uses Idx
        j = sympy.Idx("j")
        E = Expressive("a[j] + b[j+1]", symbols=j)  # exercises single value path
        self.assertTrue("j" not in E._symbols)
        indexer = next(iter(E._indexers))
        self.assertTrue(indexer.name == "j")
        self.assertTrue(indexer is j)  # exact ref
        self.assertTrue(E._indexers[indexer] == [0, 1])

    def test_symbols_indexed_errors(self):
        # naive use fails due to wrong types
        a, b, i = sympy.symbols("a b i")
        with self.assertRaisesRegex(TypeError, r"should be type .*IndexedBase.*but got.*Symbol"):
            E = Expressive("a[i] + b[i+1]", symbols=(a, b))
        with self.assertRaisesRegex(TypeError, r"should be type .*Idx.*but got.*Symbol"):
            E = Expressive("a[i] + b[i+1]", symbols=(i,))

    def test_various_errors(self):
        # get more coverage for specific errors
        for symbols, exception, match_re in [
            ("a",    TypeError, r"expected a collection of SymPy Symbols, but got "),
            (["a"],  TypeError, r"symbols must be a collection of SymPy Symbols, but got "),
            ([None], TypeError, r"symbols must be a collection of SymPy Symbols, but got "),
            ({"a": sympy.Symbol("a"), 1: sympy.Symbol("b")}, TypeError, r"all names must be strings"),
            ({"a": sympy.Symbol("a"), 'b': 1}, TypeError, r"unsupported Symbol.*expected"),
        ]:
            with self.assertRaisesRegex(exception, match_re):
                E = Expressive("a + b", symbols=symbols)

        with must_warn_re([
            r"^name 'a' doesn't match symbol\.name 'b'.*$",
            r"some symbols were not used",  # not specific to this, just happens to continue
        ]):
            symbols = {"a": sympy.Symbol("b")}
            E = Expressive("a + b", symbols=symbols)

        with must_warn_re(r"^some symbols were not used: \[b\]$"):
            symbols = sympy.symbols("a b")
            E = Expressive("a**2", symbols=symbols)

        # trigger `tidy_list_str()` during unused symbols warn
        # see also TestExtendFunctionality.test_parsers_tidy_list_str
        with must_warn_re(re.escape("some symbols were not used: [a,b,c .. e,f]")):
            symbols = sympy.symbols("a b c d e f")
            E = Expressive("x**2", symbols=symbols)


class TestSingleValues(unittest.TestCase):

    def test_simple(self):
        data = {
            "a": numpy.arange(100, dtype="int64"),
            "b": 5,
        }

        result_expected = numpy.arange(100) + 5
        E = Expressive("a + b")
        E.build(data)
        result = E(data)
        self.assertTrue(numpy.array_equal(result_expected, result))

    def test_indexed_mixed(self):
        data = {
            "a": numpy.arange(100, dtype="int64"),
            "b": 5,
        }

        result_expected = numpy.arange(100) + 5
        E = Expressive("a[i] + b")
        E.build(data)
        result = E(data)
        self.assertTrue(numpy.array_equal(result_expected, result))

    def test_all_single_values(self):
        data = {
            "a": 1,
            "b": numpy.int32(2),
        }
        E = Expressive("a + b")

        # returning a single (ndim==0) value is possible, but I'm not it's useful to implement
        # for now the result length can't be determined, so raise
        msg = re.escape("only single values passed (ndim=0), no arrays (at least a result array must be passed to determine length)")
        with self.assertRaisesRegex(ValueError, "^" + msg + r".*$"):
            E.build(data)

        # however, passing an array works
        data["result"] = numpy.zeros(100)

        # build and get the result
        E.build(data)
        result = E(data)
        self.assertTrue(len(result) == 100)
        self.assertTrue(set(result) == {3})  # exclusively 3

    def test_lhs_indexed_all_single(self):
        data = {
            "a": 1,
            "b": numpy.int32(2),
            "r": numpy.zeros(100),  # avoids ValueError, see TestEqualityExtract.test_indexed
        }
        # only LHS is indexed, so the indexed template is used
        E = Expressive("r[i] = a + b")

        E.build(data)
        result = E(data)
        self.assertTrue(len(result) == 100)
        self.assertTrue(set(result) == {3})  # exclusively 3

    def test_lhs_indexed_all_single_advanced(self):
        data = {
            "a": 10,
            "b": 5,
            "r": numpy.zeros(100),  # avoids ValueError, see TestEqualityExtract.test_indexed
        }
        E = Expressive("r[i] = a ** 2 + a ** b")
        E.build(data)
        result = E(data)
        self.assertTrue(len(result) == 100)
        self.assertTrue(set(result) == {10**2 + 10**5})  # exclusively 100100

    def test_lhs_indexed_mixed_single_array(self):
        data = {
            "a": numpy.full(100, 1, dtype="int64"),
            "b": 2,
            "r": numpy.zeros(100),
        }

        # when nothing is indexed, mixing single values and arrays is fine
        E = Expressive("r = a + b")
        E.build(data)
        result = E(data)
        self.assertTrue(len(result) == 100)
        self.assertTrue(set(result) == {3})  # all 3

        # however, when LHS is indexed, unindexed symbols are treated as single values
        E = Expressive("r[i] = a + b")
        with self.assertRaisesRegex(ValueError, re.escape("'a' is not indexed, but passed array (ndim=1) value in data")):
            E.build(data)
        # or simply when the data doesn't match up
        E = Expressive("a[i] + b[i]")
        with self.assertRaisesRegex(ValueError, re.escape("'b' is indexed, but is a single (ndim=0) value in data")):
            E.build(data)  # data doesn't match indexing in instance
        # successful build with correct indexing
        E = Expressive("r[i] = a[i] + b")


class Test_input_cleanup(unittest.TestCase):

    def test_simple(self):
        # whitespace removal
        expr_string = expressive.parsers.string_expr_cleanup("a * b")
        self.assertEqual(expr_string, "a*b")

    def test_bad(self):
        # junk inputs
        with self.assertRaisesRegex(ValueError, "string"):
            expressive.parsers.string_expr_cleanup(None)
        with self.assertRaisesRegex(ValueError, "string"):
            expressive.parsers.string_expr_cleanup(3)

        # empty string
        with self.assertRaisesRegex(ValueError, "no content"):
            expressive.parsers.string_expr_cleanup("")
        with self.assertRaisesRegex(ValueError, "no content"):
            expressive.parsers.string_expr_cleanup(" ")

        # SymPy expr doesn't need these cleanups (already parsed)
        E = Expressive("a*b")
        expr = E._expr_sympy
        with self.assertRaisesRegex(ValueError, "string"):
            expressive.parsers.string_expr_cleanup(expr)

    def test_adjacent_to_mul(self):
        # simple coefficient
        expr_string = expressive.parsers.string_expr_cleanup("2x")
        self.assertEqual(expr_string, "2*x")

        # directly adjacent to the parenthesis
        expr_string = expressive.parsers.string_expr_cleanup("2(x+1)")
        self.assertEqual(expr_string, "2*(x+1)")

        # multiply value after parentheses
        # TODO should this warn? (see notes in parsers.py)
        expr_string = expressive.parsers.string_expr_cleanup("(x+1)2")
        self.assertEqual(expr_string, "(x+1)*2")
        expr_string = expressive.parsers.string_expr_cleanup("(x+1)a")
        self.assertEqual(expr_string, "(x+1)*a")

        expr_string = expressive.parsers.string_expr_cleanup("(a+1)2 - 3(b+2)")
        self.assertEqual(expr_string, "(a+1)*2-3*(b+2)")

        # multiple cleanups
        expr_string = expressive.parsers.string_expr_cleanup("1 + 2x - 7y")
        self.assertEqual(expr_string, "1+2*x-7*y")

        # handle function or symbol
        expr_string = expressive.parsers.string_expr_cleanup("3cos(2x + pi)")
        self.assertEqual(expr_string, "3*cos(2*x+pi)")

        # function with number in name
        expr_string = expressive.parsers.string_expr_cleanup("2x + 3 - log2(n)")
        self.assertEqual(expr_string, "2*x+3-log2(n)")

        # symbol with a number in the name
        expr_string = expressive.parsers.string_expr_cleanup("t0 + t2")
        self.assertEqual(expr_string, "t0+t2")

        # more complicated parses
        # FUTURE consider detecting and raise/warn for very confusing parses

        expr_string = expressive.parsers.string_expr_cleanup("log2(2value3)")
        self.assertEqual(expr_string, "log2(2*value3)")

        expr_string = expressive.parsers.string_expr_cleanup("log2(a)3(b+2)4atan(c)")
        self.assertEqual(expr_string, "log2(a)*3*(b+2)*4*atan(c)")

    def test_pow_xor(self):
        expr_string = expressive.parsers.string_expr_cleanup("2^x")
        self.assertEqual(expr_string, "2**x")

    def test_fraction(self):
        expr_string = "1/2x"

        # fails without cleanup
        with self.assertRaises(SyntaxError):
            expressive.parsers.string_expr_to_sympy(expr_string)

        # division (actually Mul internally)
        expr_string = expressive.parsers.string_expr_cleanup(expr_string)
        self.assertEqual(expr_string, "1/2*x")

        # parsed result should be consistent across inputs
        self.assertEqual(
            expressive.parsers.string_expr_to_sympy(expr_string),
            expressive.parsers.string_expr_to_sympy("""Mul(Rational(1, 2), Symbol("x"))"""),
            expressive.parsers.string_expr_to_sympy("x/2"),
        )

    def test_equality_rewrite(self):
        """ test equality parsing to Eq
            basic workflow
                A = B
                A == B
                Eq(A, B)
        """
        # basic parse
        expr_string = expressive.parsers.string_expr_cleanup("r = x**2")
        self.assertEqual(expr_string, "Eq(r, x**2)")

        # more advanced parse
        expr_string = expressive.parsers.string_expr_cleanup("r[i] = 3^5b")
        self.assertEqual(expr_string, "Eq(r[i], 3**5*b)")

        # trivial single vs double equality
        expr_string = expressive.parsers.string_expr_cleanup("foo = bar")
        self.assertEqual(expr_string, "Eq(foo, bar)")
        expr_string = expressive.parsers.string_expr_cleanup("foo == bar")
        self.assertEqual(expr_string, "Eq(foo, bar)")

        # fail for multiple equalities
        with self.assertRaisesRegex(SyntaxError, re.escape("only 1 equivalence (==) can be provided, but parsed 2")):
            expressive.parsers.string_expr_cleanup("foo = bar = baz")

        # fail for inequalities
        with self.assertRaisesRegex(ValueError, r"inequality is not supported"):
            expressive.parsers.string_expr_cleanup("x <= y")

    def test_complex_types_parse(self):
        # TODO consider if case like `a4I` or `a4j` should parse `a*4` out with imaginary constant hint
        # expr_string = expressive.parsers.string_expr_cleanup("a4I + 2b")  # [ISSUE 69]
        expr_string = expressive.parsers.string_expr_cleanup("4a*I + 2b")
        self.assertEqual(expr_string, "4*a*I+2*b")

        expr_sympy, symbols, syms_idx, syms_result = expressive.parsers.string_expr_to_sympy(expr_string)

        # ensure it really read SymPy's imaginary `I`
        self.assertTrue(sympy.I in expr_sympy.atoms())

        # extract symbols and compare to constructed expr
        a, b = symbols["a"], symbols["b"]
        self.assertEqual(
            expr_sympy.rhs,
            4 * a * sympy.I + 2 * b,
        )

    def test_warn_for_name_mashing(self):
        # generate a real config for use here
        config = Expressive("a")._config
        self.assertEqual(config["translate_simplify.parse.name_mashing_multiply"], "warn")

        # warn the user when they have a weird structure that will be mashed
        for expr_string in [
            "foo bar",
            "a cos(b)",  # otherwise silently becomes `acos(b)`!
            "a 3",  # likely numeric errors
            "1 1",  # FUTURE paired numbers should almost-certainly raise
        ]:
            with must_warn_re("atoms '.*' will become joined"):
                expressive.parsers.string_expr_cleanup(expr_string, config)

        # never warn for non-mashing, handled cases
        with unittest.mock.patch("expressive.parsers.warn") as mock:
            for expr_string, expr_expected in {
                "3 cos(b)": "3*cos(b)",  # fully (also tested earlier) "3 cos(b)" -> "3cos(b)" -> "3*cos(b)"
                "3 a":      "3*a",       # '\d (name)' is allowed, but '(name) \d' and '\d \d' are warned
            }.items():
                expr_result = expressive.parsers.string_expr_cleanup(expr_string, config)
                if expr_expected is not None:
                    self.assertEqual(expr_result, expr_expected)
                mock.assert_not_called()
            mock.assert_not_called()

        # show raise and multiply feature
        expr_string = "a cos(b)"
        config["translate_simplify.parse.name_mashing_multiply"] = "raise"
        with self.assertRaisesRegex(ValueError, "atoms '.*' will become joined"):
            expressive.parsers.string_expr_cleanup(expr_string, config)

        config["translate_simplify.parse.name_mashing_multiply"] = "multiply"
        expr_result = expressive.parsers.string_expr_cleanup(expr_string, config)
        self.assertEqual(expr_result, "a*cos(b)")

        # full example showing recursively replacing multiplication
        with modify_config_global():
            expressive.CONFIG["translate_simplify.parse.name_mashing_multiply"] = "multiply"
            E = Expressive("a sin(b c) d e f g")
            expr = sympy.parse_expr("a*sin(b*c)*d*e*f*g")
            self.assertEqual(E._expr_sympy.rhs, expr)


class TestRelativeOffsets(unittest.TestCase):

    def test_paired(self):
        data = {
            "a": numpy.arange(100, dtype="int64"),
            "b": numpy.arange(100, dtype="int64"),
            "c": numpy.arange(100, dtype="int64"),
        }
        E = Expressive("a[i+1] + b[i-1] + c[i]")
        E.build(data)

        # give it a spin
        data = {
            "a": numpy.arange(10000, dtype="int64"),
            "b": numpy.arange(10000, dtype="int64"),
            "c": numpy.arange(10000, dtype="int64"),
        }
        result = E(data)

        # cherry-pick test cases
        self.assertEqual(result[   1],    0 +    2 +    1)
        self.assertEqual(result[5000], 4999 + 5000 + 5001)
        self.assertEqual(result[9000], 8999 + 9000 + 9001)
        # slice and verify whole array
        self.assertTrue(numpy.array_equal(
            result[1:-1],
            (numpy.arange(10000) * 3)[1:-1],
        ))

    def test_bad(self):
        # multiple indexers
        with self.assertRaisesRegex(ValueError, r"only a single Idx is supported, but got:"):
            E = Expressive("a[i] + b[n]")


class TestTensorsMultidim(unittest.TestCase):

    # NOTE numpy.matrix() is deprecated (though still seems to work even without `.A`)
    # https://numpy.org/doc/stable/reference/generated/numpy.matrix.html
    # https://numpy.org/doc/stable/user/numpy-for-matlab-users.html#array-or-matrix-which-should-i-use

    def test_tensor_simple(self):
        data = {
            "a": numpy.array([[1,2],[3,4]]),
            "b": numpy.array([[1,2],[3,4]]),
        }
        E = Expressive("a+b")
        E.build(data)
        result = E(data)
        self.assertTrue(numpy.all(result == numpy.array([[2,4],[6,8]])))

    def test_tensor_functions(self):
        data = {
            "a": numpy.array([[1,2],[3,4]]),
            "b": numpy.array([[1,2],[3,4]]),
            "c": numpy.array([[1,2],[3,4]]),
            "d": 5,
        }
        E = Expressive("a + log(b) + c**3 + d")
        E.build(data)
        result = E(data)
        # NOTE numpy.pow is an alias for numpy.power after 2.0
        #   https://numpy.org/doc/2.1/release/2.0.0-notes.html#array-api-compatible-functions-aliases
        result_expected = numpy.array([[1,2],[3,4]]) + numpy.log([[1,2],[3,4]]) + numpy.power(numpy.array([[1,2],[3,4]]), 3) + 5
        self.assertTrue(numpy.allclose(result, result_expected))

    def test_tensor_warns(self):
        # general expr to use
        E = Expressive("a+b")

        # general mixed dimension broadcasting warn
        data = {
            "a": numpy.array([[1,2,3,4],[1,2,3,4]]),
            "b": numpy.array([[1,2],[3,4]]),
        }
        with must_warn_re("mixed dimensions may not broadcast correctly, got shapes="):
            expressive.data.data_cleanup(data)

        # mismatched result dimensions without result arr
        data = {
            "a": numpy.array([[1,2],[3,4]]),
            "b": numpy.array([[[1,2]],[[3,4]]]),
        }
        with self.assertRaisesRegex(ValueError, r"couldn't determine result dimensions from data, please provide a result array"):
            with must_warn_re("mixed dimensions may not broadcast correctly, got shapes="):
                E.build(data)

        # mismatched result dimensions with result given
        data = {
            "a": numpy.array([[1,2],[3,4]]),
            "b": numpy.array([[1,2],[3,4]]),
            "result": numpy.array([[[0,0]],[[0,0]]]),  # deeper result nesting causes mismatch
        }
        with self.assertRaisesRegex(ValueError, re.escape("result dimensions (ndim=3) do not match inputs:")):
            with must_warn_re("mixed dimensions may not broadcast correctly, got shapes="):
                E.build(data)

    def test_tensor_deeper(self):
        data = {
            "a": numpy.array([[[1,2],[3,4]],[[1,2],[3,4]]]),
            "b": numpy.array([[[1,2],[3,4]],[[1,2],[3,4]]]),
        }
        self.assertEqual(data["a"].shape, (2, 2, 2))
        E = Expressive("a+b")
        E.build(data)

        # now run with a large dataset
        data = {
            "a": numpy.arange(80000).reshape(-1, 2, 2),  # 2*2*2*10000
            "b": numpy.arange(80000).reshape(-1, 2, 2),
        }
        self.assertEqual(data["a"].shape, (20000, 2, 2))
        result = E(data)

        self.assertEqual(result[0][0][0], 0)
        self.assertEqual(result[-1][-1][-1], 80000*2-2)

    def test_indexed_tensor(self):
        data = {
            "a": numpy.array([[1,2],[3,4]]),
            "b": numpy.array([[1,2],[3,4]]),
        }
        E = Expressive("a[i]+b[i+1]")
        E.build(data)

        self.assertEqual(len(E.signatures_mapper), 1)

        result = E(data)  # call
        result_expected = numpy.array([[4,6],[-1,-1]])
        self.assertTrue(numpy.array_equal(result_expected, result))

        # now retry with result array
        self.assertTrue("result" not in data)
        data["result"] = numpy.array([[0,0],[0,0]])
        E.build(data)  # FUTURE this should warn that it's rebuilding [ISSUE 194]

        # both signatures are the same now after [ISSUE 192]
        self.assertEqual(len(E.signatures_mapper), 1)

        # show array is filled correctly
        result = E(data)  # call
        result_expected = numpy.array([[4,6],[0,0]])
        self.assertTrue(numpy.array_equal(result_expected, result))

    def test_bad_broadcasting(self):
        data = {
            "a": numpy.array([[1,2,3],[1,2,3]]),
            "b": numpy.array([[1,2],[3,4]]),  # unequal data dimensions
        }
        E = Expressive("a+b")
        with must_warn_re([  # exactly 3 times
            re.escape("mixed dimensions may not broadcast correctly, got shapes={(2, 3), (2, 2)}"),
            re.escape("mixed dimensions may not broadcast correctly, got shapes={(2, 3), (2, 2)}"),
            re.escape("mixed dimensions may not broadcast correctly, got shapes={(2, 3), (2, 2)}"),
            ], ordered=True
        ):
            # fails when verifying
            with self.assertRaisesRegex(ValueError, re.escape("operands could not be broadcast together with shapes (2,3) (2,2)")):
                E.build(data, verify=True)
            # bypass verify
            E.build(data, verify=False)
            # TODO improve error (though user ignored warnings and also didn't verify test data)
            with self.assertRaisesRegex(AssertionError, r"Sizes of a, b do not match on <string> \(\d+\)"):  # \d is line in template
                E(data)

    def test_bad_broadcasting_indexed(self):
        data = {
            "a": numpy.array([[1,2],[3,4]]),
            "b": numpy.array([[1,2],[3,4]]),
            "result": numpy.array([[0,0,0],[0,0,0]]),  # wrong shape results in warns and then error
        }
        E = Expressive("a[i]+b[i+1]")
        msg_broadcast_warn = re.escape("mixed dimensions may not broadcast correctly, got shapes={(2, 3), (2, 2)}")
        with must_warn_re(
            [msg_broadcast_warn, msg_broadcast_warn, msg_broadcast_warn],  # exactly 3 times
            ordered=True,
        ):
            # fails when verifying
            with self.assertRaisesRegex(ValueError, re.escape("could not broadcast input array from shape (2,) into shape (3,)")):
                E.build(data, verify=True)
            # bypass verify
            E.build(data, verify=False)
            # TODO consider making this an internal error (or detect bad slicing in verify)
            # later versions of NumPy include the shape
            warn_re = r"cannot assign slice (from input of different size|of shape \(2,?\) from input of shape \(3,?\))"
            with self.assertRaisesRegex(ValueError, warn_re):
                E(data)  # this should raise ValueError
                raise AssertionError(f"BUG: didn't raise, got result={data['result']} and signatures={E.signatures_mapper.keys()}")


class TestAutoBuilding(unittest.TestCase):

    def test_autobuild_basic(self):
        data = {
            "a": numpy.arange(100_000, dtype="int32"),
            "b": numpy.arange(100_000, dtype="int32"),
        }

        result_expected = numpy.arange(100_000, dtype="int32") * 2

        E = Expressive("a + b", allow_autobuild=True)
        self.assertTrue(len(E.signatures_mapper) == 0)  # no cached builds

        # ensure config has expected setting
        self.assertTrue(E._config["builder.autobuild.usage_warn_nag"])
        with must_warn_re(r"autobuild took [\d\.]+s .*prefer \.build\("):
            result = E(data)

        self.assertTrue(numpy.array_equal(result_expected, result))
        self.assertTrue(len(E.signatures_mapper) == 1)  # exactly one build

        # config option to drop warning
        E._config["builder.autobuild.usage_warn_nag"] = False
        data["b"] = numpy.arange(100_000, dtype="int64")
        E(data)  # NOTE does not warn about usage here
        self.assertTrue(len(E.signatures_mapper) == 2)  # really did build again due to new signature

    def test_autobuild_error(self):
        data = {
            "a": numpy.arange(100, dtype="int32"),
        }
        E = Expressive("a**2")
        with self.assertRaisesRegex(KeyError, r"no matching signature for data: use .build"):
            result = E(data)
        # updated internal config allows the build to progress
        E._config["builder.autobuild.allow_autobuild"] = True
        E._config["builder.autobuild.usage_warn_nag"] = False
        result = E(data)  # autobuild is now enabled
        # check it really worked
        self.assertTrue(len(E.signatures_mapper) == 1)
        self.assertEqual(result[50], 2500)

class TestExprDisplay(unittest.TestCase):
    # consider combining with TestIPythonREPR

    def test_version(self):
        """ version property must be available and sensible """
        self.assertTrue(re.match(r"^\d+\.\d+\.\d+$", expressive.__version__))

    def test_display_basic(self):
        E = Expressive("a + b")
        self.assertTrue("a + b" in str(E))
        self.assertTrue("build_signatures=0" in repr(E))
        self.assertTrue("allow_autobuild=False" in repr(E))

    # FUTURE this can be moved when more tests exist here
    def test_messaging_tidy_list_str(self):
        for result_expected, collection in {
            "[0,1,2,3,4]":    range(5),
            "[0,1,2 .. 8,9]": range(10),  # long collections are compressed
            "[foo,bar,baz]":  ["foo", "bar", "baz"],
            "[['a']]":        [["a"]],
            "[['a', 'b']]":   [["a", "b"]],
            "[['a'],['b']]":  [["a"], ["b"]],
        }.items():
            result = expressive.messaging.tidy_list_str(collection)
            self.assertEqual(result, result_expected)

        # really overdoing it with stringify callable overide
        result = expressive.messaging.tidy_list_str(range(10), stringify=lambda a: "test")
        self.assertEqual(result, "[test,test,test .. test,test]")

        result = expressive.messaging.tidy_list_str([sympy.Symbol("a")])
        self.assertEqual(result, "[a]")
        result = expressive.messaging.tidy_list_str([sympy.Symbol("a")], stringify=lambda a: str(a.atoms()))
        self.assertEqual(result, r"[{a}]")

        with self.assertRaisesRegex(TypeError, r"couldn't coerce collection to list.*NoneType"):
            expressive.messaging.tidy_list_str(None)


class TestVerify(unittest.TestCase):

    def test_verify(self):
        data = {
            "a": numpy.array([1, 2, 3, 4], dtype="int64"),
            "b": numpy.array([5, 6, 7, 8], dtype="int64"),
        }
        E = Expressive("a + b")
        E.build(data, verify=True)

    def test_verify_indexed(self):
        # skips the SymPy .subs() branch
        data = {
            "a": numpy.array([1, 2, 3, 4], dtype="int64"),
            "b": numpy.array([5, 6, 7, 8], dtype="int64"),
        }
        E = Expressive("a[i] + b[i+1]")
        self.assertEqual(len(E._indexers), 1)
        indexer = next(iter(E._indexers))
        self.assertEqual(E._indexers[indexer], [0, 1])
        self.assertTrue(indexer not in E._symbols)
        E.build(data, verify=True)

    # FUTURE test for exclusively single values (no arrays), raises `data_cleanup({'a':1,'b':1})` for now [ISSUE 53]

    def test_log0(self):
        """ generally a big reason to implement this functionality """
        data = {
            "a": numpy.arange(10, dtype="int64"),  # NOTE begins with 0
        }
        E = Expressive("log(a)")        # not valid at 0
        # make it rain
        with must_warn_re(r"^divide by zero encountered in log$"):   # Python(NumPy)
            E.build(data, verify=True)

    def test_too_much_data(self):
        data = {
            "a": numpy.arange(5000, dtype="int64"),
            "b": numpy.arange(5000, dtype="int64"),
        }
        E = Expressive("a + b")
        # with must_warn_re(r"^excessive data may be slowing native verify.*{'a': 5000, 'b': 5000}\)$"):
        with must_warn_re(r"excessive data may be slowing native verify"):
            with unittest.mock.patch("time.process_time_ns") as mock:
                mock.side_effect = [0, 15*10**9, 0, 10000]  # 15s in ns
                E.build(data, verify=True)

    def test_NaN(self):
        data = {
            "a": numpy.array([0, 1, 2, 3, numpy.nan, 4, 5], dtype="float32"),  # NOTE begins with 0
        }
        E = Expressive("log(a)")         # not valid at 0
        with must_warn_re([
            "some data in a is NaN",
            r"^divide by zero encountered in log$"  # Python(NumPy)
        ]):
            E.build(data, verify=True)

        # sympy.nan are expressly rejected because object isn't a valid dtype
        # FUTURE consider making this error clearer, though `dtype="object"` can actually be anything
        data = {
            "a": numpy.array([0, 1, 2, 3, sympy.nan, 4, 5])
        }
        with self.assertRaisesRegex(TypeError, re.escape("unsupported dtype (a:object)")):
            E.build(data, verify=True)

    def test_None(self):
        data = {
            "a": numpy.array([0, 1, 2, 3, None, 4, 5], dtype="float32"),  # NOTE begins with 0
        }
        E = Expressive("log(a)")         # not valid at 0
        with must_warn_re([
            "some data in a is NaN",
            r"^divide by zero encountered in log$"  # Python(NumPy)
        ]):
            E.build(data, verify=True)

    def test_warnings(self):
        data = {
            # "a": numpy.array([1, 2, 3, 4], dtype="int32"),
            "a": numpy.arange(10000, dtype="int32"),
        }

        # extremely simple functions which will act as if they return an array
        def fn_python(a):
            return [1, 2, 3, 4]

        def fn_compiled(a):  # still behaves like the compiled function for this purpose
            return [1, 2, 3, 1]

        # TODO is it better to mock warnings.warn?
        with must_warn_re([
            re.escape("verify took a long time python:0.00s, compiled:35.00s"),
            re.escape("compiled function (35000000000ns) may be slower than direct NumPy (10000ns) (data lengths {'a': 10000})"),
        ]):
            with unittest.mock.patch("time.process_time_ns") as mock:
                mock.side_effect = [0, 10000, 0, 35 * 10**9]  # 35s in nanoseconds
                with self.assertRaisesRegex(RuntimeError, re.escape("not allclose(False) when comparing between NumPy and compiled function")):
                    result = expressive.expressive.verify_cmp(
                        data,
                        None,  # ignored when indexers are present
                        fn_python,
                        fn_compiled,
                        {None: [0, 0]},  # impossible, but contentful indexers to skip SymPy expr
                    )

    def test_auto_verify(self):
        """ test if verify_cmp() is called automatically for varying lengths of data """
        E = Expressive("a + b")

        for datalen, verify_expected in (
            (10,  True),
            (100, False),
        ):
            with unittest.mock.patch("expressive.expressive.verify_cmp") as mock:
                mock.side_effect = [(None, None)]  # just needs to be unpackable
                data = {
                    "a": numpy.arange(datalen, dtype="int64"),
                    "b": numpy.arange(datalen, dtype="int64"),
                }
                E.build(data)
                self.assertEqual(mock.called, verify_expected)

    def test_complex_result(self):
        data = {
            "a": 1j,  # possibly better in TestSingleValues
            "b": numpy.arange(100),
        }
        E = Expressive("(a + b)*3")
        E.build(data, verify=True)

        data = {
            "a": 1j,
            "b": numpy.arange(10000),
        }
        result = E(data)

        self.assertEqual(result.dtype, numpy.dtype("complex128"))
        self.assertEqual(result[1], 3+3j)
        self.assertEqual(result[2], 6+3j)
        self.assertEqual(result[-1], (9999*3)+3j)


class TestIPythonREPR(unittest.TestCase):
    """ unit tests for special IPython display method(s)
        currently only _repr_html_() is supported

        refer to Notes block of `IPython.display.display` docs
        https://ipython.readthedocs.io/en/latest/api/generated/IPython.display.html#IPython.display.display
    """

    def test_repr_basic(self):
        """ html output is as-expected """
        E = Expressive("x**3 - 2y")
        block = E._repr_html_()
        self.assertTrue("Expressive(Eq(result, x**3 - 2*y))" in block)
        self.assertTrue(r"\(\displaystyle result = x^{3} - 2 y\)" in block)  # transformed by mathjax client-side
        self.assertTrue("&lt;build_signatures=0,allow_autobuild=False&gt;</li>" in block)  # NOTE repr unstable

    def test_demote_warn(self):
        """ patch SymPy LaTeX repr to trigger warning path """
        E = Expressive("x**3 - 2y")
        with must_warn_re(r"^unexpected expr format .*: mocked LaTeX repr result$"):
            with unittest.mock.patch("sympy.Eq._repr_latex_") as mock:  # outer atom is always Eq
                mock.side_effect = ["mocked LaTeX repr result"]
                block = E._repr_html_()  # triggers warn path as not wrapped "$expr$" or "$$expr$$" (transformed to "\(expr\)")
                self.assertTrue("html" not in block)  # returns basic repr instead of html
                self.assertEqual(block, repr(E))

    # FUTURE render javascript
    # FUTURE ensure integrity check works (assures .js from jsdelivr)


class TestSumCompiler(unittest.TestCase):
    """ test Sum extracting compiling function
        FUTURE also do Product?
    """

    def test_basic(self):
        """ simplify trivial `Sum()` instances or error """

        data = {}
        # simple `Sum()` instances with fixed end values can be directly computed
        #   >>> expr
        #   Sum((b + x)**2, (x, 1, 10))
        #   >>> expr.doit()
        #   10*b**2 + 110*b + 385
        E = Expressive("Sum((x+b)**2, (x, 1, 10))")
        expr, symbols, indexers, results, block_sum_functions = expressive.codegen.breakout_Sum_to_loop(
            E._expr_sympy.rhs,
            E._symbols,
            E._indexers,
            E._results,
            "result",
            data,
            config=E._config,
        )
        if VERSION_SYMPY <= (1, 7):  # pragma nocover (path only used in older versions)
            # less-simplified version probably returned in older sympy (deprecated python tests)
            #   >>> import sympy
            #   >>> sympy.__version__  # at least 1.6 and 1.7 report this error
            #   '1.6'
            #   >>> e = sympy.parse_expr("Sum((x+b)**2, (x, 1, 10))")
            #   >>> e.replace(sympy.Sum, sympy.summation)
            #   (b + 1)**2 + (b + 2)**2 + (b + 3)**2 + (b + 4)**2 + (b + 5)**2 + (b + 6)**2 + (b + 7)**2 + (b + 8)**2 + (b + 9)**2 + (b + 10)**2
            #   >>> e.replace(sympy.Sum, sympy.summation).simplify()
            #   10*b**2 + 110*b + 385
            _expr = expr.simplify()  # FUTURE maybe always simplified in the future (this test dropped or inverted) [ISSUE 122]
            if str(_expr) == str(expr):
                warnings.warn(f"this block may no longer be needed for sympy v{VERSION_SYMPY}", RuntimeWarning)
            expr = _expr
        self.assertEqual(
            expr,
            sympy.parse_expr("10*b**2 + 110*b + 385")
        )
        self.assertEqual(  # shouldn't create any custom functions
            block_sum_functions,
            ""
        )

        # expr_simplified

        # additionally, floating-point functions in `Sum()` with known args can be combined
        # specifically this combines the summation of exact logarithms (logically just log(10!))
        #   `log(1) + log(2) + log(3) + log(4) + log(5) + log(6) + log(7) + log(8) + log(9) + log(10)`
        #   15.104412573075515295225709329251070371882250744292...
        expr_expected = sympy.parse_expr("10*b + log(factorial(10))")

        expr, symbols, indexers, results, block_sum_functions = expressive.codegen.breakout_Sum_to_loop(
            sympy.parse_expr("Sum(log(x)+b, (x, 1, 10))"),
            E._symbols,
            E._indexers,
            E._results,
            "result",
            data,
            E._config,
        )
        if VERSION_SYMPY <= (1, 7):  # pragma nocover (path only used in older versions)
            # similarly not as simplfied as above (tested in 1.6)
            #   >>> e.replace(sympy.Sum, sympy.summation)
            #   10*b + log(2) + log(3) + log(4) + log(5) + log(6) + log(7) + log(8) + log(9) + log(10)
            #   >>> e.replace(sympy.Sum, sympy.summation).simplify()
            #   10*b + log(3628800)
            _expr = expr.simplify()
            if str(_expr) == str(expr):
                warnings.warn(f"this block may no longer be needed for sympy v{VERSION_SYMPY}", RuntimeWarning)
            expr = _expr
        # `N()` here sets the floating-point precision so they are exactly equal (they are logically before `.n()`)
        self.assertEqual(
            sympy.N(expr,      8),
            sympy.N(expr_expected, 8)
        )
        self.assertEqual(  # shouldn't create any custom functions
            block_sum_functions,
            ""
        )

    def test_builds_over_Sum(self):
        # FUTURE improved support for non-trivial `Sum()`
        data = {
            "b": numpy.arange(10),
            # "m": numpy.arange(10),  # FIXME allow and maybe warn for unused data [ISSUE 43]
        }

        # from direct (1->50)
        E = Expressive("Sum(log(x) + b, (x, 1, 50))")
        E.build(data, verify=True)
        E(data)
        # if comparing later
        # d = {
        # 'nb': numpy.array([148.47776695, 198.47776695, 248.47776695, 298.47776695, 348.47776695, 398.47776695, 448.47776695, 498.47776695, 548.47776695, 598.47776695]),
        # 'py': numpy.array([148.47776695, 198.47776695, 248.47776695, 298.47776695, 348.47776695, 398.47776695, 448.47776695, 498.47776695, 548.47776695, 598.47776695]),
        # 'sp': [148.47776695177302, 198.47776695177302, 248.47776695177302, 298.47776695177305, 348.47776695177305, 398.47776695177305, 448.47776695177305, 498.47776695177305, 548.477766951773, 598.477766951773]
        # }

        # from indirect (1->m)
        E = Expressive("Sum(log(x) + b, (x, 1, m))")
        data["m"] = numpy.arange(10)
        E.build(data, verify=True)
        result = E(data)
        # values lifted from verify, but fixed here to ensure they stay the same
        # can also reproduce with this (note b and m are the same for each row, named z in fast builder)
        #   [parse_expr(f"Sum(log(x) + {z}, (x, 1, {z}))").evalf() for z in range(10)]
        # compared with
        #   >>> l = [parse_expr(f"Sum(log(x) + {z}, (x, 1, {z}))").evalf() for z in range(10)]
        #   >>> l = [numpy.float64(v) for v in l]
        #   >>> numpy.allclose(d["sp"], l)
        #   True
        self.assertTrue(numpy.allclose(
            result,
            numpy.array([0.0, 1.0, 4.693147180559945, 10.791759469228055, 19.178053830347945, 29.787491742782045, 42.5792512120101, 57.525161361065415, 74.60460290274526, 93.80182748008147])
        ))

    def test_single_values(self):
        data = {
            "a":   1,  # probably `S.One` when viewed as a limit
            "b": 100,  # `sympy.Integer` when viewed as a limit
            "m": numpy.arange(1000),
        }
        E = Expressive("Sum(log(x) * m, (x, a, b))")
        E.build(data)
        E(data)  # TODO check result

        data["c"] = 5
        E = Expressive("Sum(log(x * c) * m, (x, a, b))")
        E.build(data)
        E(data)  # TODO check result

    def test_result_passed(self):
        """ test result array is not replaced """

        E = Expressive("r = Sum(x + log(b), (x, a, b))")

        # ensure calls simplifying route
        data = {
            "a":  5,
            "b": 10,
            "r": numpy.arange(10, dtype="float32"),
        }
        ref = data["r"]
        with unittest.mock.patch("sympy.simplify", wraps=sympy.simplify) as mock:
            E.build(data)
            mock.assert_called_once()  # called exactly once
        result = E(data)
        self.assertTrue(ref is result)

        data = {
            "a":  5,
            "b": 10,
            "r": numpy.arange(10, dtype="int64"),  # force a different signature
        }
        ref = data["r"]
        # now skip simplify step
        E._config["translate_simplify.build.sum.try_algebraic_convert"] = False
        E.build(data)  # should trigger path in `symbols.items()` loop which fixes single vars [ISSUE 120]
        result = E(data)
        self.assertTrue(ref is result)

    def test_vectorized_limits(self):
        data = {
            "a": numpy.arange(1000),  # needed to determine length, see test_summation_warns
            "m": numpy.arange(1000),
        }
        E = Expressive("Sum(log(x) * a, (x, 1, m))")
        E.build(data)

        data = {
            "a": numpy.arange(1000),
            "m": numpy.arange(1000),
        }
        E = Expressive("Sum(log(x) * a, (x, m, 1000))")
        E.build(data)

    def test_indexed_Sum(self):
        data = {
            "a": numpy.arange(10),
            "m": numpy.arange(10),
        }
        for expr in [
            # "Sum(log(x) * a[i], (x, m,    1000))",  # ValueError: 'm' is not indexed, but passed array (ndim=1) value in data
            # "Sum(log(x) * a,    (x, m[i], 1000))",  # ValueError: 'a' is not indexed, but passed array (ndim=1) value in data
            "Sum(log(x) * a[i], (x, m[i], 1000))",
            "Sum(log(x),        (x, m[i], 1000)) * a[i]",  # completely rejected in expr for now
        ]:
            with self.assertRaisesRegex(NotImplementedError, re.escape(r"mixing indexing and Sum is not (yet) supported")):
                E = Expressive(expr)

    def test_nested_SumSum(self):
        """ test nested Sum instance handling Sum(Sum(Sum))
        """
        data = {
            "m": numpy.arange(10),
            "n": numpy.arange(10),
        }
        with self.assertRaisesRegex(NotImplementedError, r"nested Sum instances not yet supported.*wraps"):
            E = Expressive("Sum( log(Sum(a*log(x),(x,1,n))) , (a, 1, 100) )")

        # see also `symbol.items()` loop which flatly excludes all dummy vars (raises BUG for now)

    def test_summation_warns(self):
        # TODO warn the user when a dummy var is in the data, but will be dropped when Sum() is resolved
        # data = {
        #     "x": numpy.arange(10),  # dummy var won't be used
        #     "b": numpy.arange(10),
        #     "m": numpy.arange(10),
        # }
        # E = Expressive("Sum(x + b, (x, 1, m))")
        # print(f"symbols for {E}")
        # print(E._symbols)
        # print(E._symbols_dummy)
        # with must_warn_re(r"dummy symbols in data will be ignored: {x}"):
        #     E._prepare(data, numpy.dtype("int64"))
        # E = Expressive("Sum(x + b, (x, 1, m)) + x")  # dummy var is used
        # E._prepare(data, numpy.dtype("int64"))  # doesn't warn

        with self.assertRaisesRegex(NotImplementedError, re.escape("only exactly 1 Sum() limits is supported for now")):
            E = Expressive("Sum(a + b, (a, 1, m), (b, 1, m))")

        # alert the user to fixed limits that have no range
        data = {
            "b": numpy.arange(10),
        }
        with self.assertRaisesRegex(ValueError, re.escape("fixed Sum() limits start(3) > stop(2) represents a zero or negative range")):
            E = Expressive("Sum(log(a) + b, (a, 3, 2))")

        # TODO does it make sense for this to come from `dummy_symbols_split()` or during build? (or both)
        with self.assertRaisesRegex(NotImplementedError, re.escape("only exactly 1 Sum() limits is supported for now")):
            E = Expressive("Sum(a + b, (a, 1, m), (b, 1, m))")

        # extremely contrived expr that uses every variant of {idx..idx_z}
        exprs = []
        for char_try in " abcdefghijklmnopqrstuvwxyz":
            indexer = f"idx_{char_try}".rstrip("_ ")  # "idx_ " -> "idx"
            expr = f"Sum({indexer} + c, ({indexer}, a, b))"
            exprs.append(expr)
        data = {
            "a": numpy.arange(10),
            "b": numpy.arange(10),
            "c": numpy.arange(10),
        }
        expr_full = " + ".join(exprs)
        E = Expressive(expr_full)
        E._config["translate_simplify.build.sum.try_algebraic_convert"] = False
        with self.assertRaisesRegex(ValueError, "couldn't find a suitable indexer, all ascii lowercase characters used in expr"):
            E.build(data)

        # reject wacky limits
        data = {
            "m": numpy.arange(10),
        }
        with self.assertRaisesRegex(TypeError, r"unsupported type for limit start"):
            E = Expressive("Sum(log(a), (a, 1.2, m))")
        with self.assertRaisesRegex(TypeError, r"unsupported type for limit stop"):
            E = Expressive("Sum(log(a), (a, m, 100.3))")

        # originally in test_result_passed, but it needed a floating-point call to get a full simplification
        # E = Expressive("r = Sum(x, (x, a, b))")
        E = Expressive("r = Sum(x, (x, 1, 10)) + a*b")
        data = {
            "a":  5,
            "b": 10,
            "r": numpy.arange(10),
        }
        ref = data["r"]
        # do not simplify
        E._config["translate_simplify.build.sum.try_algebraic_convert"] = False
        with must_warn_re(re.escape("Sum() has no non-dummy symbols (skipped simplification?)")):
            E.build(data)  # should trigger path in `symbols.items()` loop which fixes single vars [ISSUE 120]
        result = E(data)
        self.assertTrue(ref is result)

        # without any way to determine the result length, generate an error
        # failed previous attempt (reduced)
        #   data = {
        #       "a": 10,
        #       "b": 11,
        #   }
        #   # E = Expressive("Sum(sin(x**a) + (a*b), (x, 1, 100))")  # hangs forever [ISSUE 99]
        #   E = Expressive("Sum(log(x**a) + (a*b), (x, 1, 100))")  # can be decomposed
        #   data["c"] = numpy.arange(10)
        #   E = Expressive("Sum(log(x) + (a*b), (x, 1, 100)) + c")
        # FIXME test works fine now without this, is the error still relevant?
        # data = {
        #     "m": numpy.arange(1000),
        # }
        # E = Expressive("Sum(log(x), (x, 1, m))")
        # with self.assertRaisesRegex(ValueError, "no member Symbol had >0 dimensions to determine result length for Sum"):
        #     E.build(data)

    def test_warn_thread(self):
        timeout = 1  # seconds
        data = {
            "m": numpy.array([1, 2, 3, 4, 5, 100]),  # avoids log(0) -> zoo and Sum(.., (a, 1, 0))
        }

        def snooze(e, timeout=timeout):
            """ add a little delay when used as Mock().side_effect
                https://docs.python.org/3/library/unittest.mock.html#unittest.mock.DEFAULT
            """
            time.sleep(timeout + 1)
            return unittest.mock.DEFAULT  # ignore this and use wraps return

        E = Expressive("Sum(a + log(m), (a, 1, m))")
        E._config["translate_simplify.build.sum.threaded_timeout_warn"] = timeout
        # timeout coerced to float in config
        self.assertTrue(isinstance(E._config["translate_simplify.build.sum.threaded_timeout_warn"], float))
        timeout = float(timeout)
        with must_warn_re([
            # re.escape(r"Sum() has no non-dummy symbols"),
            re.escape(f"failed to simplify a Sum() instance in expr after {timeout}s perform algebraic expand before .build"),
        ]):
            with unittest.mock.patch("sympy.simplify", wraps=sympy.simplify) as mock:
                mock.side_effect = snooze   # FUTURE don't sleep for real time in tests
                E.build(data)


class TestPiecewiseExtractor(unittest.TestCase):

    def test_Sum_Piecewise_solution(self):
        """ handle the Sum->Piecewise simplification which originally identified this issue
                >>> expr = parse_expr("Sum(a ** x, (x, 1, b))")
                >>> expr
                Sum(a**x, (x, 1, b))
                >>> expr.replace(sympy.Sum, sympy.summation)
                Piecewise((b, Eq(a, 1)), ((a - a**(b + 1))/(1 - a), True))
        """
        expr_str = "Sum(a ** x, (x, 1, b))"  # known to form a Piecewise
        data = {
            "a": numpy.arange(10),
            "b": numpy.arange(10),
        }

        # ensure this really does simplify into a Piecewise
        expr = sympy.parse_expr(expr_str)
        expr = expr.replace(sympy.Sum, sympy.summation)       # try to evaluate
        self.assertTrue(not expr.atoms(sympy.Sum))            # Sum is gone
        self.assertTrue(expr.atoms(sympy.Piecewise))          # definitely contains Piecewise
        self.assertTrue(expr in expr.atoms(sympy.Piecewise))  # result is set of self

        E = Expressive(expr_str)

        # keep a reference to return the correct values
        proxy_p = expressive.codegen.breakout_Piecewise_to_condition_block

        with unittest.mock.patch("expressive.codegen.debug_inspect_template") as mock_t:
            with unittest.mock.patch("expressive.codegen.breakout_Piecewise_to_condition_block") as mock_p:
                mock_p.side_effect = proxy_p
                E.build(data)
                result = E(data)
                mock_p.assert_called_once()  # only .build() relies on breakout_Piecewise_to_condition_block
            template_fn = mock_t.call_args[0][0]  # get the function template argument from helper

        # template must have the expected if-statements
        statements = re.findall(r"if .*; continue", template_fn)  # NOTE proves regex works for test_Sum_Piecewise_SumLoop
        # FIXME these are really overly-specific to constrain the result, so probably
        #   need modifying to only check components match in the future if the structure changes
        #   however, SymPy (display) ordering rules seem very consistent!
        self.assertEqual(len(statements), 2)
        self.assertTrue("if ((a[idx] == 1)): result[idx] = b[idx] ; continue" in statements)
        self.assertTrue("if (True): result[idx] = (a[idx] - a[idx]**(b[idx] + 1))/(1 - a[idx]) ; continue" in statements)
        # must not have any SumLoop members
        self.assertTrue("sumloop" not in template_fn.lower())

        # result is as-expected
        result_expected = numpy.array([0, 1, 6, 39, 340, 3905, 55986, 960799, 19173960, 435848049])
        self.assertTrue(numpy.array_equal(result, result_expected))

    def test_Sum_Piecewise_SumLoop(self):
        expr_str = "Sum(a ** x, (x, 1, b))"  # known to form a Piecewise
        data = {
            "a": numpy.arange(10),
            "b": numpy.arange(10),
        }

        # disable breakout_Piecewise_to_condition_block path
        # breakout_Sum_to_loop skips simplifications which result in a Piecewise
        config = {"translate_simplify.build.sum.allow_piecewise_in_simplification": False}
        E = Expressive(expr_str, config=config)

        # keep a reference to return the correct values
        proxy_p = expressive.codegen.breakout_Piecewise_to_condition_block
        with unittest.mock.patch("expressive.codegen.debug_inspect_template") as mock_t:
            with unittest.mock.patch("expressive.codegen.breakout_Piecewise_to_condition_block") as mock_p:
                mock_p.side_effect = proxy_p
                E.build(data)
                result = E(data)
                mock_p.assert_not_called()  # skipped in favor of SumLoop route
            template_fn = mock_t.call_args[0][0]  # get the function template argument from helper

        # must not have Piecewise-style if-statements
        self.assertFalse(re.findall(r"if .*; continue", template_fn))
        # must not have SumLoop member(s)
        self.assertTrue("SumLoop0" in template_fn)

        # result is as-expected
        result_expected = numpy.array([0, 1, 6, 39, 340, 3905, 55986, 960799, 19173960, 435848049])
        self.assertTrue(numpy.array_equal(result, result_expected))

    def test_Piecewise_expr_internal(self):
        """ Expressive currently doesn't support providing a Piecewise directly, so hack it in for now
            at a minimum, multiple instances of Eq() need a support change
                expr = "Eq(result[i], Piecewise((b[i], b[i] > 3), (b[i+1], x>3)))"
                expr = "Piecewise((b[i], b[i] > 3), (b[i+1], x>3))"
        """
        # block only added to fail test if this is corrected
        # FUTURE direct support for Piecewise (this test is cumbersome and can probably go away then)
        # show SymPy can parse this successfully, but it's rejected by Expressive
        msg = re.escape("Piecewise is only supported as a result of Sum() simplification for now")
        expr_str = "Eq(result, Piecewise((a, a > 3), (b, a < 1), (c, True)))"
        self.assertTrue(sympy.parse_expr(expr_str).atoms(sympy.Piecewise))
        with self.assertRaisesRegex(ValueError, msg):
            Expressive(expr_str)

        # create expr with the same keys
        expr_str = "result[i] = b[i] + x + b[i-1]"
        E = Expressive(expr_str)
        sym_local = deepcopy(E._symbols)
        sym_local.update(E._results)
        self.assertTrue(len(E._indexers) == 1)
        indexers = {s.name: s for s in E._indexers.keys()}  # maps {Idx:[offsets]}
        sym_local.update(indexers)
        # create a SymPy expr passing all the symbols (SymPy doesn't directly parse indexed values)
        generated_expr = sympy.parse_expr("Eq(result[i], Piecewise((b[i], b[i] > 3), (b[i-1], Eq(x,3))))", sym_local)
        E._expr_sympy = generated_expr

        # now go through the normal pipeline!
        data = {
            "b": numpy.arange(10),
            "x": 5,
        }
        E.build(data)
        result = E(data)

        result_expected = numpy.array([-1, -1, -1, -1, 4, 5, 6, 7, 8, 9])
        self.assertTrue(numpy.array_equal(result, result_expected))

        # expected switch-like behavior works
        # lower values become set, while the first value is still dropped (offset correctly)
        data["x"] = 3
        result = E(data)
        result_expected = numpy.array([-1, 0, 1, 2, 4, 5, 6, 7, 8, 9])
        self.assertTrue(numpy.array_equal(result, result_expected))

        # FUTURE consider injecting nested Sum(), though it may need indexing support [ISSUE 155]

    def test_Piecewise_piecewise_fold_simplify(self):
        # block only added to fail test if this is corrected
        # FUTURE direct support for Piecewise (this test is cumbersome and can probably go away then)
        # show SymPy can parse this successfully, but it's rejected by Expressive
        msg = re.escape("Piecewise is only supported as a result of Sum() simplification for now")
        expr_str = "Eq(result, Piecewise((a, a > 3), (b, a < 1), (c, True)))"
        self.assertTrue(sympy.parse_expr(expr_str).atoms(sympy.Piecewise))
        with self.assertRaisesRegex(ValueError, msg):
            Expressive(expr_str)

        # create safe expr with the same keys, then clobber it with another to avoid parsing step
        # which currently rejects `Piecewise()` and multiple instances of `Eq()`
        E = Expressive("result = log(b) + log(a)")
        # custom expr has opposing conditions, so it can be simplified to just `a + b`
        expr = sympy.parse_expr(
            "Eq(result, Piecewise((a, Eq(a, 1)), (b, True)) + Piecewise((b, Eq(a, 1)), (a, True)))",
            E._symbols,
        )

        # ensure the `Piecewise()` are not simplified out until `piecewise_fold()` is called internally
        #   >>> e = parse_expr("Piecewise((b, Eq(a, 1)), (a, True)) + Piecewise((a, Eq(a, 1)), (b, True))")
        #   >>> e
        #   Piecewise((a, Eq(a, 1)), (b, True)) + Piecewise((b, Eq(a, 1)), (a, True))
        #   >>> piecewise_fold(e)
        #   a + b
        self.assertEqual(len(expr.atoms(sympy.Piecewise)), 2)
        self.assertEqual(len(sympy.piecewise_fold(expr).atoms(sympy.Piecewise)), 0)
        self.assertEqual(len(expr.atoms(sympy.Piecewise)), 2)  # not somehow modified

        E._expr_sympy = expr

        data = {
            "a": numpy.arange(10),
            "b": 5,
        }

        with unittest.mock.patch("expressive.codegen.debug_inspect_template") as mock_t:
            E.build(data)
            result = E(data)
            template_fn = mock_t.call_args[0][0]  # get the function template argument from helper
        # ensure the trivial template is created
        self.assertTrue("result[:] = a + b" in template_fn)

        # still works
        result_expected = numpy.arange(5, 15)
        self.assertTrue(numpy.array_equal(result, result_expected))

    def test_Piecewise_fail(self):
        """ ensure raising during build gives feedback on avoiding the codepath """
        expr_str = "Sum(a ** x, (x, 1, b))"  # known to form a Piecewise
        data = {
            "a": numpy.arange(10),
            "b": numpy.arange(10),
        }
        E = Expressive(expr_str)

        msg = "custom error message"

        def cause_Exception(*args):
            raise RuntimeError(f"{msg} {args}")

        with unittest.mock.patch("sympy.piecewise_fold") as mock_p:
            mock_p.side_effect = cause_Exception
            try:
                E.build(data)
            except Exception as ex:  # avoid using `assertRaisesRegex()` to allow more checks
                self.assertTrue(isinstance(ex, RuntimeError))
                self.assertTrue("caught Exception breaking Piecewise() into a series of conditional statements" in str(ex))
                self.assertTrue("translate_simplify.build.sum.allow_piecewise_in_simplification" in str(ex))
                self.assertTrue(msg in str(ex))  # did come from inner exception


class TestModulo(unittest.TestCase):

    def test_modulo(self):
        data = {
            "a": numpy.arange(1, 100),
            "b": numpy.arange(1, 100)[::-1],
        }
        E = Expressive("a % b")
        E.build(data)
        result = E(data)
        # with must_warn_re("divide by zero"):  # dropped zero from `arange()` above..
        result_expected = numpy.mod(data["a"], data["b"])
        self.assertTrue(numpy.array_equal(result_expected, result))

    def test_modulo_operator(self):
        for count_Mod, has_name_mod, expr_string, block_sympy in [
            # no work to do
            (1, False, "a % b", r"a % b"),
            # simplest case
            (1, False, "a mod b",     r"a % b"),
            (1, False, "(a) mod b",   r"a % b"),
            (1, False, "a mod (b)",   r"a % b"),
            (1, False, "(a) mod (b)", r"a % b"),
            # multiple values
            (2, False, "a mod b mod c",       r"a % b % c"),  # Mod(Mod(a, b), c)
            (2, False, "(a) mod b mod (c)",   r"a % b % c"),
            (2, False, "(a) mod (b) mod (c)", r"a % b % c"),
            (2, False, "(a) mod (b) mod c",   r"a % b % c"),
            (2, False, "(a) mod(b)mod c",     r"a % b % c"),
            (2, False, "(a)mod(b)mod( c)",    r"a % b % c"),
            (2, False, "(a mod b)mod(c )",    r"a % b % c"),
            (2, False, "a mod (b mod(c ))", r"a % (b % c)"),  # Mod(a, Mod(b, c))
            (2, False, "a mod (b mod(c ))", r"a % (b % c)"),
            # more advanced cases
            (1, False, "tan(a) mod (b)",    r"tan(a) % b"),
            (1, False, "tan(a) mod cos(b)", r"tan(a) % cos(b)"),
            (1, False, "tan(x) mod Sum(x, (x, a, b))", "Mod(tan(x), Sum(x, (x, a, b)))"),
            # mod is a name and warned about
            (0, True,  "a + mod", "a + mod"),
            (0, True,  "mod + b", "mod + b"),
            (0, True,  "a + mod + b", "a + mod + b"),
            (0, True,  "mod + (a*b) + 3", "mod + (a*b) + 3"),
            (0, True,  "2mod", "mod*2"),
            (0, True,  "mod**2", "Pow(mod, 2)"),
            # both
            # FUTURE consider makihg this a direct error, though the data must match it
            (1, True,  "a mod 3 + mod**5", "a % 3 + mod**5"),  # please don't do this
        ]:
            # FUTURE prefer calling the internal parser directly [ISSUE 190]
            if has_name_mod:
                with must_warn_re(re.escape("using the name 'mod' as a Symbol may unexpectedly conflict with modulo `%`: ")):
                    E = Expressive(expr_string)
            else:
                E = Expressive(expr_string)

            expr = E._expr_sympy
            expr_compare = sympy.parse_expr(f"Eq(result, {block_sympy})")
            self.assertEqual(len(expr.atoms(sympy.Mod)), count_Mod)
            self.assertEqual(expr, expr_compare)

    def test_modulo_indexed(self):
        data = {
            "a": numpy.arange(1, 100),
            "b": numpy.arange(1, 100)[::-1],
        }
        E = Expressive("a[i] % b[i-1]")
        E.build(data)
        result = E(data)
        result_expected = numpy.mod(data["a"], (data["b"] + 1))  # reversed range means +1 is the same
        self.assertTrue(result.dtype == numpy.dtype("int64"))
        result_expected[0] = -1  # Expressive fills the array with -1 for int64 and 0-index is never set
        self.assertTrue(numpy.array_equal(result_expected, result))

    def test_mod_name_extra(self):
        data = {
            "a":   numpy.array([1,2,3,4]),
            "b":   numpy.array([1,2,3,4]),
            "mod": numpy.full(4, 10),  # the name mod
        }
        # the name mod can be used
        # warning issued for potential future issue
        with must_warn_re(re.escape("using the name 'mod' as a Symbol may unexpectedly conflict with modulo `%`: ")):
            E = Expressive("mod + (a*b) + 3")
        E.build(data)
        result = E(data)
        result_expected = data["mod"] + (data["a"] * data["b"]) + 3
        self.assertTrue(numpy.array_equal(result_expected, result))

        # however, Mod can't be used as a name
        with self.assertRaisesRegex(TypeError, "unsupported.*Function.*Integer"):
            Expressive("Mod + 3")

        # the function `mod()` is transformed to `Mod()`
        E = Expressive("mod(a, b) + 3")
        atoms = E._expr_sympy.atoms(sympy.Mod)
        self.assertEqual(len(atoms), 1)
        self.assertEqual(str(atoms.pop()), "Mod(a, b)")
        # works as-expected
        del data["mod"]  # alt disable unused data warn
        E.build(data)
        result = E(data)
        result_expected = data["a"] % data["b"] + 3
        self.assertTrue(numpy.array_equal(result_expected, result))


class TestConfig(unittest.TestCase):

    def test_config_simple(self):
        c_test = Expressive("a + b")._config

        # assorted possible config types
        for config in [
            None,  # default arg is rejected from `.update()` path
            {},
            {"builder.autobuild.allow_autobuild": True},  # packed dicts are the most-likely
            {"builder.autobuild.allow_autobuild": True, "builder.autobuild.usage_warn_nag": True},
            c_test,  # existing ConfigWrapper(UserDict) instance
        ]:
            E = Expressive("a + b + c", config=config)
            self.assertTrue(E._config is not c_test)  # never the same object

    def test_bad(self):
        """ easy coverage on error path"""

        # config itself doesn't have a sensible value
        for config in [
            # None is the default for no work!
            False,
            "",
            (),
            [],
            "foo",
            1,
        ]:
            with self.assertRaisesRegex(TypeError, re.escape(f"config must be a dict-like, but got {type(config)}")):
                Expressive("a + b", config=config)

        # non-string config keys are also expressly rejected
        config = Expressive("a + b")._config
        for key in [
            None,
            False,
            1,
            {},
            frozenset(),
        ]:
            with self.assertRaisesRegex(TypeError, re.escape(f"keys must be str, but got {type(key)}")):
                config[key] = "testing"

        # unknown keys are rejected
        with self.assertRaisesRegex(KeyError, re.escape("unknown key 'foo.bar'")):
            config["foo.bar"] = "baz"

        # keys that could be a typo are referred to a difflib "close match"
        key_real = "translate_simplify.build.sum.try_algebraic_convert"
        value    = not config[key_real]
        for modifier in [
            lambda k: k[:-5],                 # truncate some characters
            lambda k: k.replace(".", ""),     # drop all "."
            lambda k: k.replace("sum.", ""),  # missing middle
            lambda k: k.replace("build.", ""),
            lambda k: k.split(".")[-1],       # just the name
        ]:
            key_trial = modifier(key_real)
            with self.assertRaisesRegex(KeyError, re.escape(f"unknown key '{key_trial}', did you mean '{key_real}'?")):
                config[key_trial] = value
        self.assertEqual(config[key_real], not value)  # no update made a change

        # yet another trial to show doesn't suggest for really wrong keys (no potential IndexError)
        try:
            config["foo.bar"] = "baz"
        except KeyError as ex:
            self.assertTrue("did you mean" not in str(ex))

    def test_unique_per_instance(self):
        """ ensure instance configs are unique once created """

        # NOTE beware of string interning et al. when creating tests here
        #   singleton object IDs may be the same! (such as None and False)

        E1 = Expressive("a + b")
        E2 = Expressive("a + b")

        # internal `copy.deepcopy()` should force these instances to be unique
        ids = set(map(id, (
            expressive.CONFIG,
            E1._config,
            E2._config,
        )))
        self.assertEqual(len(ids), 3)

        # additionally inner calculations are different instances
        id1 = id(E1._config)
        id2 = id(E2._config)
        self.assertTrue(id1 != id2)

    def test_setting(self):
        # TODO consider `not(value from CONFIG)` so it's definitely different if updated
        E1 = Expressive("a + b")
        E2 = Expressive("a + b", config={"translate_simplify.build.sum.try_algebraic_convert": False})

        valueC = expressive.CONFIG["translate_simplify.build.sum.try_algebraic_convert"]
        value1 = E1._config["translate_simplify.build.sum.try_algebraic_convert"]
        value2 = E2._config["translate_simplify.build.sum.try_algebraic_convert"]

        self.assertTrue(value1 == valueC)  # takes upstream
        self.assertTrue(value1 != value2)  # set by argument

        # doesn't modify the main config
        E1._config["translate_simplify.build.sum.try_algebraic_convert"] = False
        value1 = E1._config["translate_simplify.build.sum.try_algebraic_convert"]
        self.assertTrue(value1 != valueC)

    def test_UNSET_singleton(self):
        d1 = {
            "a": expressive.unset.UNSET,
            "b": {
                "c": [expressive.unset.UNSET]
            },
        }
        d2 = deepcopy(d1)

        # same object despite deepcopy
        self.assertTrue(d1["a"] is d2["a"])
        self.assertTrue(d1["b"]["c"][0] is d2["b"]["c"][0])

        msg = "compare instances with is, not =="

        # expressly incomparable via ==
        self.assertTrue(expressive.unset.UNSET is expressive.unset.UNSET)
        with self.assertRaisesRegex(TypeError, msg):
            expressive.unset.UNSET == expressive.unset.UNSET
        with self.assertRaisesRegex(TypeError, msg):
            d1["a"] == d2["a"]
        with self.assertRaisesRegex(TypeError, msg):
            d1["a"] == "foo"
        with self.assertRaisesRegex(TypeError, msg):
            "foo" == d1["a"]

    def test_legacy(self):
        # with self.assertRaisesRegex(ValueError, "all keys must be flattened and dot-separated"):
        #     expressive.CONFIG["translate_simplify"]

        msg = "all keys must be flattened and dot-separated, legacy key retrieval will be removed in a future version"

        # don't manipulate the default config as it will affect other tests
        # TODO consider using a setup/teardown for this TestCase instead
        config = Expressive("a + b")._config

        # key retrieval works
        config["translate_simplify.build.sum.try_algebraic_convert"] = True
        with must_warn_re(msg):
            self.assertEqual(
                config["translate_simplify"]["build"]["sum"]["try_algebraic_convert"],
                True
            )
        config["translate_simplify.build.sum.try_algebraic_convert"] = False
        with must_warn_re(msg):
            self.assertEqual(
                config["translate_simplify"]["build"]["sum"]["try_algebraic_convert"],
                False
            )

        # key setting works
        with must_warn_re(msg):
            config["translate_simplify"]["build"]["sum"]["try_algebraic_convert"] = True
        self.assertEqual(
            config["translate_simplify.build.sum.try_algebraic_convert"],
            True
        )
        with must_warn_re(msg):
            config["translate_simplify"]["build"]["sum"]["try_algebraic_convert"] = False
        self.assertEqual(
            config["translate_simplify.build.sum.try_algebraic_convert"],
            False
        )

        # invalid or more deeply-nested keys are rejected
        with self.assertRaisesRegex(KeyError, "failed to set"):
            with must_warn_re(msg):
                config["translate_simplify"]["build"]["sum"]["fake"] = True
        with self.assertRaisesRegex(ValueError, "all keys must be flattened and dot-separated"):
            config["some_fake_key"]
        # builtin dict KeyError
        with self.assertRaisesRegex(KeyError, "'some_fake_key.fake_depth'"):
            config["some_fake_key.fake_depth"]
        # TODO consider a good way to handle this (raises when can't assign to bool)
        # with self.assertRaisesRegex(KeyError, "failed to set"):
        #     with must_warn_re(msg):
        #         config["translate_simplify"]["build"]["sum"]["try_algebraic_convert"]["deeper"] = True

    def test_migrated_renamed_key(self):
        E = Expressive("log(b)**3")
        msg = re.escape("renamed key 'builder.allow_autobuild' is now 'builder.autobuild.allow_autobuild'")

        # check on the default
        # NOTE this could change, but probably won't
        self.assertEqual(E._config["builder.autobuild.allow_autobuild"], False)
        with must_warn_re(msg):
            value = E._config["builder.allow_autobuild"]
        self.assertEqual(value, False)

        # warning is triggered on read and assignment
        with must_warn_re(msg):
            E._config["builder.allow_autobuild"] = True
        with must_warn_re(msg):
            value = E._config["builder.allow_autobuild"]
        self.assertEqual(value, True)  # updated key can still assign

        # also works with global CONFIG and the local change hasn't modified it
        with must_warn_re(msg):
            outer = expressive.CONFIG["builder.allow_autobuild"]
        self.assertEqual(outer, False)

    def test_display(self):
        config = Expressive("a + b")._config
        lines = config.display()
        self.assertEqual(len(config.keys()), len(lines.split("\n")))
        self.assertTrue("translate_simplify.build.sum.try_algebraic_convert" in lines)


class TestSchemas(unittest.TestCase):

    def test_schema_collection_f(self):
        """ ensure schema checks are correct and get coverage on their errors """
        UNSET = expressive.unset.UNSET

        # member in collection
        for value, collection in [
            ("foo", ["foo", "bar", "baz"]),  # different types of collections are fine as long as they're iterable
            ("foo", ("foo", "bar", "baz")),
            ("foo", {"foo", "bar", "baz"}),
            (None,  [1, 2, 3, None]),        # mixed types are allowed
            # (3,     range(10)),              # an older version also allowed range objects
            (True,  [False, UNSET, True]),   # UNSET singleton allowed
            # (UNSET, [False, UNSET, True]),  # can't use assertEqual to compare
            (1,     [0, 1, 2]),
            (0,     [0, 1, 2]),
            (1,     [0, 1, 2, True, False]),  # bool and 1,0 can be mixed in a list
            (0,     [0, 1, 2, True, False]),
        ]:
            fn = expressive.schemas.schema_collection_f(collection)
            self.assertEqual(value, fn(value))

        # special test for UNSET which avoids `.assertEqual()`
        fn = expressive.schemas.schema_collection_f([False, UNSET, True])
        self.assertTrue(fn(UNSET) is UNSET)

        # outside collection
        for value, collection in [
            (None,  [1, 2, 3]),  # really checks presence
            (1,     [2, 3, 4]),
            (0,     [2, 3, 4]),
            ("foo", ["bar", "baz"]),
            (1,     [True, False]),  # 1,0 are not coerced to match bools
            (0,     [True, False]),
            (True,  [1, 0]),
            (False, [1, 0]),
            (UNSET, [False, None]),
        ]:
            fn = expressive.schemas.schema_collection_f(collection)
            with self.assertRaisesRegex(ValueError, r"value must be one of \["):
                fn(value)

        # unsupported value(s)
        for value in [
            object(),
            complex("3"),  # only int and float are allowed
        ]:
            collection = [1,2,value]
            with self.assertRaisesRegex(TypeError, "collection can only contain UNSET,None,bool,int,float,str but got"):
                expressive.schemas.schema_collection_f(collection)

        # set with numbers or bool (must be a list)
        with self.assertRaisesRegex(TypeError, "True and False literals or numbers in sets are expressly rejected"):
            expressive.schemas.schema_collection_f({1,2,3})
        with self.assertRaisesRegex(TypeError, "True and False literals or numbers in sets are expressly rejected"):
            expressive.schemas.schema_collection_f({True})

        # dict is rejected
        with self.assertRaisesRegex(TypeError, "collection must be a list, tuple, or set"):
            expressive.schemas.schema_collection_f({"a": "b"})

    def test_schema_number_f(self):
        # expressive.schemas.schema_number_f(callback=int, limits=None, accept_None=False)
        UNSET = expressive.unset.UNSET
        with self.assertRaisesRegex(ValueError, "expected value, but got UNSET"):
            expressive.schemas.schema_number_f()(UNSET)
        value = expressive.schemas.schema_number_f(accept_UNSET=True)(UNSET)
        self.assertTrue(value is UNSET)
        with self.assertRaisesRegex(ValueError, "expected value, but got None"):
            expressive.schemas.schema_number_f()(None)
        value = expressive.schemas.schema_number_f(accept_None=True)(None)
        self.assertTrue(value is None)

        # outside limits
        with self.assertRaisesRegex(ValueError, r"value must be within \(1, 4\), but got "):
            expressive.schemas.schema_number_f(limits=(1, 4))(5)
        value = expressive.schemas.schema_number_f(limits=(1, 4))(3)
        self.assertEqual(value, 3)
        with self.assertRaisesRegex(ValueError, r"^value must be within \([^\)]+\), but got "):
            expressive.schemas.schema_number_f(float, limits=(0.2, 0.7))(0.8)
        value = expressive.schemas.schema_number_f(float, limits=(0.2, 0.7))(0.6)
        self.assertEqual(value, 0.6)

        # str coerce
        value = expressive.schemas.schema_number_f(limits=(1, 10))("3")
        self.assertEqual(value, 3)

        # TODO consider some bad callback tests, but practically "don't do that"
        #   alternatively, does it make sense for the type from limits to hint float?

    def test_schema_bool(self):
        # schema_bool
        for value in [True, False]:
            expressive.schemas.schema_bool(value)  # doesn't raise
        for value in [
            None,
            0,       # never allowed as 1,0 cause many small confusions
            1,
            "True",  # an older version would coerce strings
            "false",
        ]:
            with self.assertRaisesRegex(ValueError, r"value must be True or False literal, but got"):
                expressive.schemas.schema_bool(value)

    def test_basic_usage(self):
        """ schema checks are applied during realistic usage """
        # FUTURE this should be moved to some new integration tests location [ISSUE 190]
        # initial create
        with self.assertRaisesRegex(ValueError, "value must be True or False literal"):
            E = Expressive("a + b", config={"translate_simplify.build.sum.try_algebraic_convert": "test"})
        with self.assertRaisesRegex(ValueError, "value must be True or False literal"):
            E = Expressive("a + b", config={"translate_simplify.build.sum.allow_piecewise_in_simplification": "test"})
        # post-create
        E = Expressive("a + b")
        with self.assertRaisesRegex(ValueError, "value must be True or False literal"):
            E._config["translate_simplify.build.sum.allow_piecewise_in_simplification"] = "test"
        with self.assertRaisesRegex(ValueError, "value must be True or False literal"):
            E._config["translate_simplify.build.sum.try_algebraic_convert"] = "test"


class TestExtendFunctionality(unittest.TestCase):

    def test_extend_basics(self):
        data = {
            "a": numpy.arange(10),
            "b": numpy.arange(10),
        }
        # generated `a = numpy.arange(10) ; 3 * (a+1)**a + 5`
        result_expected = numpy.array([8, 11, 32, 197, 1880, 23333, 352952, 6291461, 129140168, 3000000005])

        # closures to get the text of
        # FIXME do the names need to match?
        def bar(a):  # pragma nocover
            return a + 1

        def baz(z, y):  # pragma nocover
            tmp = z**y
            return tmp

        for extend in [
            {  # direct strings
                "foo": 5,
                "bar": "def bar(a): return a + 1",
                "baz": text_dedent("""
                    def baz(z, y):
                        tmp = z**y
                        return tmp
                """).strip()
            },
            {  # references for `inspect.getsource()` to read
                "foo": 5,
                "bar": bar,
                "baz": baz,
            },
        ]:
            E = Expressive("3baz(bar(a), b) + foo", extend=extend)
            # keys are all Symbolic instances
            names_extended    = {s.name for s in E._extend_names.keys()}
            closures_extended = {s.name for s in E._extend_closures.keys()}
            self.assertEqual(len(names_extended), 1)
            self.assertEqual(len(closures_extended), 2)
            self.assertTrue("foo" in names_extended)
            self.assertTrue("bar" in closures_extended)
            self.assertTrue("baz" in closures_extended)
            E.build(data)
            result = E(data)
            self.assertTrue(numpy.array_equal(result_expected, result))

    def test_extend_keying(self):
        # wrong type for collection  # NOTE None is permitted and the default
        for extend in [
            "",
            (),
            [],
            frozenset(),
        ]:
            with self.assertRaisesRegex(TypeError, r"extend must be a dict if given"):
                expressive.parsers.extra_functionality_parse(extend)

        # invalid key types
        for key in [
            None,
            (),
            frozenset(),
            sympy.Symbol("a"),  # the very first version allowed Symbol/Function keys and deduplcated 'em
            sympy.Dummy("a"),  # str(Dummy("a")) -> "_a"
        ]:
            extend = {key: 100}  # value arbitrarily chosen
            with self.assertRaisesRegex(ValueError, r"extend keys must be str, but passed 1 nonstr keys: "):
                expressive.parsers.extra_functionality_parse(extend)

        # unsuitable identifiers
        for key in [
            "",
            "has space",
            "2test",
            "a\n",
            ":",
            "a:",
            ":a",
            "_",  # exactly start or end with _ is not allowed
            "_foo_",
            "π",  # FUTURE consider allowing π and similar (valid identifier) or coerce to `sympy.pi` expr
            "∂",
        ]:
            extend = {key: 100}  # value arbitrarily chosen
            with self.assertRaisesRegex(ValueError, r"extend keys must be valid Python names without a leading or trailing underscore '_',"):
                expressive.parsers.extra_functionality_parse(extend)

        # None returns a pair of empty dicts
        a, b = expressive.parsers.extra_functionality_parse(None)
        self.assertTrue(a == b == {})

    def test_extend_values(self):
        # single values are coerced to their base number
        expr_string = "foo(a + b) + bar"
        extend = {"bar": numpy.array(5)}
        E = Expressive(expr_string, extend=extend)
        # but they must have ndim==0
        for value in [
            numpy.array([5]),
            numpy.array([5,6]),
            numpy.array([[5,6,7]]),
        ]:
            extend["bar"] = value
            msg = re.escape(f"extend[bar] expected ndim==0, but has ndim=={value.ndim}")
            with self.assertRaisesRegex(ValueError, msg):
                expressive.parsers.extra_functionality_parse(extend)

        # many types are allowed, but they're named in DTYPES_SUPPORTED
        # NOTE NumPy and Python complex() rejects spaces in str->complex
        #   >>> numpy.complex128("3+1j")
        #   (3+1j)
        #   >>> numpy.complex128("3 +1j")  # traceback omitted
        #   ValueError: complex() arg is a malformed string
        #   >>> complex("3+1j")
        #   (3+1j)
        #   >>> complex("3 +1j")           # traceback omitted
        #   ValueError: complex() arg is a malformed string
        expr_string = "foo(a + b + c)"
        extend = {
            # "foo": "def foo(z): return log(z)",
            "a": numpy.array(12, dtype="float64"),
            "b": 10,
            "c": numpy.complex128("3+1j"),
        }
        E = Expressive(expr_string, extend=extend)
        # unsuitable dtypes
        for value in [
            numpy.array(10, dtype="float128"),
            numpy.array(10, dtype="object"),  # no object/float support [ISSUE 100]
            numpy.float128(10),  # Numba doesn't support float128 (yet? see [ISSUE 65])
            # numpy.bool_(True),   # scalar, see https://numpy.org/devdocs/release/1.20.0-notes.html#deprecations
        ]:
            extend["foo"] = value
            msg = re.escape(f"extend[foo] unsupported dtype '{value.dtype}'")
            with self.assertRaisesRegex(TypeError, msg):
                expressive.parsers.extra_functionality_parse(extend)

        # unusable values go to the end of `extra_functionality_parse()`
        for value in [
            None,
            (),
            (1,2,3),
            [],
            [1,2,3],
            {},
            set(),
            frozenset(),
            sympy.Symbol("a"),
        ]:
            msg = re.escape(f"extend[bar] expected number or function-like, but got {type(value)}")
            extend = {"bar": value}
            with self.assertRaisesRegex(ValueError, msg):
                expressive.parsers.extra_functionality_parse(extend)

    def test_extend_bad_functions(self):
        # TODO function parser should be clearer about enforcing the names match at least
        #   in addition to verifying that the string probably represents a function
        expr_string = "foo(a + b)"

        # not a function definition (later SyntaxError, catch it now)
        # FUTURE prefer AST over and maybe with regex (current implementation) internally
        msg = re.escape("extend[foo] unsable value, expected function 'def' prefix:")
        for value in [
            "zdef foo(n): return n+1",
            "defz foo(n): return n+1",
            "deffoo(n): return n+1",
            "async def foo(n): return n+1",  # might not be outright caught by a future AST implementation
        ]:
            extend = {"foo": value}
            with self.assertRaisesRegex(ValueError, msg):
                expressive.parsers.extra_functionality_parse(extend)

        # mismatched key and function name
        extend = {"foo": "def bar(n): return n+1"}
        with self.assertRaisesRegex(ValueError, re.escape("extend[foo] doesn't match function value's name 'bar'")):
            expressive.parsers.extra_functionality_parse(extend)

    def test_extend_clobbering(self):
        """ show extend can be used to clobber builtins due to its closer scoping """
        data = {"a": numpy.arange(10)}

        # name clobbering
        for extend, factor in [
            ({"pi": 4},        4),  # https://en.wikipedia.org/wiki/Indiana_pi_bill
            (None,      numpy.pi),
        ]:
            result_expected = data["a"] * factor
            E = Expressive("a * pi", extend=extend)
            E.build(data)
            result = E(data)
            self.assertTrue(numpy.allclose(result_expected, result))

        # function clobbering
        data = {"a": numpy.arange(1, 25)}  # log(0) warns
        for extend, result_expected in [
            ({"log": "def log(n): return 2"}, numpy.full(24, 2, dtype="float64")),
            (None,                            numpy.log(data["a"])),
        ]:
            E = Expressive("log(a)", extend=extend)
            E.build(data)
            result = E(data)
            self.assertTrue(numpy.allclose(result_expected, result))

    def test_extend_numba_embedding(self):
        """ create a proper Numba instance to pass in """
        expr_string = "foo(a, b)"

        # TODO sort out both using the template to define its own result array if possible
        # and detecting the log instance in the closure, which will result in a float
        # and/or embedding some typecast for coercing the result of the function to match
        # currently fixed by adding a result array, which avoids
        #   No conversion from array(float64, 1d, C) to array(int64, 1d, C) for '$22return_value.8', defined at None
        data = {
            "a": numpy.arange(10),
            "b": numpy.arange(10),
            "result": numpy.zeros(10, dtype="float64"),  # FIXME needed to enable undetected log
        }

        def foo(x, y):  # pragma nocover (jit only reads signature)
            return numpy.log(x + y)

        foo_py = foo  # keep a reference for comparison
        foo = numba.jit(foo)  # normally @numba.jit
        self.assertEqual(len(foo.signatures), 0)
        self.assertTrue(foo.py_func is foo_py)  # FIXME is this assert sensible?

        extend = {"foo": foo}

        # TODO should this mock and check `inspect.getsource()` was called? probably not needed
        E = Expressive(expr_string, extend=extend)
        E.build(data)
        result_1 = E(data)

        self.assertEqual(len(foo.signatures), 0)  # didn't build foo  # TODO might do in the future

        result_2 = foo(data["a"], data["b"])  # builds foo, should have same result as same as E(data)
        self.assertEqual(len(foo.signatures), 1)  # there really is a build

        # now warns due to signature
        # msg = re.escape("extend[foo] prebuilt Numba function (.signatures=1) will be coerced to closure")
        msg = re.escape(r"extend[foo] prebuilt Numba function (.signatures=1) will be coerced to a closure for now")
        with must_warn_re(msg):
            E = Expressive(expr_string, extend=extend)
        E.build(data)
        result_3 = E(data)

        # results really are the same
        # generated `a = numpy.arange(10) ; numpy.log(a + a)`
        self.assertTrue(numpy.allclose(
            result_1,
            numpy.array([-numpy.inf, 0.69314718, 1.38629436, 1.79175947, 2.07944154, 2.30258509, 2.48490665, 2.63905733, 2.77258872, 2.89037176])
        ))
        self.assertTrue(numpy.array_equal(result_1, result_2))
        self.assertTrue(numpy.array_equal(result_1, result_3))

    # def test_extend_faux_numba(self):
    #     """ it should be possible to make a good structure for this .. but to catch accidents,
    #         create a fake Numba class that sort of behaves the same to trigger deeper warnings
    #         about it..
    #         Numba instances are almost-certainl a CPUDispatcher (for now?), but my parser
    #         (ab)uses stringifying the type to guess if it's a Numba instance of some kind
    #         in case that's not always the case, but a user can provide something suitable

    #         patches numba.core.registry.CPUDispatcher ?

    #         FUTURE consider additional warnings when mixing Numba GPU instances or similar
    #           when CUDA/HIP is actually not supported or inappropriately mixed somehow?..
    #     """
    #     # use autospec?
    #     # m = unittest.mock.create_autospec(numba.core.registry.CPUDispatcher)
    #     def foo(x, y):  # pragma nocover (jit only reads signature)
    #         return numpy.log(x + y)

    #     with unittest.mock.patch("numba.core.registry.CPUDispatcher") as mock_d:
    #         with unittest.mock.patch("numba.jit") as mock_j:
    #             mock_j.return_value = mock_d
    #             # foo_py = foo  # keep a reference for comparison
    #             # del mock.py_func
    #             foo = numba.jit(foo)  # normally @numba.jit
    #             extend = {"foo": foo}
    #             extend_names, extend_closures = expressive.parsers.extra_functionality_parse(extend)
    #             print(extend_names)
    #             print(extend_closures)
    #             mock_j.assert_called_once()
    #             mock_d.assert_called_once()


    # TODO test `verify=True` (currently disabled for `None` regardless of datalen until this works!)
    # TODO test users can use the common `np` import alias for `numpy` (and others?)


class TestMany(unittest.TestCase):
    # integration test, not a unittest packed in here
    # maybe move to examples
    # generally this sort of test is bad because it provides too much coverage
    # for too little test
    # also it can take a long time (and quite long if generating really big arrays)

    def test_many(self):
        # size = 2**(32-1) - 1  # fill int32
        size = 10**7
        data = {              # lots of data created
            "a": numpy.arange(size, dtype="int32"),
            "b": numpy.arange(size, dtype="int64"),
            "c": 5,                                  # single value to be coerced
            "r": numpy.arange(size, dtype="int32"),  # force type and content
        }

        # indexed function
        # chain from .build()
        # 3log is converted to 3*log
        E = Expressive("r[i-2] = c*r[i+5] + a[i-3]**1.1 + 3log(b[i-2])", allow_autobuild=True).build(data)
        # print(data["r"][:10])

        # doesn't generate a warning (already built above)
        time_start = time.time()  # should be fast!
        result = E(data)
        runtime = time.time() - time_start
        self.assertTrue(runtime < 5)

        # the first and last 5 values remained the same
        self.assertEqual(data["r"][0], 0)
        self.assertEqual(data["r"][-1], size-1)
        self.assertEqual(data["r"][-2], size-2)
        self.assertEqual(data["r"][-3], size-3)
        self.assertEqual(data["r"][-4], size-4)
        self.assertEqual(data["r"][-5], size-5)
        # self.assertEqual(data["r"][-6], size-6)

        # inner values are filled       c   r     a     b
        self.assertEqual(data["r"][ 1], 5 * (8) + (0) + int(3 * numpy.log(1)))  # written at `i=3`
        self.assertEqual(data["r"][ 2], 5 * (9) + (1) + int(3 * numpy.log(2)))  # written at `i=4`
        # self.assertEqual(data["r"][-8], 5 * (size-6+5) + int((size-6+3)**1.1) + int(3 * numpy.log(size-7)))  # written at `i=size-6`
        # self.assertEqual(data["r"][-8], 5 * (size-6+5) + int((size-6-3)**1.1) + int(3 * numpy.log(size-6+2)))  # written at `i=size-6`
        a = data["r"][-8]
        b = 5 * (size-6+5) + int((size-6-3)**1.1) + 3 * int(numpy.log(size-6+2))  # written at `i=size-6`
        c = 5 * (size-6+5) +    ((size-6-3)**1.1) + 3 *    (numpy.log(size-6+2))  # floating-point version
        # print(f"a: {a}, b: {b}, c: {c}")
        self.assertTrue(numpy.isclose(a, b, c))

        # result and data["r"] really are the same
        self.assertTrue(data["r"] is result)  # they are really the same array
        self.assertEqual(data["r"][10], result[10])

        # generates a new build and promotes the resulting type
        self.assertEqual(result.dtype, numpy.dtype("int32"))  # from data["r"] forces int32
        del data["r"]  # drop r from data to force detect and create
        E.build(data)
        result = E(data)
        self.assertEqual(result.dtype, numpy.dtype("float64"))  # discovered dtype


if __name__ == "__main__":
     # don't shorten output strings!
     unittest.util._shorten = lambda s, prefixlen, suffixlen: s

     # env vars are used to avoid shadowing coverage args during call
     verbosity = 2 if os.environ.get("TEST_VERBOSE") == "true" else 1
     failfast = True if os.environ.get("TEST_FAILFAST") == "true" else None

     r = unittest.main(exit=False, verbosity=verbosity, failfast=failfast)
     if not r.result.wasSuccessful():
        sys.exit("some tests failed")  # pragma nocover
