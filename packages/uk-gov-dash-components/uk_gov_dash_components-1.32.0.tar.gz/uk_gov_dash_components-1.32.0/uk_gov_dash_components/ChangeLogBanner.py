# AUTO GENERATED FILE - DO NOT EDIT

import typing  # noqa: F401
from typing_extensions import TypedDict, NotRequired, Literal # noqa: F401
from dash.development.base_component import Component, _explicitize_args

ComponentType = typing.Union[
    str,
    int,
    float,
    Component,
    None,
    typing.Sequence[typing.Union[str, int, float, Component, None]],
]

NumberType = typing.Union[
    typing.SupportsFloat, typing.SupportsInt, typing.SupportsComplex
]


class ChangeLogBanner(Component):
    """A ChangeLogBanner component.


Keyword arguments:

- updates (list of dicts; optional):
    Array of dictionaries representing changelog updates.

    `updates` is a list of dicts with keys:

    - type (string; required)

    - date (string; optional)

    - heading (string; required)

    - link (string; optional)

    - linkTitle (string; optional)"""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'uk_gov_dash_components'
    _type = 'ChangeLogBanner'
    Updates = TypedDict(
        "Updates",
            {
            "type": str,
            "date": NotRequired[str],
            "heading": str,
            "link": NotRequired[str],
            "linkTitle": NotRequired[str]
        }
    )


    def __init__(
        self,
        updates: typing.Optional[typing.Sequence["Updates"]] = None,
        **kwargs
    ):
        self._prop_names = ['updates']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['updates']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args}

        super(ChangeLogBanner, self).__init__(**args)

setattr(ChangeLogBanner, "__init__", _explicitize_args(ChangeLogBanner.__init__))
