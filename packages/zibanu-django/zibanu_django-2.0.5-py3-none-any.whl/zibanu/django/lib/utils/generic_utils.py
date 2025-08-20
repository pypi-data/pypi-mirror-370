# -*- coding: utf-8 -*-

#  Developed by CQ Inversiones SAS. Copyright ©. 2019 - 2024. All rights reserved.
#  Desarrollado por CQ Inversiones SAS. Copyright ©. 2019 - 2024. Todos los derechos reservado

# ****************************************************************
# IDE:          PyCharm
# Developed by: macercha
# Date:         28/02/24 15:27
# Project:      Zibanu - Django
# Module Name:  object_to_list
# Description:
# ****************************************************************
# Default imports
from typing import Any
from django.utils.translation import gettext_lazy as _
from django.utils.module_loading import import_string


def object_to_list(obj: Any) -> list:
    """
    Recursive function to convert an object to a list of strings.

    Parameters
    ----------
    obj: Any
        The object to be converted to a list.

    Returns
    -------
    list[str|Any]
        A list of strings.
    """
    l_return = []
    if isinstance(obj, str):
        l_return.append(obj)
    elif isinstance(obj, dict):
        for key, value in obj.items():
            if isinstance(value, dict):
                l_return = l_return + object_to_list(value)
            elif isinstance(value, list):
                for value_detail in value:
                    if len(value_detail) > 0:
                        if isinstance(value_detail, dict):
                            l_return = l_return + object_to_list(value_detail)
                        else:
                            l_return.append(_(key) + ": " + str(value_detail))
            elif isinstance(value, str):
                l_return.append(_(key) + ": " + value)
            elif isinstance(value, object):
                # If value is a translation or lazy proxy object.
                if "proxy" in value.__class__.__name__:
                    l_return = l_return + object_to_list({str(key): str(value)})
    elif isinstance(obj, list):
        l_return = obj.copy()
    else:
        l_return.append(str(obj))

    return l_return


def import_class(class_name: str = None) -> Any:
    """
    Function to import a class from string definition.

    Parameters
    ----------
    class_name : str
        Class with full qualified name

    Returns
    -------
    None
    """
    try:
        return import_string(class_name)
    except ImportError:
        msg = _("Could not import the class: ") + class_name
        raise ImportError(msg)
