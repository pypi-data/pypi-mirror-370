import requests
import json


class McSixRuAPI:
    def __init__(self):
        self.url = "https://openrouter.ai/api/v1/chat/completions"
        self.api_key = "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"

    def a(self, question):
        """Основная функция для запросов к AI"""
        try:
            response = requests.post(
                url=self.url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://github.com/McSixRu/McSixRu",
                    "X-Title": "McSixRu Library",
                },
                data=json.dumps({
                    "model": "deepseek/deepseek-chat-v3-0324:free",
                    "messages": [
                        {
                            "role": "user",
                            "content": question
                        }
                    ]
                }),
                timeout=30
            )

            # Отладочная информация
            print(f"Status Code: {response.status_code}")

            response.raise_for_status()
            response_data = response.json()

            if "choices" in response_data and len(response_data["choices"]) > 0:
                return response_data["choices"][0]["message"]["content"]
            else:
                return f"Ошибка: Неожиданный формат ответа"

        except requests.exceptions.RequestException as e:
            return f"Ошибка запроса: {str(e)}"
        except json.JSONDecodeError as e:
            return f"Ошибка JSON: {str(e)}. Ответ: {response.text}"
        except Exception as e:
            return f"Неожиданная ошибка: {str(e)}"


# Создаем экземпляр для импорта
api = McSixRuAPI()
a = api.a