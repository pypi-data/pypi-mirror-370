# -*- coding: utf-8 -*-

#  Developed by CQ Inversiones SAS. Copyright ©. 2019 - 2022. All rights reserved.
#  Desarrollado por CQ Inversiones SAS. Copyright ©. 2019 - 2022. Todos los derechos reservado

# ****************************************************************
# IDE:          PyCharm
# Developed by: macercha
# Date:         19/12/22 3:18 PM
# Project:      Zibanu Django Project
# Module Name:  __init__.py
# Description:
# ****************************************************************
from .model_viewset import ModelViewSet
from .viewset import ViewSet
from rest_framework.viewsets import ViewSetMixin, GenericViewSet, ReadOnlyModelViewSet

__all__ = [
    "ModelViewSet",
    "ViewSet",
    "ViewSetMixin",
    "GenericViewSet",
    "ReadOnlyModelViewSet"
]

