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


class Accordion(Component):
    """An Accordion component.
Lazy loaded Accordion Component

This Accordion component dynamically creates sections based on the provided `accordionHeadings`.
Each section can be independently opened or closed. The `defaultSectionsOpen` array corresponds
to the sections defined by `accordionHeadings`, where each element in the array represents the 
open (true) or closed (false) state of the respective section on initial render.

@param {{
  id: string,                            // Unique identifier for the accordion component
  accordionHeadings: string[],           // Array of headings for each section of the accordion
  children: React.ReactNode,             // Content to be rendered inside the accordion
  showToggleText: boolean,               // Flag to show or hide toggle text  
  defaultSectionsOpen: boolean[],        // Array indicating the initial open state of each section
}} [props={}]                            // Component props with default empty object
@return {React.ReactElement}             // Returns a React element representing the accordion

Keyword arguments:

- children (list of a list of or a singular dash component, string or numbers | a list of or a singular dash component, string or number; optional):
    Array of accordion children.

- id (string; optional):
    The ID of this component, used to identify dash components in
    callbacks. The ID needs to be unique across all of the components
    in an app.

- accordionHeadings (list of strings; optional):
    Array of accordion headings.

- bannerSections (list of number | a value equal to: nulls; optional):
    Array that determines the creation of banners for each section.
    Each item in the array corresponds to a section on the page. If an
    item is an integer, a banner with a button is created.  The button
    focuses on the child content with the corresponding index. If an
    item is None, no banner is created for that section.

- defaultSectionsOpen (list of booleans; optional):
    Array of booleans that determines the initial open/closed state of
    each section in the component. Each item in the array corresponds
    to a section. If an item is True, the corresponding section is
    open  by default when the component is first rendered. If an item
    is False, the corresponding section is closed by default.

- showToggleText (boolean; default True):
    Whether to display \"Show\" / \"Hide\" text before Accordion
    heading."""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'uk_gov_dash_components'
    _type = 'Accordion'


    def __init__(
        self,
        children: typing.Optional[ComponentType] = None,
        id: typing.Optional[typing.Union[str, dict]] = None,
        accordionHeadings: typing.Optional[typing.Sequence[str]] = None,
        bannerSections: typing.Optional[typing.Sequence[typing.Union[NumberType, Literal[None]]]] = None,
        showToggleText: typing.Optional[bool] = None,
        defaultSectionsOpen: typing.Optional[typing.Sequence[bool]] = None,
        **kwargs
    ):
        self._prop_names = ['children', 'id', 'accordionHeadings', 'bannerSections', 'defaultSectionsOpen', 'showToggleText']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['children', 'id', 'accordionHeadings', 'bannerSections', 'defaultSectionsOpen', 'showToggleText']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}

        super(Accordion, self).__init__(children=children, **args)

setattr(Accordion, "__init__", _explicitize_args(Accordion.__init__))
