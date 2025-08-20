"""
Пример использования EmbeddingServiceAsyncClient (асинхронный клиент).

USAGE:
    python embed_client/example_async_usage_ru.py --base-url http://localhost --port 8001
    # или
    python -m asyncio embed_client/example_async_usage_ru.py --base-url http://localhost --port 8001

    # Можно также использовать переменные окружения:
    export EMBED_CLIENT_BASE_URL=http://localhost
    export EMBED_CLIENT_PORT=8001
    python embed_client/example_async_usage_ru.py

    # ВАЖНО:
    # --base-url и --port должны быть отдельными аргументами (через пробел),
    # а не через = (НЕ --base_url=...)
    # base_url должен содержать http:// или https://

EXAMPLES:
    python embed_client/example_async_usage_ru.py --base-url http://localhost --port 8001
    python -m asyncio embed_client/example_async_usage_ru.py --base-url http://localhost --port 8001
    export EMBED_CLIENT_BASE_URL=http://localhost
    export EMBED_CLIENT_PORT=8001
    python embed_client/example_async_usage_ru.py
"""

import asyncio
import sys
import os
from embed_client.async_client import (
    EmbeddingServiceAsyncClient,
    EmbeddingServiceConnectionError,
    EmbeddingServiceHTTPError,
    EmbeddingServiceAPIError,
    EmbeddingServiceError,
)

def get_params():
    base_url = None
    port = None
    for i, arg in enumerate(sys.argv):
        if arg in ("--base-url", "-b") and i + 1 < len(sys.argv):
            base_url = sys.argv[i + 1]
        if arg in ("--port", "-p") and i + 1 < len(sys.argv):
            port = sys.argv[i + 1]
    if not base_url:
        base_url = os.environ.get("EMBED_CLIENT_BASE_URL")
    if not port:
        port = os.environ.get("EMBED_CLIENT_PORT")
    if not base_url or not port:
        print("Error: base_url and port must be provided via [--base-url | --port] arguments or [EMBED_CLIENT_BASE_URL/EMBED_CLIENT_PORT] environment variables.")
        sys.exit(1)
        return None, None
    return base_url, int(port)

async def main():
    base_url, port = get_params()
    # Always use try/except to handle all possible errors
    try:
        async with EmbeddingServiceAsyncClient(base_url=base_url, port=port) as client:
            # Check health
            try:
                health = await client.health()
                print("Service health:", health)
            except EmbeddingServiceConnectionError as e:
                print("[Connection error]", e)
                return
            except EmbeddingServiceHTTPError as e:
                print(f"[HTTP error] {e.status}: {e.message}")
                return
            except EmbeddingServiceError as e:
                print("[Other error]", e)
                return

            # Request embeddings for a list of texts
            texts = ["hello world", "test embedding"]
            try:
                result = await client.cmd("embed", params={"texts": texts})
                # Use client's extract method for compatibility with both old and new formats
                vectors = client.extract_embeddings(result)
                print(f"Embeddings for {len(texts)} texts:")
                for i, vec in enumerate(vectors):
                    print(f"  Text: {texts[i]!r}\n  Vector: {vec[:5]}... (total {len(vec)} dims)")
                
                # Try to extract additional data if new format is available
                try:
                    embedding_data = client.extract_embedding_data(result)
                    print("\nAdditional data from new format:")
                    for i, data in enumerate(embedding_data):
                        print(f"  Text: {data['body']!r}")
                        print(f"  Tokens: {data['tokens']}")
                        print(f"  BM25 tokens: {data['bm25_tokens']}")
                        
                    # Extract tokens and BM25 tokens separately
                    tokens = client.extract_tokens(result)
                    bm25_tokens = client.extract_bm25_tokens(result)
                    print(f"\nExtracted tokens: {tokens}")
                    print(f"Extracted BM25 tokens: {bm25_tokens}")
                    
                except ValueError as e:
                    print(f"(Old format detected - no additional data available): {e}")
                    
            except EmbeddingServiceAPIError as e:
                print("[API error]", e.error)
            except EmbeddingServiceHTTPError as e:
                print(f"[HTTP error] {e.status}: {e.message}")
            except EmbeddingServiceConnectionError as e:
                print("[Connection error]", e)
            except EmbeddingServiceError as e:
                print("[Other error]", e)

            # Example: error handling for invalid command
            try:
                await client.cmd("not_a_command")
            except EmbeddingServiceAPIError as e:
                print("[API error for invalid command]", e.error)

            # Example: error handling for empty texts
            try:
                await client.cmd("embed", params={"texts": []})
            except EmbeddingServiceAPIError as e:
                print("[API error for empty texts]", e.error)

    except Exception as e:
        print("[Unexpected error]", e)

if __name__ == "__main__":
    asyncio.run(main()) 