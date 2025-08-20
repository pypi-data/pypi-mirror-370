# -*- coding: utf-8 -*-

# ****************************************************************
# IDE:          PyCharm
# Developed by: macercha
# Date:         7/07/23 7:31
# Project:      Zibanu - Django
# Module Name:  timezones
# Description:
# ****************************************************************
from timezone_utils.choices import ALL_TIMEZONES_CHOICES
from rest_framework import status
from rest_framework.response import Response

from zibanu.django.rest_framework.viewsets import ViewSet


class TimeZoneViewSet(ViewSet):
    """
    View set to expose TimeZone available list.
    """

    def list(self, request) -> Response:
        """
        List timezones available

        Parameters
        ----------
        request: HTTP request object

        Returns
        -------
        response: Response object with status and list of timezones.
            status = 200 if length of timezones list > 0, else 204

        """
        timezones = {
            "timezones": []
        }

        for timezone_tuple in ALL_TIMEZONES_CHOICES:
            timezones["timezones"].append(timezone_tuple[0])

        http_status = status.HTTP_200_OK if len(timezones) > 0 else status.HTTP_204_NO_CONTENT

        return Response(status=http_status, data=timezones)
