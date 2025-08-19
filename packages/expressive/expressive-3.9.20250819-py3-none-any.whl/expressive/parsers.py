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
from inspect import getsource as inspect_source_text
from textwrap import dedent as text_dedent

import numba
import numpy
import sympy

from .config import DTYPES_SUPPORTED
from .messaging import warn, tidy_list_str


def symbols_given_cleanup(expr, symbols):
    """ helper for producing a mapping of names to symbols
        if unsure or only partially available, prefer to return less over guessing
        this lets a user pass only what the need and let Expressive figure out
        the rest

        FUTURE make some use of SymPy Assumptions (.assumptions0)
          https://docs.sympy.org/latest/guides/assumptions.html
          https://docs.sympy.org/latest/modules/core.html#sympy.core.basic.Basic.assumptions0
    """
    # all are extracted from expr post-parsing if no Symbols are passed (probably None)
    if not symbols:
        return {}

    types_supported_symbols = (sympy.Symbol, sympy.IndexedBase, sympy.Idx)

    if isinstance(symbols, types_supported_symbols):  # singular Symbol as argument
        return {symbols.name: symbols}

    if isinstance(symbols, (list, tuple, set)):
        for symbol in symbols:
            if not isinstance(symbol, types_supported_symbols):
                raise TypeError(f"symbols must be a collection of SymPy Symbols, but got {type(symbol)}")
        return {s.name: s for s in symbols}

    if isinstance(symbols, dict):
        for name, symbol in symbols.items():
            if not isinstance(name, str):
                raise TypeError(f"all names must be strings (str), but got {type(name)}: {name}")
            if not isinstance(symbol, types_supported_symbols):
                raise TypeError(f"unsupported Symbol {type(symbol)}: {symbol}, expected {types_supported_symbols}")
            if symbol.name != name:
                warn(f"name '{name}' doesn't match symbol.name '{symbol.name}' ({sympy.srepr(symbol)})")
        return symbols

    raise TypeError(f"expected a collection of SymPy Symbols, but got ({type(symbols)})")


class SymbolOptional(sympy.Symbol):
    """ Optional Symbol such as a constant provided by the user via extend which
        should be baked into the function template
        in the future, this might be useful to supply optional args when different
        values are available in the passed data

        for numbers, it would be nice to provide a `sympy.NumberSymbol` wrapper
        however, it's behavior expects instances to be singular, atomic values
        which are defined by a single instance of a custom class

        alternatively, `Dummy` instances are intended to be unique and have custom
        naming logic, such that they display like `f"_{self.name}"`
        that said, perhaps it makes sense to inherit from both
    """
    # TODO should additional guarantees or assumptions be applied here?
    #   they might help or hinder later parsing and simplification(s)
    # is_number = True


