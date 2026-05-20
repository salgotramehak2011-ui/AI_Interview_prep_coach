"""Unit tests for Hugging Face client and Model Router fallback."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.llm.hf_client import HFClient
from app.llm.model_router import ModelRouter
from app.config import get_settings


@pytest.mark.asyncio
async def test_hf_client_not_configured():
    settings = get_settings()
    with patch.object(settings, "HF_TOKEN", None):
        client = HFClient()
        assert not client.is_configured()
        with pytest.raises(ValueError):
            await client.generate("test prompt")


@pytest.mark.asyncio
async def test_hf_client_generate_success():
    settings = get_settings()
    with patch.object(settings, "HF_TOKEN", "fake-token"):
        client = HFClient()
        assert client.is_configured()

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Hugging Face Mock Response"}}]
        }

        with patch("httpx.AsyncClient.post", return_value=mock_response) as mock_post:
            res = await client.generate("test prompt", system="system prompt")
            assert res == "Hugging Face Mock Response"
            mock_post.assert_called_once()
            _, kwargs = mock_post.call_args
            assert kwargs["headers"]["Authorization"] == "Bearer fake-token"


@pytest.mark.asyncio
async def test_model_router_no_hf_token_fallback():
    settings = get_settings()
    with patch.object(settings, "HF_TOKEN", None):
        router = ModelRouter()
        assert not router.hf_client.is_configured()

        with patch.object(router.ollama_client, "complete_with_fallback", return_value="Ollama Direct Response") as mock_ollama:
            res = await router.invoke("test prompt")
            assert res == "Ollama Direct Response"
            mock_ollama.assert_called_once_with("test prompt", system=None)


@pytest.mark.asyncio
async def test_model_router_hf_failure_fallback():
    settings = get_settings()
    with patch.object(settings, "HF_TOKEN", "fake-token"):
        router = ModelRouter()
        assert router.hf_client.is_configured()

        with patch.object(router.hf_client, "generate", side_effect=Exception("HF API error")):
            with patch.object(router.ollama_client, "complete_with_fallback", return_value="Ollama Fallback Response") as mock_ollama:
                res = await router.invoke("test prompt")
                assert res == "Ollama Fallback Response"
                mock_ollama.assert_called_once_with("test prompt", system=None)
