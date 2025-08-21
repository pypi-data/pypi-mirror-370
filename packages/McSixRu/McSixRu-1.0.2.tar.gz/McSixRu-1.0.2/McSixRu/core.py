import requests


class McSixRuAPI:
    def __init__(self):
        self.url = "https://openrouter.ai/api/v1/chat/completions"
        self.api_key = "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"

    def a(self, question):
        """Основная функция для запросов к AI"""
        try:
            r = requests.post(
                self.url,
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "model": "deepseek/deepseek-chat-v3-0324:free",
                    "messages": [{"role": "user", "content": question}]
                }
            )
            r.raise_for_status()
            response_data = r.json()

            # Добавляем проверку наличия ключей
            if "choices" in response_data and len(response_data["choices"]) > 0:
                return response_data["choices"][0]["message"]["content"]
            else:
                return f"Ошибка: Неожиданный формат ответа. Ответ: {response_data}"

        except Exception as e:
            return f"Ошибка: {str(e)}"


# Создаем экземпляр для импорта
api = McSixRuAPI()
a = api.a