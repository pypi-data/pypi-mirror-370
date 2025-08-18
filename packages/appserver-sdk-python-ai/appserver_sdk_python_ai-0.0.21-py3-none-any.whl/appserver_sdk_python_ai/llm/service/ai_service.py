# appserver_sdk_python_ai/llm/service/ai_service.py
"""
Serviço principal de IA
======================

Implementa os clientes síncronos e assíncronos para comunicação com APIs de IA.
"""

import asyncio
import logging
from collections.abc import AsyncGenerator
from typing import Any

import httpx
import requests
from pydantic import BaseModel, Field

from appserver_sdk_python_ai.llm.exceptions import (
    LLMAuthenticationError,
    LLMError,
    LLMNetworkError,
    LLMProviderError,
    LLMRateLimitError,
    LLMTimeoutError,
)


class Message(BaseModel):
    """Modelo para mensagens de chat."""

    role: str = Field(..., description="Papel da mensagem (system, user, assistant)")
    content: str = Field(..., description="Conteúdo da mensagem")


class Usage(BaseModel):
    """Modelo para informações de uso de tokens."""

    prompt_tokens: int = Field(0, description="Tokens usados no prompt")
    completion_tokens: int = Field(0, description="Tokens usados na resposta")
    total_tokens: int = Field(0, description="Total de tokens usados")


class ChatResponse(BaseModel):
    """Modelo para resposta de chat."""

    content: str = Field(..., description="Conteúdo da resposta")
    model: str = Field(..., description="Modelo usado")
    usage: Usage = Field(
        default_factory=lambda: Usage(
            prompt_tokens=0, completion_tokens=0, total_tokens=0
        ),
        description="Informações de uso",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Metadados adicionais"
    )


class StreamChunk(BaseModel):
    """Modelo para chunk de streaming."""

    content: str = Field(..., description="Conteúdo do chunk")
    is_final: bool = Field(False, description="Se é o último chunk")
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Metadados do chunk"
    )


class AIConfig(BaseModel):
    """Configuração para o cliente de IA."""

    base_url: str = Field(
        "https://api.appserver.com.br/ai/v1", description="URL base da API"
    )
    api_key: str = Field(..., description="Chave da API")
    model: str = Field("gpt-3.5-turbo", description="Modelo a ser usado")
    max_tokens: int = Field(150, description="Máximo de tokens na resposta")
    temperature: float = Field(0.7, description="Temperatura para geração")
    timeout: int = Field(30, description="Timeout em segundos")
    max_retries: int = Field(3, description="Máximo de tentativas")
    retry_delay: float = Field(1.0, description="Delay entre tentativas")
    backoff_factor: float = Field(2.0, description="Fator de backoff")
    verify_ssl: bool = Field(True, description="Verificar SSL")
    debug: bool = Field(False, description="Modo debug")
    log_requests: bool = Field(True, description="Log de requisições")
    log_responses: bool = Field(False, description="Log de respostas")
    headers: dict[str, str] = Field(
        default_factory=dict, description="Headers customizados"
    )


