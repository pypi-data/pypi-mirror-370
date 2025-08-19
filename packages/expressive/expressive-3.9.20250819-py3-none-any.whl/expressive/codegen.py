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
import threading
from textwrap import dedent as text_dedent
from textwrap import indent as text_indent

import numba
import numpy
import sympy
import sympy.printing.pycode
from sympy.utilities.lambdify import MODULES as lambdify_modules

from .config import (
    DTYPES_FILLER_HINT,
    SYMPY_ATOMS_FP,
)
from .data import dtype_result_guess
from .parsers import SymbolOptional
from .unset import UNSET

from .messaging import warn


def signature_generate(symbols, results, data, dtype_result, config):
    """ generate a signature like
          `Array(int64, 1d, C)(Array(int64, 1d, C))`
        note that Arrays can be named and they begin with the name "array", which
          `repr()` -> `array(int64, 1d, C)`

        refer to Numba types docs and Numba Array(Buffer) classes for more details
          https://numba.readthedocs.io/en/stable/reference/types.html
    """
    # FUTURE support for names (mabye an upstream change to numba)
    #   likely further C-stlye like `void(int32 a[], int64 b)`
    # without names, the dtypes are positional, so ordering must be maintained
    # within logic that could reorder the arguments after fixing the signature!
    # however, when the user calls the Expressive instance,
    # data is passed as kwargs `fn(**data)` to the inner function
    mapper = []

    if len(results) != 1:
        raise RuntimeError("BUG: results symbols should have exactly 1 member: {results}")
    name_result   = next(iter(results.keys()))  # NOTE dict of len==1 if given
    result_passed = bool(name_result in data)  # directly check membership

    names_symbols = list(symbols.keys())
    if not result_passed:
        names_symbols.pop()  # drop the result name (guaranteed to be last symbol in dict)
    for name in names_symbols:  # use symbol ordering, not data ordering
        ref   = data[name]
        field = numba.typeof(ref)  # `numba.types.Array(dtype, dims, layout)` or scalar type
        mapper.append(field)

    # TODO consider warning the user that dummy symbols in the data won't be used
    # NOTE collection only contains symbols which are exclusively a dummy
    # dummy_symbols_in_data = {s.name for s in symbols_dummy if s.name in data}
    # if dummy_symbols_in_data:
    #     warn(f"dummy symbols in data will be ignored: {dummy_symbols_in_data}")
    # TODO warn or raise if not all data names used (+config) [ISSUE 43]
    #   len() is sufficient (KeyError earlier if fewer, but may wrap that too)

    # discover result array dimensions
    # TODO simplify result_passed and dims by using `data[name_result]`->`KeyError` to determine path?
    if result_passed:
        dims = set(data[name].ndim for name in names_symbols if (name != name_result and data[name].ndim != 0))
        ndim_result = data[name_result].ndim
        if dims:  # ignore special case where only single values were passed
            # if len(dims) != 1:
            #     warn(f"unequal data dimensions may result in an error: {dims}")
            if ndim_result not in dims:
                raise ValueError(f"result dimensions (ndim={ndim_result}) do not match inputs: {dims}")
    else:
        dims = set(data[name].ndim for name in names_symbols) - {0}
        if not dims:  # should be detected in `data_cleanup`
            raise RuntimeError("BUG: impossible code path reached, cannot determine result array length from input arrays")
        if len(dims) != 1:
            raise ValueError(f"couldn't determine result dimensions from data, please provide a result array: {dims}")
        ndim_result = dims.pop()

    # now build complete signature for Numba to compile
    # FUTURE consider support for additional dimensions in result
    if not result_passed:
        dtype = getattr(numba.types, str(dtype_result))
        result_ntype = numba.types.Array(dtype, ndim_result, "C")
        mapper.append(result_ntype)

    # range offsets when using threadpool parallelizer
    if config["builder.parallel_model.native_threadpool"]:
        mapper.append(numba.types.int64)  # FUTURE is 2**(32-1) enough values to index any real array?
        mapper.append(numba.types.int64)  # FUTURE might pass data length around as some property too

    return numba.types.void(*mapper), result_passed


