# -*- coding: utf-8 -*-

#  Developed by CQ Inversiones SAS. Copyright ©. 2019 - 2023. All rights reserved.
#  Desarrollado por CQ Inversiones SAS. Copyright ©. 2019 - 2023. Todos los derechos reservado

# ****************************************************************
# IDE:          PyCharm
# Developed by: macercha
# Date:         8/11/23 06:41
# Project:      Zibanu - Django
# Module Name:  owner_or_read_only
# Description:
# ****************************************************************
# Default imports
from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permissions to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        """
        Override method to validate object owner

        Parameters
        ----------
        request : Request object from HTTP
        view : View Object
        obj : Model Object

        Returns
        -------
        boolean: True if successfully, otherwise False
        """
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.owner == request.user
