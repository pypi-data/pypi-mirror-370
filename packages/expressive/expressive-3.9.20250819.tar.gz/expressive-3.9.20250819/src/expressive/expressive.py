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

import time
from copy import deepcopy
from collections import UserDict

from .analyze import verify_cmp
from .codegen import (
    do_compile,
    loop_function_template_builder,
    signature_generate,
)
from .config import CONFIG
from .data import (
    data_cleanup,
    get_result_dtype,
    verify_indexed_data_vs_symbols,
)
from .messaging import warn, html_display, tidy_list_str
from .parallel import parallel_runner
from .parsers import (
    parse_inputs,
    parse_parallel_model,
)
from .version import version as __version__  # noqa F401


class Expressive:

    def __init__(
        self,
        expr,
        name_result=None,
        symbols=None,
        *,
        config=None,
        extend=None,
        allow_autobuild=None,
        parallel_model=None,
    ):
        # determine parallelization model
        parallel_model = parse_parallel_model(parallel_model)

        # construct local config
        self._config = deepcopy(CONFIG)
        if config is not None:  # NOTE `UserDict.update()` passes most iterables like `""`
            if not isinstance(config, (dict, UserDict)):
                raise TypeError(f"config must be a dict-like, but got {type(config)}")
            self._config.update(config)
        self._config.update(parallel_model)  # always compute parallel mode
        if allow_autobuild is not None:
            self._config["builder.autobuild.allow_autobuild"] = allow_autobuild

        # FUTURE make cleanup optional (arg or config)
        (
            self._expr_sympy,
            self._symbols,
            self._indexers,
            self._results,
            self._symbols_dummy,
            self._extend_names,
            self._extend_closures,
        ) = parse_inputs(expr, symbols, name_result, extend, self._config)

        # set up some needed collections
        # self._verifications = {}  # FIXME unstable contents for now
        self.signatures_mapper = {}

    def __str__(self):
        # NOTE unstable result for now
        return f"{type(self).__name__}({self._expr_sympy})"

    def __repr__(self):
        # NOTE unstable result for now
        # FUTURE display some major config settings (but most in a dedicated output)
        # FUTURE consider how to support or use `sympy.srepr()`
        allow_autobuild = self._config["builder.autobuild.allow_autobuild"]
        content = [
            f"build_signatures={len(self.signatures_mapper)}",
            f"allow_autobuild={allow_autobuild}",
        ]
        return f"{str(self)} <{','.join(content)}>"

    def _repr_html_(self):
        """ dedicated Jupyter/IPython notebook pretty printer method
            this is loaded into an iframe, so mathjax is dynamically acquired too
            in order to render the LaTeX output from SymPy
            returns a complete html block or 1-liner string (for error)
        """
        # FUTURE consider display with intermediate template views from builder [ISSUE 152]
        return html_display(
            expr=self._expr_sympy,
            string_repr=repr(self),
        )

    def _prepare(self, data, dtype_result):
        """ prepare before build or __call__ """
        data = data_cleanup(data)
        dtype_result = get_result_dtype(self._expr_sympy, self._results, data, dtype_result)
        signature, result_passed = signature_generate(self._symbols, self._results, data, dtype_result, self._config)
        if self._indexers:  # when indexed, the data shape (array vs single values) matter much more
            verify_indexed_data_vs_symbols(self._symbols, result_passed, data)

        return data, dtype_result, signature, result_passed

    def build(self, data, *, dtype_result=None, verify=None):  # arch target?
        """ compile function and collect it in signatures_mapper """
        dtype_result_pre = dtype_result  # keep a reference to hint about small types if error
        data, dtype_result, signature, result_passed = self._prepare(data, dtype_result)

        if self._config["builder.parallel_model.native_threadpool"]:
            parallel_runner.start()  # begins threadpool (idempotent)

        # automatically set to verify when the array is small
        # only happens for pre-builds as __call__ sets `verify=False` when autobuilding
        if verify is None:
            if self._extend_names or self._extend_closures:  # FIXME interrupts verify for now (keep ref in dict/object?)
                verify = False
            else:
                # approximate max array length (ignores offsets)
                lengths_max = max((len(ref) if ref.ndim == 1 else 1) for ref in data.values())
                if lengths_max <= 50:  # FIXME magic numbers to config subsystem [ISSUE 29]
                    verify = True

        # generate Python function
        T_inner, T_outer, expr_namespace = loop_function_template_builder(
            self._expr_sympy,
            self._symbols,
            self._indexers,
            self._results,
            result_passed,
            dtype_result,
            data,
            self._config,  # FUTURE improve argument ordering
            self._extend_names,
            self._extend_closures,
        )

        fn_outer, fn_py = do_compile(
            self._config,
            signature,
            T_inner,
            T_outer,
            expr_namespace,
            dtype_result_pre,
        )

        if verify:
            result, results = verify_cmp(data, self._expr_sympy, fn_py, fn_outer, self._indexers)
            # self._verifications[signature] = result, results  # unstable contents for now

        self.signatures_mapper[signature] = fn_outer

        # FUTURE does it make sense to return the result(s) from verify?
        #   return self, {"py": result_py, "nb": result_nb, "sp": result_sp}
        # no: probably better to make the result(s) a new property
        return self  # enable dot chaining

    def __call__(self, data, dtype_result=None):
        """ call the relevant compiled function for a particular data collection on it
            if signatures_mapper doesn't have the signature, allow_autobuild can be used
            to create it dynamically, though this loses a lot of the runtime execution speed
            benefits available to users who are able to pre-build for all the data
            signatures they have
        """
        data, dtype_result, signature, result_passed = self._prepare(data, dtype_result)

        try:
            fn = self.signatures_mapper[signature]
        except KeyError as ex:
            if not self._config["builder.autobuild.allow_autobuild"]:
                raise KeyError(f"no matching signature for data: use .build() with representative sample data (or set allow_autobuild=True): {repr(ex)}")
            # FUTURE consider adding autobuild callback for any additional caller housekeeping
            if self._config["builder.autobuild.usage_warn_nag"]:
                time_start = time.process_time()
            self.build(data, dtype_result=dtype_result, verify=False)
            if self._config["builder.autobuild.usage_warn_nag"]:
                time_build = time.process_time() - time_start
                warn(f"autobuild took {time_build:.2f}s of process time, prefer .build(sample_data) in advance if possible")
            try:
                fn = self.signatures_mapper[signature]
            except KeyError:  # pragma nocover - bug path
                raise RuntimeError(f"BUG: failed to match signature after autobuild {len(self.signatures_mapper)} signatures")

        if self._config["builder.parallel_model.native_threadpool"]:
            return parallel_runner.parallelize(self, fn, data, dtype_result, result_passed)

        try:
            return fn(**data)
        except TypeError as ex:
            if "got an unexpected keyword argument" not in str(ex):
                raise ex
            _data = {name: ref for name, ref in data.items() if name in self._symbols}
            if result_passed:
                name_result = next(iter(self._results))
                try:
                    _data[name_result] = data[name_result]
                except KeyError:  # pragma nocover - bug path
                    raise RuntimeError(
                        f"BUG: impossible code path, result array '{name_result}' missing from data"
                        f" something is very wrong with _prepare(), data_cleanup(), or the data object {type(data)}"
                    )
            if self._config["data.runtime.unused_data_callback"] != "ignore":
                _unused_data_names = set(data.keys()) - set(_data.keys())
                msg_err = f"some passed data was not used {tidy_list_str(_unused_data_names)}"
                if self._config["data.runtime.unused_data_callback"] == "raise":
                    raise TypeError(f"{msg_err}: {repr(ex)}")
                warn(f"{msg_err}, set data.runtime.unused_data_callback to modify behavior")
            return fn(**_data)
