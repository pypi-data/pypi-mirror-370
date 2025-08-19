from django.apps import AppConfig


class YandexCaptchaConfig(AppConfig):
    name = "yandex_captcha"
    verbose_name = "Yandex Captcha"

    def ready(self):
        pass
