# -*- coding: utf-8 -*-

#  Developed by CQ Inversiones SAS. Copyright ©. 2019 - 2024. All rights reserved.
#  Desarrollado por CQ Inversiones SAS. Copyright ©. 2019 - 2024. Todos los derechos reservados.

# ****************************************************************
# IDE:          PyCharm
# Developed by: macercha
# Date:         3/04/24
# Project:      Zibanu Django
# Module Name:  dial_codes
# Description:
# ****************************************************************
from django.utils.translation import gettext_lazy as _
from django.db.models import TextChoices
from typing import List


class DialCodes(TextChoices):
    AR = "+54", _("Argentina")
    BO = "+591", _("Bolivia")
    BR = "+55", _("Brazil")
    CL = "+56", _("Chile")
    CN = "+86", _("China")
    CO = "+57", _("Colombia")
    CR = "+506", _("Costa Rica")
    CU = "+53", _("Cuba")
    DO_1 = "+1809", _("Dominican Republic")
    DO_2 = "+1829", _("Dominican Republic")
    DO_3 = "+1849", _("Dominican Republic")
    EC = "+593", _("Ecuador")
    EG = "+20", _("Egypt")
    SV = "+503", _("El Salvador")
    FR = "+33", _("France")
    GT = "+502", _("Guatemala")
    GY = "+592", _("Guyana")
    HN = "+504", _("Honduras")
    IT = "+39", _("Italy")
    KZ_RU = "+7", _("Kazakhstan/Russia")
    MX = "+52", _("Mexico")
    NI = "+505", _("Nicaragua")
    PA = "+507", _("Panama")
    PY = "+595", _("Paraguay")
    PE = "+51", _("Peru")
    PR_1 = "+1787", _("Puerto Rico")
    PR_2 = "+1939", _("Puerto Rico")
    SP = "+34", _("Spain")
    GB = "+44", _("United Kingdom")
    USA_CA = "+1", _("United States/Canada")
    UY = "+598", _("Uruguay")
    VE = "+58", _("Venezuela")

    @classmethod
    def dial_codes_list(cls):
        return [x[0] for x in cls.choices]

    @classmethod
    def sorted(cls, alphabetic: bool = True) -> List[tuple]:
        index = 0 if not alphabetic else 1
        return sorted(cls.choices, key=lambda x: x[index])