def next_free_indexer(symbols, dummy_symbols):
    """ get the next free indexer lexically (idx, idx_a, idx_b...) """
    for char_try in " abcdefghijklmnopqrstuvwxyz":
        indexer = f"idx_{char_try}".rstrip("_ ")  # "idx_ " -> "idx"
        if indexer not in symbols and indexer not in dummy_symbols:  # string compare
            return sympy.Idx(indexer)  # FUTURE indexers might become normal Symbols [ISSUE 183]
    raise ValueError(f"couldn't find a suitable indexer, all ascii lowercase characters used in expr: {symbols}")


def index_vectorized_symbols(symbols, dummy_symbols, indexers, results, data):
    """ discover unindexed Symbols which could become IndexedBase
        returns
            indexers          (also mutated by-ref)
            offset_values     new symbols as {name: IndexedBase}
            indexed_variants  mapper for using .subs() on the existing Symbols
    """
    if indexers:
        raise RuntimeError(f"BUG: tried to re-index Indexed symbols: {indexers}")
    indexer = next_free_indexer(symbols, dummy_symbols)
    indexers.update({indexer: [0, 0]})  # always have 0 spread
    offset_values = {}
    indexed_variants = {}
    for name, symbol in symbols.items():
        if name in dummy_symbols:  # dummy members will redefined later
            # continue  # FUTURE nested Sum() instances probably need/support this
            raise RuntimeError(f"BUG: problematic ref is a Symbol and dummy var: {name}")
        base = sympy.IndexedBase(name)
        try:
            if data[name].ndim == 0:
                continue
        except KeyError as ex:       # might be the result name when not passed in data
            if name not in results:  # this should be impossible
                raise RuntimeError(f"BUG: unknown Symbol '{name}' not in data({data.keys()}): {repr(ex)}")
        offset_values[name]      = base
        indexed_variants[symbol] = sympy.Indexed(base, indexer)

    return indexers, offset_values, indexed_variants


