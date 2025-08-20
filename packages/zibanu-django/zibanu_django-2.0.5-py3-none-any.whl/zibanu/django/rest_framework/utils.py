# -*- coding: utf-8 -*-

# ****************************************************************
# IDE:          PyCharm
# Developed by: macercha
# Date:         18/03/24
# Project:      Zibanu Django
# Module Name:  utils
# Description:
# ****************************************************************
from rest_framework.views import exception_handler as rest_exception_handler


def exception_handler(exc, context):
    """
    Custom exception handler for Django REST Framework

    Parameters
    ----------
    exc : Exception
        The exception instance received from view
    context : dict
        Dictionary to be used by the exception handler

    Returns
    -------
    Response:
        Object response with data that contains the error details and status code
    """
    response = rest_exception_handler(exc, context)
    if response is not None and "detail" in response.data:
        response.data["errors"] = [response.data.pop("detail")]
        response.data["code"] = "not_authenticated"

    return response
