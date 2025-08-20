# vvz-embed-client

## Quick Start: Примеры запуска

**Вариант 1: через аргументы командной строки**

```sh
python embed_client/example_async_usage.py --base-url http://localhost --port 8001
python embed_client/example_async_usage_ru.py --base-url http://localhost --port 8001
```

**Вариант 2: через переменные окружения**

```sh
export EMBED_CLIENT_BASE_URL=http://localhost
export EMBED_CLIENT_PORT=8001
python embed_client/example_async_usage.py
python embed_client/example_async_usage_ru.py
```

**Важно:**
- Используйте `--base-url` (через дефис), а не `--base_url` (через подчеркивание).
- Значение base_url должно содержать `http://` или `https://`.
- Аргументы должны быть отдельными (через пробел), а не через `=`.