def extra_functionality_parse(extend):
    """ split and transform extend into dicts
            extra_functions  {sympy.Function: string function}
            extra_symbols    {SymbolOptional: number-like}

        this is not intended to create an inner system hell, just accelerate some math!
        see also https://en.wikipedia.org/wiki/Greenspun%27s_tenth_rule

        consider enabling a global collection of user functions and constants
        and/or enabling `import` statements
    """
    if extend is None:  # no extras, but still provide dicts to ease later `locals_dict.update()`
        return {}, {}
    if not isinstance(extend, dict):
        raise TypeError(f"extend must be a dict if given, but got {type(extend)}")

    # aggressively verify keys before doing any other work
    # the first logic here allowed both str and symbols and deduplicated them, but it seemed needlessly complex
    keys_nonstr  = []
    keys_badname = []
    for key in extend.keys():
        if not isinstance(key, str):
            keys_nonstr.append(key)
            continue  # avoid AttributeError from missing string methods next
        if not key.isidentifier() or key.startswith("_") or key.endswith("_") or not re.match(r"^[a-zA-Z\d_]+$", key):
            keys_badname.append(key)
    if keys_nonstr:
        raise ValueError(f"extend keys must be str, but passed {len(keys_nonstr)} nonstr keys: {tidy_list_str(keys_nonstr)}")
    if keys_badname:
        raise ValueError(
            f"extend keys must be valid Python names without a leading or trailing underscore '_',"
            f" but passed {len(keys_badname)} invalid keys: {tidy_list_str(keys_badname)}"
        )

    # extend_imports  = []  # list of string imports  # TODO consider enabling additional imports
    extend_names    = {}  # {SymbolOptional: number-like}
    extend_closures = {}  # {sympy.Function: string function}

    for key, value in extend.items():
        # TODO prefer lazy message building over immediately for every pair..
        # TODO better show closure value, though strings won't have a length limit and might make huge errors..
        # msg_err = f"expected mapping{{(str,NumberSymbol,Function):(callable,numeric)}}, but got {key}:{type(value)}"

        # determine if value is a single number
        if isinstance(value, (int, float, complex, numpy.number, numpy.ndarray)):
            if hasattr(value, "ndim") and value.ndim != 0:
                raise ValueError(f"extend[{key}] expected ndim==0, but has ndim=={value.ndim}")
            if hasattr(value, "dtype") and value.dtype not in DTYPES_SUPPORTED:
                raise TypeError(f"extend[{key}] unsupported dtype '{value.dtype}'")
            key = SymbolOptional(key)
            value = numpy.array(value)[()]  # TODO use data to improve resulting type
            extend_names[key] = value
            continue

        # coerce functions to embeddable strings (for now?)
        # TODO support for Expressive instances, may require Build instances [ISSUE 154]
        # TODO consider better supporting prebuilt Numba callables (generate and compare signature?)
        #   for now, this instead attempts to get the `.py_func` property from them and raises
        #   if it's not available (probably `inspect.getsource as inspect_source_text` -> `OSError`)
        #   maybe also relevant, consider `from inspect import signature as inspect_signature`
        # TODO improve any later namespace errors related to these, at least suggesting
        #   that they only use from supported imports (numpy et al.)
        #   keeping and reporting the string collection of imports might be sufficient
        # TODO consider str->lambda support, even if they're then transformed into function definitions
        if callable(value):  # try to coerce function to its full text
            if isinstance(value, numba.core.dispatcher.Dispatcher):  # only `numba.core.registry.CPUDispatcher`?
                count_signatures = len(value.signatures)  # FIXME is it possible for this to raise?
                if count_signatures >= 1:  # this is a pre-built Numba function!
                    # WARNING there may not actually be a matching signature for its later use
                    # FUTURE allow direct inclusion
                    warn(f"extend[{key}] prebuilt Numba function (.signatures={count_signatures}) will be coerced to a closure for now")
                value = value.py_func  # FIXME is this somewhat evil?
            value = inspect_source_text(value)  # can raise TypeError (builtins) or OSError (no source text)
            # continue to str path
            # NOTE that the function string may include any amount of leading spaces as-written in the code

        if isinstance(value, str):
            value = text_dedent(value)  # strips all leading spaces
            if not value.startswith("def "):
                raise ValueError(f"extend[{key}] unsable value, expected function 'def' prefix: {value[:50]}")
            name_fn = re.match(r"def ([^\(]+)\(", value).group(1)  # TODO consider AST parse (both?)
            if name_fn != key:
                # TODO consider warning and replacing instead of raising
                #   enforce naming like key as above if changing
                raise ValueError(f"extend[{key}] doesn't match function value's name '{name_fn}'")
            key = sympy.Function(key)
            extend_closures[key] = value
            continue

        raise ValueError(f"extend[{key}] expected number or function-like, but got {type(value)}")

    return extend_names, extend_closures


