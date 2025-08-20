import sys
import pytest
import asyncio
from unittest.mock import patch, AsyncMock

@pytest.mark.asyncio
async def test_example_async_usage_ru(monkeypatch):
    monkeypatch.setattr(sys, 'argv', ['example_async_usage_ru.py', '--base-url', 'http://test', '--port', '8001'])
    with patch('embed_client.example_async_usage_ru.EmbeddingServiceAsyncClient.__aenter__', new=AsyncMock(return_value=AsyncMock())), \
         patch('embed_client.example_async_usage_ru.EmbeddingServiceAsyncClient.health', new=AsyncMock(return_value={"status": "ok"})):
        import importlib
        import embed_client.example_async_usage_ru as example
        importlib.reload(example)
        await example.main()

@pytest.mark.asyncio
async def test_example_async_usage_ru_no_base_url(monkeypatch):
    monkeypatch.setattr(sys, 'argv', ['example_async_usage_ru.py'])
    with patch('builtins.print') as mock_print, patch('sys.exit') as mock_exit:
        import importlib
        import embed_client.example_async_usage_ru as example
        importlib.reload(example)
        await example.main()
        mock_print.assert_called()
        mock_exit.assert_called() 