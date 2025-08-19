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

from .messaging import tidy_list_str
from .unset import UNSET


def schema_collection_f(collection):
    """ returns a function which accepts value and checks if it's a member of a collection

        pedantically forces bools and 1,0 to be different values
            >>> isinstance(True, int)
            True
            >>> 1.0 in [1,0]
            True
            >>> 0 in {True, False}
            True
        as it's possible to get this condition without knowing when hashing, this also rejects any
        bools or numbers in sets as they could contain True,False literal
            >>> {False, 1, True, 0}
            {False, 1}
            >>> {False, True, 0, 1}
            {False, True}
            >>> {0, 1, True, False}
            {0, 1}
    """
    collection_has_UNSET    = False
    collection_has_0        = False
    collection_has_1        = False
    collection_has_True     = False
    collection_has_False    = False
    collection_has_numerics = False

    for item in collection:
        if item is None:
            continue
        if item is UNSET:  # avoid comparison by ==, which the object rejects
            collection_has_UNSET = True
            continue
        if item is True:
            collection_has_True = True
            continue
        if item is False:
            collection_has_False = True
            continue
        if isinstance(item, (int, float)):  # NOTE complex 1,0 also match, so it's rejected next
            collection_has_numerics = True
            if item == 1:
                collection_has_1 = True
            elif item == 0:
                collection_has_0 = True
            continue  # accept all other numbers too!
        if not isinstance(item, str):
            raise TypeError(f"collection can only contain UNSET,None,bool,int,float,str but got '{type(item)}': {repr(item)}")

    if isinstance(collection, (set, frozenset)):
        if collection_has_True or collection_has_False or collection_has_numerics:
            raise TypeError(
                "True and False literals or numbers in sets are expressly rejected"
                " as (True,False) hash the same as (1,0), consider passing a list or using schema_bool or schema_number_f"
            )
    elif not isinstance(collection, (list, tuple)):
        raise TypeError(f"collection must be a list, tuple, or set, but got {type(collection)}: {tidy_list_str(collection)}")

    def schema_collection_inner(value):
        # FIXME don't repeat error and generate it instead
        # never compare UNSET with ==, which the object rejects
        if value is UNSET:
            if collection_has_UNSET:
                return value
            raise ValueError(f"value must be one of [{','.join(repr(a) for a in collection)}], but got '{repr(value)}'")
        # trap True and False before comparing with 1,0 as they're `==` equal
        if value is True:
            if collection_has_True:
                return value
            raise ValueError(f"value must be one of [{','.join(repr(a) for a in collection)}], but got '{repr(value)}'")
        if value is False:
            if collection_has_False:
                return value
            raise ValueError(f"value must be one of [{','.join(repr(a) for a in collection)}], but got '{repr(value)}'")
        # FUTURE consider splitting int and float too
        # trap 1,0 before comparing with `in`, which will match in True,False
        if value == 1:
            if collection_has_1:
                return value
            raise ValueError(f"value must be one of [{','.join(repr(a) for a in collection)}], but got '{repr(value)}'")
        if value == 0:
            if collection_has_0:
                return value
            raise ValueError(f"value must be one of [{','.join(repr(a) for a in collection)}], but got '{repr(value)}'")
        if value in collection:
            return value
        # don't use `tidy_list_str()` as all keys are relevant
        raise ValueError(f"value must be one of [{','.join(repr(a) for a in collection)}], but got '{repr(value)}'")

    return schema_collection_inner


def schema_number_f(callback=int, limits=None, accept_None=False, accept_UNSET=False):
    # FUTURE consider some checks on callback and limits

    def schema_number_inner(value):
        if value is None:
            if accept_None:
                return value
            raise ValueError(f"expected value, but got {value}")
        if value is UNSET:
            if accept_UNSET:
                return value
            raise ValueError(f"expected value, but got {value}")
        value = callback(value)  # can coerce strings
        # TODO consider allowing a range object as limits, but fail for step setting
        #   though beware that `X in range()` only supports exact integer members
        if limits is not None and (value < limits[0] or value > limits[1]):
            # TODO further enforce limits properties (tuple of len=2 of int,float)
            raise ValueError(f"value must be within {limits}, but got '{value}'")
        return value

    return schema_number_inner


def schema_bool(value):
    # TODO consider coercing some strings
    # if isinstance(value, str):
    #     value = value.lower()
    #     if value == "true":
    #         value = True
    #     if value == "false":
    #         value = False
    if value is False:  # avoid coercing (1,0)
        return False
    if value is True:
        return True
    raise ValueError(f"value must be True or False literal, but got '{type(value)}': {repr(value)}")
