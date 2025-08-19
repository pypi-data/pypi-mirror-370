import logging
import sys
from urllib.error import HTTPError

from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from ipware import get_client_ip

from django_yandex_captcha.client import validate
from django_yandex_captcha.widgets import YandexCaptcha

logger = logging.getLogger(__name__)


class YandexCaptchaField(forms.CharField):
    widget = YandexCaptcha
    default_error_messages = {
        "captcha_invalid": _("Error verifying Yandex Captcha, please try again."),
        "captcha_error": _("Error verifying Yandex Captcha, please try again."),
    }

    def __init__(self, client_key=None, server_key=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.required = True

        # Setup instance variables.
        self.server_key = server_key or getattr(
            settings, "YANDEX_CAPTCHA_SERVER_KEY", ""
        )
        self.client_key = client_key or getattr(
            settings, "YANDEX_CAPTCHA_CLIENT_KEY", ""
        )

        # Update widget attrs with data-sitekey.
        self.widget.attrs["data-clientkey"] = self.client_key

    def get_remote_ip(self) -> str | None:
        f = sys._getframe()
        while f:
            request = f.f_locals.get("request")
            if request:
                ip, _ = get_client_ip(request)
                return ip
            f = f.f_back

    def validate(self, value):
        super().validate(value)

        try:
            check_captcha = validate(
                server_key=self.server_key,
                token=value,
                ip=self.get_remote_ip(),
            )

        except HTTPError:  # Catch timeouts, etc
            raise ValidationError(
                self.error_messages["captcha_error"], code="captcha_error"
            )

        if not check_captcha.is_valid:
            logger.warning("Yandex Captcha validation failed")
            raise ValidationError(
                self.error_messages["captcha_invalid"], code="captcha_invalid"
            )
