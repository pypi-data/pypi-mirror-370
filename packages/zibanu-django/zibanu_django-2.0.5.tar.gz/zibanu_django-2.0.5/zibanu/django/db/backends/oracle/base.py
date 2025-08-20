# -*- coding: utf-8 -*-

#  Developed by CQ Inversiones SAS. Copyright ©. 2019 - 2023. All rights reserved.
#  Desarrollado por CQ Inversiones SAS. Copyright ©. 2019 - 2023. Todos los derechos reservado

# ****************************************************************
# IDE:          PyCharm
# Developed by: macercha
# Date:         6/02/23 20:30
# Project:      Zibanu Django Project
# Module Name:  base
# Description:
# ****************************************************************
from django.db.backends.utils import truncate_name
from django.db.backends.oracle.base import DatabaseWrapper as OracleWrapper
from django.db.backends.oracle.operations import DatabaseOperations as OracleOperations


class DatabaseOperations(OracleOperations):
    """
    Class to override DatabaseOperation class from django Oracle Client.
    This class allow the use of fields with names between '""', like reserved words for example.
    """

    def quote_name(self, name):
        """
        Override Method to get the field name respecting double quotes.
        Parameters
        ----------
        name: Name of table field

        Returns
        -------
        name: Name of field with double quotes if applies.
        """
        if not name.startswith('"') and not name.endswith('"'):
            name = '"%s"' % truncate_name(name.upper(), self.max_name_length())
        return name.replace("%", "%%")


class DatabaseWrapper(OracleWrapper):
    """
    Database wrapper class to use a new DatabaseOperation class
    """
    ops_class = DatabaseOperations

