import os
import re
import json
from gigachat import GigaChat
from gigachat.models import Chat, Function, FunctionParameters, Messages, MessagesRole
from gigachat.exceptions import ResponseError
from dotenv import load_dotenv

load_dotenv()
CREDS_ENV = "GIGACHAT_CREDS"

def _get_credentials():
    creds = os.getenv(CREDS_ENV)
    if not creds:
        raise RuntimeError(f"Environment variable {CREDS_ENV} is missing")
    return creds

def _make_client():
    return GigaChat(credentials=_get_credentials(), verify_ssl_certs=False)

def safe_calculate(expression: str) -> str:
    """Выполняет математическое выражение безопасно"""
    if not re.fullmatch(r'[\d+\-*/().\s]+', expression):
        return "Ошибка: выражение содержит недопустимые символы."
    try:
        if len(expression) > 50:
            return "Ошибка: выражение слишком сложное или длинное."
        result = eval(expression, {"__builtins__": {}}, {})
        print("функция вызвана")
        return str(result)
    except Exception as e:
        return f"Ошибка вычисления: {str(e)}"

# Создаем объект функции для GigaChat
calculate_func = Function(
    name="calculate",
    description="Выполняет математические вычисления. Передавай ТОЛЬКО выражение в виде строки, например: '2 + 3 * 4'.",
    parameters=FunctionParameters(
        type="object",
        properties={
            "expression": {
                "type": "string",
                "description": "Математическое выражение (только цифры, +, -, *, /, **, скобки)"
            }
        },
        required=["expression"],
    ),
)

class ResilientGiga:
    def __init__(self):
        self._client = _make_client()

    def _is_auth_error(self, exc: Exception) -> bool:
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
        if any(k in s for k in ("401", "unauthoriz", "invalid token", "token expired", "can't decode 'authorization'")):
            return True
        return False

    def chat(self, prompt: str):
        messages = [Messages(role=MessagesRole.USER, content=prompt)]
        chat_payload = Chat(messages=messages, functions=[calculate_func])
        try:
            resp = self._client.chat(chat_payload).choices[0]
            message = resp.message

            if resp.finish_reason == "function_call":
                func_call = message.function_call
                if func_call.name == "calculate":
                    expr = func_call.arguments.get("expression", "")
                    result = safe_calculate(expr)
                    # Возвращаем результат модели
                    messages.extend([
                        message,
                        Messages(role=MessagesRole.FUNCTION, content=result)
                    ])
                    # Финальный ответ от модели
                    final_resp = self._client.chat(Chat(messages=messages)).choices[0]
                    return final_resp.message.content
            else:
                return message.content

        except Exception as e:
            if self._is_auth_error(e):
                self._client = _make_client()
                return self.chat(prompt)
            raise

if __name__ == "__main__":
    g = ResilientGiga()
    print(g.chat("Сколько будет 3*(4+5)**2?"))
    print(g.chat("Вычисли 12/4 + (6*3)**2"))
