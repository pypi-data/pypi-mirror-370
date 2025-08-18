# appserver_sdk_python_ai/webscraping/core/config.py
"""
Configurações e constantes para o módulo de webscraping.
"""

from dataclasses import dataclass
from typing import Any

# Constantes globais
DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)

DEFAULT_HEADERS = {
    "User-Agent": DEFAULT_USER_AGENT,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8,es;q=0.7",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
}


@dataclass
class ScrapingConfig:
    """Configurações para operações de scraping."""

    # Configurações de rede
    timeout: int = 30
    max_content_length: int = 50 * 1024 * 1024  # 50MB
    follow_redirects: bool = True
    max_redirects: int = 5
    verify_ssl: bool = True
    encoding: str | None = None

    # Configurações de retry
    retry_attempts: int = 3
    retry_delay: float = 1.0

    # Configurações de conteúdo
    clean_html: bool = True
    include_images: bool = True
    include_links: bool = True

    # Configurações de cache
    enable_cache: bool = False
    cache_ttl: int = 3600  # 1 hora
    cache_dir: str = ".webscraping_cache"

    # Headers e autenticação
    user_agent: str = DEFAULT_USER_AGENT
    headers: dict[str, str] | None = None
    cookies: dict[str, str] | None = None

    def get_headers(self) -> dict[str, str]:
        """Retorna headers combinados."""
        headers = DEFAULT_HEADERS.copy()
        headers["User-Agent"] = self.user_agent
        if self.headers:
            headers.update(self.headers)
        return headers


@dataclass
class DoclingConfig:
    """Configurações específicas para Docling."""

    do_table_structure: bool = True
    pipeline_options: dict[str, Any] | None = None


@dataclass
class GlobalWebScrapingConfig:
    """Configurações globais para o módulo de webscraping."""

    default_timeout: int = 30
    default_max_workers: int = 5
    default_cache_ttl: int = 3600
    default_user_agent: str = DEFAULT_USER_AGENT

    # Configurações de logging
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Configurações de segurança
    blocked_domains: list[str] | None = None
    rate_limit: float | None = None  # Requisições por segundo

    def __post_init__(self):
        if self.blocked_domains is None:
            self.blocked_domains = ["localhost", "127.0.0.1", "0.0.0.0", "::1"]


# Instância global de configuração
global_config = GlobalWebScrapingConfig()
