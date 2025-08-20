# -*- coding: utf-8 -*-

#  Developed by CQ Inversiones SAS. Copyright ©. 2019 - 2023. All rights reserved.
#  Desarrollado por CQ Inversiones SAS. Copyright ©. 2019 - 2023. Todos los derechos reservado

# ****************************************************************
# IDE:          PyCharm
# Developed by: macercha
# Date:         3/12/23 07:06
# Project:      Zibanu - Django
# Module Name:  receivers_utils
# Description:
# ****************************************************************
# Default imports
import logging
import traceback
from django.utils.translation import gettext_lazy as _
from typing import Any


def get_receiver_id(**kwargs) -> str:
    if "signal" in kwargs:
        receivers = kwargs.get("signal").receivers
        receiver_id = receivers[-1][0][0]
        if isinstance(receiver_id, str):
            return receiver_id


def get_sender_name(sender: Any) -> str:
    if isinstance(sender, str):
        sender_name = sender
    elif isinstance(sender, type):
        sender_name = sender.__name__
    elif isinstance(sender, object):
        sender_name = sender.__class__.__name__
        if hasattr(sender, "action"):
            sender_name += "." + sender.action
    else:
        sender_name = ""
    return sender_name
