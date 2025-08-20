# -*- coding: utf-8 -*-

#  Developed by CQ Inversiones SAS. Copyright ©. 2019 - 2022. All rights reserved.
#  Desarrollado por CQ Inversiones SAS. Copyright ©. 2019 - 2022. Todos los derechos reservado

# ****************************************************************
# IDE:          PyCharm
# Developed by: macercha
# Date:         14/12/22 4:14 AM
# Project:      Zibanu Django Project
# Module Name:  api_exception
# Description:
# ****************************************************************
import logging
import traceback
from typing import Any

from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.exceptions import APIException as SourceException
from zibanu.django.lib.utils import object_to_list


class ApiError:
    errors = list
    code = "api_exception"


class APIException(SourceException):
    """
    Inherited class from rest_framework.exceptions.ApiException
    """
    default_detail = _("API Exception")
    default_code = "api_exception"
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    __default_messages = {
        "304": _("Object has not been created."),
        "400": _("Generic error."),
        "401": _("You are not authorized for this resource."),
        "403": _("You do not have permission to perform this action."),
        "404": _("Object does not exists."),
        "406": _("Data validation error."),
        "409": _("Database error"),
        "412": _("Data required not found."),
        "500": _("Not controlled exception error. Please contact administrator."),
    }

    __default_codes = {
        "304": "object_not_created",
        "400": "error",
        "401": "unauthorized",
        "403": "forbidden",
        "404": "not_found",
        "406": "validation_error",
        "409": "database_error",
        "412": "precondition_failed",
        "500": "not_controlled_exception"
    }

    def __init__(self, detail: Any = None, code: str = None, status_code: int = None, **kwargs) -> None:
        """
        Overwrite constructor method

        Parameters
        ----------
        detail : str: String message to be sent through exception.
        code : str: String exception code to be sent through exception.
        http_status: int: HTTP Status code
        msg: Message to send trough exception. (Legacy)
        error: Error code or long description. (Legacy)
        """
        if status_code is not None:
            self.status_code = status_code
        else:
            self.status_code = kwargs.get("http_status", self.status_code)

        # Set detail from msg if exists and detail is None
        if detail is None:
            detail = kwargs.get("msg", self.default_detail)

        # Set default detail based on detail object
        detail = object_to_list(detail)

        # Set default code
        if code is None:
            code = kwargs.get("error", self.default_code)

        self.detail = {
            "errors": detail.copy(),
            "code": code
        }

        # Save Logging
        logging.error(self.default_detail)
        logging.debug(traceback.format_exc())