class AIService:
    """Cliente síncrono para serviços de IA."""

    def __init__(
        self, api_key: str | None = None, config: AIConfig | None = None, **kwargs
    ):
        """Inicializa o cliente de IA.

        Args:
            api_key: Chave da API
            config: Configuração do cliente
            **kwargs: Argumentos adicionais para configuração
        """
        if config is None:
            if api_key is None:
                raise ValueError("api_key é obrigatório quando config não é fornecido")

            config = AIConfig(
                api_key=api_key,
                base_url=kwargs.get("base_url", "https://api.appserver.com.br/ai/v1"),
                model=kwargs.get("model", "gpt-3.5-turbo"),
                max_tokens=kwargs.get("max_tokens", 150),
                temperature=kwargs.get("temperature", 0.7),
                timeout=kwargs.get("timeout", 30),
                max_retries=kwargs.get("max_retries", 3),
                retry_delay=kwargs.get("retry_delay", 1.0),
                backoff_factor=kwargs.get("backoff_factor", 2.0),
                verify_ssl=kwargs.get("verify_ssl", True),
                debug=kwargs.get("debug", False),
                log_requests=kwargs.get("log_requests", True),
                log_responses=kwargs.get("log_responses", False),
                headers=kwargs.get("headers", {}),
            )

        self.config = config
        self.logger = logging.getLogger(__name__)

        # Configurar headers padrão
        self.headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "AppServer-SDK-Python-AI/1.0",
            **self.config.headers,
        }

        # Configurar sessão HTTP
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def chat(
        self,
        prompt: str,
        model: str = "gpt-3.5-turbo",
        max_tokens: int | None = None,
        temperature: float = 0.7,
        **kwargs,
    ) -> ChatResponse:
        """Executa um chat com o modelo de IA.

        Args:
            prompt: Prompt para o modelo
            model: Nome do modelo
            max_tokens: Máximo de tokens na resposta
            temperature: Temperatura para geração
            **kwargs: Argumentos adicionais

        Returns:
            Resposta do chat

        Raises:
            LLMError: Erro na comunicação com a API
        """
        messages: list[Message | dict[str, str]] = [{"role": "user", "content": prompt}]
        return self.chat_with_messages(
            messages, model, max_tokens, temperature, **kwargs
        )

    def chat_with_messages(
        self,
        messages: list[Message | dict[str, str]],
        model: str = "gpt-3.5-turbo",
        max_tokens: int | None = None,
        temperature: float = 0.7,
        **kwargs,
    ) -> ChatResponse:
        """Executa um chat com lista de mensagens.

        Args:
            messages: Lista de mensagens
            model: Nome do modelo
            max_tokens: Máximo de tokens na resposta
            temperature: Temperatura para geração
            **kwargs: Argumentos adicionais

        Returns:
            Resposta do chat

        Raises:
            LLMError: Erro na comunicação com a API
        """
        # Converter mensagens para formato dict se necessário
        formatted_messages = []
        for msg in messages:
            if isinstance(msg, Message):
                formatted_messages.append({"role": msg.role, "content": msg.content})
            else:
                formatted_messages.append(msg)

        payload = {
            "model": model,
            "messages": formatted_messages,
            "temperature": temperature,
            **kwargs,
        }

        if max_tokens is not None:
            payload["max_tokens"] = max_tokens

        try:
            self._make_request("POST", "/chat/completions", json=payload)

            # Simular resposta para desenvolvimento
            # TODO: Implementar integração real com API
            return ChatResponse(
                content=f"Resposta simulada para: {formatted_messages[-1]['content'][:50]}...",
                model=model,
                usage=Usage(prompt_tokens=10, completion_tokens=20, total_tokens=30),
                metadata={"simulated": True},
            )

        except Exception as e:
            self.logger.error(f"Erro no chat: {e}")
            raise LLMError(f"Erro na comunicação com a API: {e}") from e

    def _make_request(self, method: str, endpoint: str, **kwargs) -> dict[str, Any]:
        """Faz uma requisição HTTP.

        Args:
            method: Método HTTP
            endpoint: Endpoint da API
            **kwargs: Argumentos para a requisição

        Returns:
            Resposta da API

        Raises:
            LLMError: Erro na requisição
        """
        url = f"{self.config.base_url.rstrip('/')}{endpoint}"

        for attempt in range(self.config.max_retries + 1):
            try:
                if self.config.log_requests:
                    self.logger.info(f"Fazendo requisição {method} para {url}")

                response = self.session.request(
                    method=method,
                    url=url,
                    timeout=self.config.timeout,
                    verify=self.config.verify_ssl,
                    **kwargs,
                )

                if response.status_code == 200:
                    response_data: dict[str, Any] = response.json()
                    return response_data
                elif response.status_code == 401:
                    raise LLMAuthenticationError("Credenciais inválidas", "openai")
                elif response.status_code == 429:
                    raise LLMRateLimitError("Limite de taxa excedido")
                else:
                    raise LLMProviderError(
                        f"Erro da API: {response.status_code} - {response.text}",
                        "openai",
                    )

            except requests.exceptions.Timeout:
                if attempt == self.config.max_retries:
                    raise LLMTimeoutError("Timeout na requisição", 30.0) from None
            except requests.exceptions.ConnectionError as e:
                if attempt == self.config.max_retries:
                    raise LLMNetworkError(f"Erro de conexão: {e}") from e
            except Exception as e:
                if attempt == self.config.max_retries:
                    raise LLMError(f"Erro inesperado: {e}") from e

            # Aguardar antes da próxima tentativa
            if attempt < self.config.max_retries:
                delay = self.config.retry_delay * (self.config.backoff_factor**attempt)
                self.logger.warning(
                    f"Tentativa {attempt + 1} falhou, aguardando {delay}s"
                )
                import time

                time.sleep(delay)

        raise LLMError("Máximo de tentativas excedido")


