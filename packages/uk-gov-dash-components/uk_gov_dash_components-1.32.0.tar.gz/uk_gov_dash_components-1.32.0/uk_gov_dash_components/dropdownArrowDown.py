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


class dropdownArrowDown(Component):
    """A dropdownArrowDown component.
Default dropdown arrow

@param {string} { className }

Keyword arguments:

- className (string; optional):
    Class name to add to SVG."""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'uk_gov_dash_components'
    _type = 'dropdownArrowDown'


    def __init__(
        self,
        className: typing.Optional[str] = None,
        **kwargs
    ):
        self._prop_names = ['className']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['className']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args}

        super(dropdownArrowDown, self).__init__(**args)

setattr(dropdownArrowDown, "__init__", _explicitize_args(dropdownArrowDown.__init__))