def breakout_Piecewise_to_condition_block(expr, symbols, indexers, results, data):
    """ convert Piecewise (after breakout_Sum_to_loop) into a set of conditional statements

        expected simplification
            Sum(a**x, (x, 1, b))
            Eq(result, Sum(a**x, (x, 1, b)))
            Eq(result, Piecewise((b, Eq(a, 1)), ((a - a**(b + 1))/(1 - a), True)))
            Piecewise((Eq(result, b), Eq(a, 1)), (Eq(result, (a - a**(b + 1))/(1 - a)), True)))
            Piecewise((Eq(result, b[idx]), Eq(a[idx], 1)), (Eq(result, (a[idx] - a[idx]**(b[idx] + 1))/(1 - a[idx])), True)))

        final statements
            if ((a[idx] == 1)): result[idx] = b[idx] ; continue
            if (True): result[idx] = (a[idx] - a[idx]**(b[idx] + 1))/(1 - a[idx]) ; continue

        completed template
            def expressive_wrapper(a, b):
                length = len(a)
                result = numpy.full_like(a, -1, dtype=int64)
                for idx in prange(0, length):
                    if ((a[idx] == 1)): result[idx] = b[idx] ; continue
                    if (True): result[idx] = (a[idx] - a[idx]**(b[idx] + 1))/(1 - a[idx]) ; continue
                return result

        NOTE that the rationale for creating a Piecewise() when simplifying this Sum()
        seems to be avoiding the division by zero at a==1
    """
    if not expr.atoms(sympy.Piecewise):
        raise RuntimeError(f"BUG: expected Piecewise(): {expr}")
    if not expr.atoms(sympy.Eq):  # impossible as added during parse
        raise RuntimeError(f"BUG: expected Eq() wrapper: {expr}")

    # coerce the entire expression and all Piecewise sub-functions instances into a single Piecewise
    # ideally this can avoid some calls and/or duplicate calculations, though it may result in a
    # lengthy series of checks in some cases
    # NOTE this also distributes the outer `Eq(result, ...)` into each Piecewise arg
    # TODO consider if a collection of new functions styled like the sum loops is better
    #   `for index, piecewise_block in enumerate(expr_piecewise.atoms(sympy.Piecewise)):`
    # as-written, this would represent a bug in SymPy as `piecewise_fold()` should consume them all
    expr_piecewise = sympy.piecewise_fold(expr)

    # TODO consider `.piecewise_exclusive()` with or without `skip_nan=True` (then skip filling from caller)
    #   the latter might improve effect on results dtype too (must be Float for NaN?)
    #   and skipping a write might be a little faster
    #   `expr_piecewise = sympy.piecewise_exclusive(expr_piecewise)`
    # FUTURE consider if the order can be optimized in validator (though this is surely very data-dependent)
    #   which may also require `.piecewise_exclusive()` to enable reordering

    count_piecewise = len(expr_piecewise.atoms(sympy.Piecewise))

    # it is possible for `piecewise_fold()` to simplify out all `Piecewise()` when multiple exist
    #   >>> e = parse_expr("Piecewise((b, Eq(a, 1)), (a, True)) + Piecewise((a, Eq(a, 1)), (b, True))")
    #   >>> e
    #   Piecewise((a, Eq(a, 1)), (b, True)) + Piecewise((b, Eq(a, 1)), (a, True))
    #   >>> piecewise_fold(e)
    #   a + b
    # otherwise it should result in exactly 1 combined instance
    if count_piecewise < 1:
        return expr_piecewise, "", indexers, symbols
    if count_piecewise != 1:  # likely represents bug in SymPy as it should always be possible to combine
        raise RuntimeError(f"BUG: failed to coerce all Piecewise into a single call: {expr} -> {expr_piecewise}")
    # TODO consider showing Eq distribution
    # if str(expr_piecewise).count("Eq") < 2:
    #     raise RuntimeError(f"BUG: Eq not distributed to inner blocks: {expr} -> {expr_piecewise}")

    # substitute all symbols for Indexed versions with an indexer
    if not expr.atoms(sympy.Indexed):
        indexers, offset_values, indexed_variants = index_vectorized_symbols(symbols, {}, indexers, results, data)
        expr_piecewise = expr_piecewise.subs(indexed_variants)
        symbols.update(offset_values)  # update for the new expr

    # coerce Idx to Symbol [ISSUE 183]
    expr_piecewise = expr_piecewise.subs({s: sympy.Symbol(s.name) for s in expr_piecewise.atoms(sympy.Idx)})

    conditions = []
    for sub_expr, interval in expr_piecewise.args:
        if not isinstance(sub_expr, sympy.Eq):
            raise RuntimeError(f"BUG: failed to distribute Eq to expression {sub_expr}")
        condition = sympy.printing.pycode(interval).strip()
        condition = f"if ({condition}): {sub_expr.lhs} = {sub_expr.rhs} ; continue"  # embed condition block
        if "not supported in python" in condition.lower() or "\n" in condition:
            raise RuntimeError(f"BUG: failed to transform interval to condition: {interval} -> {condition}")
        conditions.append(condition)

    # TODO warn for insufficient conditions?

    # merge all the condition strings into a single block of text
    # caller is responsible for embedding them sensibly
    block_conditions = "\n".join(conditions)

    return None, block_conditions, indexers, symbols


