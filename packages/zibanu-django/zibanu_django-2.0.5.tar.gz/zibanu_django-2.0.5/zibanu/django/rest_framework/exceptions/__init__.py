# -*- coding: utf-8 -*-

#  Developed by CQ Inversiones SAS. Copyright ©. 2019 - 2022. All rights reserved.
#  Desarrollado por CQ Inversiones SAS. Copyright ©. 2019 - 2022. Todos los derechos reservado

# ****************************************************************
# IDE:          PyCharm
# Developed by: macercha
# Date:         13/12/22 1:15 PM
# Project:      Zibanu Django Project
# Module Name:  __init__.py
# Description:
# ****************************************************************
from .not_implemented_exception import NotImplementedException
from .api_exception import APIException
from .multiple_login_error import MultipleLoginError
from .permission_denied import PermissionDenied
from .not_authenticated import NotAuthenticated
from rest_framework.exceptions import ValidationError, ParseError, UnsupportedMediaType
from rest_framework.exceptions import NotFound, AuthenticationFailed, MethodNotAllowed, NotAcceptable

__all__ = [
    "AuthenticationFailed",
    "APIException",
    "MethodNotAllowed",
    "MultipleLoginError",
    "NotAcceptable",
    "NotFound",
    "ParseError",
    "PermissionDenied",
    "NotImplementedException",
    "UnsupportedMediaType",
    "ValidationError",
    "NotAuthenticated"
]
