# -*- coding: utf-8 -*-

# ****************************************************************
# IDE:          PyCharm
# Developed by: macercha
# Date:         8/08/23 8:10
# Project:      Zibanu - Django
# Module Name:  language
# Description:
# ****************************************************************
from django.conf import settings
from rest_framework import status
from rest_framework.response import Response

from zibanu.django.rest_framework.viewsets import ViewSet


class LanguageViewSet(ViewSet):
    """
    View set to expose REST services to list django available languages.
    """

    def list(self, request, *args, **kwargs) -> Response:
        """
        REST service to list django available languages from settings.

        Parameters
        ----------
        request: HTTP request object.
        *args: Tuple with parameters
        **kwargs: Dictionary with key/value parameters

        Returns
        -------
        languages: List with django languages from settings.
        """
        lang_list = {
            "default": settings.LANGUAGE_CODE,
            "languages": []
        }

        if hasattr(settings, "LANGUAGES"):
            lang_list["languages"] = dict(settings.LANGUAGES)

        return Response(status=status.HTTP_200_OK, data=lang_list)
