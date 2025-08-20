# -*- coding: utf-8 -*-

#  Developed by CQ Inversiones SAS. Copyright ©. 2019 - 2024. All rights reserved.
#  Desarrollado por CQ Inversiones SAS. Copyright ©. 2019 - 2024. Todos los derechos reservados.

# ****************************************************************
# IDE:          PyCharm
# Developed by: macercha
# Date:         28/08/24
# Project:      Zibanu Django
# Module Name:  base_model_controller
# Description:
# ****************************************************************
import logging
import traceback
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils.translation import gettext_lazy as _
from typing import Any
from zibanu.django.db.models import Model
from zibanu.django.lib.metaclasses import ModelControllerMetaClass
from zibanu.django.lib.utils.generic_utils import import_class
from zibanu.django.lib.utils.request_utils import get_request_from_stack

class BaseModelController(metaclass=ModelControllerMetaClass):
    """ Base model controller class. """

    def __init__(self, pk: int = None, **kwargs: dict[str, ...]) -> None:
        """ Constructor method for BaseModelController class."""
        self.__id = pk
        self.__attrs = None
        self.__request = kwargs.pop("request", None)
        if self.__request is None:
            self.__request = get_request_from_stack()
        if {"id", "pk"} <= kwargs.keys():
            raise ValidationError({
                self.verbose_name: _("The keys 'id' or 'pk' cannot be used in arguments.")
            })
        self._instance = None
        self._load(kwargs)

    def _load(self, kwargs: dict[str, ...] = None) -> None:
        """ Protected method to load properties from kwargs. """
        try:
            if kwargs is not None:
                self.__attrs = kwargs
            # Load base instance
            self._instance = kwargs.pop("instance", None)
            if self._instance is not None:
                self.__id = self._instance.id
            else:
                if self.is_adding:
                    self._instance = self.model()
                else:
                    self._instance = self.model.objects.get(pk=self.id)

            # If instance exists, load its attrs and child objects.
            if self._instance:
                # Load model properties.
                for key, value in self._instance.__dict__.items():
                    if not key.startswith("_") and key != "id":
                        if key in self.fields:
                            setattr(self, "_" + key, value)

                for index, field in enumerate(self.related_fields):
                    if self.is_adding:
                        setattr(self, "_" + field, None)
                    else:
                        # Load child attributes if not is adding.
                        if len(self.related_objects) > index:
                            # Load related attrs, in related objects if exists
                            tmp_attr = []
                            imported_class = import_class(self.related_objects[index])
                            field_data = getattr(self._instance, field).all()
                            for data in field_data:
                                if hasattr(data, "id"):
                                    tmp_attr.append(imported_class(data.id))
                        else:
                            # *****************************************************************************
                            # COMMENT: Validate if field exists and if it is a queryset or model instance.
                            # Modified by: macercha
                            # Modified at: 2025-03-4, 6:53
                            # *****************************************************************************
                            # Load child instances, and its attributes from main attrs.
                            if hasattr(self._instance, field):
                                related_field = getattr(self._instance, field)
                                if isinstance(related_field, Model):
                                    setattr(self, "_" + field, getattr(self._instance, field))
                                else:
                                    setattr(self, "_" + field, getattr(self._instance, field).all())
        except self.model.DoesNotExist as exc:
            logging.error(str(exc))
            logging.debug(traceback.format_exc())
            raise ValidationError({
                self.verbose_name: _("The object does not exists.")
            })
        except Exception as exc:
            logging.error(str(exc))
            logging.debug(traceback.format_exc())
            raise ValidationError({
                self.verbose_name: str(exc)
            })

    @property
    def is_adding(self):
        """ Flag to indicate if the object is in adding status or not. """
        return self.__id is None

    @property
    def request(self):
        """ HTTP Request object. """
        return self.__request

    @property
    def id(self):
        return self.__id

    @property
    def verbose_name(self):
        return self._meta.verbose_name

    @property
    def model(self):
        return self._meta.model

    @property
    def fields(self):
        return self._meta.fields

    @property
    def related_fields(self):
        return self._meta.related_fields

    @property
    def related_objects(self):
        return self._meta.related_objects

    def save(self, attrs: dict[str, ...] = None) -> Any:
        with transaction.atomic():
            try:
                if attrs is None and self.__attrs is None:
                    raise ValidationError({
                        self.verbose_name: _("The object attributes are required to save it.")
                    })
                elif attrs is not None:
                    self.__attrs = attrs.copy()
                # Save own attributes.
                self._instance.set(self.__attrs, force_update= not self.is_adding)
            except Exception:
                raise
            else:
                return self._instance