def dummy_symbols_split(expr, symbols):
    """ extract names that are exclusively used as dummy variables
        for example in `Sum(x, (x, 1, y))`, `x` is not needed or used from data
        and replaced by some function of `y`

        only symbols which are exclusively a dummy will be split out
    """
    dummy_symbols = {}

    # collect dummy values from `Sum()` limits
    # TODO move verification to an earlier step in Expressive.__init__()
    for sum_block in expr.atoms(sympy.Sum):
        if expr.atoms(sympy.Indexed):
            raise NotImplementedError(f"mixing indexing and Sum is not (yet) supported: {expr.atoms(sympy.Indexed)}")
        fn_sum = sum_block.function
        limits = sum_block.limits  # tuple of tuples
        # easy validity checks
        if len(limits) != 1:
            raise NotImplementedError(f"only exactly 1 Sum() limits is supported for now: {limits}")
        if fn_sum.atoms(sympy.Sum):
            raise NotImplementedError(f"nested Sum instances not yet supported: {sum_block} wraps {fn_sum}")
        # entire expr is checked for IndexedBase for now
        # if fn_sum.atoms(sympy.Indexed):  # TODO consider walrus operator and including IndexedBase
        #     raise NotImplementedError(f"indexed Sum are not yet supported: {sum_block} -> {fn_sum.atoms(sympy.Indexed)}")

        # separate and compare limit features
        dummy_var, limit_start, limit_stop = limits[0]
        if not isinstance(limit_start, (sympy.Symbol, sympy.Integer)):
            raise TypeError(f"unsupported type for limit start '{limit_start}': {type(limit_start)}")
        if not isinstance(limit_stop, (sympy.Symbol, sympy.Integer)):
            raise TypeError(f"unsupported type for limit stop '{limit_stop}': {type(limit_stop)}")
        if isinstance(limit_start, sympy.Integer) and isinstance(limit_stop, sympy.Integer):
            if limit_start > limit_stop:  # TODO consider support for negative sum range (`{Sum((_,a,b)):-Sum((_,b,a))}`?)
                raise ValueError(f"fixed Sum() limits start({limit_start}) > stop({limit_stop}) represents a zero or negative range")
            # if limit_start == limit_stop:  # FUTURE simplifier can directly convert this to fn_sum (all fixed limits?)
            #     warn(f"fixed Sum() limits start({limit_start}),stop({limit_stop}) can be eliminated")

        # keep a collection of all dummy_symbols
        # TODO can this use `dummy_symbols_split()` result? (mostly avoiding KeyError from data[dummy])
        dummy_symbols[dummy_var.name] = dummy_var

    # TODO rename dummy_symbols so it's clear they're all in some way optional to provide (or never called?)
    #   plausibly it makes sense to smooth making them optional arguments
    for name, sym in symbols.items():
        if isinstance(sym, SymbolOptional) and name not in dummy_symbols:
            dummy_symbols[name] = sym

    # remove dummy symbols from args collection
    # NOTE symbols collection is mutated here (by-ref) in addition to being returned
    for name in dummy_symbols.keys():
        try:
            del symbols[name]
        except KeyError as ex:  # pragma nocover impossible/bug path
            raise RuntimeError(f"BUG: dummy var '{name}' missing during split from symbols collection: {repr(ex)}")

    return symbols, dummy_symbols