def breakout_Sum_to_loop(expr, symbols, indexers, results, name_result, data, config):
    """ better take on reducing Sum instances
    """
    if indexers or expr.atoms(sympy.Indexed):
        raise RuntimeError(f"BUG: escaped indexers (should be impossible): {indexers} vs {expr.atoms(sympy.Indexed)}")

    attempt_simplify      = config["translate_simplify.build.sum.try_algebraic_convert"]
    threaded_timeout_warn = config["translate_simplify.build.sum.threaded_timeout_warn"]
    allow_piecewise       = config["translate_simplify.build.sum.allow_piecewise_in_simplification"]

    # collection of `Sum()` instances to work with and replace
    exprs_sums = expr.atoms(sympy.Sum)

    if attempt_simplify:
        # FUTURE `.simplify()` (and `summation()`?) can take an indefinite amount of time, consider
        #  - simple timeout [ISSUE 99] (warn user might optimize, then continue with loop functions?)
        #    consider `fork()` or multiprocessing so `simplify()` can be killed after timeout
        #  - tuning `ratio` arg
        #  - additional custom heuristics for `measure`, perhaps just marking `Sum()`
        if threaded_timeout_warn:
            # FUTURE warn for each `sum_block()` so with several the problematic one can be identified
            def watcher_simplify_warn(e, timeout):
                e.wait(timeout)
                if not e.is_set():
                    warn(
                        f"failed to simplify a Sum() instance in expr after {timeout}s"
                        " perform algebraic expand before .build()ing or set or pass config property"
                        " config['translate_simplify.build.sum.try_algebraic_convert']=False to force "
                        " loop codegen path if operation hangs indefinitely"
                    )

            event_watcher  = threading.Event()
            thread_watcher = threading.Thread(target=watcher_simplify_warn, args=(event_watcher, threaded_timeout_warn), daemon=True)
            thread_watcher.start()

        for sum_block in exprs_sums:
            sum_evaluated = sum_block.replace(sympy.Sum, sympy.summation)
            if not sum_evaluated.atoms(sympy.Sum):  # successfully decomposed `Sum()`
                # attempt to simplify numeric intermediates if any floating-point Atoms are used
                # as the result will be a Float and ideally the precision will remain the same
                #   >>> e = parse_expr("Sum(log(x/b), (x,1,10))")
                #   >>> e.doit()  # more precise, but may require many operations
                #   log(1/b) + log(2/b) + log(3/b) + log(4/b) + log(5/b) + log(6/b) + log(7/b) + log(8/b) + log(9/b) + log(10/b)
                #   >>> e.doit().simplify()      # 10! already exceeds 2**16
                #   10*log(1/b) + log(3628800)
                #   >>> e.doit().simplify().n()  # simplified
                #   10.0*log(1/b) + 15.1044125730755
                # NOTE evaluated functions which simplify to a number become `Float`, so
                #   this won't affect the result dtype
                # FUTURE does this make sense to apply to all inputs?
                #   probably not, but some subset could benefit
                if sum_evaluated.atoms(*SYMPY_ATOMS_FP):
                    # NOTE simplify function instead of method used to ease test mocks
                    sum_evaluated = sympy.simplify(sum_evaluated).n()
                # allow user to avoid replacing Sum with a simplified Piecewise and instead
                # continue to generate a SumLoop for it
                # as the Sum instance will still exist, the faster return below won't trigger
                # specifically this avoids `breakout_Piecewise_to_condition_block()` later
                # in case it's discovered to be problematic for some case(s)
                # NOTE other Sum() instances may still be simplified and replaced if more
                # than one exists in the expr
                if sum_evaluated.atoms(sympy.Piecewise) and not allow_piecewise:
                    continue
                expr = expr.replace(sum_block, sum_evaluated)

        if threaded_timeout_warn:
            event_watcher.set()
            thread_watcher.join()

        if not expr.atoms(sympy.Sum):  # successfully simplified all Sum() instances
            block_sum_functions = ""
            return expr, symbols, indexers, results, block_sum_functions

    # iterate to extract dummy vars and raise for problematic structures
    dummy_symbols = {}
    for sum_block in exprs_sums:
        fn_sum = sum_block.function
        limits = sum_block.limits  # tuple of tuples
        # separate and compare limit features
        dummy_var, limit_start, limit_stop = limits[0]

        # keep a collection of all dummy_symbols
        # TODO can this use `dummy_symbols_split()` result? (mostly avoiding KeyError from data[dummy])
        dummy_symbols[dummy_var.name] = dummy_var

    # identify and prepare to convert all vector/tensor Symbols to IndexedBase
    sum_functions = {}
    indexers, offset_values, indexed_variants = index_vectorized_symbols(symbols, dummy_symbols, indexers, results, data)

    # TODO is it possible for there to be no offset_values?
    #   I think this can only happen if all values are singular and a result array is given
    #   otherwise no result length can be determined
    #   though it is possible for an individual `Sum()` to avoid having any

    # FUTURE support and reorder Sum instances to best order if they're nested (consider recursion too)
    #   trivially, maybe `sort()` where key is the count of Sum() atoms and then lexically?
    #   will this already handle outer dummy vars? probably

    # for each Sum(), create a new custom Function which simply iterates across each dummy in its range
    mapper_new_Sum_functions = {}
    for index, sum_block in enumerate(exprs_sums):
        fn_sum = sum_block.function
        limits = sum_block.limits  # tuple of tuples
        dummy_var, limit_start, limit_stop = limits[0]

        # discover and fill arguments
        args = {s.name: s for s in fn_sum.atoms(sympy.Symbol) - {dummy_var}}
        args = {name: args[name] for name in sorted(args.keys())}  # rebuild in lexical order
        # complain about some edge cases
        set_symbols_inner = set(args.keys()) | {s.name for s in limit_start.atoms(sympy.Symbol)} | {s.name for s in limit_stop.atoms(sympy.Symbol)}
        if not set_symbols_inner:
            warn(f"Sum() has no non-dummy symbols (skipped simplification?): {sum_block}")
        if "rowscalar" in set_symbols_inner:
            raise NotImplementedError("BUG: the name literally 'rowscalar' is reserved in Sum() for now (to mangle or by-ref) [ISSUE 143]")

        # TODO consider crushing sum_block to be a safe name then collection + numbering
        # TODO prefix with 0 for length of exprs_sums
        fn_name = f"SumLoop{index}"

        result_dtype_sum = dtype_result_guess(fn_sum, data)  # returns a type like numpy.foo

        # TODO needs some careful analysis about `stop` vs `stop+1` syntax
        # NOTE Symbols are not replaced by IndexedBase instances yet and frozen as-is here
        T = f"""
        def {fn_name}(start, stop, {", ".join(args.keys())}):
            rowscalar = numpy.{str(result_dtype_sum)}(0)
            for {dummy_var} in range(start, stop+1):
                rowscalar += {fn_sum}
            return rowscalar
        """

        # NOTE start and end can independently be Symbol or numeric
        F = sympy.Function(fn_name)(limit_start, limit_stop, *args.values())
        sum_functions[F] = text_dedent(T)  # maps Function to per-row finalized string

        # create a new Function with indexed args which when embedded will refer to the new loop
        F_indexed = sympy.Function(F.name)(*map(
            lambda a: indexed_variants.get(a, a),
            (limit_start, limit_stop, *args.values())
        ))
        mapper_new_Sum_functions[sum_block] = F_indexed

    # make a single block of string functions to embed as closure(s)
    block_sum_functions = "\n".join(sum_functions.values())

    # rewrite each `Sum()` instance in expr with indexed versions with the new name
    for sum_block, F_new in mapper_new_Sum_functions.items():
        expr = expr.replace(sum_block, F_new)

    # update symbols and the result value
    symbols.update(offset_values)
    indexer = next(iter(indexers.keys()))
    expr = expr.replace(results[name_result], sympy.Indexed(symbols[name_result], indexer))

    return expr, symbols, indexers, results, block_sum_functions


