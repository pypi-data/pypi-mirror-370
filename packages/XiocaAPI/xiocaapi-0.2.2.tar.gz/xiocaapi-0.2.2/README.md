# XiocaAPI Python Client

[![PyPI version](https://badge.fury.io/py/xiocaapi.svg)](https://badge.fury.io/py/xiocaapi)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Асинхронный и синхронный клиент для взаимодействия с [Xioca API](https://xioca.live/).

## Установка

```bash
pip install XiocaAPI
```

## Быстрый старт

### 1. Получение API ключа

Для использования библиотеки вам понадобится API ключ.

➡️ Получить его можно бесплатно в Telegram боте: [@xioca_apibot](https://t.me/xioca_apibot)

### 2. Использование

Ключ можно передать напрямую в клиент или использовать переменную окружения `XIOCA_API_KEY`.

### Поддерживаемые модели

**Текстовые модели:**
- `deepseek-v3`
- `deepseek-r1`
- `qwen3`
- `deepcoder`
- `llama-3.3`

**Генерация изображений:**
- `flux`

Текстовые модели поддерживают следующие параметры:
- `online` (boolean) - поиск в интернете
- `temperature` (float/int) - креативность ответа (0-2)

### Асинхронное использование

```python
import asyncio
from XiocaAPI import AsyncXiocaAPI, APIError

async def main():
    # Передайте ключ напрямую:
    client = AsyncXiocaAPI(api_key="ВАШ_КЛЮЧ")
    try:
        # Пример текстового запроса
        response = await client.chat.create(
            model="deepseek-v3",
            messages=[{"role": "user", "content": "Привет, мир!"}],
            online=True,
            temperature=0.7
        )
        print(response.choices[0].message.content)

        # Пример генерации изображения
        image = await client.images.generate(
            model="flux",
            prompt="an eagle soaring over a futuristic city"
        )
        print(image.url)
    except APIError as e:
        print(f"Ошибка API: {e}")
    finally:
        # Важно закрывать клиент, если он создан не через 'async with'
        await client.close()

if __name__ == "__main__":
    asyncio.run(main())
```

### Синхронное использование

```python
from XiocaAPI import XiocaAPI, APIError

try:
    # Передайте ключ напрямую:
    client = XiocaAPI(api_key="ВАШ_КЛЮЧ")

    # Пример текстового запроса
    response = client.chat.create(
        model="deepseek-v3",
        messages=[{"role": "user", "content": "Привет, мир!"}],
        online=False,
        temperature=1.0
    )
    print(response.choices[0].message.content)

    # Пример генерации изображения
    image = client.images.generate(
        model="flux",
        prompt="реалистичный кот в космосе"
    )
    print(image.url)
except APIError as e:
    print(f"Ошибка API: {e}")
```

## Лицензия

Этот проект распространяется под лицензией MIT.