def string_expr_cleanup(expr_string, config=None):
    """ a few rounds of basic cleanup to ease usage
        equality is transformed to Eq() form
            `LHS = RHS` -> `LHS==RHS` -> `Eq(LHS,RHS)`
    """
    # FUTURE consider if these can or should use the SymPy transformation system
    #   https://docs.sympy.org/latest/modules/parsing.html#parsing-transformations-reference
    if not isinstance(expr_string, str):
        raise ValueError("expr must be a string")

    # FUTURE allowing None makes testing a little smoother at the cost of inconsistency [ISSUE 204]
    name_mashing_multiply = (config or {}).get("translate_simplify.parse.name_mashing_multiply", "raise")

    # FUTURE consider accepting/allowing Piecewise inputs directly
    #   trivial here perhaps as `and "Piecewise" not in expr_string` in addition to <>
    #   however, additional robustness is needed especially to support additional `==`/`Eq()` instances
    #   it's also possible (though inadvisable) to hack the expr in by creating a simpler expr
    #   with the same symbol names, then clobbering instance._expr_sympy with the Piecewise
    # FUTURE also fix bad casing of Piecewise
    #   `expr_string = re.sub(r"\b[Pp]iece[Ww]ise\b", r"Piecewise", expr_string)`
    #   or more powerfully .lower() -> \bregex\b -> replace by-position (as IGNORECASE flag is not sufficient)
    if "piecewise" in expr_string.lower():
        raise ValueError("Piecewise is only supported as a result of Sum() simplification for now")
    if "<" in expr_string or ">" in expr_string:
        raise ValueError("inequality is not supported")

    # help support more inputs for modulo
    # using the name literally "mod" is allowed, but it might not behave well
    # `mod(` is safe to transform to `Mod(` as it couldn't be used as a Function prior to this
    # eventually, `Mod()` becomes `numpy.mod()` in the builder
    # this also preempts name mashing and should allow all or most cases where is a name
    #
    # internal workflow
    #   `A mod B` -> `A % B` -> `Mod(A, B)`  # %->Mod performed by SymPy
    #   `mod (A, B)`         -> `Mod(A, B)`
    #                           `Mod(A, B)` -> `numpy.mod(A, B)`  # codegen/builder
    expr_string = re.sub(r"(?<=[a-zA-Z\d]|\))\s*\bmod\b\s*(?=[a-zA-Z\d]|\()", r" % ", expr_string)
    # transform mod->Mod when it's used as a Function
    expr_string = re.sub(r"\bmod\s*\(", r"Mod(", expr_string)
    if any(re.finditer(r"\b\d*mod\b", expr_string)):  # TODO is .match or .findall somehow better?
        warn(f"using the name 'mod' as a Symbol may unexpectedly conflict with modulo `%`: {expr_string}")

    # alert user that some names will become joined, which are probably an error and/or
    # intended to be multiplication when whitespace is cleared
    #   ie. "a cos(b)" -> "acos(b)" or "2 5x" -> "25x"
    if name_mashing_multiply != "ignore":
        for match in re.finditer(r"(([a-zA-Z\d]*[a-zA-Z]+)(\s+)([a-zA-Z\d]+)|((\d)(\s+)(\d)))", expr_string):
            block_joined = f"{match.group(2)}{match.group(4)}"
            block_mul    = f"{match.group(2)}*{match.group(4)}"
            if name_mashing_multiply == "multiply":
                start, end = match.start(), match.end()
                expr_string = f"{expr_string[:start]}{block_mul}{expr_string[end:]}"
                # FUTURE consider try/except and warning about recursion depth `sys.getrecursionlimit()`
                return string_expr_cleanup(expr_string, config)
            msg = f"atoms '{match.group(1)}' will become joined '{block_joined}' did you mean '{block_mul}'?"
            if name_mashing_multiply == "warn":
                warn(
                    f"{msg} this may raise ValueError in a future version,"
                    " set CONFIG[translate_simplify.parse.name_mashing_multiply] to control this"
                )
                continue
            raise ValueError(msg)

    # discard all whitespace to ease further processing
    expr_string = re.sub(r"\s+", r"", expr_string)

    # coerce runs of "=" into exactly "=="
    # ideally only (0,1,2) exist, but let users be really excited ==== for now
    expr_string = re.sub(r"=+", "==", expr_string)
    count_equalities = expr_string.count("=") // 2
    if count_equalities == 1:
        lhs, rhs = expr_string.split("==")  # ValueError if doesn't unpack exactly
        # recurse for each half, then rejoin 'em
        lhs = string_expr_cleanup(lhs, config)
        rhs = string_expr_cleanup(rhs, config)
        return f"Eq({lhs}, {rhs})"
    elif count_equalities > 1:  # not exactly 0 or 1 (==)
        raise SyntaxError(f"only 1 equivalence (==) can be provided, but parsed {count_equalities}: {expr_string}")

    # user probably meant Pow() not bitwise XOR
    # TODO add to warning subsystem `if "^" in expr_string:`
    # TODO allow configuring this warning too [ISSUE 29]
    expr_string = expr_string.replace("^", "**")

    # multiplication cleanup blocks
    # SymPy expects symbols to be separated from Numbers for multiplication
    #   ie. "5x+7" -> "5*x+7"
    # however, care needs to be taken to avoid splitting symbols and functions
    # which contain a number, like `t3`, `log2()`, etc.

    # clean up the case where trailing names or numbers should probably be multiplied
    #   ie. "(a+b)2" -> "(a+b)*2"
    # TODO add to warning subsystem as it feels like an unusual style [ISSUE 29]
    #   and could easily be a typo like missing Pow '^' or other operator which
    #   would otherwise be silently "fixed"
    expr_string = re.sub(r"\)(\w)", r")*\1", expr_string)

    # consider matches where a number appears directly after
    #   start of string | basic operators "+-*/" | open parenthesis
    # and directly before a case where
    #   new string starts (symbol or function)
    #   new parentheses block starts "3(a+b)" -> "3*(a+b)"
    # likely this could be better tokenized by Python AST or SymPy itself
    expr_string = re.sub(r"(^|[\+\-\*\/]|\()(\d+)([a-zA-Z]|\()", r"\1\2*\3", expr_string)

    # make sure there's something left after parsing
    # at least user didn't just pass "", " ", etc., or something went badly awry above
    if not expr_string:
        raise ValueError("no content after cleanup")

    return expr_string