def discover_parallelization(data, config):
    """ determine if build should use `numba.prange` """
    if config["builder.parallel_model.native_threadpool"]:
        return False, True
    if config["builder.parallel_model.allow_prange"] is not UNSET:
        return config["builder.parallel_model.allow_prange"], False
    if max(d.ndim for d in data.values()) <= 1:  # at least shouldn't have broadcasting errors
        return True, False
    # internal threading can ignore some broadcasting errors (and more?) [ISSUE 145]
    return False, False


def template_tidy(T):
    """ tidy up template """
    T = text_dedent(T)
    # ideally these wouldn't be needed, but they're very fast and help let closures be
    # embedded directly in code .. this also prepares for future display via [ISSUE 154]
    T = re.sub(r":\n+", r":\n", T)          # drop newline after new scope
    T = re.sub(r"(\s*)def", r"\n\1def", T)  # ensure all closures have a leading newline
    T = re.sub(r"\n{3,}", "\n\n", T)        # replace all excessive newlines
    T = T.strip()
    return T


def debug_inspect_template(t):
    """ helper function which can be easily mocked to get the final template
        there is no need to mock the return as it's never used, only called

        with unittest.mock.patch("expressive.codegen.debug_inspect_template") as mock_t:
            # do stuff
            template_fn = mock_t.call_args[0][0]  # get the function template argument from helper

        FUTURE constructed templates to be kept by unique Build object helpers [ISSUE 154]
    """
    return t


