# appserver_sdk_python_ai/webscraping/__init__.py
"""
Módulo de Web Scraping para appserver_sdk_python_ai
============================================

Este módulo fornece funcionalidades avançadas de web scraping com conversão
para markdown usando Docling e outras ferramentas.

Componentes principais:
- DoclingWebScraper: Scraper principal com Docling
- Utilitários de limpeza e validação
- Sistema de cache robusto
- Processamento em lote
- Tratamento avançado de erros

Exemplo de uso básico:
    from appserver_sdk_python_ai.webscraping import DoclingWebScraper, ScrapingConfig

    config = ScrapingConfig(clean_html=True, enable_cache=True)
    scraper = DoclingWebScraper(config)
    result = scraper.scrape_to_markdown("https://example.com")

Exemplo de uso simplificado:
    from appserver_sdk_python_ai.webscraping import quick_scrape
    markdown = quick_scrape("https://example.com")
"""

# Importações padrão
import logging
import warnings
from typing import Any, Optional, Union

# Importar funcionalidades comuns do módulo shared
from appserver_sdk_python_ai.shared import (
    DependencyChecker,
    HealthChecker,
    SDKLogger,
    VersionInfo,
)

__version__ = "1.0.0"
__author__ = "appserver_sdk_python_ai"


# Importar DEFAULT_USER_AGENT
try:
    from appserver_sdk_python_ai.webscraping.core.config import DEFAULT_USER_AGENT
except ImportError:
    DEFAULT_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

# Importações principais
from appserver_sdk_python_ai.webscraping.core.config import (
    DoclingConfig,
    GlobalWebScrapingConfig,
    ScrapingConfig,
    global_config,
)
from appserver_sdk_python_ai.webscraping.core.models import (
    BatchScrapingResult,
    CacheEntry,
    ScrapingResult,
    ScrapingStatus,
    WebPageMetadata,
)
from appserver_sdk_python_ai.webscraping.exceptions import (
    AuthenticationError,
    CacheError,
    ContentTooLargeError,
    ConversionError,
    JavaScriptError,
    NetworkError,
    ParsingError,
    ProxyError,
    RateLimitError,
    RobotsTxtError,
    ScrapingConfigError,
    SSLVerificationError,
    TimeoutError,
    UnsupportedFormatError,
    ValidationError,
    WebScrapingError,
)

# Importações condicionais para evitar erros quando dependências não estão instaladas
try:
    from appserver_sdk_python_ai.webscraping.docling.scraper import DoclingWebScraper

    SCRAPER_AVAILABLE = True
except ImportError as e:
    DoclingWebScraper = None  # type: ignore
    SCRAPER_AVAILABLE = False
    import warnings

    warnings.warn(f"DoclingWebScraper não pôde ser importado: {e}", stacklevel=2)

# OCR agora é um módulo independente
# Para usar OCR, importe diretamente: from appserver_sdk_python_ai.ocr import ...
OCR_AVAILABLE = False  # Mantido para compatibilidade, mas OCR não está mais aqui

try:
    from appserver_sdk_python_ai.webscraping.utils.cache import (
        CacheManager,
        MemoryCache,
    )
    from appserver_sdk_python_ai.webscraping.utils.cleaner import ContentCleaner
    from appserver_sdk_python_ai.webscraping.utils.validators import (
        ContentValidator,
        RobotsTxtChecker,
        URLValidator,
    )

    UTILS_AVAILABLE = True
except ImportError as e:
    ContentCleaner = None  # type: ignore
    CacheManager = None  # type: ignore
    MemoryCache = None  # type: ignore
    URLValidator = None  # type: ignore
    ContentValidator = None  # type: ignore
    RobotsTxtChecker = None  # type: ignore
    UTILS_AVAILABLE = False
    import warnings

    warnings.warn(f"Utilitários não puderam ser importados: {e}", stacklevel=2)

# Verificar disponibilidade do Docling
try:
    import docling

    DOCLING_AVAILABLE = True
    DOCLING_VERSION = getattr(docling, "__version__", "unknown")
except ImportError:
    DOCLING_AVAILABLE = False
    DOCLING_VERSION = None


# Funções de conveniência
def quick_scrape(
    url: str,
    clean_html: bool = True,
    include_images: bool = True,
    enable_cache: bool = False,
) -> str:
    """
    Função de conveniência para scraping rápido.

    Args:
        url: URL para fazer scraping
        clean_html: Se deve limpar HTML
        include_images: Se deve incluir imagens
        enable_cache: Se deve habilitar cache

    Returns:
        str: Conteúdo em markdown

    Raises:
        WebScrapingError: Em caso de erro no scraping
    """
    if not SCRAPER_AVAILABLE or DoclingWebScraper is None:
        raise WebScrapingError(
            "DoclingWebScraper não está disponível. Verifique as dependências."
        )

    config = ScrapingConfig(
        clean_html=clean_html, include_images=include_images, enable_cache=enable_cache
    )

    scraper = DoclingWebScraper(config)
    result = scraper.scrape_to_markdown(url)

    if not result.success:
        raise WebScrapingError(f"Falha no scraping: {result.error}", url)

    return result.content


