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
            return r.json()["choices"][0]["message"]["content"]
        except Exception as e:
            return f"Ошибка: {str(e)}"


# Создаем экземпляр для импорта
api = McSixRuAPI()
a = api.a