def debug_inspect_namespace(namespace):
    """ helper for testing and debug, see `debug_inspect_template()` """
    return namespace


def loop_function_template_builder(
    expr,
    symbols,
    indexers,
    results,
    result_passed,
    dtype_result,
    data,
    config,
    extend_names,
    extend_closures,
):
    """ generate environment and code to support the function
         - create namespace
         - fill template
         - exec() to generate the code
         - extract new function
    """

    # parallization features
    allow_prange, use_native_threadpool = discover_parallelization(data, config)
    result_passed = result_passed or use_native_threadpool  # use_native_threadpool always provides an array

    # get ready to build the template (note dict of len==1)
    name_result = next(iter(results.keys()))

    if not expr.atoms(sympy.Sum):
        block_sum_functions = ""
    else:
        # experimental Sum removal
        expr, symbols, indexers, results, block_sum_functions = breakout_Sum_to_loop(
            expr,
            symbols,
            indexers,
            results,
            name_result,
            data,
            config,
        )

    block_conditions = None
    if expr.atoms(sympy.Piecewise):
        # FIXME is this ok to let pass? testing ahoy
        #   it shouldn't be possible to pass a Piecewise directly, so all Sum instances
        #   which simplify into a Piecewise probably completely dissolve ..
        #   however, this might be useful in the future too and some user might have a case
        #   for nesting Sum() in Piecewise() and vice-versa
        if block_sum_functions:
            warn(f"BUG: Sum simplification to Piecewise should transform all Sum instances: {expr}")
        # NOTE this almost-always coerces Symbols to be IndexedBase [ISSUE 181]
        #   however, extremely rare cases may simplify and leave them unchanged
        # TODO can this subvert the initial dtype guess?
        try:
            expr, block_conditions, indexers, symbols = breakout_Piecewise_to_condition_block(
                expr,
                symbols,
                indexers,
                results,
                data,
            )
        except Exception as ex:
            raise RuntimeError(
                "caught Exception breaking Piecewise() into a series of conditional statements.."
                " if this is the result of simplifying a Sum() instance, setting the config option"
                " config['translate_simplify.build.sum.allow_piecewise_in_simplification']=False"
                f" or adjusting the sum limits might allow a successful build: {repr(ex)}"
            )

    # build namespace with everything needed to support the new callable
    # simplified version of sympy.utilities.lambdify._import
    _, _, translations, import_cmds = lambdify_modules["numpy"]
    expr_namespace = {"I": 1j}  # alt `copy.deepcopy(lambdify_modules["numpy"][1])`
    for import_line in import_cmds:
        exec(import_line, expr_namespace)
    # NOTE older SymPy versions may not have any translations at all
    #   while the latest seems to be just `{'Heaviside': 'heaviside'}`
    #   however, this is left as a trivial case for my multi-version build+test tool,
    #   which detects this as a line that is not run and has no other testing
    for sympyname, translation in translations.items():
        expr_namespace[sympyname] = expr_namespace[translation]

    # embed some custom functions
    # FUTURE maintain a collection of these and/or upstream these transform(s)
    # NOTE names here will still be overriden by embed if users have custom functions
    #   due to closures having a higher (highest? closest?) scoping, though this may
    #   change in the future and should be carefully attented, especially for the case
    #   of Numba functions and especially any support for functions without a Python
    #   representation (cffi et al.), though users can apply them before or after
    #   using Expressive on their data..
    if expr is None and not block_conditions:  # comparing expr to None avoids TypeError
        raise RuntimeError("BUG: impossible code path: expr or block_conditions must exist")
    # highlight any new instance of upstream `Mod` support (feels unlikely)
    if (expr is not None and expr.atoms(sympy.Mod)) or (block_conditions and re.match("\bMod\b", block_conditions)):
        if "Mod" in expr_namespace:
            warn("upstream Mod (modulo) support is now available, but may be overriden")
            # TODO consider keeping a copy of expr and/or doing more work if a function might be used
    expr_namespace["Mod"] = numpy.mod  # element-wise modulo (alias of `numpy.remainder()`)

    # determine if range or prange should be used for outer loop
    # NOTE this causes the internal logic to use threads and can result in serious
    #   errors which are lost while still returning success!
    if allow_prange:
        exec("from numba import prange", expr_namespace)

    # construct further template components
    names_symbols = list(symbols.keys())  # avoids mutating symbols
    if use_native_threadpool:  # always include result for native_threadpool
        names_symbols.append("_offset_start")
        names_symbols.append("_offset_end")
    block_args = ", ".join(names_symbols)

    # FUTURE manage this with uneven arrays if implemented [ISSUE 10]
    # NOTE this will use the first discovery it can as arrays all have the same length
    #   or will not pass `data_cleanup()`
    name_size_symbol = None
    if result_passed:  # go ahead and use the passed array if possible
        name_size_symbol = name_result
    elif block_conditions:
        name_size_symbol = next(n for n, s in symbols.items() if isinstance(s, sympy.IndexedBase))
    else:
        atom = sympy.IndexedBase if indexers else sympy.Symbol
        for symbol in expr.rhs.atoms(atom):  # pragma nocover  # set order depends on hash seeding PYTHONHASHSEED
            name_symbol = symbol.name
            # some names definitely can't be used
            #  - result not passed
            #  - extend names definitely can't be used (note extend_names is a collection of SymbolOptional:numberlike)
            #  - single entries in data can't be used
            if name_symbol == name_result:
                continue
            if isinstance(symbol, SymbolOptional):  # FUTURE `and name_symbol not in data:`
                continue
            try:
                if data[name_symbol].ndim == 0:
                    continue
            except KeyError as ex:  # should be impossible without manipulating `._extend_names` property
                warn(f"BUG: Symbol '{name_symbol}' not in data is not SymbolOptional ({type(symbol)}): {repr(ex)}")
                continue
            name_size_symbol = name_symbol
            break
    # condition should have been detected in `data_cleanup()` or `verify_indexed_data_vs_symbols()`
    if name_size_symbol is None:
        raise ValueError("BUG: couldn't determine size of result array, at least one symbol must be an array or pass a result array to fill")

    # prepare values to fill template
    if result_passed or use_native_threadpool:
        block_result = ""  # if the result array is passed in, fill it by-index
    else:                  # without it, dynamically create an array of discovered length
        result_filler = DTYPES_FILLER_HINT[dtype_result]  # KeyError should be impossible
        # FUTURE consider allowing `order='F'` [ISSUE 35]
        block_result = f"{name_result} = numpy.full_like({name_size_symbol}, {result_filler}, dtype={dtype_result}, order='C')"
    block_sum_functions = "\n" + text_indent(block_sum_functions, "    " * 3)  # TODO calculate indent

    # build embedded names block (might be just `"\n\n"`)
    block_extend_names = "\n".join(f"{k.name} = {v}" for k, v in extend_names.items())
    block_extend_names = "\n" + text_indent(block_extend_names, "    " * 3) + "\n"

    # build closures block (might be just `"\n\n"`)
    block_extend_closures = "\n\n".join(extend_closures.values())
    block_extend_closures = "\n" + text_indent(block_extend_closures, "    " * 3) + "\n"

    # construct template
    # FUTURE consider errno or errno-like arg to retrieve extra information from namespace
    if not indexers:
        # FUTURE coerce all Symbols to be Indexed in non-trivial exprs [ISSUE 181]
        # always broadcast as `expressive_inner()` takes `result_array` by-reference after [ISSUE 192]
        T = f"""
        def expressive_inner({block_args}):
            {block_extend_names}
            {block_extend_closures}
            {expr.lhs}[:] = {expr.rhs}
        """
    elif len(indexers) == 1:
        indexer, (start, end) = next(iter(indexers.items()))
        # construct range sequence
        start = -start  # flip start to be positive (no -0 in "normal" Python)
        end   = "length" if end == 0 else f"length - {end}"
        if use_native_threadpool:
            block_range  = "range(_offset_start, _offset_end)"
        else:
            range_fn = "prange" if allow_prange else "range"
            # start = -start  # flip start to be positive (no -0 in "normal" Python)
            # end   = f"length" if end == 0 else f"length - {end}"
            block_range  = f"{range_fn}({start}, {end})"

        if block_conditions is None:
            block_loop_inner = f"{expr.lhs} = {expr.rhs}"
        else:
            block_loop_inner = "\n" + text_indent(block_conditions, "    " * 4)  # TODO calculate indent

        # TODO improve accounting for result LHS in range
        # TODO consider disallowing negative LHS offset, though it feels useful
        # TODO is it better to pass length or duplicate it in the wrapper?
        T = f"""
        def expressive_inner({block_args}):
            {block_extend_names}
            {block_extend_closures}
            {block_sum_functions}
            length = len({name_result})
            for {indexer} in {block_range}:
                {block_loop_inner}
        """
    else:
        # FUTURE consider if it's possible to implement this as nested loops [ISSUE 91]
        raise RuntimeError(f"BUG: indexers must be len 1 when provided (see string_expr_to_sympy): {indexers}")

    T_inner = template_tidy(T)

    # wrapper to handle creating result array when `not result_passed` and more
    if result_passed:
        block_args_outer = block_args
    else:
        # TODO prefer symbols collection over re-parsing string?
        # NOTE result array always passed when `use_native_threadpool` which adds the extra range members
        block_args_outer, test_name_result = block_args.rsplit(", ", 1)
        if test_name_result != name_result or test_name_result == "_offset_end":
            raise RuntimeError(f"BUG: bad block_args line trailing name '{test_name_result}': {block_args}")

    # `expressive_inner()` operates by-reference after [ISSUE 192]
    T = f"""
    def expressive_outer({block_args_outer}):
        {block_result}
        expressive_inner_ref({block_args})
        return {name_result}
    """
    T_outer = template_tidy(T)

    # trivial `lambda t:t` helpers for tests to access template string see also [ISSUE 154]
    debug_inspect_namespace(expr_namespace)
    debug_inspect_template(T_outer)
    debug_inspect_template(T_inner)
    return T_inner, T_outer, expr_namespace