def get_or_create_symbol(dict_search, name, symbol_cls):
    """ helper like `dict.get(name, sym(name))` which checks matches are the expected type
        this is useful specifically to ensure passed Symbols are more specific types
            IndexedBase
            Idx
        otherwise they can't be used later
    """
    try:
        value = dict_search[name]
    except KeyError:
        return symbol_cls(name)  # directly make one from the name
    if not isinstance(value, symbol_cls):  # name in dict, but wrong type!
        raise TypeError(f"{name} should be type {symbol_cls}, but got {type(value)}")
    return value


def string_expr_indexing_offsets(expr_string, symbols):
    """ detect and manage relative offsets
        returns tuple with
         - offset values like `symbols` mapping {name:Symbol}
         - range the index can be (inclusive)
        symbols will be used if they have the same name as discovered values
        raising if the name is the same, but the Symbol type is wrong
        (refer to get_or_create_symbol)

        for example, given
            a[i+1] + b[i-1]
        this returns like
            offset_values {
                "a": IndexedBase("a")
                "b": IndexedBase("b")
                "i": Idx("i")
            }
            offset_ranges {
                Idx("i"): [-1, 1],
            }
    """
    # FUTURE handle advanced relative indexing logic [ISSUE 11]
    # FUTURE consider if multiple Idx can generate deeper loops
    offset_values = {}
    offset_ranges = {}  # spread amongst offsets as name:[min,max]
    for chunk in re.findall(r"(\w+)\[(.+?)\]", expr_string):
        base, indexing_block = chunk
        indexer = str(sympy.parse_expr(indexing_block).free_symbols.pop())
        try:  # extract the offset amount ie. x[i-1] is -1
            offset = sympy.parse_expr(indexing_block).atoms(sympy.Number).pop()
        except KeyError:
            offset = 0  # no offset like x[i]
        offset_values[base]    = get_or_create_symbol(symbols, base, sympy.IndexedBase)
        offset_values[indexer] = get_or_create_symbol(symbols, indexer, sympy.Idx)
        # now update the spread for the offset
        indexer = offset_values[indexer]  # use Idx ref directly, not name
        spread = offset_ranges.get(indexer, [0, 0])  # start fresh if missing
        spread[0] = min(spread[0], offset)
        spread[1] = max(spread[1], offset)
        offset_ranges[indexer] = spread  # creates if new

    # really make sure there is exactly zero or one indexing Symbols Idx
    if len(offset_ranges) > 1:
        raise ValueError(f"only a single Idx is supported, but got: {offset_ranges}")

    return offset_values, offset_ranges


