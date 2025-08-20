# -*- coding: utf-8 -*-

# ****************************************************************
# IDE:          PyCharm
# Developed by: macercha
# Date:         7/07/23 7:31
# Project:      Zibanu - Django
# Module Name:  __init__.py
# Description:
# ****************************************************************
from .dial_codes import DialCodesViewSet
from .language import LanguageViewSet
from .timezone import TimeZoneViewSet

__all__ = [
    "DialCodesViewSet",
    "LanguageViewSet",
    "TimeZoneViewSet"
]