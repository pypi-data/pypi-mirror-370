# Django Yandex SmartCaptcha

Django Smart Captcha form field/widget integration app.

## Installation

1. Sign up for [Yandex SmartCaptcha](https://yandex.cloud/en/docs/smartcaptcha/).
2. Install with pip install `django-yandex-captcha`.
3. Configure Yandex SmartCaptcha credentials in `settings.py`:

```python
YANDEX_CAPTCHA_CLIENT_KEY = "..."
YANDEX_CAPTCHA_SERVER_KEY = "..."
```

## Usage

Just add the field to your Django form:

```python
from django import forms
from django_yandex_captcha.fields import YandexCaptchaField


class FormWithCaptcha(forms.Form):
    captcha = YandexCaptchaField()
```

## Credits

Based on [django-recaptcha](https://github.com/django-recaptcha/django-recaptcha).
