# -*- coding: utf-8 -*-

#  Developed by CQ Inversiones SAS. Copyright ©. 2019 - 2022. All rights reserved.
#  Desarrollado por CQ Inversiones SAS. Copyright ©. 2019 - 2022. Todos los derechos reservado

# ****************************************************************
# IDE:          PyCharm
# Developed by: macercha
# Date:         20/12/22 2:35 PM
# Project:      Zibanu Django Project
# Module Name:  mail
# Description:
# ****************************************************************
import smtplib
import logging
from django.apps import apps
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.exceptions import TemplateSyntaxError
from django.template.exceptions import TemplateDoesNotExist
from django.template.loader import get_template
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from typing import Any
from uuid import uuid4


class Email(EmailMultiAlternatives):
    """
    Inherited EmailMultiAlternatives class for create an email from html template and html text.
    """

    def __init__(self, subject: str = "", body: str = "", from_email: str = None, to: list = None, bcc: list = None,
                 connection: Any = None, attachments: list = None, headers: dict = None, cc: list = None,
                 reply_to: list = None, context: dict = None):
        """
        Class constructor to override and delegate super constructor class setting some auxiliary attributes.

        Parameters
        ----------
        subject : Subject for email.
        body : Body text for email.
        from_email : From email address
        to : List or tuple of recipient addresses.
        bcc : A list or tuple of addresses used in the “Bcc” header when sending the email.
        connection : Email backend connection instance.
        attachments : List of attachment files.
        headers : A dictionary of extra headers to put on the message. The keys are the header name, values are the header values.
        cc : A list or tuple of recipient address used in the "Cc" header when sending the email.
        reply_to : A list or tuple of recipient addresses used in the "Reply-To" header when sending the email.
        context : Context dictionary for some extra vars.
        """
        # Define message id for unique id
        self.__text_content = None
        self.__html_content = None
        self.__message_id = uuid4().hex
        self.__context = context
        self.error_messages = {
            "error_mail": _("Error sending mail: %(error_str)s with code: %(error_code)d."),
            "template_syntax_error": _("Syntax error loading template %(template)s."),
            "template_not_exists": _("Template %(template)s does not exists.")
        }
        # Set default values
        from_email = from_email if from_email is not None else settings.ZB_MAIL_DEFAULT_FROM
        reply_to = reply_to if reply_to is not None else [settings.ZB_MAIL_REPLY_TO]
        # Analyze errors
        cc = cc if cc is not None else []
        if headers is None:
            headers = {
                "Message-ID": self.__message_id
            }
        else:
            headers["Message-ID"] = self.__message_id
        super().__init__(subject=subject, body=body, from_email=from_email, to=to, bcc=bcc, connection=connection,
                         attachments=attachments, headers=headers, cc=cc, reply_to=reply_to)

    def __get_template_content(self, template: str, context: dict = None) -> Any:
        """
        Return template content after render with context values if exists.

        Parameters
        ----------
        template : Full path and file name of template.
        context : Context dictionary with extra values.

        Returns
        -------
        template_content: String with rendered template.
        """
        try:
            if context is None:
                context = dict()

            if "email_datetime" not in context:
                context["email_datetime"] = timezone.now().astimezone(tz=timezone.get_default_timezone()).strftime(
                    "%Y-%m-%d %H:%M:%S")
            if "email_id" not in context:
                context["email_id"] = str(uuid4())

            template = get_template(template_name=template)
            template_content = template.render(context)
        except TemplateSyntaxError:
            logging.critical(self.error_messages.get("template_syntax_error") % {"template": template})
            raise TemplateSyntaxError(self.error_messages.get("template_syntax_error") % {"template": template})
        except TemplateDoesNotExist:
            logging.critical(self.error_messages.get("template_not_exists") % {"template": template})
            raise TemplateDoesNotExist(self.error_messages.get("template_not_exists") % {"template": template})
        else:
            return template_content

    def set_text_template(self, template: str, context: dict = None):
        """
        Set a text template for body email.

        Parameters
        ----------
        template : Full path and file name of template.
        context : Context dictionary with extra vars.

        """
        if not template.lower().endswith(".txt"):
            template = template + ".txt"

        if context is not None:
            self.__context = context
        self.body = self.__get_template_content(template=template, context=self.__context)

    def set_html_template(self, template: str, context: dict = None):
        """
        Set html template for body email construction.

        Parameters
        ----------
        template : Full path and file name of template.
        context : Context dictionary with extra vars.

        """
        if not template.lower().endswith(".html"):
            template = template + ".html"

        if context is not None:
            self.__context = context
        self.attach_alternative(self.__get_template_content(template=template, context=self.__context), "text/html")

    def send(self, fail_silently=False):
        """
        Override method to send email message.

        Parameters
        ----------
        fail_silently : Flag to determine if an error is caught or not

        """
        smtp_code = 0
        smtp_error = None
        error_messages = {

        }
        try:
            super().send(fail_silently=fail_silently)
        except smtplib.SMTPResponseException as exc:
            smtp_code = exc.smtp_code
            smtp_error = exc.smtp_error
        except smtplib.SMTPException as exc:
            smtp_code = exc.errno
            smtp_error = exc.strerror
        except ConnectionRefusedError as exc:
            smtp_code = exc.errno
            smtp_error = exc.strerror
        finally:

            # Send signal if zibanu.django.logging is installed.
            if apps.is_installed("zibanu.django.logging"):
                from zibanu.django.logging.lib.signals import send_mail
                send_mail.send(sender=self.__class__, mail_from=self.from_email, mail_to=self.to,
                               subject=self.subject, smtp_error=smtp_error, smtp_code=smtp_code)
            # Save on logging class
            if smtp_code != 0 and smtp_error is not None:
                logging.warning(
                    self.error_messages.get("error_mail") % {"error_str": smtp_error, "error_code": smtp_code})
                raise smtplib.SMTPException(
                    self.error_messages.get("error_mail") % {"error_str": smtp_error, "error_code": smtp_code})
