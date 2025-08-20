# -*- coding: utf-8 -*-
import base64
import io
import logging
import mimetypes
from typing import Any

# ****************************************************************
# IDE:          PyCharm
# Developed by: macercha
# Date:         12/08/23 17:11
# Project:      Zibanu - Django
# Module Name:  hybrid_image
# Description:
# ****************************************************************
from django.core.exceptions import ValidationError
from django.db.models.fields.files import ImageFieldFile
from django.utils.translation import gettext_lazy as _
from drf_extra_fields.fields import HybridImageField as SourceHybridImageField
from drf_extra_fields.fields import Base64FieldMixin, ImageField


class HybridImageField(SourceHybridImageField):
    """
    Inherited class from drf_extra_fields.field.HybridImageField to allow size validation and implement the use image
    format and size validation
    """
    invalid_file_size_message = _("The width or height of the file is invalid.")
    width_key = "image_width"
    height_key = "image_height"
    resize_key = "image_size"

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """
        HybridImageField class constructor

        Parameters
        ----------
        *args: Tuple with parameters values
        **kwargs: Parameter dictionary with key/values
        """
        self.max_image_width = kwargs.pop(self.width_key, 0)
        self.max_image_height = kwargs.pop(self.height_key, 0)
        self.image_size = kwargs.pop(self.resize_key, None)
        super().__init__(*args, **kwargs)

    def to_representation(self, file: ImageFieldFile) -> Any:
        """
        Override method to allow size validation and implement the use image

        Parameters
        ----------
        file : ImageFieldFile
            Instance of ImageFieldFile to validate

        Returns
        -------
        str | Base64FieldMixin
            String representation of image or image field
        """
        if self.represent_in_base64:
            if not file:
                return ""

            try:
                # Allow image_size object if defined.
                if self.context and self.resize_key in self.context:
                    self.image_size = self.context.get(self.resize_key)

                with file.open() as f:
                    mime_type = mimetypes.guess_type(file.path)[0]
                    prepend_info = f"data:{mime_type};base64"
                    base64_data = self.__image_resize(base64.b64encode(f.read()).decode(), mime_type)
            except Exception as exc:
                logging.critical(str(exc))
                raise OSError(_("Error encoding image file"))
            else:
                representation = f"{prepend_info},{base64_data}"
        else:
            representation = super().to_representation(file)
        return representation

    def to_internal_value(self, data):
        """
        Override method to process internal data from serializer

        Parameters
        ----------
        data: Data received from serializer (raw post data)

        Returns
        -------
        Python data compatible
        """

        if self.represent_in_base64:
            # Overwrite max_image_width and max_image_height from context serializer
            if self.context and {self.width_key, self.height_key} <= self.context.keys():
                self.max_image_width = self.context.get(self.width_key)
                self.max_image_height = self.context.get(self.height_key)

            if self.max_image_width > 0 and self.max_image_height > 0:
                width, height = self.__get_file_size(data)
                if width > self.max_image_width or height > self.max_image_height:
                    raise ValidationError(self.invalid_file_size_message)
            image_field = Base64FieldMixin.to_internal_value(self, data)
        else:
            image_field = ImageField.to_internal_value(self, data)
        return image_field

    def __get_file_size(self, b64data: str) -> tuple[int, int]:
        """
        Get the file size from base64 encoded bytes

        Parameters
        ----------
        b64data: str
            Base64 encoded bytes

        Returns
        -------
        width, height: tuple [int, int]
            Tuple with width and height values
        """
        try:
            from PIL import Image
            data = b64data.split(",")
            data = data[0] if len(data) == 1 else data[1]
            base64_data = base64.b64decode(data)
            image = Image.open(io.BytesIO(base64_data))
        except (ImportError, OSError):
            raise ValidationError(self.INVALID_FILE_MESSAGE)
        except Exception:
            raise
        else:
            width, height = image.size
            return width, height

    def __image_resize(self, b64data: str, mime_type: str) -> str:
        """
        Resize the image to specified percent size.

        Parameters
        ----------
        b64data : str
            Base64 encoded bytes
        mime_type: str
            File extension

        Returns
        -------
        str
            Resized image base64 encoded bytes
        """
        try:
            if self.image_size:
                from PIL import Image
                ext = mime_type.split("/")[-1]
                image = Image.open(io.BytesIO(base64.b64decode(b64data)))
                width, height = image.size
                image = image.resize((int(width * self.image_size / 100), int(height * self.image_size / 100)))
                buffer = io.BytesIO()
                image.save(buffer, ext)
                b64data = base64.b64encode(buffer.getvalue()).decode()
        except Exception:
            raise
        else:
            return b64data


