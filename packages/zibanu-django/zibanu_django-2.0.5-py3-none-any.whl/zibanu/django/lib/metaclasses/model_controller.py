# -*- coding: utf-8 -*-

#  Developed by CQ Inversiones SAS. Copyright ©. 2019 - 2024. All rights reserved.
#  Desarrollado por CQ Inversiones SAS. Copyright ©. 2019 - 2024. Todos los derechos reservados.

# ****************************************************************
# IDE:          PyCharm
# Developed by: macercha
# Date:         21/08/24
# Project:      Zibanu Django
# Module Name:  model_controller
# Description:
# ****************************************************************
from django.utils.translation import gettext_lazy as _


class ModelControllerMetaClass(type):
    """
    Metaclass for BaseModelController class.
    @properties
    model: Model of entity to control.
    verbose_name: verbose name of entity.
    fields: List of fields to be used.
    related_fields: List of related fields to be used.
    """
    def __new__(cls, name, bases, attrs, **kwargs):
        """ Before constructor method. """
        super_new = super().__new__
        # If the class has not been instantiated, returns the base class.
        parents = [b for b in bases if isinstance(b, ModelControllerMetaClass)]
        if not parents:
            return super_new(cls, name, bases, attrs)
        # Get meta attributes
        attr_meta = attrs.pop("Meta", None)
        new_class = super_new(cls, name, bases, attrs, **kwargs)
        meta = attr_meta or getattr(new_class, "Meta", None)
        # Validate verbose_name or set it if it does not exist.
        if not hasattr(meta, "verbose_name"):
            setattr(meta, "verbose_name", name)

        # Validate related_fields or set it if it does not exist.
        if not hasattr(meta, "related_fields"):
            setattr(meta, "related_fields", [])
        else:
            # Validate related_fields type
            assert isinstance(meta.related_fields, list) or isinstance(meta.related_fields, tuple), _(
                "The related fields must be a list."
            )
            if isinstance(meta.related_fields, tuple):
                meta.related_fields = list(meta.related_fields)

        # Validate related_objects or set it if it does not exist.
        if not hasattr(meta, "related_objects"):
            setattr(meta, "related_objects", [])
        else:
            # Validate related_objects type
            assert isinstance(meta.related_objects, list) or isinstance(meta.related_objects, tuple), _(
                "The related objects must be a list.")
            if isinstance(meta.related_objects, tuple):
                meta.related_objects = list(meta.related_objects)

        assert hasattr(meta, "model"), _("The model property must be defined in metaclass.")
        assert hasattr(meta, "fields"), _("The fields property must be defined in metaclass.")
        # Set the attributes to new class
        setattr(new_class, "_meta", meta)
        return new_class