def indexed_offsets_from_expr(expr):
    """ parse indexed offset features from a SymPy expr

        parallels `string_expr_indexing_offsets()`, though this expects
        the caller to ensure any symbols are present in expr before calling
    """
    if not isinstance(expr, (sympy.core.expr.Expr, sympy.core.relational.Equality)):
        raise RuntimeError(f"BUG: expected SymPy Expr or Equality, but got {type(expr)}")

    offset_values = {}
    offset_ranges = {}  # spread amongst offsets as name:[min,max]
    for block in expr.atoms(sympy.Indexed):
        base    = block.atoms(sympy.IndexedBase)
        indexer = block.atoms(sympy.Idx)
        if len(base) != 1:
            raise ValueError(f"multiple or nested IndexedBase: {block}")
        if len(indexer) != 1:
            raise ValueError(f"indexer must be a single Idx, but got {block}")
        base    = base.pop()  # exactly 1 value exists
        indexer = indexer.pop()
        # now calculate the offset
        offset = (block.atoms(sympy.Rational, sympy.Float) or {0})  # ideally Integer or empytset{}->{0}
        if offset != (block.atoms(sympy.Integer) or {0}):  # error for fractional indicies
            raise ValueError(f"expected a single Integer (or nothing: 0) as the offset, but parsed {block}")
        offset_values[base]    = base
        offset_values[indexer] = indexer
        offset = offset.pop()  # {N} -> N
        spread = offset_ranges.get(indexer, [0, 0])  # start fresh if missing (alt. defaultdict(lambda))
        spread[0] = min(spread[0], offset)
        spread[1] = max(spread[1], offset)
        offset_ranges[indexer] = spread  # creates entry if this is the first instance

    if len(offset_ranges) > 1:
        raise ValueError(f"only a single Idx is supported, but got: {offset_ranges}")

    return offset_values, offset_ranges


def string_expr_to_sympy(expr_string, name_result=None, symbols=None, extend_names=None, extend_closures=None):
    """ parse string to a SymPy expression
        this is largely support logic to help sympy.parse_expr()
         - support for indexing Symbols via IndexBase[Idx]
         - helps make symbol reference collections consistent before and after parsing
           ie. `reference in e.atoms(IndexedBase)` or `foo is atom` are True

        note that `parse_expr()` creates new symbols for any un-named values

        collections of Symbols are returned as dicts mapping {name:Symbol},
        even if there is only a single Symbol
        while any indexer (Idx) is returned as a mapping of
          {Idx:[low index,high index]}
        so the templated loop won't over or under-run its array indices

        FUTURE work with transformation system over regex hackery where possible
    """
    if symbols is None:
        symbols = {}
    if extend_names is None:
        extend_names = {}
    if extend_closures is None:
        extend_closures = {}

    # collection of {name:Symbol} mappings for `sympy.parse_expr()`
    local_dict = symbols.copy()  # dereference so extend values can be added

    # enable user-provided functions (NOTE these might be {})
    local_dict.update({s.name: s for s in extend_names.keys()})
    local_dict.update({s.name: s for s in extend_closures.keys()})

    # get indexing Symbols (IndexedBase, Idx) and the spread of any indexer(s)
    #   members of symbols will be used if they're the correct type, otherwise
    #   TypeError will be raised for names which exist, but are not valid for
    #   their respective types (see `get_or_create_symbol()`)
    # NOTE for now there can only be exactly 1 or 0 indexers (Idx) (for now?)
    offset_values, offset_ranges = string_expr_indexing_offsets(expr_string, symbols)

    # continue to build up symbols dict for `sympy.parse_expr()`
    local_dict.update(offset_values)

    # convert forms like `expr_rhs` into `Eq(result_lhs, expr_rhs)`
    verify_literal_result_symbol = False  # avoid NameError in later check
    if not expr_string.startswith("Eq("):
        if "=" in expr_string:
            raise RuntimeError(f"BUG: failed to handle equality during cleanup: {expr_string}")
        if name_result is None:
            verify_literal_result_symbol = True  # enable later warning path checks
            name_result = "result"
        # rewrite `expr_string` to `Eq()` form
        if offset_values:
            syms_result = get_or_create_symbol(symbols, name_result, sympy.IndexedBase)
            # FUTURE reconsider if supporting multiple indexers
            # unpack name (rather than smuggling it from the earlier loop..)
            indexer = next(iter(offset_ranges))
            expr_string = f"Eq({syms_result.name}[{indexer.name}], {expr_string})"
        else:
            syms_result = get_or_create_symbol(symbols, name_result, sympy.Symbol)
            expr_string = f"Eq({syms_result.name}, {expr_string})"
        # pack result into locals before parse
        local_dict.update({name_result: syms_result})

    expr_sympy = sympy.parse_expr(expr_string, local_dict=local_dict)

    if not expr_sympy.atoms(sympy.Eq):  # ensures (lhs,rhs) properties, alt: hasattr
        raise RuntimeError(f"BUG: didn't coerce into Eq(LHS, RHS) form: {expr_sympy}")

    # now (re-)extract the result Symbol from LHS
    # NOTE IndexedBase coerced to Symbol [ISSUE 9]
    atoms_lhs = expr_sympy.lhs.atoms(sympy.Symbol)
    # FUTURE opportunity to extract Number from LHS to fail or divide out
    if len(atoms_lhs) == 1:
        pass  # pop later, set of exactly 1 Symbol
    elif len(atoms_lhs) == 2:
        atoms_lhs = expr_sympy.lhs.atoms(sympy.IndexedBase)
        if len(atoms_lhs) != 1:
            raise ValueError(f"multiple possible result values: {atoms_lhs}")
    else:
        raise ValueError(f"multiple or no possible result values from LHS atoms:{atoms_lhs}")
    symbol_result = atoms_lhs.pop()  # now dissolve set: {x} -> x

    if name_result is not None and name_result != symbol_result.name:
        raise ValueError(f"mismatch between name_result ({name_result}) and parsed symbol name ({symbol_result.name})")

    # make dicts of {name:Symbol} for caller
    # NOTE `symbol_result` must be last to simplify dropping via slicing in later logic
    # NOTE `.atoms(Symbol)` picks up IndexedBase, but demotes them to new `Symbol` instances [ISSUE 9]

    # warn the user if they passed unused symbols
    symbols_unused = set(symbols.keys()) - {s.name for s in expr_sympy.atoms(sympy.Symbol)}
    if symbols_unused:  # should be emptyset
        warn(f"some symbols were not used: {tidy_list_str(symbols_unused)}")

    symbols = {s.name: s for s in expr_sympy.atoms(sympy.Symbol)}
    symbols.update({s.name: s for s in expr_sympy.atoms(sympy.IndexedBase)})
    symbols.pop(symbol_result.name)  # restored later as the last entry
    for indexer in offset_ranges.keys():  # expressly remove Idx name(s)
        del symbols[indexer.name]

    # force lexical ordering by-name for consistency (becomes args, etc.)
    symbols = {name: symbols[name] for name in sorted(symbols.keys())}

    # make a dict (len==1) of the result symbol
    syms_result = {symbol_result.name: symbol_result}
    # now append it to the symbols dict so it can be an argument
    symbols.update(syms_result)  # always the last symbol

    # hint that user may be misusing "result" name in their RHS
    if verify_literal_result_symbol and (
        name_result in {a.name for a in expr_sympy.rhs.atoms(sympy.Symbol)}) and (
        name_result not in offset_values.keys()
    ):
        warn("symbol 'result' in RHS refers to result array, but not indexed or passed as name_result")

    return expr_sympy, symbols, offset_ranges, syms_result


