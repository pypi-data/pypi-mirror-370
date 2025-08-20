# -*- coding: utf-8 -*-

#  Developed by CQ Inversiones SAS. Copyright ©. 2019 - 2022. All rights reserved.
#  Desarrollado por CQ Inversiones SAS. Copyright ©. 2019 - 2022. Todos los derechos reservado

# ****************************************************************
# IDE:          PyCharm
# Developed by: macercha
# Date:         13/12/22 3:33 PM
# Project:      Zibanu Django Project
# Module Name:  model_serializer
# Description:
# ****************************************************************
from rest_framework.serializers import ModelSerializer as SourceModelSerializer
from rest_framework.fields import empty
from typing import Any, Type


class ModelSerializer(SourceModelSerializer):
    """
    Override class for ModelSerializer
    """

    @property
    def is_adding(self):
        """ Property to validate if the operation is adding or updating """
        return self.instance is None