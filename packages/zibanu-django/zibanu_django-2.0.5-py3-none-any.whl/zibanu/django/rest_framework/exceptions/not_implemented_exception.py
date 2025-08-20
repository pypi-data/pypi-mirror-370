# -*- coding: utf-8 -*-

#  Developed by CQ Inversiones SAS. Copyright ©. 2019 - 2023. All rights reserved.
#  Desarrollado por CQ Inversiones SAS. Copyright ©. 2019 - 2023. Todos los derechos reservado

# ****************************************************************
# IDE:          PyCharm
# Developed by: macercha
# Date:         8/11/23 22:19
# Project:      Zibanu - Django
# Module Name:  service_not_implemented
# Description:
# ****************************************************************
# Default imports
import logging
import traceback
from django.utils.translation import gettext_lazy as _
from .api_exception import APIException
from rest_framework import status


class NotImplementedException(APIException):
    """
    Class to raise error for not implemented method
    """
    def __init__(self):
        super().__init__(detail=_("Service not implemented"), code="not_implemented", status_code=status.HTTP_405_METHOD_NOT_ALLOWED)