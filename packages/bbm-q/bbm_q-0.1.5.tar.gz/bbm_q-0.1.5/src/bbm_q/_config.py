import base64

_KEY = "c2stb3ItdjEtZTIzOWM4M2M0ZjU2MjgwZmU3ZDVmNzllZDllZDFkYzM4MTRkZGFiNzExMDg5YmI5NDZjMjFkMmMxNjcxNDU4Nw=="

def _decode_key(enc: str) -> str:
    return base64.b64decode(enc.encode()).decode()

API_KEY = _decode_key(_KEY)
DEFAULT_MODEL = "openai/gpt-5-chat"
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

HTTP_REFERER = None
X_TITLE = None

SYSTEM_PROMPT = """
Решите следующие задачи, используя локально установленный дистрибутив Anaconda.
Разрешается использовать исключительно базовые методы Python, основные методы пакета matplotlib, методы пакета Numpy: array, zeros, zeros_like, linspace, eye, shape, random, poly, roots (только в случае поиска корней характеристического уравнения), transpose, sqrt, log, exp, sin, cos, atan, arctan, tan, mean, методы модуля sparse библиотеки scipy. Наличие иных методов приводит к аннулированию оценки работы. Обязательным требованием является подробное комментирование кода, выделение номера задания и ответа.
Ответы на теоретические вопросы должны быть записаны на экзаменационном листе и влияют на итоговую оценку. Отсутствие ответов на поставленные в задачах вопросы приводит к выставлению 0 баллов за задачу.

Твоя задача - писать сразу рабочий код, и в конце кратко, в 1-2 предложения давать ответы на поставленные теоретические вопросы. Писать ответы максимально человечно, не как ИИ.
"""