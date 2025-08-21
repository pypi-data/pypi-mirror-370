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


class AdditionalDetails(Component):
    """An AdditionalDetails component.


Keyword arguments:

- id (string; required):
    Id of component.

- detailsText (string; default "Add details text"):
    Detailed text to be shown when expanded.

- hidden (boolean; default False):
    Whether the component renders or not.

- summaryText (string; default "Add summary text"):
    Text to be shown as a summary."""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'uk_gov_dash_components'
    _type = 'AdditionalDetails'


    def __init__(
        self,
        id: typing.Optional[typing.Union[str, dict]] = None,
        summaryText: typing.Optional[str] = None,
        detailsText: typing.Optional[str] = None,
        hidden: typing.Optional[bool] = None,
        **kwargs
    ):
        self._prop_names = ['id', 'detailsText', 'hidden', 'summaryText']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'detailsText', 'hidden', 'summaryText']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args}

        for k in ['id']:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')

        super(AdditionalDetails, self).__init__(**args)

setattr(AdditionalDetails, "__init__", _explicitize_args(AdditionalDetails.__init__))
