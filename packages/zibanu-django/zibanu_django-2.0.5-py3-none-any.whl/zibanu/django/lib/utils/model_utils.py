# -*- coding: utf-8 -*-

#  Developed by CQ Inversiones SAS. Copyright ©. 2019 - 2024. All rights reserved.
#  Desarrollado por CQ Inversiones SAS. Copyright ©. 2019 - 2024. Todos los derechos reservado

# ****************************************************************
# IDE:          PyCharm
# Developed by: macercha
# Date:         29/01/24 20:55
# Project:      Zibanu - Django
# Module Name:  models
# Description:
# ****************************************************************
# Default imports
from django.apps import apps

from zibanu.django.lib.classes.model_name import ModelName


def get_model_list(app_label: str = None):
    """
    Script que retorna una lista de los modelos contenidos en un proyecto de Django, o en una app específica.

    Parameters
    ----------
    app_label: str: Nombre de la app contenido en el proyecto de Django.

    Returns
    -------
    model_list: list: Lista de los nombres de los modelos
    """
    models = apps.get_models()
    model_list = [ModelName(x._meta.app_label + "." + x.__name__) for x in models if
                  not x._meta.abstract and not x._meta.proxy]
    if app_label:
        model_list = [x for x in model_list if x.split(".")[0] == app_label]
    return model_list


def get_model_fields(app_label: str = None, model_name: str = None):
    """
    Script que retorna un diccionario con los nombres de los modelos y sus campos.

    Parameters
    ----------
    app_label: str (optional): Nombre de la app contenido en el proyecto de Django
    model_name: str (optional): Nombre del modelo del cual se quieren listar los campos

    Returns
    -------
    fields: dict: Diccionario que contiene los nombres de los modelos como clave y sus campos como valor. En caso de
        que el modelo no exista, retorna un diccionario vacío.
    """
    fields = dict()
    models = get_model_list(app_label)
    if model_name:
        try:
            model = apps.get_model(app_label, model_name)
            fields[model._meta.app_label + "." + model.__name__] = [x.name for x in
                                                                    model._meta.get_fields(include_hidden=False)]
        except LookupError:
            pass
    else:
        for model in models:
            fields[model] = [x.name for x in
                             apps.get_model(model.app_label, model.model_name)._meta.get_fields(include_hidden=False)]
    return fields
