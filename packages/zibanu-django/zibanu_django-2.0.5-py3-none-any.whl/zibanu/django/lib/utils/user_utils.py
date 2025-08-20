# -*- coding: utf-8 -*-

#  Developed by CQ Inversiones SAS. Copyright ©. 2019 - 2022. All rights reserved.
#  Desarrollado por CQ Inversiones SAS. Copyright ©. 2019 - 2022. Todos los derechos reservado

from typing import Any

# ****************************************************************
# IDE:          PyCharm
# Developed by: macercha
# Date:         14/12/22 4:21 AM
# Project:      Zibanu Django Project
# Module Name:  user
# Description:
# ****************************************************************
from django.apps import apps
from django.contrib import auth
from rest_framework_simplejwt.models import TokenUser


def get_user(user: Any) -> Any:
    """
    Function to get user from SimpleJWT TokenUser token or django user.

    Parameters
    ----------
    user : User object to review.

    Returns
    -------
    local_user: Django user object.
    """
    local_user = user
    # Set user proxy model if zibanu.django.auth is installed
    if apps.is_installed("zibanu.django.auth"):
        from zibanu.django.auth.models import User
        user_model = User
    else:
        user_model = auth.get_user_model()

    if isinstance(user, TokenUser):
        local_user = user_model.objects.get(pk=local_user.id)

    return local_user


def get_user_object(user: Any) -> Any:
    """
    Legacy function. Use "get_user" instead. This function will be removed in future versions.

    Parameters
    ----------
    user : User object to review.

    Returns
    -------
    Django user object.
    """
    return get_user(user)