def parse_sympy_expr(expr, name_result, symbols):
    """ get a compatible set of objects for later use, mirroring `string_expr_to_sympy()`,
        but for a valid SymPy expr (may be an Expr or Equality)
            expr           SymPy expr
            symbols        {s:s.name}             sorted, no indexer, result last
            offset_ranges  {indexer:[min,max]}    indexer is Idx
            result         {result:resultsymbol}  always a dict of len 1
    """
    if symbols:  # NOTE rewritten later from expr
        symbols_unused = set(symbols.values()) - expr.atoms(sympy.Symbol, sympy.IndexedBase, sympy.Idx)
        if symbols_unused:
            raise ValueError(f"some symbols not present in expr: {symbols_unused}")

    offset_values, offset_ranges = indexed_offsets_from_expr(expr)

    if expr.atoms(sympy.Eq):  # form Eq(LHS,RHS) TODO consider `isinstance(e,Equality)` instead
        if len(expr.atoms(sympy.Eq)) != 1:
            raise ValueError(f"only a single equality can exist, but got {expr.atoms(sympy.Eq)}")
        result = (expr.lhs.atoms(sympy.IndexedBase) or expr.lhs.atoms(sympy.Symbol))
        if len(result) != 1:  # `indexed_offsets_from_expr()` ensures only a single value exists
            raise ValueError(f"BUG: expected a single result, but got {expr.lhs}")
        result = result.pop()
        if name_result is not None and result.name != name_result:
            raise ValueError(f"mismatched name between name_result({name_result}) and LHS({result})")
    else:  # form RHS -> Eq(result,RHS)
        # NOTE because all symbols exist, user can't pass "result" naively
        if name_result is None:
            name_result = "result"
            if "result" in (a.name for a in expr.atoms(sympy.Symbol, sympy.IndexedBase, sympy.Idx)):
                warn("symbol 'result' in RHS refers to result array, but not indexed or passed as name_result")
        if expr.atoms(sympy.IndexedBase):  # RHS reveals indexing
            indexer = next(iter(offset_ranges))
            result  = get_or_create_symbol(symbols, name_result, sympy.IndexedBase)
            expr    = sympy.Eq(result[indexer], expr)
        else:
            result  = get_or_create_symbol(symbols, name_result, sympy.Symbol)
            expr    = sympy.Eq(result, expr)

    symbols = {s.name: s for s in expr.atoms(sympy.Symbol)}
    symbols.update({s.name: s for s in expr.atoms(sympy.IndexedBase)})
    symbols.pop(result.name)  # restored later as the last entry
    for indexer in offset_ranges.keys():  # expressly remove Idx name(s)
        del symbols[indexer.name]

    # force lexical ordering by-name for consistency (becomes args, etc.)
    symbols = {name: symbols[name] for name in sorted(symbols.keys())}

    # make a dict (len==1) of the result symbol
    result_dict = {result.name: result}
    # now append it to the symbols dict so it can be an argument
    symbols.update(result_dict)  # always the last symbol

    return expr, symbols, offset_ranges, result_dict


