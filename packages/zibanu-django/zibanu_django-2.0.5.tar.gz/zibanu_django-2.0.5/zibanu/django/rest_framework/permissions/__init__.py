# -*- coding: utf-8 -*-

#  Developed by CQ Inversiones SAS. Copyright ©. 2019 - 2023. All rights reserved.
#  Desarrollado por CQ Inversiones SAS. Copyright ©. 2019 - 2023. Todos los derechos reservado

# ****************************************************************
# IDE:          PyCharm
# Developed by: macercha
# Date:         8/11/23 06:41
# Project:      Zibanu - Django
# Module Name:  __init__.py
# Description:
# ****************************************************************
# Default imports
import logging
import traceback
from django.utils.translation import gettext_lazy as _
from .is_owner_or_read_only import IsOwnerOrReadOnly
