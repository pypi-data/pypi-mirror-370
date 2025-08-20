# -*- coding: utf-8 -*-

#  Developed by CQ Inversiones SAS. Copyright ©. 2019 - 2022. All rights reserved.
#  Desarrollado por CQ Inversiones SAS. Copyright ©. 2019 - 2022. Todos los derechos reservado

# ****************************************************************
# IDE:          PyCharm
# Developed by: macercha
# Date:         12/12/22 12:03 PM
# Project:      Zibanu Django Project
# Module Name:  date_time
# Description:
# ****************************************************************
import logging
import traceback
from django.utils import timezone
from datetime import datetime
from zoneinfo import ZoneInfo


def change_timezone(date_to_change: datetime, new_timezone: ZoneInfo = None) -> datetime:
    """
    Function to change timezone to a datetime value.

    Parameters
    ----------
    date_to_change : Datetime value to change timezone.
    new_timezone : New timezone from ZoneInfo.

    Returns
    -------
    Datetime with a new timezone.
    """
    # If timezone is none, assume default time zone from django
    if new_timezone is None:
        new_timezone = timezone.get_default_timezone()

    try:
        date_to_change = date_to_change.replace(tzinfo=new_timezone)
    except ValueError as exc:
        pass
    except Exception as exc:
        logging.warning(str(exc))
        logging.debug(traceback.format_exc())
        raise Exception from exc
    else:
        return date_to_change


def add_timezone(date_to_change: datetime, tz: ZoneInfo = None) -> datetime:
    """
    Function to add timezone to a naive datetime value.

    Parameters
    ----------
    date_to_change : Naive datetime value to add timezone.
    tz : Timezone to be assigned a datetime value.

    Returns
    -------
    Datetime with a new timezone.
    """
    if tz is None:
        tz = timezone.get_default_timezone()

    if timezone.is_naive(date_to_change):
        date_to_change = tz.make_aware(date_to_change, timezone=tz)
    return date_to_change