def parse_inputs(expr, symbols, name_result, extend, config):
    # clean up initial symbols
    symbols = symbols_given_cleanup(expr, symbols)

    # TODO more aggressively insist it's a valid Python name
    if name_result is not None and not isinstance(name_result, str):
        raise ValueError(f"name_result must be None or a str, but got {type(name_result)}")

    # split extend into {SymbolOptional: number} and {sympy.Function: string function}
    extend_names, extend_closures = extra_functionality_parse(extend)

    if isinstance(expr, str):
        expr = string_expr_cleanup(expr, config)
        expr, symbols, indexers, results = string_expr_to_sympy(expr, name_result, symbols, extend_names, extend_closures)
    elif isinstance(expr, (sympy.core.expr.Expr, sympy.core.relational.Equality)):
        expr, symbols, indexers, results = parse_sympy_expr(expr, name_result, symbols)
        # TODO detect non-standard Functions in expr which are not in the extend collections?
        #   maybe `.free_symbols` can help?
    else:
        raise ValueError(f"unexpected expr type({type(expr)}), must be str or SymPy Expr")

    # take any dummy symbols out of collection as they're not required in data
    symbols, symbols_dummy = dummy_symbols_split(expr, symbols)

    return expr, symbols, indexers, results, symbols_dummy, extend_names, extend_closures


def parse_parallel_model(parallel_model=None):
    # TODO should this be merged with instance config? probably yes

    # keep defaults (subject to change, likely warning for non-None)
    if parallel_model is None:
        return {}

    # expressly disable all parallization
    # won't lose errors in Numba threads and slightly-shorter build times
    if parallel_model == "disabled":
        return {
            "builder.parallel_model.numba_parallel":    False,
            "builder.parallel_model.allow_prange":      False,
            "builder.parallel_model.native_threadpool": False,
        }

    if parallel_model == "prange":
        return {
            "builder.parallel_model.numba_parallel": True,
            "builder.parallel_model.allow_prange":   True,
        }

    if parallel_model == "native_threadpool":
        return {
            "builder.parallel_model.numba_parallel":    False,
            "builder.parallel_model.allow_prange":      False,
            "builder.parallel_model.native_threadpool": True,
        }

    raise ValueError(f"parallel_model must be one of (None,'disabled','prange'), but got '{parallel_model}'")
