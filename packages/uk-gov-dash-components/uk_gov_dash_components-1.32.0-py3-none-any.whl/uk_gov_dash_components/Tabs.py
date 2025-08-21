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


class Tabs(Component):
    """A Tabs component.
Lazy loaded Tabs

@param {
	id,
 tabHeadings,
 defaultTab,
 children,
} [props={}]
@return {*}

Keyword arguments:

- children (list of a list of or a singular dash component, string or numbers; optional):
    Array of tab children.

- id (string; optional):
    The ID of this component, used to identify dash components in
    callbacks. The ID needs to be unique across all of the components
    in an app.

- defaultTab (number; optional):
    The default active tab.

- tabHeadings (list of strings; optional):
    Array of accordion headings."""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'uk_gov_dash_components'
    _type = 'Tabs'


    def __init__(
        self,
        children: typing.Optional[ComponentType] = None,
        id: typing.Optional[typing.Union[str, dict]] = None,
        tabHeadings: typing.Optional[typing.Sequence[str]] = None,
        defaultTab: typing.Optional[NumberType] = None,
        **kwargs
    ):
        self._prop_names = ['children', 'id', 'defaultTab', 'tabHeadings']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['children', 'id', 'defaultTab', 'tabHeadings']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}

        super(Tabs, self).__init__(children=children, **args)

setattr(Tabs, "__init__", _explicitize_args(Tabs.__init__))
