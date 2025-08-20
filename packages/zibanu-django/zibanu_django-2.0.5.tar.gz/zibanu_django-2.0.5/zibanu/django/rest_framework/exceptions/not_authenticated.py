# -*- coding: utf-8 -*-
# ****************************************************************
# IDE:          PyCharm
# Developed by: "Jhony Alexander Gonzalez Córdoba"
# Date:         18/12/2024 4:24 p. m.
# Project:      zibanu-django
# Module Name:  not_authenticated
# Description:  
# ****************************************************************
from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework import exceptions

from zibanu.django.rest_framework.exceptions import APIException


class NotAuthenticated(APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = _('Authentication credentials were not provided.')
    default_code = "not_authenticated"


exceptions.NotAuthenticated = NotAuthenticated
