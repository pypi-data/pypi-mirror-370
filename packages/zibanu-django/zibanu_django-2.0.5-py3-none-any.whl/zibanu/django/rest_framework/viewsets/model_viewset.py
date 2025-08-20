# -*- coding: utf-8 -*-

#  Developed by CQ Inversiones SAS. Copyright ©. 2019 - 2022. All rights reserved.
#  Desarrollado por CQ Inversiones SAS. Copyright ©. 2019 - 2022. Todos los derechos reservado

# ****************************************************************
# IDE:          PyCharm
# Developed by: macercha
# Date:         19/12/22 3:18 PM
# Project:      Zibanu Django Project
# Module Name:  model_viewset
# Description:
# ****************************************************************
from typing import Any

from django.db import DatabaseError
from django.conf import settings
from django.db.models import ProtectedError, RestrictedError
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import ValidationError as CoreValidationError
from rest_framework import authentication
from rest_framework import permissions
from rest_framework import status
from rest_framework.request import Request
from rest_framework.generics import QuerySet
from rest_framework.viewsets import ModelViewSet as RestModelViewSet
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework_simplejwt.authentication import JWTTokenUserAuthentication

from zibanu.django.rest_framework.exceptions import APIException
from zibanu.django.rest_framework.exceptions import NotImplementedException
from zibanu.django.rest_framework.exceptions import ValidationError
from zibanu.django.lib.utils import ErrorMessages


