# -*- coding: utf-8 -*-

#  Developed by CQ Inversiones SAS. Copyright ©. 2019 - 2024. All rights reserved.
#  Desarrollado por CQ Inversiones SAS. Copyright ©. 2019 - 2024. Todos los derechos reservado

# ****************************************************************
# IDE:          PyCharm
# Developed by: macercha
# Date:         30/01/24 08:57
# Project:      Zibanu - Django
# Module Name:  model_name
# Description:
# ****************************************************************
# Default imports

MODEL_SEPARATOR = "."


class ModelName(str):
    @property
    def app_label(self):
        return self.split(MODEL_SEPARATOR)[0]

    @property
    def model_name(self):
        return self.split(MODEL_SEPARATOR)[1]
