import os
from gigachat import GigaChat
from gigachat.exceptions import ResponseError
import httpx
from dotenv import load_dotenv

load_dotenv()  # загружает переменные из .env в os.environ
CREDS_ENV = "GIGACHAT_CREDS"  # переменная окружения с site-issued base64-строкой


def _get_credentials():
    creds = os.getenv(CREDS_ENV)
    if not creds:
        raise RuntimeError(f"Environment variable {CREDS_ENV} is missing")
    return creds


def _make_client():
    return GigaChat(credentials=_get_credentials(), verify_ssl_certs=False)


class ResilientGiga:
    def __init__(self):
        self._client = _make_client()

    def _is_auth_error(self, exc: Exception) -> bool:

        # Цель: поймать 401 / invalid token / can't decode Authorization и похожие
        try:
            if isinstance(exc, ResponseError):
                if getattr(exc, "status_code", None) == 401:
                    return True
            resp = getattr(exc, "response", None)
            if resp is not None and getattr(resp, "status_code", None) == 401:
                return True
        except Exception:
            pass
        s = str(exc).lower()
        if any(
            k in s
            for k in (
                "401",
                "unauthoriz",
                "invalid token",
                "token expired",
                "can't decode 'authorization'",
            )
        ):
            return True
        return False

    def chat(self, prompt: str):
        try:
            return self._client.chat(prompt)
        except Exception as e:
            if self._is_auth_error(e):
                # пересоздать клиент на основе переменной окружения (server-issued base64)
                self._client = _make_client()
                return self._client.chat(prompt)
            raise


if __name__ == "__main__":
    g = ResilientGiga()
    resp = g.chat("Привет! Как дела?")
    print(resp.choices[0].message.content)
