# -*- coding: utf-8 -*-

#  Developed by CQ Inversiones SAS. Copyright ©. 2019 - 2023. All rights reserved.
#  Desarrollado por CQ Inversiones SAS. Copyright ©. 2019 - 2023. Todos los derechos reservado

# ****************************************************************
# IDE:          PyCharm
# Developed by: macercha
# Date:         10/01/23 1:47 PM
# Project:      Zibanu Django Project
# Module Name:  code_generator
# Description:
# ****************************************************************
import logging
import os
import re
import string
import secrets
import traceback
from uuid import SafeUUID, UUID

from django.utils.translation import gettext_lazy as _

from zibanu.django.lib.classes.regex import RegEx


class CodeGenerator:
    """
    Class to generate different types of codes randomly.
    """
    punctuation = "\u00A1!#$%&()*+.@/_\u002D"

    def __init__(self, action: str, is_safe: bool = True, code_length: int = 8):
        """
        Constructor method

        Parameters
        ----------
        action : Code of action to reference it at cache if needed.
        is_safe : Flag to indicate if it uses UUID safe mode.
        code_length : Length of generated code
        """
        self.__action = action
        self._uuid_safe = SafeUUID.safe if is_safe else SafeUUID.unsafe
        self.__code_length = code_length
        self.__code = None
        self.__uuid = None

    @property
    def is_safe(self):
        """
        Property getter for _uuid_safe value

        Returns
        -------
        Boolean value: True if UUID uses safe mode, otherwise False
        """
        return self._uuid_safe == SafeUUID.safe

    @is_safe.setter
    def is_safe(self, value: bool):
        """
        Property setter for _uuid_safe value

        Parameters
        ----------
        value : Boolean parameter to set SafeUUID.safe if True, else set SafeUUID.unsafe
        """
        self._uuid_safe = SafeUUID.safe if value else SafeUUID.unsafe

    @property
    def code(self) -> str:
        """
        Property getter for __code value

        Returns
        -------
        String value with generated code
        """
        return self.__code

    @property
    def action(self) -> str:
        """
        Property getter for __action value

        Returns
        -------
        String value with action description
        """
        return self.__action

    def get_numeric_code(self, length: int = None) -> str:
        """
        Get a numeric code with the length defined in the constructor or received in the parameter "length" of
        this method.

        Parameters
        ----------
        length : Length of generated code. Override length defined in the class.

        Returns
        -------
        String with numeric code
        """
        if length is not None:
            self.__code_length = length
        self.__code = "".join(secrets.choice(string.digits) for i in range(self.__code_length))
        return self.code

    def get_alpha_numeric_code(self, length: int = None) -> str:
        """
        Get an alphanumeric code with the length defined in the constructor or received in the parameter "length"
        of this method.

        Parameters
        ----------
        length : Length of generated code. This parameter override length defined in the class.

        Returns
        -------
        String with numeric code
        """
        if length is not None:
            self.__code_length = length
        # Force LowerCase
        self.__code = "".join(secrets.choice(string.ascii_lowercase) for i in range(self.__code_length * 2))
        # Force UpperCase
        self.__code = "".join(
            secrets.choice(string.ascii_uppercase + self.__code) for i in range(self.__code_length * 2))
        # Force include digits
        self.__code = self.code[0:1] + "".join(
            secrets.choice(string.digits + self.code) for i in range(self.__code_length - 1))
        return self.code

    def get_secure_code(self, length: int = None) -> str:
        """
        Get a secure code with the length defined in the constructor or received in the parameter "length" of
        this method.

        Parameters
        ----------
        length : Length of generated code. This parameter override length defined in the class.

        Returns
        -------
        String with numeric code
        """
        if length is not None:
            self.__code_length = length
        # Get Alphanumeric code
        self.__code = self.get_alpha_numeric_code(self.__code_length)
        # Force include punctuation
        self.__code = self.code[0:1] + "".join(
            secrets.choice(self.punctuation + string.digits + self.__code) for i in range(self.__code_length - 1))
        return self.code

    def generate_uuid(self) -> bool:
        """
        Method to generate a UUID in safe mode, depending on the parameter set in the constructor

        Returns
        -------
        True if successfully, otherwise False.
        """
        try:
            self.__uuid = UUID(bytes=os.urandom(16), version=4, is_safe=self._uuid_safe)
        except Exception as exc:
            logging.warning(str(exc))
            logging.debug(traceback.format_exc())
            return False
        else:
            return True

    def generate_dict(self, is_numeric: bool = True) -> dict:
        """
        Method to generate a dictionary with uuid, code and action.

        Parameters
        ----------
        is_numeric : Flag to indicate if generated code is numeric or alphanumeric.

        Returns
        -------
        Dictionary with uuid, code and action keys.
        """
        if is_numeric:
            self.get_numeric_code()
        else:
            self.get_alpha_numeric_code()

        if self.generate_uuid():
            return {"uuid": self.__uuid, "code": self.code, "action": self.action}
        else:
            raise ValueError(_("The generated values are invalid."))

    @classmethod
    def validate_code(cls, code: str, min_length: int = 8, max_length: int = 32, secure: bool = False) -> bool:
        """
        Class method to validate if code is secure.

        Parameters
        ----------
        code : str
            Code to be validated
        min_length : int
            Min length of code to be validated
        max_length : int
            Max length of code to be validated
        secure : boolean
            If you validate a secure password.

        Returns
        -------
        b_return : bool
            True if validation success, otherwise False
        """
        b_return = False
        if re.search(RegEx.get(body=[RegEx.LETTERS, RegEx.DIGITS, cls.punctuation], min_length=min_length,
                               max_length=max_length), code):
            b_return = True
            if secure:
                is_punctuation = False
                is_numeric = False
                is_lowercase = False
                is_uppercase = False
                for char in code:
                    if not is_punctuation and char in cls.punctuation:
                        is_punctuation = True
                    if not is_numeric and char in string.digits:
                        is_numeric = True
                    if not is_lowercase and char in string.ascii_lowercase:
                        is_lowercase = True
                    if not is_uppercase and char in string.ascii_uppercase:
                        is_uppercase = True
                    b_return = is_punctuation and is_lowercase and is_uppercase and is_numeric
                    if b_return:
                        break
        return b_return
