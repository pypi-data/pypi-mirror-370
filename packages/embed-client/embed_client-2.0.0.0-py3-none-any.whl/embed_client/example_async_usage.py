"""
Example usage of EmbeddingServiceAsyncClient.

USAGE:
    python embed_client/example_async_usage.py --base-url http://localhost --port 8001
    # или
    python -m asyncio embed_client/example_async_usage.py --base-url http://localhost --port 8001

    # Можно также использовать переменные окружения:
    export EMBED_CLIENT_BASE_URL=http://localhost
    export EMBED_CLIENT_PORT=8001
    python embed_client/example_async_usage.py

    # ВАЖНО:
    # --base-url и --port должны быть отдельными аргументами (через пробел),
    # а не через = (НЕ --base_url=...)
    # base_url должен содержать http:// или https://

EXAMPLES:
    python embed_client/example_async_usage.py --base-url http://localhost --port 8001
    python -m asyncio embed_client/example_async_usage.py --base-url http://localhost --port 8001
    export EMBED_CLIENT_BASE_URL=http://localhost
    export EMBED_CLIENT_PORT=8001
    python embed_client/example_async_usage.py

Explicit session close example:
    import asyncio
    from embed_client.async_client import EmbeddingServiceAsyncClient
    async def main():
        client = EmbeddingServiceAsyncClient(base_url="http://localhost", port=8001)
        # ... use client ...
        await client.close()  # Explicitly close session
    asyncio.run(main())
"""

import asyncio
import sys
import os
from embed_client.async_client import (
    EmbeddingServiceAsyncClient,
    EmbeddingServiceError,
    EmbeddingServiceAPIError,
    EmbeddingServiceHTTPError,
    EmbeddingServiceConnectionError,
    EmbeddingServiceTimeoutError,
    EmbeddingServiceJSONError,
    EmbeddingServiceConfigError
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
        print("Error: base_url and port must be provided via --base-url/--port arguments or EMBED_CLIENT_BASE_URL/EMBED_CLIENT_PORT environment variables.")
        sys.exit(1)
        return None, None
    return base_url, int(port)

def extract_vectors(result):
    """Extract embeddings from the API response, supporting both old and new formats."""
    # Handle direct embeddings field (old format compatibility)
    if "embeddings" in result:
        return result["embeddings"]
    
    # Handle result wrapper
    if "result" in result:
        res = result["result"]
        
        # Handle direct list in result (old format)
        if isinstance(res, list):
            return res
        
        if isinstance(res, dict):
            # Handle old format: result.embeddings
            if "embeddings" in res:
                return res["embeddings"]
            
            # Handle old format: result.data.embeddings
            if "data" in res and isinstance(res["data"], dict) and "embeddings" in res["data"]:
                return res["data"]["embeddings"]
            
            # Handle new format: result.data[].embedding
            if "data" in res and isinstance(res["data"], list):
                embeddings = []
                for item in res["data"]:
                    if isinstance(item, dict) and "embedding" in item:
                        embeddings.append(item["embedding"])
                    else:
                        raise ValueError(f"Invalid item format in new API response: {item}")
                return embeddings
    
    raise ValueError(f"Cannot extract embeddings from response: {result}")

async def main():
    try:
        base_url, port = get_params()
        # Explicit open/close example
        client = EmbeddingServiceAsyncClient(base_url=base_url, port=port)
        print("Explicit session open/close example:")
        await client.close()
        print("Session closed explicitly (manual close example).\n")
        async with EmbeddingServiceAsyncClient(base_url=base_url, port=port) as client:
            # Check health
            try:
                health = await client.health()
                print("Service health:", health)
            except EmbeddingServiceConnectionError as e:
                print(f"Connection error during health check: {e}")
                return
            except EmbeddingServiceTimeoutError as e:
                print(f"Timeout error during health check: {e}")
            except EmbeddingServiceError as e:
                print(f"Error during health check: {e}")

            # Request embeddings for a list of texts
            texts = ["hello world", "test embedding"]
            try:
                result = await client.cmd("embed", params={"texts": texts})
                vectors = extract_vectors(result)
                print(f"Embeddings for {len(texts)} texts:")
                for i, vec in enumerate(vectors):
                    print(f"  Text: {texts[i]!r}\n  Vector: {vec[:5]}... (total {len(vec)} dims)")
            except EmbeddingServiceAPIError as e:
                print(f"API error during embedding: {e}")
            except EmbeddingServiceConnectionError as e:
                print(f"Connection error during embedding: {e}")
            except EmbeddingServiceTimeoutError as e:
                print(f"Timeout error during embedding: {e}")
            except EmbeddingServiceError as e:
                print(f"Error during embedding: {e}")

            # Example: health check via cmd
            try:
                result = await client.cmd("health")
                print("Health check result:", result)
            except EmbeddingServiceError as e:
                print(f"Error during health command: {e}")

            # Example: error handling for empty command
            try:
                result = await client.cmd("")
                print("Empty command result:", result)
            except EmbeddingServiceAPIError as e:
                print(f"Expected error for empty command: {e}")
            except EmbeddingServiceError as e:
                print(f"Error for empty command: {e}")

    except EmbeddingServiceConfigError as e:
        print(f"Configuration error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 