def batch_scrape_simple(
    urls: list, output_dir: str = "scraped_content", max_workers: int = 5
) -> dict:
    """
    Função de conveniência para scraping em lote.

    Args:
        urls: Lista de URLs
        output_dir: Diretório de saída
        max_workers: Número máximo de workers

    Returns:
        dict: Dicionário com status de sucesso para cada URL
    """
    if not SCRAPER_AVAILABLE or DoclingWebScraper is None:
        raise WebScrapingError(
            "DoclingWebScraper não está disponível. Verifique as dependências."
        )

    scraper = DoclingWebScraper()
    results = scraper.batch_scrape(urls, output_dir, max_workers)

    return {result.url: result.success for result in results}


def create_custom_scraper(
    timeout: int = 30,
    user_agent: str | None = None,
    clean_html: bool = True,
    include_images: bool = True,
    enable_cache: bool = False,
    **kwargs,
):
    """
    Cria um scraper customizado com configurações específicas.

    Args:
        timeout: Timeout para requisições
        user_agent: User agent customizado
        clean_html: Se deve limpar HTML
        include_images: Se deve incluir imagens
        enable_cache: Se deve habilitar cache
        **kwargs: Outros parâmetros de configuração

    Returns:
        DoclingWebScraper: Instância configurada
    """
    if not SCRAPER_AVAILABLE or DoclingWebScraper is None:
        raise WebScrapingError(
            "DoclingWebScraper não está disponível. Verifique as dependências."
        )

    config = ScrapingConfig(
        timeout=timeout,
        user_agent=user_agent or global_config.default_user_agent,
        clean_html=clean_html,
        include_images=include_images,
        enable_cache=enable_cache,
        **kwargs,
    )

    return DoclingWebScraper(config)


# Funções de OCR foram movidas para o módulo independente appserver_sdk_python_ai.ocr
# Para usar OCR, importe diretamente:
# from appserver_sdk_python_ai.ocr import quick_ocr, batch_ocr, create_custom_ocr_processor


def _ocr_deprecated_warning():
    """Aviso sobre a mudança do OCR para módulo independente."""
    import warnings

    warnings.warn(
        "As funções de OCR foram movidas para o módulo independente 'appserver_sdk_python_ai.ocr'. "
        "Use: from appserver_sdk_python_ai.ocr import quick_ocr, batch_ocr, create_custom_ocr_processor",
        DeprecationWarning,
        stacklevel=3,
    )


def process_pdf_with_ocr(
    pdf_path: str,
    output_file: str | None = None,
    extract_images: bool = True,
    extract_tables: bool = True,
    **kwargs,
) -> "ScrapingResult":
    """
    Processa um PDF com OCR e extração de imagens/tabelas usando Docling.

    Args:
        pdf_path: Caminho para o arquivo PDF
        output_file: Caminho opcional para salvar o markdown
        extract_images: Se deve extrair imagens
        extract_tables: Se deve extrair tabelas
        **kwargs: Argumentos adicionais para o scraper

    Returns:
        ScrapingResult: Resultado do processamento

    Raises:
        ConversionError: Se o Docling não estiver disponível
        ValidationError: Se o arquivo não for encontrado
    """
    if not SCRAPER_AVAILABLE or DoclingWebScraper is None:
        raise WebScrapingError(
            "DoclingWebScraper não está disponível. Verifique as dependências."
        )

    scraper = DoclingWebScraper(**kwargs)
    return scraper.process_pdf_with_ocr(
        pdf_path=pdf_path,
        output_file=output_file,
        extract_images=extract_images,
        extract_tables=extract_tables,
    )


def batch_process_pdfs(
    pdf_paths: list[str],
    output_dir: str | None = None,
    max_workers: int = 3,
    extract_images: bool = True,
    extract_tables: bool = True,
    progress_callback=None,
    **kwargs,
) -> list["ScrapingResult"]:
    """
    Processa múltiplos PDFs em paralelo com OCR.

    Args:
        pdf_paths: Lista de caminhos para PDFs
        output_dir: Diretório de saída (opcional)
        max_workers: Número máximo de threads
        extract_images: Se deve extrair imagens
        extract_tables: Se deve extrair tabelas
        progress_callback: Callback para acompanhar progresso
        **kwargs: Argumentos adicionais para o scraper

    Returns:
        List[ScrapingResult]: Lista de resultados
    """
    if not SCRAPER_AVAILABLE or DoclingWebScraper is None:
        raise WebScrapingError(
            "DoclingWebScraper não está disponível. Verifique as dependências."
        )

    scraper = DoclingWebScraper(**kwargs)
    return scraper.batch_process_pdfs(
        pdf_paths=pdf_paths,
        output_dir=output_dir,
        max_workers=max_workers,
        extract_images=extract_images,
        extract_tables=extract_tables,
        progress_callback=progress_callback,
    )


