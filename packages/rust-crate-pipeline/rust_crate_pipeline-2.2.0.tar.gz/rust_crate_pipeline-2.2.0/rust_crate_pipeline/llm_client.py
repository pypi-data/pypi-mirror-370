# llm_client.py
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, AsyncIterator
import asyncio
import json
import os
import httpx

# Optional imports for different providers
try:
    from llama_cpp import Llama

    LLAMA_CPP_AVAILABLE = True
except ImportError:
    LLAMA_CPP_AVAILABLE = False

try:
    import litellm

    LITELLM_AVAILABLE = True
except ImportError:
    LITELLM_AVAILABLE = False


# --------------------------- Config & Errors ---------------------------


@dataclass
class LLMConfig:
    provider: str  # "ollama" | "openai" | "azure" | "llama-cpp" | "litellm"
    model: str  # e.g. "gpt-oss:120b" or model path for llama-cpp
    api_base: Optional[str] = None  # e.g. "http://<ip>:11434/v1" for Ollama
    api_key: Optional[str] = None  # "ollama" or real key
    request_timeout: float = 120.0  # per-request timeout (seconds)
    connect_timeout: float = 10.0
    max_retries: int = 6
    min_backoff: float = 0.25  # first backoff (seconds)
    max_backoff: float = 6.0  # cap
    # Ollama-specific niceties
    num_ctx: Optional[int] = 8192
    keep_alive: Optional[str] = "1h"
    # llama-cpp specific
    model_path: Optional[str] = None
    n_gpu_layers: Optional[int] = None
    n_ctx: Optional[int] = None
    # LiteLLM specific
    litellm_model_name: Optional[str] = None


class LLMError(RuntimeError):
    def __init__(self, message: str, *, status: Optional[int] = None, body: Any = None):
        super().__init__(message)
        self.status = status
        self.body = body


# --------------------------- Base Client Interface ---------------------------


