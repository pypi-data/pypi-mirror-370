# -*- coding: utf-8 -*-

#  Developed by CQ Inversiones SAS. Copyright ©. 2019 - 2022. All rights reserved.
#  Desarrollado por CQ Inversiones SAS. Copyright ©. 2019 - 2022. Todos los derechos reservado

# ****************************************************************
# IDE:          PyCharm
# Developed by: macercha
# Date:         13/12/22 10:14 AM
# Project:      Zibanu Django Project
# Module Name:  base_model
# Description:
# ****************************************************************
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db import models
from django.utils.translation import gettext_lazy as _
from enum import IntEnum


class RelationShipType(IntEnum):
    ONE_TO_MANY = 0
    ONE_TO_ONE = 1
    MANY_TO_MANY = 2
    MANY_TO_ONE = 3

class Model(models.Model):
    """
    Inherited abstract class from models.Model to add the "use_db" attribute.
    """
    # Protected attribute
    use_db = "default"

    def __get_relationship_type(self, related_object):
        if related_object.one_to_many:
            return RelationShipType.ONE_TO_MANY
        elif related_object.one_to_one:
            return RelationShipType.ONE_TO_ONE
        elif related_object.many_to_many:
            return RelationShipType.MANY_TO_MANY
        else:
            return RelationShipType.MANY_TO_ONE

    def __get_attrs_instances(self, data: dict[str, ...]) -> tuple:
        """
        Private method to separate own data from  child entity data.

        Parameters
        ----------
        data: dict
            Set of attributes to create or update the entity instance.

        Returns
        -------
        tuple
            Return external and own attributes tuple.
        """
        related_objects = dict()
        children_data = dict()
        # Obtain related objects.
        for related_object in self._meta.related_objects:
            related_object_name = related_object.related_name if related_object.related_name is not None else related_object.name + "_set"
            if related_object_name is not None:
                # Load related objects only if it is one-2-one or one-2-many
                if self.__get_relationship_type(related_object) in [RelationShipType.ONE_TO_MANY, RelationShipType.ONE_TO_ONE]:
                    related_objects[related_object_name] = {
                        "model": related_object.related_model,
                        "type": self.__get_relationship_type(related_object),
                        "related_field": related_object.remote_field.name,
                    }
        # Obtain external attributes from received attributes and self._meta.model attributes.
        for key, value in data.items():
            # If key of attribute is in related_objects key set.
            if key in related_objects.keys():
                if hasattr(self._meta.model, key):
                    if not hasattr(self, key):
                        child_attr = getattr(self._meta.model, key)
                        setattr(self, key, child_attr.related.related_model())
                    attr = getattr(self, key)
                    if isinstance(attr, models.Model) or (hasattr(attr, "field") and isinstance(getattr(attr, "field"), models.ForeignKey)):
                        children_data[key] = value
        # Get own instance attributes.
        own_data = {key: value for key, value in data.items() if key not in children_data}
        return children_data, own_data, related_objects

    def set(self, attributes: dict = None, force_update: bool = True, **kwargs) -> bool:
        try:
            if "fields" in kwargs:
                attributes = kwargs.pop("fields")

            with transaction.atomic():
                # Assign force insert or update flag.
                force_insert = not force_update


                # Separate own attributes and related instances attributes
                children_data, own_data, related_objects = self.__get_attrs_instances(attributes)

                # Save own attributes in instance
                own_fields = self._meta.fields
                for key, value in own_data.items():
                    exists = len([x for x in own_fields if x.name == key]) > 0
                    if exists:
                        setattr(self, key, value)
                self.save(force_update=force_update, force_insert=force_insert)

                # Analyze and delete one-to-one child objects if it does not found in json.
                if len(children_data) > 0:
                    for key, value in related_objects.items():
                        if hasattr(self, key) and value.get("type") == RelationShipType.ONE_TO_ONE:
                            if key not in children_data:
                                child_object = getattr(self, key)
                                child_object.delete()

                # Analyze and set attributes in child models
                for key, child_data in children_data.items():
                    if key in related_objects.keys():
                        related_object = related_objects.get(key)
                        own_attribute = getattr(self, key)
                        if related_object.get("type") == RelationShipType.ONE_TO_ONE:
                            child_object = own_attribute
                            if child_object.id is not None and "id" in child_data:
                                if child_data["id"] == child_object.id:
                                    child_object.set(child_data, force_update=True)
                                else:
                                    raise ValidationError(
                                        {self._meta.verbose_name: _("The child object id is different from sent id.")}
                                    )
                            # *****************************************************************************
                            # COMMENT: If child_object if a Model object instance, make the update on it.
                            # Modified by: macercha
                            # Modified at: 2025-03-4, 11:44
                            # *****************************************************************************
                            elif child_object is not None and "id" not in child_data:
                                if hasattr(child_object, "id") and child_object.id is None:
                                    related_field = related_object.get("related_field")
                                    setattr(child_object, related_field, self)
                                    force_update = False
                                else:
                                    force_update = True
                                child_object.set(child_data, force_update=force_update)
                            elif child_object.id is None and "id" not in child_data:
                                related_field = related_object.get("related_field")
                                child_object = related_object.get("model")()
                                setattr(child_object, related_field, self)
                                child_object.set(child_data, force_update=False)
                            else:
                                raise ValidationError(
                                    {self._meta.verbose_name: _("The child object cannot be created from sent id.")}
                                )
                        elif related_object.get("type") == RelationShipType.ONE_TO_MANY:
                            children_objects = own_attribute.all()
                            # Delete related object does not exists in json data.
                            for child_object in children_objects:
                                exists = len([x for x in child_data if x.get("id", 0) == child_object.id]) > 0
                                if not exists:
                                    child_object.delete()

                            # Update or create objects from json data
                            for grandson_data in child_data:
                                if "id" in grandson_data:
                                    child_object = children_objects.filter(pk=grandson_data.get("id")).first()
                                    if child_object is not None:
                                        child_object.set(grandson_data, force_update=True)
                                    else:
                                        raise ValidationError(
                                            {self._meta.verbose_name: _("The child object does not exists.")}
                                        )
                                else:
                                    related_field = related_object.get("related_field")
                                    child_object = related_object.get("model")()
                                    setattr(child_object, related_field, self)
                                    child_object.set(grandson_data, force_update=False)
                        else:
                            raise ValidationError(
                                {self._meta.model_name: _("Relationship not supported.")}
                            )
        except:
            raise
        else:
            return True

    def save(self, *args, force_insert=False, force_update=False, using=None, update_fields=None):
        """
        Override method to save the model forcing full clean.

        Parameters
        ----------
        args: list
            Arguments list passed to super class.
        force_insert : bool|False
            Flag to indicate if force insert record instead of updating it. Defaults to False.
        force_update : bool|False
            Flag to indicate if force update record instead of insert it. Defaults to False.
        using : str|None
            Setting db name to user
        update_fields : list|None
            List of attrs to be updated

        Returns
        -------
        None
        """
        self.full_clean()
        return super().save(force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)

    class Meta:
        """
        Metaclass for Model class.
        """
        abstract = True
