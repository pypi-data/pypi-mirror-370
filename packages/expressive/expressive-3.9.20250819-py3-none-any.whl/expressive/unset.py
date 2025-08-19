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


class UNSET:

    def __repr__(self):
        return "UNSET"

    def __deepcopy__(self, memo):
        # help maintain singleton as deepcopy will return the same object for `is` equality
        return self

    def __eq__(self, other):
        raise TypeError("compare instances with is, not ==")


# somewhat-dirty clobber name to help prevent new instances from accidentally being created
# NOTE new instances can still be created via `type(UNSET)()`
UNSET = UNSET()
