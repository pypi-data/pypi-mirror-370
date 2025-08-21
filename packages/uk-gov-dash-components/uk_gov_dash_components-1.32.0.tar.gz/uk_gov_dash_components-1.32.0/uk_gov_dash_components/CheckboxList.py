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


class CheckboxList(Component):
    """A CheckboxList component.
Lazy loaded CheckboxList

@param {
	id,
	options,
	value,
} [props={}]
@return {*}

Keyword arguments:

- id (string; optional):
    The ID of this component, used to identify dash components in
    callbacks. The ID needs to be unique across all of the components
    in an app.

- options (list of dicts; optional):
    An array of options.

    `options` is a list of string | number | booleans | dict | list of
    dicts with keys:

    - label (a list of or a singular dash component, string or number; required):
        The option's label.

    - value (string | number | boolean; required):
        The value of the option. This value corresponds to the items
        specified in the `value` property.

    - disabled (boolean; optional):
        If True, this option is disabled and cannot be selected.

    - title (string; optional):
        The HTML 'title' attribute for the option. Allows for
        information on hover. For more information on this attribute,
        see
        https://developer.mozilla.org/en-US/docs/Web/HTML/Global_attributes/title.

- value (list of string | number | booleans; optional):
    The currently selected value."""
    _children_props = ['options[].label']
    _base_nodes = ['children']
    _namespace = 'uk_gov_dash_components'
    _type = 'CheckboxList'
    Options = TypedDict(
        "Options",
            {
            "label": ComponentType,
            "value": typing.Union[str, NumberType, bool],
            "disabled": NotRequired[bool],
            "title": NotRequired[str]
        }
    )


    def __init__(
        self,
        options: typing.Optional[typing.Union[typing.Sequence[typing.Union[str, NumberType, bool]], dict, typing.Sequence["Options"]]] = None,
        value: typing.Optional[typing.Sequence[typing.Union[str, NumberType, bool]]] = None,
        id: typing.Optional[typing.Union[str, dict]] = None,
        **kwargs
    ):
        self._prop_names = ['id', 'options', 'value']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'options', 'value']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args}

        super(CheckboxList, self).__init__(**args)

setattr(CheckboxList, "__init__", _explicitize_args(CheckboxList.__init__))