# Funções de informação
def get_version_info():
    """Retorna informações sobre a versão e dependências."""
    return VersionInfo.create_version_info(
        module_name="webscraping",
        module_version=__version__,
        dependencies=check_dependencies(),
        additional_info={
            "docling_available": DOCLING_AVAILABLE,
            "docling_version": DOCLING_VERSION,
        },
    )


def check_dependencies():
    """Verifica se todas as dependências estão instaladas."""
    return DependencyChecker.check_dependencies(
        ["requests", "beautifulsoup4", "lxml", "docling"]
    )


def health_check():
    """Verifica a saúde do módulo e suas dependências."""
    dependencies = check_dependencies()
    features = {
        "docling_conversion": DOCLING_AVAILABLE,
        "cache_system": True,
        "batch_processing": True,
        "ocr_processing": OCR_AVAILABLE,
    }

    return HealthChecker.create_health_report(
        module_name="webscraping",
        version=__version__,
        dependencies=dependencies,
        features=features,
        critical_deps=["requests", "beautifulsoup4"],
        optional_deps=["lxml", "docling"],
    )


def print_status():
    """Imprime status do módulo."""
    health = health_check()

    # Adicionar informações específicas do webscraping
    print("=" * 60)
    print("MÓDULO WEB SCRAPING - appserver_sdk_python_ai")
    print("=" * 60)
    print(f"Versão: {__version__}")
    print(f"Status: {health['status']}")
    print(f"Docling: {'✅ Disponível' if DOCLING_AVAILABLE else '❌ Não disponível'}")
    print(f"OCR: {'✅ Disponível' if OCR_AVAILABLE else '❌ Não disponível'}")

    # Usar o método padrão para o resto
    HealthChecker.print_health_status(
        health, show_dependencies=True, show_features=True
    )

    # Informação adicional específica do webscraping
    print("\n🔍 Informações adicionais:")
    print("  • OCR foi movido para módulo independente 'appserver_sdk_python_ai.ocr'")


# Configuração de logging


def setup_logging(level=logging.INFO, format_string=None):
    """
    Configura logging para o módulo.

    Args:
        level: Nível de logging
        format_string: Formato customizado para logs
    """
    if format_string is None:
        format_string = global_config.log_format

    return SDKLogger.setup_logging(
        level=level,
        format_string=format_string,
        logger_name="appserver_sdk_python_ai.webscraping",
    )


# Exportar tudo necessário
__all__ = [
    # Classes principais
    "DoclingWebScraper",
    "ScrapingConfig",
    "DoclingConfig",
    "GlobalWebScrapingConfig",
    "global_config",
    # Modelos
    "ScrapingResult",
    "BatchScrapingResult",
    "WebPageMetadata",
    "CacheEntry",
    "ScrapingStatus",
    # Exceções
    "WebScrapingError",
    "NetworkError",
    "TimeoutError",
    "AuthenticationError",
    "RateLimitError",
    "ProxyError",
    "SSLVerificationError",
    "ContentTooLargeError",
    "UnsupportedFormatError",
    "ValidationError",
    "ConversionError",
    "CacheError",
    "ScrapingConfigError",
    "JavaScriptError",
    "ParsingError",
    "RobotsTxtError",
    # Utilitários
    "ContentCleaner",
    "CacheManager",
    "MemoryCache",
    "URLValidator",
    "ContentValidator",
    "RobotsTxtChecker",
    # Funções de conveniência
    "quick_scrape",
    "batch_scrape_simple",
    "create_custom_scraper",
    "process_pdf_with_ocr",
    "batch_process_pdfs",
    # Informações e configuração
    "get_version_info",
    "check_dependencies",
    "health_check",
    "print_status",
    "setup_logging",
    # Constantes
    "__version__",
    "DOCLING_AVAILABLE",
    "DOCLING_VERSION",
    "OCR_AVAILABLE",  # Mantido para compatibilidade
    "DEFAULT_USER_AGENT",
]

# Inicialização automática
logger = logging.getLogger(__name__)
logger.info(f"Módulo webscraping v{__version__} carregado")

if not DOCLING_AVAILABLE:
    logger.warning("Docling não disponível - usando conversão básica")
