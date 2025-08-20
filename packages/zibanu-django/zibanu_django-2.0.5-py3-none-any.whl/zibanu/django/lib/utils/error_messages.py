# -*- coding: utf-8 -*-

#  Developed by CQ Inversiones SAS. Copyright ©. 2019 - 2022. All rights reserved.
#  Desarrollado por CQ Inversiones SAS. Copyright ©. 2019 - 2022. Todos los derechos reservado

# ****************************************************************
# IDE:          PyCharm
# Developed by: macercha
# Date:         19/12/22 3:36 PM
# Project:      Zibanu Django Project
# Module Name:  error_messages
# Description:
# ****************************************************************
from django.utils.translation import gettext_lazy as _


class ErrorMessages:
    """
    Error messages compilation constants
    """
    FIELD_REQUIRED = _("Error! The field is required.")
    CREATE_ERROR = _("Error! Record has not been created.")
    UPDATE_ERROR = _("Error! Record has not been updated.")
    NOT_FOUND = _("Error! There is not record matching.")
    DELETE_ERROR = _("Error! Record can not be deleted.")
    DATA_REQUIRED = _("Error! The data required not found.")
    DATABASE_ERROR = _("Error at database.")
    DATA_REQUEST_NOT_FOUND = _("Data required at request not found.")
    NOT_CONTROLLED = _("Error! Exception not controlled.")
    FIELD_LIST_ERROR = _("A list type field was expected.")
    PROTECTED_ERROR = _("Cannot update/delete this record, it has dependent relationships.")
