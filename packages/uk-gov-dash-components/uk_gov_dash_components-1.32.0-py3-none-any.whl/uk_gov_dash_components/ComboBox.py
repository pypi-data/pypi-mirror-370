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


class ComboBox(Component):
    """A ComboBox component.


Keyword arguments:

- id (string; optional):
    The ID used to identify this component in Dash callbacks.

- allowsCustomValue (boolean; optional)

- defaultInputValue (string; optional)

- defaultItems (boolean | number | string | dict | list; optional)

- items (list | list; optional)

- label (string; optional)

- menuTrigger (string; optional)

- selectedKey (string | number; optional)"""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'uk_gov_dash_components'
    _type = 'ComboBox'


    def __init__(
        self,
        id: typing.Optional[typing.Union[str, dict]] = None,
        label: typing.Optional[str] = None,
        defaultInputValue: typing.Optional[str] = None,
        defaultItems: typing.Optional[typing.Any] = None,
        items: typing.Optional[typing.Union[typing.Sequence[typing.Any]]] = None,
        onSelectionChange: typing.Optional[typing.Any] = None,
        allowsCustomValue: typing.Optional[bool] = None,
        onInputChange: typing.Optional[typing.Any] = None,
        selectedKey: typing.Optional[typing.Union[str, NumberType]] = None,
        menuTrigger: typing.Optional[str] = None,
        **kwargs
    ):
        self._prop_names = ['id', 'allowsCustomValue', 'defaultInputValue', 'defaultItems', 'items', 'label', 'menuTrigger', 'selectedKey']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'allowsCustomValue', 'defaultInputValue', 'defaultItems', 'items', 'label', 'menuTrigger', 'selectedKey']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args}

        super(ComboBox, self).__init__(**args)

setattr(ComboBox, "__init__", _explicitize_args(ComboBox.__init__))
