# -*- coding: utf-8 -*-

# ****************************************************************
# IDE:          PyCharm
# Developed by: macercha
# Date:         7/07/23 7:44
# Project:      Zibanu - Django
# Module Name:  urls
# Description:
# ****************************************************************
from django.urls import path
from zibanu.django.api.services import DialCodesViewSet
from zibanu.django.api.services import LanguageViewSet
from zibanu.django.api.services import TimeZoneViewSet

urlpatterns = [
    path("dial_codes/list/", DialCodesViewSet.as_view({"post": "list"}), name="Dial codes list"),
    path("timezone/list/", TimeZoneViewSet.as_view({"post": "list"}), name="TimeZone list"),
    path("language/list/", LanguageViewSet.as_view({"post": "list"}), name="Django languages list")
]