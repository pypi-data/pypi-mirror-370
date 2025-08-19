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
import warnings
from html import escape as html_escape
from textwrap import dedent as text_dedent


# helpers for warnings
class ExpressiveWarning(RuntimeWarning):
    pass


def warn(msg):
    warnings.warn(msg, ExpressiveWarning)


def tidy_list_str(collection, stringify=None, *, maxlen=5, minwidth=2):
    """ helper for tidying up long collections to display """
    if stringify is None:
        stringify = lambda a: a if isinstance(a, str) else repr(a)  # noqa E731
    if not isinstance(collection, list):
        try:
            collection = sorted(collection)  # coerce to list
        except Exception as ex:
            raise TypeError(f"couldn't coerce collection to list ({type(collection)}) via sorted: {repr(ex)}")
    if len(collection) > maxlen and maxlen > (minwidth * 2):  # setting minwidth is not recommended
        head = ",".join(map(stringify, collection[:maxlen - minwidth]))
        tail = ",".join(map(stringify, collection[-minwidth:]))
        return f"[{head} .. {tail}]"
    return f"[{','.join(map(stringify, collection))}]"


def html_display(expr, string_repr):
    """ dedicated Jupyter/IPython notebook pretty printer method
        this is loaded into an iframe, so mathjax is dynamically acquired too
     in order to render the LaTeX output from SymPy
    """
    # NOTE unstable result for now

    expr_latex = expr._repr_latex_()

    # ensure expr can be displayed properly
    # output wrapped by $$ is the normal output, however, it causes the result to be centered
    # instead, \(expr\) form is preferred which makes the result "inline" and aligned as parent
    expr_latex = re.sub(r"^\$\$?([^\$]+)\$\$?$", r"\(\1\)", expr_latex)
    if not (expr_latex.startswith(r"\(") and expr_latex.endswith(r"\)") and len(expr_latex) >= 5):
        # TODO this should probably be an Exception
        warn(rf"unexpected expr format (should be wrapped in $ -> \(\)): {expr_latex}")
        return string_repr

    # TODO improved templating (though I want to keep deps low)
    #   consider some template engine when available
    # generated as-suggested on mozilla https://developer.mozilla.org/en-US/docs/Web/Security/Subresource_Integrity
    #   `cat src/tex-chtml.js | openssl dgst -sha384 -binary | openssl base64 -A`
    # https://github.com/mathjax/MathJax 3.2.2@227c4fecc0037cef1866d03c64c3af10b685916d
    # see also https://github.com/mathjax/MathJax-src
    # TODO get values from config
    # TODO backend options
    #  - local (embed JS string)
    #  - jsdelivr CDN (suggested and current)
    #  - custom (easily allow orgs to use their own CDN or a completely custom renderer)
    template = """
    <!DOCTYPE html>
    <html>
    <head>
    <script type="text/javascript" id="MathJax-script"
        src="https://cdn.jsdelivr.net/npm/mathjax@3.2.2/es5/tex-chtml.js"
        integrity="sha348-AHAnt9ZhGeHIrydA1Kp1L7FN+2UosbF7RQg6C+9Is/a7kDpQ1684C2iH2VWil6r4"
        crossorigin="anonymous"></script>
    </head>
    <body>
    <ul style="list-style-type:none;padding-left:0;">
    {html_list}
    </ul>
    </body>
    </html>
    """

    # stack entries in unordered list
    collected_values = [
        expr_latex,   # advanced representation
        string_repr,  # FIXME unstable
    ]
    html_list = "\n    ".join(f"<li>{html_escape(a)}</li>" for a in collected_values)

    # fill template
    content = text_dedent(template.format(
        html_list=html_list,
    ))

    return content
