# -*- coding: utf-8 -*-

# ****************************************************************
# IDE:          PyCharm
# Developed by: macercha
# Date:         16/03/23 10:42
# Project:      Zibanu Django Project
# Module Name:  request_utils
# Description:
# ****************************************************************
import hashlib
from typing import Any
def get_ip_address(request:Any) -> str:
    """
    Get the IP address from HTTP request

    Parameters
    ----------
    request : object: HTTP request object

    Returns
    -------
    ip_address: str: IP address of the HTTP request
    """
    ip_address = None
    if request is not None:
        ip_address = request.META.get("REMOTE_ADDR", None)
    return ip_address

def get_http_origin(request: Any, md5: bool = False) -> str:
    """
    Get http origin from request

    Parameters
    ----------
    request : object: Request object from HTTP
    md5 : str: MD5 hash of request

    Returns
    -------
    http_origin: str: HTTP origin from request
    """
    http_origin = None
    if request is not None:
        http_origin = request.META.get("HTTP_ORIGIN", "undefined")
        if md5:
            http_origin = hashlib.md5(http_origin.encode("utf-8")).hexdigest()
    return http_origin


def get_request_from_stack():
    import inspect
    request = None
    frame_record = [x for x in inspect.stack() if x[3] == "get_response"]
    if len(frame_record) > 0:
        request = frame_record[0].frame.f_locals["request"]
    return request