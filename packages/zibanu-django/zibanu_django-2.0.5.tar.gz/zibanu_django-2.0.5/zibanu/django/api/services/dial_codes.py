# -*- coding: utf-8 -*-

#  Developed by CQ Inversiones SAS. Copyright ©. 2019 - 2024. All rights reserved.
#  Desarrollado por CQ Inversiones SAS. Copyright ©. 2019 - 2024. Todos los derechos reservados.

# ****************************************************************
# IDE:          PyCharm
# Developed by: macercha
# Date:         4/04/24
# Project:      Zibanu Django
# Module Name:  dial_codes
# Description:
# ****************************************************************
from rest_framework import status
from rest_framework.response import Response
from zibanu.django.lib import DialCodes
from zibanu.django.rest_framework.viewsets import ViewSet


class DialCodesViewSet(ViewSet):
    def list(self, request) -> Response:
        name = True if request.data.get("sorted", "name") == "name" else False
        country_codes = DialCodes.sorted(alphabetic=name)
        list_return = [{"name": x[1] + " " + x[0], "dial_code": x[0]} for x in country_codes]
        return Response(data=list_return, status=status.HTTP_200_OK)
