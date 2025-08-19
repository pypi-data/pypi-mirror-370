from urllib.parse import urlencode

from django.conf import settings
from django.forms.widgets import Widget

from django_yandex_captcha.constants import DEFAULT_YANDEX_CAPTCHA_DOMAIN


class YandexCaptcha(Widget):
    template_name = "django_yandex_captcha/widget.html"
    yandex_captcha_response_name = "smart-token"

    def __init__(self, api_params=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.api_params = api_params or {}

        if not self.attrs.get("class", None):
            self.attrs["class"] = "yandex-captcha"

    def value_from_datadict(self, data, files, name):
        return data.get(self.yandex_captcha_response_name, None)

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        api_params = urlencode(self.api_params)
        domain = getattr(
            settings, "YANDEX_CAPTCHA_DOMAIN", DEFAULT_YANDEX_CAPTCHA_DOMAIN
        )
        context.update(
            {
                "client_key": self.attrs["data-clientkey"],
                "api_params": api_params,
                "yandex_captcha_domain": domain,
            }
        )
        return context

    def build_attrs(self, base_attrs, extra_attrs=None):
        attrs = super().build_attrs(base_attrs, extra_attrs)
        return attrs
