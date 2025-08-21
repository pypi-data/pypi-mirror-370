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


class ExpandableMenuItem(Component):
    """An ExpandableMenuItem component.
Lazy loaded ExpandableMenuItem

@param {
	id,
 title,
 collapsedByDefault,
 children,
 expandedClass,
 collapsedClass,
 ariaLabel,
 subMenuClass,
 titleClass,
} [props={}]
@return {*}

Keyword arguments:

- children (list of a list of or a singular dash component, string or numbers | a list of or a singular dash component, string or number; optional):
    An array of li HTML elements that will displayed on click or a
    single html element.

- id (string; optional):
    The ID of this component, used to identify dash components in
    callbacks. The ID needs to be unique across all of the components
    in an app.

- ariaLabel (string; optional):
    Accessible text to describe the expandable menu element, attached
    to Li element that wraps the children.

- collapsedByDefault (boolean; default True):
    Default behaviour of whether or not the sub-menu is collapsed on
    load.

- collapsedClass (string; optional):
    CSS class that will be applied when the menu is collapsed.

- expandedClass (string; optional):
    CSS class that will be applied when the menu is expanded.

- subMenuClass (string; optional):
    CSS class that will be applied to the sub nav menu.

- title (string; optional):
    The clickable text to display sub-menu.

- titleClass (string; optional):
    CSS class that will be applied to the title of the sub nav menu."""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'uk_gov_dash_components'
    _type = 'ExpandableMenuItem'


    def __init__(
        self,
        children: typing.Optional[ComponentType] = None,
        id: typing.Optional[typing.Union[str, dict]] = None,
        title: typing.Optional[str] = None,
        collapsedByDefault: typing.Optional[bool] = None,
        expandedClass: typing.Optional[str] = None,
        collapsedClass: typing.Optional[str] = None,
        ariaLabel: typing.Optional[str] = None,
        subMenuClass: typing.Optional[str] = None,
        titleClass: typing.Optional[str] = None,
        **kwargs
    ):
        self._prop_names = ['children', 'id', 'ariaLabel', 'collapsedByDefault', 'collapsedClass', 'expandedClass', 'subMenuClass', 'title', 'titleClass']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['children', 'id', 'ariaLabel', 'collapsedByDefault', 'collapsedClass', 'expandedClass', 'subMenuClass', 'title', 'titleClass']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}

        super(ExpandableMenuItem, self).__init__(children=children, **args)

setattr(ExpandableMenuItem, "__init__", _explicitize_args(ExpandableMenuItem.__init__))
