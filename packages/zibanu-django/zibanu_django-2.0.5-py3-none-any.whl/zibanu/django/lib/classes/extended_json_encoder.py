# -*- coding: utf-8 -*-

#  Developed by CQ Inversiones SAS. Copyright ©. 2019 - 2024. All rights reserved.
#  Desarrollado por CQ Inversiones SAS. Copyright ©. 2019 - 2024. Todos los derechos reservado

# ****************************************************************
# IDE:          PyCharm
# Developed by: macercha
# Date:         30/01/24 16:08
# Project:      Zibanu - Django
# Module Name:  extended_json_encoder
# Description:
# ****************************************************************
# Default imports
import datetime
import json

from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Model
from django.db.models.fields.files import FileField, ImageFieldFile
from django.forms.models import model_to_dict
from typing import Any


class ExtendedJSONEncoder(DjangoJSONEncoder):
    """
    Extended JSON encoder for Django models that use ImageField, FileField and DateTimeField
    """

    def default(self, obj: Any):
        if isinstance(obj, FileField) or isinstance(obj, ImageFieldFile):
            return str(obj)
        elif isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%M-%d %H:%M:%S')
        elif isinstance(obj, datetime.date):
            return obj.strftime('%Y-%m-%d')
        elif isinstance(obj, Model):
            o_dict = model_to_dict(obj)
            return json.dumps(o_dict, cls=ExtendedJSONEncoder)
        else:
            return super().default(obj)
