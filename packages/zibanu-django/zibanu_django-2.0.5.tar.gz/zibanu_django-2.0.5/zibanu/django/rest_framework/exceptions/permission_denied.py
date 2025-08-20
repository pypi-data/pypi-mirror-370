# -*- coding: utf-8 -*-

# ****************************************************************
# IDE:          PyCharm
# Developed by: macercha
# Date:         13/03/24 9:34
# Project:      Zibanu Django
# Module Name:  permissiondenied_exception
# Description:
# *****************
import logging
import traceback
from typing import Any
from django.utils.translation import gettext_lazy as _
from rest_framework import status
from zibanu.django.rest_framework.exceptions import APIException


class PermissionDenied(APIException):
    """
    Override class PermissionDeniedException to make compatible with Zibanu Django Rest Framework
    """
    status_code = status.HTTP_401_UNAUTHORIZED

    def __init__(self, detail: str = _("You do not have permission to perform this action."),
                 code: str = "permission_denied") -> None:
        """
        Class constructor
        Parameters
        ----------
        detail: str: Exception detail string
        code: str: code string
        """
        super().__init__(detail=detail, code=code)
