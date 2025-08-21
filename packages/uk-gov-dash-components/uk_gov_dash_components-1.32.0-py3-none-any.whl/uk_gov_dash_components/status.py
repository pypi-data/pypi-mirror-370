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


class status(Component):
    """A status component.
Display ststus

@export
@class Status
@extends {Component}

Keyword arguments:

- id (string; optional):
    The ID used to identify this component in Dash callbacks.

- length (number; optional):
    length.

- minQueryLength (number; optional):
    min Query Length.

- queryLength (number; optional):
    Query Length.

- selectedOption (boolean | number | string | dict | list; optional):
    Selected option.

- selectedOptionIndex (number; optional):
    Selected Option Index."""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'uk_gov_dash_components'
    _type = 'status'


    def __init__(
        self,
        id: typing.Optional[typing.Union[str, dict]] = None,
        length: typing.Optional[NumberType] = None,
        minQueryLength: typing.Optional[NumberType] = None,
        queryLength: typing.Optional[NumberType] = None,
        selectedOption: typing.Optional[typing.Any] = None,
        selectedOptionIndex: typing.Optional[NumberType] = None,
        tQueryTooShort: typing.Optional[typing.Any] = None,
        tNoResults: typing.Optional[typing.Any] = None,
        tSelectedOption: typing.Optional[typing.Any] = None,
        tResults: typing.Optional[typing.Any] = None,
        **kwargs
    ):
        self._prop_names = ['id', 'length', 'minQueryLength', 'queryLength', 'selectedOption', 'selectedOptionIndex']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'length', 'minQueryLength', 'queryLength', 'selectedOption', 'selectedOptionIndex']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args}

        super(status, self).__init__(**args)

setattr(status, "__init__", _explicitize_args(status.__init__))
