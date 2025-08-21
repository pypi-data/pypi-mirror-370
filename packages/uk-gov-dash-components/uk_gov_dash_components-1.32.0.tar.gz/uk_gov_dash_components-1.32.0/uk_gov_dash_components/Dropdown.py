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


class Dropdown(Component):
    """A Dropdown component.
@param {{
	label: string,
	labelStyle,
	id,
	autoselect,
	cssNamespace,
	value,
	minLength,
	name,
	placeholder,
	onConfirm,
	confirmOnBlur,
	showNoOptionsFound,
	required,
	tNoResults,
	tAssistiveHint,
	source,
	templates,
	dropdownArrow: dropdownArrowFactory,
	tStatusQueryTooShort,
	tStatusNoResults,
	tStatusSelectedOption,
	tStatusResults,
 errorMessage,
 errorMessageWhenEmpty,
 menu_open,
}} [props={}]

@return {*}

Keyword arguments:

- id (string; optional):
    The ID used to identify this component in Dash callbacks.

- autoselect (boolean; optional):
    Should auto select.

- confirmOnBlur (boolean; optional):
    No Description.

- cssNamespace (string; optional):
    cssNamespace.

- dropdownArrow (boolean | number | string | dict | list; optional):
    React component for dropdown arrow.

- errorMessage (string; optional):
    Error message to display when invalid input entered in dropdown.

- errorMessageWhenEmpty (boolean; optional):
    Whether to display error message when query is empty in dropdown.

- label (string; optional):
    Label text.

- labelStyle (boolean | number | string | dict | list; optional):
    Override the css style of the dropdown label text.

- menu_open (boolean; optional):
    Whether the dropdown menu is open. Used to fire a callback   when
    the menu is opened.

- minLength (number; optional):
    No Description.

- name (string; optional):
    No Description.

- placeholder (string; optional):
    No Description.

- required (boolean; optional):
    No Description.

- selectElement (boolean | number | string | dict | list; optional):
    Accessible element.

- showNoOptionsFound (boolean; optional):
    No Description.

- source (boolean | number | string | dict | list; optional):
    No Description.

- tStatusNoResults (boolean | number | string | dict | list; optional):
    No Description.

- tStatusResults (boolean | number | string | dict | list; optional):
    No Description.

- templates (boolean | number | string | dict | list; optional):
    No Description.

- value (string; optional):
    The value displayed in the input.

- wrapperRef (boolean | number | string | dict | list; optional):
    wrapperRef."""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'uk_gov_dash_components'
    _type = 'Dropdown'


    def __init__(
        self,
        id: typing.Optional[typing.Union[str, dict]] = None,
        label: typing.Optional[str] = None,
        labelStyle: typing.Optional[typing.Any] = None,
        autoselect: typing.Optional[bool] = None,
        cssNamespace: typing.Optional[str] = None,
        minLength: typing.Optional[NumberType] = None,
        name: typing.Optional[str] = None,
        placeholder: typing.Optional[str] = None,
        onConfirm: typing.Optional[typing.Any] = None,
        confirmOnBlur: typing.Optional[bool] = None,
        showNoOptionsFound: typing.Optional[bool] = None,
        required: typing.Optional[bool] = None,
        tNoResults: typing.Optional[typing.Any] = None,
        tAssistiveHint: typing.Optional[typing.Any] = None,
        source: typing.Optional[typing.Any] = None,
        templates: typing.Optional[typing.Any] = None,
        tStatusQueryTooShort: typing.Optional[typing.Any] = None,
        tStatusNoResults: typing.Optional[typing.Any] = None,
        tStatusSelectedOption: typing.Optional[typing.Any] = None,
        tStatusResults: typing.Optional[typing.Any] = None,
        dropdownArrow: typing.Optional[typing.Any] = None,
        selectElement: typing.Optional[typing.Any] = None,
        value: typing.Optional[str] = None,
        wrapperRef: typing.Optional[typing.Any] = None,
        style: typing.Optional[typing.Any] = None,
        errorMessage: typing.Optional[str] = None,
        errorMessageWhenEmpty: typing.Optional[bool] = None,
        menu_open: typing.Optional[bool] = None,
        **kwargs
    ):
        self._prop_names = ['id', 'autoselect', 'confirmOnBlur', 'cssNamespace', 'dropdownArrow', 'errorMessage', 'errorMessageWhenEmpty', 'label', 'labelStyle', 'menu_open', 'minLength', 'name', 'placeholder', 'required', 'selectElement', 'showNoOptionsFound', 'source', 'style', 'tStatusNoResults', 'tStatusResults', 'templates', 'value', 'wrapperRef']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'autoselect', 'confirmOnBlur', 'cssNamespace', 'dropdownArrow', 'errorMessage', 'errorMessageWhenEmpty', 'label', 'labelStyle', 'menu_open', 'minLength', 'name', 'placeholder', 'required', 'selectElement', 'showNoOptionsFound', 'source', 'style', 'tStatusNoResults', 'tStatusResults', 'templates', 'value', 'wrapperRef']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args}

        super(Dropdown, self).__init__(**args)

setattr(Dropdown, "__init__", _explicitize_args(Dropdown.__init__))