def do_compile(config, signature, T_inner, T_outer, expr_namespace, dtype_result_pre=None):
    # build and extract the inner template (Python function)
    exec(T_inner, expr_namespace)
    fn_inner = expr_namespace["expressive_inner"]

    # pre-compile function as the signature is given
    # FUTURE collect into a class with additional properties (just build time?)
    fn_inner_numba = numba.jit(
        signature,
        nopython=True,  # now the default
        # fastmath=True,  # FUTURE config setting [ISSUE 29]
        parallel=config["builder.parallel_model.numba_parallel"],
    )(fn_inner)

    # now dynamically create wrapper which also returns the result array
    expr_namespace["expressive_inner_ref"] = fn_inner_numba
    exec(T_outer, expr_namespace)
    fn_outer = expr_namespace["expressive_outer"]

    # mangle names for verifying
    # TODO should this be part of `loop_function_template_builder()` instead?
    T_outer_py = T_outer
    T_outer_py = re.sub(r"def expressive_outer\(", "def expressive_outer_py(", T_outer_py)
    T_outer_py = re.sub(r"expressive_inner_ref\(", "expressive_inner(", T_outer_py)

    exec(T_outer_py, expr_namespace)
    fn_py = expr_namespace["expressive_outer_py"]

    return fn_outer, fn_py