class ModelViewSet(RestModelViewSet):
    """
    Inherited class from rest_framework.viewsets.ModelViewSet to override
    """
    authentication_classes = list()
    model = None
    http_method_names = ["post"]
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes.append(JWTTokenUserAuthentication)

    if settings.DEBUG:
        authentication_classes.append(authentication.TokenAuthentication)

    def perform_authentication(self, request: Request):
        """
        Override method to intercept InvalidToken exception.

        Parameters
        ----------
        request: Request
            Request object from HTTP

        Returns
        -------
        None
        """
        try:
            super().perform_authentication(request)
        except InvalidToken as exc:
            detail = []
            if isinstance(exc.detail, dict) and "messages" in exc.detail and isinstance(exc.detail["messages"], list):
                for message in exc.detail.get("messages", []):
                    if "message" in message:
                        detail.append(message.get("message"))
            if len(detail) == 0:
                detail.append(_("Invalid Token"))
            raise APIException(detail=detail, code="invalid_token", status_code=exc.status_code) from exc
        except Exception as exc:
            raise APIException(str(exc), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR) from exc

    @staticmethod
    def _get_pk(request) -> Any:
        """
        Get PK value from received request data dictionary.

        Parameters
        ----------
        request: Request object from HTTP

        Returns
        -------
        pk_value: Value obtained from request.data
        """
        if request.data:
            if "pk" in request.data.keys():
                pk_value = request.data.get("pk", None)
            elif "id" in request.data.keys():
                pk_value = request.data.get("id", None)
            else:
                raise APIException(ErrorMessages.DATA_REQUIRED, "pk_required", status.HTTP_406_NOT_ACCEPTABLE)
        else:
            raise APIException(ErrorMessages.DATA_REQUIRED, "pk_required", status.HTTP_406_NOT_ACCEPTABLE)
        return pk_value

    def get_queryset(self, **kwargs) -> QuerySet:
        """
        Get a queryset from model from **kwargs parameters. If you want queryset pk based on, send "pk" key in kwargs.
        Parameters
        ----------
        **kwargs: Dictionary with key, value parameters.

        Returns
        -------
        qs: Queryset object from model
        """
        pk = kwargs.get("pk", None)
        qs = self.model.objects.get_queryset()
        if pk is not None:
            qs = qs.filter(pk=pk)
        elif len(kwargs) > 0:
            qs = qs.filter(**kwargs)
        else:
            qs = qs.all()

        return qs

    @staticmethod
    def __get_detail_exception(exc):
        """
        Gets the details of the ValidationError exception from django.core.exception.
        :param exc: Error Object.
        :return: Details of the ValidationError exception.
        """
        detail = exc.message_dict
        if exc.error_dict.get("__all__", None) is not None:
            error_list = []
            for e in exc.error_dict.get("__all__", None):
                model_name = e.params.get('model_name')
                message = e.params.get("field_labels") + _(" already exists.")
                error_list.append(f"{model_name}: {message}")
            detail = error_list
        return detail

    def _list(self, request, *args, **kwargs) -> Response:
        """
        Protected method to get a list of records from model entity

        Parameters
        ----------
        request: Request object from HTTP
        *args: Tuple of parameters
        **kwargs: Dictionary of key, value parameters.

        Returns
        -------
        response: Response object with status and dataset list.
            status -> 200 if data exists
            status -> 204 if empty data
        """
        try:
            # Get Context
            context = kwargs.pop("context", None)
            # Get Order by
            order_by = None
            if "order_by" in kwargs.keys():
                order_by = kwargs.pop("order_by")
                if isinstance(order_by, str):
                    order_by = (order_by,)

            qs = self.get_queryset(**kwargs)

            # Set Order by
            if order_by is not None:
                qs = qs.order_by(*order_by)

            serializer = self.get_serializer(instance=qs, many=True, context=context)
            data_return = serializer.data
            status_return = status.HTTP_200_OK if len(data_return) > 0 else status.HTTP_204_NO_CONTENT
            data_return = data_return
        except APIException:
            raise
        except CoreValidationError as exc:
            raise APIException(detail=exc.message_dict, status_code=status.HTTP_406_NOT_ACCEPTABLE) from exc
        except Exception as exc:
            raise APIException(detail=str(exc), code="not_controlled_exception",
                               status_code=status.HTTP_500_INTERNAL_SERVER_ERROR) from exc
        else:
            return Response(data=data_return, status=status_return)

    def list(self, request, *args, **kwargs):
        """
        Overridden class method to disallow access

        Parameters
        ----------
        request :   Request object from HTTP
        args :      Tuple of parameters
        kwargs :    Dictionary of key, value parameters

        Returns
        -------
        response: Response error with HTTP 405 status code
        """
        raise NotImplementedException()

    def _retrieve(self, request, *args, **kwargs) -> Response:
        """
        REST service to get a record filtered by pk.

        Parameters
        ----------
        request: Request object from HTTP
        *args: Tuple of parameters values
        **kwargs: Dictionary with key, value parameter

        Returns
        -------
        response: Response object with status 200 if record exists and data record. If record does not exist,
        an exception is launched.
        """
        try:
            pk = self._get_pk(request)
            data_record = self.get_queryset(pk=pk).get()
            data_return = self.get_serializer(data_record).data
            status_return = status.HTTP_200_OK
        except APIException:
            raise
        except ObjectDoesNotExist as exc:
            raise APIException(detail=ErrorMessages.NOT_FOUND, code="doest_not_exists",
                               status_code=status.HTTP_404_NOT_FOUND) from exc
        except CoreValidationError as exc:
            raise APIException(detail=exc.message_dict, status_code=status.HTTP_406_NOT_ACCEPTABLE) from exc
        except Exception as exc:
            raise APIException(detail=str(exc), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR) from exc
        else:
            return Response(status=status_return, data=data_return)

    def retrieve(self, request, *args, **kwargs):
        """
        Overridden class method to disallow access

        Parameters
        ----------
        request :   Request object from HTTP
        args :      Tuple of parameters
        kwargs :    Dictionary of key, value parameters

        Returns
        -------
        response: Response error with HTTP 405 status code
        """
        raise NotImplementedException()

    def _create(self, request, *args, **kwargs) -> Response:
        """
        REST service for create a model record.

        Parameters
        ----------
        request: Request object from HTTP
        *args: Tuple of parameters values
        **kwargs: Dictionary with key, value parameter

        Returns
        -------
        response: Response object with status 201 if successfully and record created from model object.
        """
        try:
            data_return = []
            status_return = status.HTTP_400_BAD_REQUEST
            request_data = request.data
            context = kwargs.get("context", {})
            context["request"] = request

            if len(request_data) > 0:
                serializer = self.get_serializer(data=request_data, context=context)
                if serializer.is_valid(raise_exception=True):
                    created_record = serializer.create(validated_data=serializer.validated_data)
                    if created_record is not None:
                        data_return = self.get_serializer(created_record).data
                        status_return = status.HTTP_201_CREATED
                    else:
                        raise ValidationError(ErrorMessages.CREATE_ERROR, "create_object")
            else:
                raise ValidationError(ErrorMessages.DATA_REQUIRED, "data_required")
        except DatabaseError as exc:
            raise APIException(detail=str(exc), code="database_error",
                               status_code=status.HTTP_500_INTERNAL_SERVER_ERROR) from exc
        except ValidationError as exc:
            raise APIException(detail=exc.detail, status_code=status.HTTP_406_NOT_ACCEPTABLE) from exc
        except CoreValidationError as exc:
            raise APIException(detail=self.__get_detail_exception(exc),
                               status_code=status.HTTP_406_NOT_ACCEPTABLE) from exc
        except APIException:
            raise
        except Exception as exc:
            raise APIException(detail=str(exc), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR) from exc
        else:
            return Response(status=status_return, data=data_return)

    def create(self, request, *args, **kwargs):
        """
        Overridden class method to disallow access

        Parameters
        ----------
        request :   Request object from HTTP
        args :      Tuple of parameters
        kwargs :    Dictionary of key, value parameters

        Returns
        -------
        response: Response error with HTTP 405 status code
        """
        raise NotImplementedException()

    def _update(self, request, *args, **kwargs) -> Response:
        """
        REST service to update an existent record from model.

        Parameters
        ----------
        request: Request object from HTTP
        *args: Tuple of parameters values
        **kwargs: Dictionary with key, value parameter

        Returns
        -------
        response: Response object with status 200 if successfully and record updated from model object.
        """
        try:
            context = kwargs.get("context", {})
            context["request"] = request
            pk = self._get_pk(request)
            data_record = self.get_queryset(pk=pk).get()
            serializer = self.get_serializer(data_record, data=request.data, partial=True, context=context)
            if serializer.instance and serializer.is_valid(raise_exception=True):
                updated = serializer.update(instance=serializer.instance, validated_data=serializer.validated_data)
                if updated is not None:
                    data_return = self.get_serializer(updated).data
                    status_return = status.HTTP_200_OK
                else:
                    raise APIException(ErrorMessages.UPDATE_ERROR, "update", status.HTTP_418_IM_A_TEAPOT)
            else:
                raise APIException(ErrorMessages.NOT_FOUND, "update", status.HTTP_404_NOT_FOUND)
        except ObjectDoesNotExist as exc:
            raise APIException(ErrorMessages.NOT_FOUND, "update", status.HTTP_404_NOT_FOUND) from exc
        except ValidationError as exc:
            raise APIException(detail=exc.detail, status_code=status.HTTP_406_NOT_ACCEPTABLE) from exc
        except CoreValidationError as exc:
            raise APIException(detail=self.__get_detail_exception(exc),
                               status_code=status.HTTP_406_NOT_ACCEPTABLE) from exc
        except (ProtectedError, RestrictedError) as exc:
            raise APIException(detail=ErrorMessages.PROTECTED_ERROR, status_code=status.HTTP_409_CONFLICT,
                               code="protected_error") from exc
        except DatabaseError as exc:
            raise APIException(ErrorMessages.UPDATE_ERROR, status_code=status.HTTP_409_CONFLICT,
                               code="database_error") from exc
        except APIException:
            raise
        except Exception as exc:
            raise APIException(detail=str(exc), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR) from exc
        else:
            return Response(data=data_return, status=status_return)

    def update(self, request, *args, **kwargs):
        """
        Overridden class method to disallow access

        Parameters
        ----------
        request :   Request object from HTTP
        args :      Tuple of parameters
        kwargs :    Dictionary of key, value parameters

        Returns
        -------
        response: Response error with HTTP 405 status code
        """
        raise NotImplementedException()

    def _destroy(self, request, *args, **kwargs) -> Response:
        """
        REST service to delete a record from model.

        Parameters
        ----------
        request: Request object from HTTP
        *args: Tuple of parameters values
        **kwargs: Dictionary with key, value parameter

        Returns
        -------
        response: Response object with status 200 if successfully.
        """
        try:
            pk = self._get_pk(request)
            data_record = self.get_queryset(pk=pk)
            if data_record:
                data_record.delete()
                status_return = status.HTTP_200_OK
            else:
                raise APIException(ErrorMessages.NOT_FOUND, "delete", status.HTTP_404_NOT_FOUND)
        except ValidationError as exc:
            raise APIException(detail=str(exc.detail), status_code=status.HTTP_406_NOT_ACCEPTABLE,
                               code="validation_error") from exc
        except CoreValidationError as exc:
            raise APIException(detail=exc.message_dict, status_code=status.HTTP_406_NOT_ACCEPTABLE,
                               code="validation_error") from exc
        except (ProtectedError, RestrictedError) as exc:
            raise APIException(detail=ErrorMessages.PROTECTED_ERROR, status_code=status.HTTP_409_CONFLICT,
                               code="protected_error") from exc
        except DatabaseError as exc:
            raise APIException(detail=ErrorMessages.DELETE_ERROR, status_code=status.HTTP_409_CONFLICT,
                               code="database_error") from exc
        except APIException:
            raise
        except Exception as exc:
            raise APIException(detail=str(exc), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR) from exc
        else:
            return Response(status=status_return)

    def _destroy_list(self, request, *args, **kwargs):
        """
        REST service to delete a list of records from the model.

        Parameters
        ----------
        request: Request object from HTTP
        *args: Tuple of parameters values
        **kwargs: Dictionary with key, value parameter

        Returns
        -------
        response: Response object with status 200 if successfully.
        """
        try:
            ids = request.data.get("ids", [])
            if len(request.data) > 0 and len(ids) > 0:
                if isinstance(ids, list):
                    data_records = self.get_queryset(id__in=ids)
                    if data_records.count() > 0:
                        data_records.delete()
                        status_return = status.HTTP_200_OK
                    else:
                        raise APIException(ErrorMessages.NOT_FOUND, "delete", status.HTTP_404_NOT_FOUND)
                else:
                    raise APIException(detail=f"ids: {ErrorMessages.FIELD_LIST_ERROR}", code="type_field_error",
                                       status_code=status.HTTP_406_NOT_ACCEPTABLE)
            else:
                raise APIException(detail=ErrorMessages.DATA_REQUIRED, status_code=status.HTTP_406_NOT_ACCEPTABLE,
                                   code="data_required")
        except ValidationError as exc:
            raise APIException(detail=str(exc.detail), code="validation_error",
                               status_code=status.HTTP_406_NOT_ACCEPTABLE) from exc
        except CoreValidationError as exc:
            raise APIException(detail=exc.message_dict, code="validation_error",
                               status_code=status.HTTP_406_NOT_ACCEPTABLE) from exc
        except (ProtectedError, RestrictedError) as exc:
            raise APIException(detail=ErrorMessages.PROTECTED_ERROR, status_code=status.HTTP_409_CONFLICT,
                               code="protected_error") from exc
        except DatabaseError as exc:
            raise APIException(ErrorMessages.DELETE_ERROR, "database_error", status.HTTP_409_CONFLICT) from exc
        except APIException:
            raise
        except Exception as exc:
            raise APIException(detail=str(exc), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR) from exc
        else:
            return Response(status=status_return)

    def destroy(self, request, *args, **kwargs):
        """
        Overridden class method to disallow access

        Parameters
        ----------
        request :   Request object from HTTP
        args :      Tuple of parameters
        kwargs :    Dictionary of key, value parameters

        Returns
        -------
        response: Response error with HTTP 405 status code
        """

        raise NotImplementedException()
