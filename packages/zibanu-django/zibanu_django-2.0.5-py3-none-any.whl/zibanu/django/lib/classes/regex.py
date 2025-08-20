# -*- coding: utf-8 -*-
#  Developed by CQ Inversiones SAS. Copyright ©. 2019 - 2024. All rights reserved.
#  Desarrollado por CQ Inversiones SAS. Copyright ©. 2019 - 2024. Todos los derechos reservados.
# ****************************************************************
# IDE:          PyCharm
# Developed by: macercha
# Date:         29/05/24
# Project:      Zibanu Django
# Module Name:  regex
# Description:
# ****************************************************************
class RegEx:
    """
    Class with get method that allows creating regular expressions with different parameters.

    CONSTANTS:
    There are different constants defined and that can be used.

    LOWERCASE

    UPPERCASE

    ALPHANUMERIC

    DIGITS

    LETTERS

    SYMBOLS

    PUNCTUATION

    PHONE_NUMBER - Regular Expression

    TAX_ID - Regular Expression

    HEXA_LIST - Regular Expression

    MAC_ADDRESS - Regular Expression
    """
    __start = "^"
    __end = "$"
    __lowercase = "a-z"
    __uppercase = "A-Z"
    __digits = "0-9"
    __punctuation = r"""!"#$%&'()*+,./:;<=>?@[\]^_`{|}~-"""
    __symbols = "\u00A1!#$%&()*+.@/_\\-"

    LOWERCASE = __lowercase
    UPPERCASE = __uppercase
    ALPHANUMERIC = __lowercase + __uppercase + __digits
    DIGITS = __digits
    LETTERS = __lowercase + __uppercase
    SYMBOLS = __symbols
    PUNCTUATION = __punctuation
    PHONE_NUMBER = r"^([+][\d]{12})$"
    TAX_ID = r"^(?!000000$|123456$)(?=[a-zA-Z0-9]{6,20}$)(?!.*?[a-zA-Z]*?0{6})[a-zA-Z0-9]*[^ñ]*$"
    HEXA_LIST = r"^(0x[\da-fA-F]{2})(,0x[\da-fA-F]{2})*$"
    MAC_ADDRESS = r"^([0-9A-Fa-f]{2}[:]){5}([0-9A-Fa-f]{2})$"

    @classmethod
    def get(cls, body: list, starts_equal: str = None, starts_with: list = None, ends_with: list = None,
            ends_equal: str = None, min_length: int = None, max_length: int = None, regex: bool = False):
        """
        Method that allows creating regular expressions with different parameters.
        :param body: Regular expression body.
        :param starts_equal: Starts with specified characters.
        :param starts_with: Starts with at least one of the specified characters.
        :param ends_equal: Ends with specified characters.
        :param ends_with: Ends with at least one of the specified characters.
        :param min_length: Minimum length of the regular expression.
        :param max_length: Maximum length of the regular expression.
        :param regex: If it is true, a regex must be passed in the body parameter.
        :return: Regular Expression.
        """
        start_pattern = ""
        body_pattern = ""
        end_pattern = ""
        length_pattern = ""
        pattern = r""
        if regex:
            pattern = body[0]
        else:
            if starts_equal is not None:
                start_pattern = starts_equal
            elif starts_with is not None:
                for start in starts_with:
                    start_pattern = start_pattern + start
                start_pattern = "[" + start_pattern + "]"
            if ends_equal:
                end_pattern = ends_equal
            if ends_with is not None:
                for end in ends_with:
                    end_pattern = end_pattern + end
                end_pattern = "[" + end_pattern + "]"
            for b in body:
                body_pattern = body_pattern + b
            body_pattern = "[" + body_pattern + "]"
            if min_length is not None or max_length is not None:
                if min_length is not None:
                    length_pattern = str(min_length) + ","
                if max_length is not None:
                    if min_length is not None:
                        length_pattern = length_pattern + str(max_length)
                    else:
                        length_pattern = "," + str(max_length)
                length_pattern = "{" + length_pattern + "}"
            if len(pattern) > 0:
                pass
            else:
                pattern = (cls.__start + start_pattern + body_pattern +
                           (length_pattern if len(length_pattern) > 0 else "*") + end_pattern + cls.__end)
        return pattern
