# -*- coding: utf-8 -*-

# ****************************************************************
# IDE:          PyCharm
# Developed by: macercha
# Date:         27/04/23 9:57
# Project:      Zibanu - Django
# Module Name:  decorators
# Description:
# ****************************************************************
from django.contrib.auth.decorators import user_passes_test
from django.utils.translation import gettext_lazy as _
from typing import Any
from zibanu.django.rest_framework.exceptions import PermissionDenied
from zibanu.django.lib.utils import get_user_object


def permission_required(permissions: Any, raise_exception=True):
    """
    Decorator to validate permissions from django auth structure. SimpleJWT compatible.

    Parameters
    ----------
    permissions: permission name or tuple with permissions list. Mandatory
    raise_exception: True if you want to raise PermissionDenied exception, otherwise False. Default: True

    Returns
    -------
    b_return: True if successfully authorized, otherwise False.
    """

    def check_perms(user):
        """
        Internal function to check permission from master function

        Parameters
        ----------
        user: User object to validate.

        Returns
        -------
        b_return: True if permissions check success, otherwise False.
        """
        b_return = False
        is_staff = False
        local_user = get_user_object(user)

        # Build perms list
        if permissions is not None:
            if isinstance(permissions, str):
                perms = (permissions,)
            else:
                perms = permissions
        else:
            raise ValueError(_("Permission name or tuple is required."))

        if "is_staff" in perms:
            is_staff = True
            perms = tuple([perm for perm in perms if perm != "is_staff"])

        if (len(perms) > 0 and local_user.has_perms(perms)) or (is_staff and local_user.is_staff) or local_user.is_superuser:
            b_return = True
        elif raise_exception:
            raise PermissionDenied(_("You do not have permission to perform this action."))
        return b_return
    return user_passes_test(check_perms)