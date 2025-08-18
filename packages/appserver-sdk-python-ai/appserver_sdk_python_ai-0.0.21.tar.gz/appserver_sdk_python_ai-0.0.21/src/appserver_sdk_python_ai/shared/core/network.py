"""Utilitários de rede unificados para todos os módulos do SDK."""

import asyncio
import json
import logging
import time
from typing import TYPE_CHECKING, Any
from urllib.parse import urljoin, urlparse

try:
    import requests
    from requests.adapters import HTTPAdapter
    from requests.packages.urllib3.util.retry import Retry
except ImportError:
    requests = None  # type: ignore[assignment]
    HTTPAdapter = None  # type: ignore[assignment,misc]
    Retry = None  # type: ignore[assignment]

if TYPE_CHECKING:
    try:
        import aiohttp
    except ImportError:
        aiohttp = None
else:
    try:
        import aiohttp
    except ImportError:
        aiohttp = None

import builtins

from appserver_sdk_python_ai.shared.core.validation import DataValidator
from appserver_sdk_python_ai.shared.exceptions import SharedError

logger = logging.getLogger(__name__)


class NetworkError(SharedError):
    """Exceção para erros de rede."""

    pass


class RateLimitError(NetworkError):
    """Exceção para limite de taxa excedido."""

    pass


class TimeoutError(NetworkError):
    """Exceção para timeout de rede."""

    pass


class RateLimiter:
    """Limitador de taxa para requisições."""

    def __init__(self, max_requests: int = 100, time_window: int = 60):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests: list[float] = []
        self._lock = asyncio.Lock() if asyncio else None

    def can_make_request(self) -> bool:
        """Verifica se pode fazer uma requisição."""
        now = time.time()

        # Remove requisições antigas
        self.requests = [
            req_time for req_time in self.requests if now - req_time < self.time_window
        ]

        return len(self.requests) < self.max_requests

    def record_request(self) -> None:
        """Registra uma nova requisição."""
        self.requests.append(time.time())

    def wait_time(self) -> float:
        """Retorna tempo de espera necessário."""
        if self.can_make_request():
            return 0.0

        # Tempo até a requisição mais antiga expirar
        if not self.requests:
            return 0.0
        oldest_request = min(self.requests)
        return self.time_window - (time.time() - oldest_request)

    async def acquire(self) -> None:
        """Adquire permissão para fazer requisição (async)."""
        if not self._lock:
            raise RuntimeError("AsyncIO não disponível")

        async with self._lock:
            while not self.can_make_request():
                wait_time = self.wait_time()
                if wait_time > 0:
                    await asyncio.sleep(wait_time)

            self.record_request()

    def acquire_sync(self) -> None:
        """Adquire permissão para fazer requisição (sync)."""
        while not self.can_make_request():
            wait_time = self.wait_time()
            if wait_time > 0:
                time.sleep(wait_time)

        self.record_request()


class NetworkConfig:
    """Configuração de rede."""

    def __init__(
        self,
        timeout: int = 30,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        backoff_factor: float = 2.0,
        user_agent: str | None = None,
        headers: dict[str, str] | None = None,
        verify_ssl: bool = True,
        rate_limit: int | None = None,
        rate_limit_window: int = 60,
    ):
        # Validar configuração
        config_data = {
            "timeout": timeout,
            "max_retries": max_retries,
            "retry_delay": retry_delay,
            "user_agent": user_agent,
            "headers": headers or {},
        }
        DataValidator.validate_network_config(config_data)

        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.backoff_factor = backoff_factor
        self.user_agent = user_agent or "AppServer-SDK-Python/1.0"
        self.headers = headers or {}
        self.verify_ssl = verify_ssl

        # Rate limiting
        self.rate_limiter = None
        if rate_limit:
            self.rate_limiter = RateLimiter(rate_limit, rate_limit_window)

    def get_default_headers(self) -> dict[str, str]:
        """Retorna headers padrão."""
        default_headers = {
            "User-Agent": self.user_agent,
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
        }
        default_headers.update(self.headers)
        return default_headers