class BaseLLMClient:
    """Base interface for all LLM clients"""

    async def chat(
        self,
        messages: List[Dict[str, str]],
        *,
        max_tokens: int = 512,
        temperature: float = 0.2,
        extra_body: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Non-streaming chat; returns the assistant text."""
        raise NotImplementedError

    async def chat_stream(
        self,
        messages: List[Dict[str, str]],
        *,
        max_tokens: int = 512,
        temperature: float = 0.2,
        extra_body: Optional[Dict[str, Any]] = None,
    ) -> AsyncIterator[str]:
        """Streaming chat; yields text deltas."""
        raise NotImplementedError

    async def chat_json(
        self,
        messages: List[Dict[str, str]],
        *,
        schema: Optional[Dict[str, Any]] = None,
        max_tokens: int = 1024,
        temperature: float = 0.0,
    ) -> Dict[str, Any]:
        """Request structured JSON."""
        raise NotImplementedError

    async def aclose(self) -> None:
        """Close any resources."""
        pass


# --------------------------- HTTP-based Client ---------------------------


class HTTPLLMClient(BaseLLMClient):
    """
    Production-friendly, provider-agnostic chat client for HTTP-based providers.

    Supports:
      • OpenAI-compatible Chat Completions (OpenAI, Ollama, vLLM, Azure OpenAI w/ compat endpoint)
      • Robust retries with jitter for 429/5xx + network blips
      • Optional streaming
      • Structured JSON responses (OpenAI json_schema; Ollama format='json')
    """

    def __init__(self, cfg: LLMConfig):
        self.cfg = cfg
        limits = httpx.Limits(max_connections=100, max_keepalive_connections=20, keepalive_expiry=30)
        self._client = httpx.AsyncClient(
            timeout=httpx.Timeout(cfg.request_timeout, connect=cfg.connect_timeout),
            limits=limits,
            http2=True,
        )
        self._set_endpoints()

    # Allow "async with HTTPLLMClient(cfg) as llm:"
    async def __aenter__(self) -> "HTTPLLMClient":
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.aclose()

    def _set_endpoints(self) -> None:
        p = self.cfg.provider.lower()
        if p == "ollama":
            base = (self.cfg.api_base or "http://localhost:11434").rstrip("/")
            # Prefer OpenAI-compatible route (/v1/chat/completions) for ease of integration
            if not base.endswith("/v1"):
                base = base + "/v1"
            self.base = base
            self.chat_url = f"{self.base}/chat/completions"
            self.headers = {"Authorization": f"Bearer {self.cfg.api_key or 'ollama'}"}
            self.default_extra_body = {
                "keep_alive": self.cfg.keep_alive,
                "options": {k: v for k, v in {"num_ctx": self.cfg.num_ctx}.items() if v is not None},
            }
        elif p == "openai":
            base = (self.cfg.api_base or "https://api.openai.com/v1").rstrip("/")
            self.base = base
            self.chat_url = f"{self.base}/chat/completions"
            self.headers = {"Authorization": f"Bearer {self.cfg.api_key}"}
            self.default_extra_body = {}
        elif p == "azure":
            base = (self.cfg.api_base or "").rstrip("/")
            # Expect an OpenAI-compatible endpoint (most Azure setups expose one)
            self.base = base
            self.chat_url = f"{self.base}/chat/completions"
            self.headers = {"api-key": self.cfg.api_key} if self.cfg.api_key else {}
            self.default_extra_body = {}
        else:
            raise ValueError(f"Unknown HTTP provider: {self.cfg.provider}")

    async def chat(
        self,
        messages: List[Dict[str, str]],
        *,
        max_tokens: int = 512,
        temperature: float = 0.2,
        extra_body: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Non-streaming chat; returns the assistant text."""
        body = {
            "model": self.cfg.model,
            "messages": messages,
            "temperature": float(temperature),
            "max_tokens": int(max_tokens),
            **self.default_extra_body,
            **(extra_body or {}),
        }
        data = await self._post_json_with_retries(self.chat_url, body)
        try:
            return data["choices"][0]["message"]["content"]
        except Exception as e:
            raise LLMError("Unexpected response format", body=data) from e

    async def chat_stream(
        self,
        messages: List[Dict[str, str]],
        *,
        max_tokens: int = 512,
        temperature: float = 0.2,
        extra_body: Optional[Dict[str, Any]] = None,
    ) -> AsyncIterator[str]:
        """Streaming chat; yields text deltas."""
        body = {
            "model": self.cfg.model,
            "messages": messages,
            "temperature": float(temperature),
            "max_tokens": int(max_tokens),
            "stream": True,
            **self.default_extra_body,
            **(extra_body or {}),
        }
        async for delta in self._post_stream_with_retries(self.chat_url, body):
            yield delta

    async def chat_json(
        self,
        messages: List[Dict[str, str]],
        *,
        schema: Optional[Dict[str, Any]] = None,
        max_tokens: int = 1024,
        temperature: float = 0.0,
    ) -> Dict[str, Any]:
        """
        Request structured JSON.
        - OpenAI-compatible: uses response_format.json_schema when provided;
          else response_format={"type":"json_object"}.
        - Ollama: uses options {"format":"json"} via extra_body.
        """
        extra = {}
        if self.cfg.provider.lower() == "ollama":
            extra = {"options": {"format": "json"}}
        else:
            if schema:
                extra = {"response_format": {"type": "json_schema", "json_schema": schema}}
            else:
                extra = {"response_format": {"type": "json_object"}}

        txt = await self.chat(messages, max_tokens=max_tokens, temperature=temperature, extra_body=extra)
        try:
            return json.loads(txt)
        except json.JSONDecodeError as e:
            raise LLMError("Model returned non-JSON content", body=txt) from e

    async def aclose(self) -> None:
        await self._client.aclose()

    # --------------------- Retry helpers ---------------------

    def _retryable(self, status: Optional[int], exc: Optional[Exception]) -> bool:
        if exc is not None:
            # network errors, timeouts are retryable
            return True
        if status is None:
            return True
        # backoff on 408/409/429/5xx
        return status in (408, 409, 425, 429, 500, 502, 503, 504)

    async def _post_json_with_retries(self, url: str, body: Dict[str, Any]) -> Dict[str, Any]:
        attempt = 0
        while True:
            attempt += 1
            status: Optional[int] = None
            try:
                r = await self._client.post(url, headers=self.headers, json=body)
                status = r.status_code
                if 200 <= status < 300:
                    return r.json()
                # non-2xx
                if not self._retryable(status, None):
                    raise LLMError(f"Non-retryable HTTP {status}: {r.text[:500]}", status=status, body=r.text)
            except (httpx.ReadTimeout, httpx.ConnectTimeout, httpx.NetworkError, httpx.RemoteProtocolError):
                pass
            except httpx.HTTPError:
                pass

            if attempt > self.cfg.max_retries:
                raise LLMError(f"Max retries exceeded ({attempt-1})", status=status)
            backoff = min(self.cfg.max_backoff, self.cfg.min_backoff * (2 ** (attempt - 1)))
            # jitter
            backoff *= 0.5 + 0.5 * os.urandom(1)[0] / 255.0
            await asyncio.sleep(backoff)

    async def _post_stream_with_retries(self, url: str, body: Dict[str, Any]) -> AsyncIterator[str]:
        attempt = 0
        while True:
            attempt += 1
            try:
                async with self._client.stream("POST", url, headers=self.headers, json=body) as r:
                    if 200 <= r.status_code < 300:
                        async for line in r.aiter_lines():
                            if not line:
                                continue
                            # OpenAI-compatible stream is "data: {json}\n\n"
                            if line.startswith("data: "):
                                line = line[6:]
                            if line == "[DONE]":
                                break
                            try:
                                obj = json.loads(line)
                                yield obj["choices"][0]["delta"].get("content", "")
                            except Exception:
                                # Be permissive; some providers frame chunks differently
                                pass
                        return
                    if not self._retryable(r.status_code, None):
                        text = await r.aread()
                        raise LLMError(
                            f"Non-retryable HTTP {r.status_code}: {text[:500]}", status=r.status_code
                        )
            except (
                httpx.ReadTimeout,
                httpx.ConnectTimeout,
                httpx.NetworkError,
                httpx.RemoteProtocolError,
            ) as e:
                if attempt > self.cfg.max_retries:
                    raise LLMError(f"Max retries exceeded in stream ({attempt-1})") from e
                backoff = min(self.cfg.max_backoff, self.cfg.min_backoff * (2 ** (attempt - 1)))
                backoff *= 0.5 + 0.5 * os.urandom(1)[0] / 255.0
                await asyncio.sleep(backoff)
                continue


# --------------------------- llama-cpp Client ---------------------------


class LlamaCppClient(BaseLLMClient):
    """Client for direct llama-cpp-python usage"""

    def __init__(self, cfg: LLMConfig):
        if not LLAMA_CPP_AVAILABLE:
            raise ImportError("llama-cpp-python is not installed. Install with: pip install llama-cpp-python")

        self.cfg = cfg
        model_path = cfg.model_path or cfg.model

        # Initialize llama-cpp model
        self._llm = Llama(
            model_path=model_path,
            n_gpu_layers=cfg.n_gpu_layers or -1,  # Use all available GPU layers
            n_ctx=cfg.n_ctx or cfg.num_ctx or 8192,
            verbose=False,
        )

    async def chat(
        self,
        messages: List[Dict[str, str]],
        *,
        max_tokens: int = 512,
        temperature: float = 0.2,
        extra_body: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Non-streaming chat using llama-cpp-python"""
        # Convert messages to llama-cpp format
        prompt = self._messages_to_prompt(messages)

        # Run in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: self._llm(
                prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                stop=["</s>", "\n\n"],
                echo=False,
            ),
        )

        return response["choices"][0]["text"].strip()

    async def chat_stream(
        self,
        messages: List[Dict[str, str]],
        *,
        max_tokens: int = 512,
        temperature: float = 0.2,
        extra_body: Optional[Dict[str, Any]] = None,
    ) -> AsyncIterator[str]:
        """Streaming chat using llama-cpp-python"""
        prompt = self._messages_to_prompt(messages)

        loop = asyncio.get_event_loop()

        def stream_generator():
            for chunk in self._llm(
                prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                stop=["</s>", "\n\n"],
                echo=False,
                stream=True,
            ):
                if chunk["choices"][0]["text"]:
                    yield chunk["choices"][0]["text"]

        # Run streaming in thread pool
        async for chunk in self._async_stream(stream_generator, loop):
            yield chunk

    async def chat_json(
        self,
        messages: List[Dict[str, str]],
        *,
        schema: Optional[Dict[str, Any]] = None,
        max_tokens: int = 1024,
        temperature: float = 0.0,
    ) -> Dict[str, Any]:
        """Request structured JSON from llama-cpp"""
        # Add JSON instruction to messages
        json_messages = messages + [{"role": "system", "content": "Respond with valid JSON only."}]

        txt = await self.chat(json_messages, max_tokens=max_tokens, temperature=temperature)
        try:
            return json.loads(txt)
        except json.JSONDecodeError as e:
            raise LLMError("Model returned non-JSON content", body=txt) from e

    def _messages_to_prompt(self, messages: List[Dict[str, str]]) -> str:
        """Convert OpenAI-style messages to llama-cpp prompt format"""
        prompt = ""
        for msg in messages:
            role = msg["role"]
            content = msg["content"]

            if role == "system":
                prompt += f"<|system|>\n{content}\n<|end|>\n"
            elif role == "user":
                prompt += f"<|user|>\n{content}\n<|end|>\n"
            elif role == "assistant":
                prompt += f"<|assistant|>\n{content}\n<|end|>\n"

        prompt += "<|assistant|>\n"
        return prompt

    async def _async_stream(self, generator, loop):
        """Convert sync generator to async"""
        while True:
            try:
                chunk = await loop.run_in_executor(None, lambda: next(generator))
                yield chunk
            except StopIteration:
                break

    async def aclose(self) -> None:
        # llama-cpp-python doesn't need explicit cleanup
        pass


# --------------------------- LiteLLM Client ---------------------------


class LiteLLMClient(BaseLLMClient):
    """Client for LiteLLM provider"""

    def __init__(self, cfg: LLMConfig):
        if not LITELLM_AVAILABLE:
            raise ImportError("litellm is not installed. Install with: pip install litellm")

        self.cfg = cfg
        self.model_name = cfg.litellm_model_name or cfg.model

    async def chat(
        self,
        messages: List[Dict[str, str]],
        *,
        max_tokens: int = 512,
        temperature: float = 0.2,
        extra_body: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Non-streaming chat using LiteLLM"""
        loop = asyncio.get_event_loop()

        def sync_chat():
            return litellm.completion(
                model=self.model_name,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                **extra_body or {},
            )

        response = await loop.run_in_executor(None, sync_chat)
        return response.choices[0].message.content

    async def chat_stream(
        self,
        messages: List[Dict[str, str]],
        *,
        max_tokens: int = 512,
        temperature: float = 0.2,
        extra_body: Optional[Dict[str, Any]] = None,
    ) -> AsyncIterator[str]:
        """Streaming chat using LiteLLM"""
        loop = asyncio.get_event_loop()

        def sync_stream():
            return litellm.completion(
                model=self.model_name,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                stream=True,
                **extra_body or {},
            )

        stream = await loop.run_in_executor(None, sync_stream)

        for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    async def chat_json(
        self,
        messages: List[Dict[str, str]],
        *,
        schema: Optional[Dict[str, Any]] = None,
        max_tokens: int = 1024,
        temperature: float = 0.0,
    ) -> Dict[str, Any]:
        """Request structured JSON from LiteLLM"""
        # Add JSON instruction
        json_messages = messages + [{"role": "system", "content": "Respond with valid JSON only."}]

        txt = await self.chat(json_messages, max_tokens=max_tokens, temperature=temperature)
        try:
            return json.loads(txt)
        except json.JSONDecodeError as e:
            raise LLMError("Model returned non-JSON content", body=txt) from e


# --------------------------- Unified Client Factory ---------------------------


class LLMClient(BaseLLMClient):
    """
    Unified LLM client that automatically selects the appropriate backend.
    """

    def __init__(self, cfg: LLMConfig):
        self.cfg = cfg
        self._backend = self._create_backend()

    def _create_backend(self) -> BaseLLMClient:
        """Create the appropriate backend client based on provider"""
        provider = self.cfg.provider.lower()

        if provider in ["ollama", "openai", "azure"]:
            return HTTPLLMClient(self.cfg)
        elif provider == "llama-cpp":
            return LlamaCppClient(self.cfg)
        elif provider == "litellm":
            return LiteLLMClient(self.cfg)
        else:
            raise ValueError(f"Unknown provider: {provider}")

    async def chat(
        self,
        messages: List[Dict[str, str]],
        *,
        max_tokens: int = 512,
        temperature: float = 0.2,
        extra_body: Optional[Dict[str, Any]] = None,
    ) -> str:
        return await self._backend.chat(
            messages, max_tokens=max_tokens, temperature=temperature, extra_body=extra_body
        )

    async def chat_stream(
        self,
        messages: List[Dict[str, str]],
        *,
        max_tokens: int = 512,
        temperature: float = 0.2,
        extra_body: Optional[Dict[str, Any]] = None,
    ) -> AsyncIterator[str]:
        async for chunk in self._backend.chat_stream(
            messages, max_tokens=max_tokens, temperature=temperature, extra_body=extra_body
        ):
            yield chunk

    async def chat_json(
        self,
        messages: List[Dict[str, str]],
        *,
        schema: Optional[Dict[str, Any]] = None,
        max_tokens: int = 1024,
        temperature: float = 0.0,
    ) -> Dict[str, Any]:
        return await self._backend.chat_json(
            messages, schema=schema, max_tokens=max_tokens, temperature=temperature
        )

    async def aclose(self) -> None:
        await self._backend.aclose()

    # Context manager support
    async def __aenter__(self) -> "LLMClient":
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.aclose()
