import json
from dataclasses import dataclass
from urllib.parse import urlencode
from urllib.request import Request, build_opener

from django.conf import settings

from yandex_captcha.constants import DEFAULT_YANDEX_CAPTCHA_DOMAIN


@dataclass(frozen=True)
class YandexCaptchaResponse:
    status: str

    @property
    def is_valid(self) -> bool:
        return self.status.lower() == "ok"


def validate(server_key: str, token: str, ip: str) -> YandexCaptchaResponse:
    domain = getattr(settings, "YANDEX_CAPTCHA_DOMAIN", DEFAULT_YANDEX_CAPTCHA_DOMAIN)
    params = urlencode(
        {
            "secret": server_key,
            "token": token,
            "ip": ip,
        }
    )
    params = params.encode("utf-8")
    headers = {
        "Content-type": "application/x-www-form-urlencoded",
        "User-agent": "Django Yandex Captcha",
    }
    request_object = Request(
        url=f"https://{domain}/validate", data=params, headers=headers
    )

    opener = build_opener()
    timeout = getattr(settings, "YANDEX_CAPTCHA_VERIFY_REQUEST_TIMEOUT", 10)
    response = opener.open(request_object, timeout=timeout)
    data = json.loads(response.read().decode("utf-8"))
    response.close()

    return YandexCaptchaResponse(status=data["status"])