class AsyncAIService:
    """Cliente assíncrono para serviços de IA."""

    def __init__(
        self, config: AIConfig | None = None, api_key: str | None = None, **kwargs
    ):
        """Inicializa o cliente assíncrono de IA.

        Args:
            config: Configuração do cliente (objeto AIConfig)
            api_key: Chave da API (usado se config não for fornecido)
            **kwargs: Argumentos adicionais para configuração
        """
        if config is not None:
            # Se config é um objeto AIConfig, usar diretamente
            if isinstance(config, AIConfig):
                self.config = config
            else:
                # Se config é um dict, criar AIConfig
                self.config = AIConfig(
                    api_key=str(config.get("api_key", api_key or "")),
                    base_url=str(config.get("base_url", "https://api.openai.com/v1")),
                    model=str(config.get("model", "gpt-3.5-turbo")),
                    max_tokens=int(config.get("max_tokens", 150)),
                    temperature=float(config.get("temperature", 0.7)),
                    timeout=int(config.get("timeout", 30)),
                    max_retries=int(config.get("max_retries", 3)),
                    headers=dict(config.get("headers", {})),
                )
        else:
            # Criar config a partir de api_key e kwargs
            if api_key is None:
                raise ValueError("api_key é obrigatório quando config não é fornecido")

            self.config = AIConfig(
                api_key=api_key,
                base_url=kwargs.get("base_url", "https://api.appserver.com.br/ai/v1"),
                model=kwargs.get("model", "gpt-3.5-turbo"),
                max_tokens=kwargs.get("max_tokens", 150),
                temperature=kwargs.get("temperature", 0.7),
                timeout=kwargs.get("timeout", 30),
                max_retries=kwargs.get("max_retries", 3),
                retry_delay=kwargs.get("retry_delay", 1.0),
                backoff_factor=kwargs.get("backoff_factor", 2.0),
                verify_ssl=kwargs.get("verify_ssl", True),
                debug=kwargs.get("debug", False),
                log_requests=kwargs.get("log_requests", True),
                log_responses=kwargs.get("log_responses", False),
                headers=kwargs.get("headers", {}),
            )
        self.logger = logging.getLogger(__name__)

        # Configurar headers padrão
        self.headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "AppServer-SDK-Python-AI/1.0",
            **self.config.headers,
        }

        self.client: httpx.AsyncClient | None = None

    async def __aenter__(self):
        """Entrada do context manager."""
        await self._ensure_client()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Saída do context manager."""
        await self.close()

    async def _ensure_client(self):
        """Garante que o cliente HTTP está inicializado."""
        if self.client is None:
            self.client = httpx.AsyncClient(
                headers=self.headers,
                timeout=self.config.timeout,
                verify=self.config.verify_ssl,
            )

    async def close(self):
        """Fecha o cliente HTTP."""
        if self.client is not None:
            await self.client.aclose()
            self.client = None

    async def chat(
        self,
        prompt: str,
        model: str = "gpt-3.5-turbo",
        max_tokens: int | None = None,
        temperature: float = 0.7,
        **kwargs,
    ) -> ChatResponse:
        """Executa um chat assíncrono com o modelo de IA.

        Args:
            prompt: Prompt para o modelo
            model: Nome do modelo
            max_tokens: Máximo de tokens na resposta
            temperature: Temperatura para geração
            **kwargs: Argumentos adicionais

        Returns:
            Resposta do chat

        Raises:
            LLMError: Erro na comunicação com a API
        """
        messages: list[Message | dict[str, str]] = [{"role": "user", "content": prompt}]
        return await self.chat_with_messages(
            messages, model, max_tokens, temperature, **kwargs
        )

    async def chat_with_messages(
        self,
        messages: list[Message | dict[str, str]],
        model: str = "gpt-3.5-turbo",
        max_tokens: int | None = None,
        temperature: float = 0.7,
        **kwargs,
    ) -> ChatResponse:
        """Executa um chat assíncrono com lista de mensagens.

        Args:
            messages: Lista de mensagens
            model: Nome do modelo
            max_tokens: Máximo de tokens na resposta
            temperature: Temperatura para geração
            **kwargs: Argumentos adicionais

        Returns:
            Resposta do chat

        Raises:
            LLMError: Erro na comunicação com a API
        """
        await self._ensure_client()

        # Converter mensagens para formato dict se necessário
        formatted_messages = []
        for msg in messages:
            if isinstance(msg, Message):
                formatted_messages.append({"role": msg.role, "content": msg.content})
            else:
                formatted_messages.append(msg)

        payload = {
            "model": model,
            "messages": formatted_messages,
            "temperature": temperature,
            **kwargs,
        }

        if max_tokens is not None:
            payload["max_tokens"] = max_tokens

        try:
            await self._make_request("POST", "/chat/completions", json=payload)

            # Simular resposta para desenvolvimento
            # TODO: Implementar integração real com API
            return ChatResponse(
                content=f"Resposta assíncrona simulada para: {formatted_messages[-1]['content'][:50]}...",
                model=model,
                usage=Usage(prompt_tokens=10, completion_tokens=20, total_tokens=30),
                metadata={"simulated": True, "async": True},
            )

        except Exception as e:
            self.logger.error(f"Erro no chat assíncrono: {e}")
            raise LLMError(f"Erro na comunicação assíncrona com a API: {e}") from e

    async def chat_stream(
        self,
        prompt: str,
        model: str = "gpt-3.5-turbo",
        max_tokens: int | None = None,
        temperature: float = 0.7,
        **kwargs,
    ) -> AsyncGenerator[StreamChunk, None]:
        """Executa um chat com streaming.

        Args:
            prompt: Prompt para o modelo
            model: Nome do modelo
            max_tokens: Máximo de tokens na resposta
            temperature: Temperatura para geração
            **kwargs: Argumentos adicionais

        Yields:
            Chunks da resposta

        Raises:
            LLMError: Erro na comunicação com a API
        """
        # Simular streaming para desenvolvimento
        # TODO: Implementar streaming real com API
        response_text = f"Resposta em streaming simulada para: {prompt[:50]}..."
        words = response_text.split()

        for i, word in enumerate(words):
            await asyncio.sleep(0.1)  # Simular delay
            is_final = i == len(words) - 1
            yield StreamChunk(
                content=word + ("" if is_final else " "),
                is_final=is_final,
                metadata={"chunk_index": i, "total_chunks": len(words)},
            )

    async def _make_request(
        self, method: str, endpoint: str, **kwargs
    ) -> dict[str, Any]:
        """Faz uma requisição HTTP assíncrona.

        Args:
            method: Método HTTP
            endpoint: Endpoint da API
            **kwargs: Argumentos para a requisição

        Returns:
            Resposta da API

        Raises:
            LLMError: Erro na requisição
        """
        await self._ensure_client()

        if self.client is None:
            raise ValueError("Cliente assíncrono não inicializado")

        url = f"{self.config.base_url.rstrip('/')}{endpoint}"

        for attempt in range(self.config.max_retries + 1):
            try:
                if self.config.log_requests:
                    self.logger.info(
                        f"Fazendo requisição assíncrona {method} para {url}"
                    )

                response = await self.client.request(method=method, url=url, **kwargs)

                if response.status_code == 200:
                    response_data: dict[str, Any] = response.json()
                    return response_data
                elif response.status_code == 401:
                    raise LLMAuthenticationError("Credenciais inválidas", "openai")
                elif response.status_code == 429:
                    raise LLMRateLimitError("Limite de taxa excedido")
                else:
                    raise LLMProviderError(
                        f"Erro da API: {response.status_code} - {response.text}",
                        "openai",
                    )

            except httpx.TimeoutException:
                if attempt == self.config.max_retries:
                    raise LLMTimeoutError(
                        "Timeout na requisição assíncrona", 30.0
                    ) from None
            except httpx.ConnectError as e:
                if attempt == self.config.max_retries:
                    raise LLMNetworkError(f"Erro de conexão assíncrona: {e}") from e
            except Exception as e:
                if attempt == self.config.max_retries:
                    raise LLMError(f"Erro inesperado assíncrono: {e}") from e

            # Aguardar antes da próxima tentativa
            if attempt < self.config.max_retries:
                delay = self.config.retry_delay * (self.config.backoff_factor**attempt)
                self.logger.warning(
                    f"Tentativa assíncrona {attempt + 1} falhou, aguardando {delay}s"
                )
                await asyncio.sleep(delay)

        raise LLMError("Máximo de tentativas assíncronas excedido")
