"""
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Callable, cast

import svgwrite.base

from ._mixins import BaseWrapperMixin

if TYPE_CHECKING:
    from ...drawing import BaseDrawing

__all__ = [
    "BaseElement",
]


class BaseElement[ElementT: svgwrite.base.BaseElement](BaseWrapperMixin):
    """
    Wraps an `svgwrite` SVG element and corresponding API mixins.
    """

    _api_name: str
    """
    Name of svgwrite API to invoke.
    """

    _element: ElementT
    """
    Instance of svgwrite element.
    """

    _glyph_obj: BaseDrawing

    def __init__(
        self,
        drawing: BaseDrawing,
        container: svgwrite.base.BaseElement,
        *args,
        **kwargs,
    ):
        """
        Creates the corresponding `svgwrite` element, passing through
        extra kwargs. Should not be instantiated directly; use draw APIs.
        """

        self._glyph_obj = drawing

        api_attr = getattr(drawing._drawing, self._api_name)
        api = cast(Callable[..., ElementT], api_attr)

        self._element = api(*args, **kwargs)
        self._mixin_obj = self._element

        container.add(self._element)

    @property
    def iri(self) -> str:
        return self._element.get_iri()

    @property
    def funciri(self) -> str:
        return self._element.get_funciri()
