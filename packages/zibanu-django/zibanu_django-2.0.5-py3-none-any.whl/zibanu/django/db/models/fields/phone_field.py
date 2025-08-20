# -*- coding: utf-8 -*-

#  Developed by CQ Inversiones SAS. Copyright ©. 2019 - 2024. All rights reserved.
#  Desarrollado por CQ Inversiones SAS. Copyright ©. 2019 - 2024. Todos los derechos reservados.

# ****************************************************************
# IDE:          PyCharm
# Developed by: macercha
# Date:         2/04/24
# Project:      Zibanu Django
# Module Name:  phone_field
# Description:
# ****************************************************************
import json
from zibanu.django.lib import DialCodes
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.db.models.fields.json import JSONField


class PhoneField(JSONField):
    description = _("A Phone Field object")

    def __init__(self, encoder=None, decoder=None, dial_code: str = "+57", *args, **kwargs):
        self.dial_code = dial_code
        self.phone_number = 0
        self.dial_codes = kwargs.get("dial_codes", DialCodes)
        super().__init__(encoder=encoder, decoder=decoder, *args, **kwargs)

    def __str__(self):
        return f"{self.dial_code} + ' ' + {str(self.phone_number)}"

    def from_db_value(self, value, expression, connection):
        value = super().from_db_value(value, expression, connection)
        if value is not None:
            self.phone_number = value.get("phone_number")
            self.dial_code = value.get("dial_code")
        return value

    def validate(self, value, model_instance):
        super().validate(value, model_instance)
        if "dial_code" not in value:
            value["dial_code"] = self.dial_code
        if not {"dial_code", "phone_number"} <= value.keys():
            raise ValidationError(_("'dial_code' and 'phone_number' keys are required."))
        if len(value) > 2:
            raise ValidationError(_("Number of keys major than required. Please try again."))
        if not isinstance(value.get("phone_number"), int) or not isinstance(value.get("dial_code"), str):
            raise ValidationError(_("Type of field keys are wrong. Please try again."))
        if not value.get("dial_code") in self.dial_codes.dial_codes_list():
            raise ValidationError(_("Country code is not valid. Please try again."))
