from __future__ import annotations
from typing import Optional, Callable
from discord import File, Embed
from immutableType import callable_, NoneType
from ..views import EasyModifiedViews

class Page:

    @callable_(is_class=True, kwargs_types={'view': [NoneType, EasyModifiedViews], 'content': [NoneType, str], 'embed': [NoneType, Embed], 'embeds': [list], 'file': [NoneType, File], 'files': [list]})
    def __init__(self, view: EasyModifiedViews, content: Optional[str] = None, embed: Optional[Embed] = None, embeds: list[Embed] = [], file: Optional[File] = None,  files: Optional[list[File]] = []):
        """
        Init Page instance from Pagination class
        """
        self.__view: EasyModifiedViews = view if view is not None else EasyModifiedViews()
        self.content: Optional[str] = content
        self.embeds: list[Embed] = embeds if embed is None else embeds + [embed]
        self.files: list[File] = files if file is None else files + [file]

    @property
    def get_page_view(self) -> EasyModifiedViews:
        """
        Get the current page view
        """
        return self.__view