class HTTPClient:
    """Cliente HTTP unificado com retry e rate limiting."""

    def __init__(self, config: NetworkConfig | None = None):
        self.config = config or NetworkConfig()
        self._session: requests.Session | None = None
        self._setup_session()

    def _setup_session(self) -> None:
        """Configura sessão HTTP."""
        if not requests:
            raise NetworkError("Biblioteca 'requests' não está instalada")

        self._session = requests.Session()

        # Configurar retry strategy
        retry_strategy = Retry(
            total=self.config.max_retries,
            backoff_factor=self.config.backoff_factor,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS", "POST", "PUT", "DELETE"],
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        self._session.mount("http://", adapter)
        self._session.mount("https://", adapter)

        # Configurar headers padrão
        self._session.headers.update(self.config.get_default_headers())

        # Configurar SSL
        self._session.verify = self.config.verify_ssl

    def _apply_rate_limit(self) -> None:
        """Aplica rate limiting se configurado."""
        if self.config.rate_limiter:
            self.config.rate_limiter.acquire_sync()

    def request(self, method: str, url: str, **kwargs) -> requests.Response:
        """Faz requisição HTTP com retry e rate limiting."""
        try:
            self._apply_rate_limit()

            # Configurar timeout
            kwargs.setdefault("timeout", self.config.timeout)

            # Garantir que a sessão está configurada
            if self._session is None:
                self._setup_session()

            # Fazer requisição
            response = self._session.request(method, url, **kwargs)  # type: ignore[union-attr,attr-defined]

            # Log da requisição
            logger.debug(f"{method} {url} - Status: {response.status_code}")

            return response  # type: ignore[no-any-return]

        except requests.exceptions.Timeout as e:
            raise TimeoutError(f"Timeout na requisição para {url}") from e
        except requests.exceptions.RequestException as e:
            raise NetworkError(f"Erro na requisição para {url}: {e}") from e

    def get(self, url: str, **kwargs) -> requests.Response:
        """Requisição GET."""
        return self.request("GET", url, **kwargs)

    def post(self, url: str, **kwargs) -> requests.Response:
        """Requisição POST."""
        return self.request("POST", url, **kwargs)

    def put(self, url: str, **kwargs) -> requests.Response:
        """Requisição PUT."""
        return self.request("PUT", url, **kwargs)

    def delete(self, url: str, **kwargs) -> requests.Response:
        """Requisição DELETE."""
        return self.request("DELETE", url, **kwargs)

    def get_json(self, url: str, **kwargs) -> dict[str, Any]:
        """Requisição GET que retorna JSON."""
        response = self.get(url, **kwargs)
        response.raise_for_status()

        try:
            return response.json()  # type: ignore[no-any-return]
        except json.JSONDecodeError as e:
            raise NetworkError(f"Resposta não é JSON válido: {e}") from e

    def post_json(self, url: str, data: dict[str, Any], **kwargs) -> dict[str, Any]:
        """Requisição POST com dados JSON."""
        kwargs.setdefault("json", data)
        kwargs.setdefault("headers", {}).update({"Content-Type": "application/json"})

        response = self.post(url, **kwargs)
        response.raise_for_status()

        try:
            return response.json()  # type: ignore[no-any-return]
        except json.JSONDecodeError as e:
            raise NetworkError(f"Resposta não é JSON válido: {e}") from e

    def download_file(self, url: str, file_path: str, chunk_size: int = 8192) -> None:
        """Baixa arquivo da URL."""
        try:
            response = self.get(url, stream=True)
            response.raise_for_status()

            with open(file_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:
                        f.write(chunk)

            logger.info(f"Arquivo baixado: {url} -> {file_path}")

        except Exception as e:
            raise NetworkError(f"Erro ao baixar arquivo {url}: {e}") from e

    def close(self) -> None:
        """Fecha a sessão HTTP."""
        if self._session:
            self._session.close()

    def __enter__(self) -> "HTTPClient":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()


class AsyncHTTPClient:
    """Cliente HTTP assíncrono."""

    def __init__(self, config: NetworkConfig | None = None):
        self.config = config or NetworkConfig()
        self._session = None

    async def _get_session(self) -> Any:
        """Obtém ou cria sessão aiohttp."""
        if not aiohttp:
            raise NetworkError("Biblioteca 'aiohttp' não está instalada")

        if not self._session:
            timeout = aiohttp.ClientTimeout(total=self.config.timeout)
            connector = aiohttp.TCPConnector(verify_ssl=self.config.verify_ssl)

            self._session = aiohttp.ClientSession(
                timeout=timeout,
                connector=connector,
                headers=self.config.get_default_headers(),
            )

        return self._session

    async def _apply_rate_limit(self) -> None:
        """Aplica rate limiting se configurado."""
        if self.config.rate_limiter:
            await self.config.rate_limiter.acquire()

    async def request(self, method: str, url: str, **kwargs):  # type: ignore[no-any-return]
        """Faz requisição HTTP assíncrona."""
        try:
            await self._apply_rate_limit()

            session = await self._get_session()

            # Retry manual para aiohttp
            last_exception: Exception | None = None

            for attempt in range(self.config.max_retries + 1):
                try:
                    response = await session.request(method, url, **kwargs)

                    # Log da requisição
                    logger.debug(f"{method} {url} - Status: {response.status}")

                    # Se status indica retry, tentar novamente
                    if (
                        response.status in [429, 500, 502, 503, 504]
                        and attempt < self.config.max_retries
                    ):
                        await asyncio.sleep(
                            self.config.retry_delay
                            * (self.config.backoff_factor**attempt)
                        )
                        continue

                    return response

                except builtins.TimeoutError as e:
                    last_exception = e
                    if attempt < self.config.max_retries:
                        await asyncio.sleep(
                            self.config.retry_delay
                            * (self.config.backoff_factor**attempt)
                        )
                        continue
                    break
                except Exception as e:
                    last_exception = e
                    if attempt < self.config.max_retries:
                        await asyncio.sleep(
                            self.config.retry_delay
                            * (self.config.backoff_factor**attempt)
                        )
                        continue
                    break

            # Se chegou aqui, todas as tentativas falharam
            if isinstance(last_exception, asyncio.TimeoutError):
                raise TimeoutError(
                    f"Timeout na requisição para {url}"
                ) from last_exception
            else:
                raise NetworkError(
                    f"Erro na requisição para {url}: {last_exception}"
                ) from last_exception

        except Exception as e:
            if not isinstance(e, NetworkError | TimeoutError):
                raise NetworkError(
                    f"Erro inesperado na requisição para {url}: {e}"
                ) from e
            raise

    async def get(self, url: str, **kwargs):  # type: ignore[no-any-return]
        """Requisição GET assíncrona."""
        return await self.request("GET", url, **kwargs)

    async def post(self, url: str, **kwargs):  # type: ignore[no-any-return]
        """Requisição POST assíncrona."""
        return await self.request("POST", url, **kwargs)

    async def get_json(self, url: str, **kwargs) -> dict[str, Any]:
        """Requisição GET que retorna JSON."""
        response = await self.get(url, **kwargs)

        if response.status >= 400:
            raise NetworkError(f"Erro HTTP {response.status}: {response.reason}")

        try:
            result = await response.json()
            return result  # type: ignore[no-any-return]
        except Exception as e:
            raise NetworkError(f"Resposta não é JSON válido: {e}") from e

    async def post_json(
        self, url: str, data: dict[str, Any], **kwargs
    ) -> dict[str, Any]:
        """Requisição POST com dados JSON."""
        kwargs.setdefault("json", data)
        kwargs.setdefault("headers", {}).update({"Content-Type": "application/json"})

        response = await self.post(url, **kwargs)

        if response.status >= 400:
            raise NetworkError(f"Erro HTTP {response.status}: {response.reason}")

        try:
            result = await response.json()
            return result  # type: ignore[no-any-return]
        except Exception as e:
            raise NetworkError(f"Resposta não é JSON válido: {e}") from e

    async def close(self) -> None:
        """Fecha a sessão HTTP."""
        if self._session:
            await self._session.close()

    async def __aenter__(self) -> "AsyncHTTPClient":
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.close()


class URLBuilder:
    """Construtor de URLs."""

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    def build(self, path: str, **params) -> str:
        """Constrói URL com path e parâmetros."""
        url = urljoin(self.base_url + "/", path.lstrip("/"))

        if params:
            # Filtrar parâmetros None
            filtered_params = {k: v for k, v in params.items() if v is not None}

            if filtered_params:
                from urllib.parse import urlencode

                url += "?" + urlencode(filtered_params)

        return url

    def is_valid_url(self, url: str) -> bool:
        """Verifica se URL é válida."""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False


class NetworkUtils:
    """Utilitários de rede."""

    @staticmethod
    def is_url_accessible(url: str, timeout: int = 10) -> bool:
        """Verifica se URL está acessível."""
        try:
            with HTTPClient(NetworkConfig(timeout=timeout)) as client:
                response = client.get(url)
                return response.status_code < 400  # type: ignore[no-any-return]
        except Exception:
            return False

    @staticmethod
    def extract_domain(url: str) -> str | None:
        """Extrai domínio da URL."""
        try:
            parsed = urlparse(url)
            return parsed.netloc
        except Exception:
            return None

    @staticmethod
    def is_same_domain(url1: str, url2: str) -> bool:
        """Verifica se duas URLs são do mesmo domínio."""
        domain1 = NetworkUtils.extract_domain(url1)
        domain2 = NetworkUtils.extract_domain(url2)
        return bool(domain1 and domain2 and domain1 == domain2)

    @staticmethod
    def sanitize_url(url: str) -> str:
        """Sanitiza URL removendo caracteres perigosos."""
        # Remove espaços e caracteres de controle
        url = "".join(char for char in url if ord(char) >= 32)
        url = url.strip()

        # Adiciona esquema se não tiver
        if not url.startswith(("http://", "https://")):
            url = "https://" + url

        return url


# Instâncias globais padrão
default_http_client = HTTPClient()
default_network_config = NetworkConfig()
