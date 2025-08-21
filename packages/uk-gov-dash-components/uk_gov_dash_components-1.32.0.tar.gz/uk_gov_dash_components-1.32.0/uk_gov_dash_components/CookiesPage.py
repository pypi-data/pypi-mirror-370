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


class CookiesPage(Component):
    """A CookiesPage component.
Lazy loaded CookiesPage

This CookiesPage component tells users about the cookies you’re setting on their device and lets
them accept or reject different types of non-essential cookies.

@param {
id: string,                            // Unique identifier for the cookie component
tag: string                            // Google Analytics tag string
appTitle: string                       // Name of the app
previousPage: string                   // The path to the previous page                   
} [props={}]
@return {*}

Keyword arguments:

- id (string; optional):
    The ID of this component, used to identify dash components in
    callbacks. The ID needs to be unique across all of the components
    in an app.

- appTitle (string; optional):
    The name of the app to be referenced in CookiesPage.

- domain (string; optional):
    The domain of the app to be referenced in the cookies, needed for
    deletion of cookies.

- previousPage (string; optional):
    The path to the previous page, which is used in success banner on
    CookiesPage when cookies accepted/rejected.

- tag (string; optional):
    The Google Analytics tag."""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'uk_gov_dash_components'
    _type = 'CookiesPage'


    def __init__(
        self,
        id: typing.Optional[typing.Union[str, dict]] = None,
        tag: typing.Optional[str] = None,
        appTitle: typing.Optional[str] = None,
        previousPage: typing.Optional[str] = None,
        domain: typing.Optional[str] = None,
        **kwargs
    ):
        self._prop_names = ['id', 'appTitle', 'domain', 'previousPage', 'tag']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'appTitle', 'domain', 'previousPage', 'tag']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args}

        super(CookiesPage, self).__init__(**args)

setattr(CookiesPage, "__init__", _explicitize_args(CookiesPage.__init__))
