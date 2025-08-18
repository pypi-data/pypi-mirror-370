# appserver_sdk_python_ai/__init__.py
"""
SDK Python AI para AppServer
============================

SDK principal que integra diversos módulos de IA e automação.

Módulos disponíveis:
- webscraping: Módulo avançado de web scraping com conversão para markdown
- ocr: Módulo de OCR (Optical Character Recognition) para extração de texto de imagens
- llm: Módulo de integração com modelos de linguagem

Exemplo de uso:
    from appserver_sdk_python_ai.webscraping import DoclingWebScraper, ScrapingConfig

    config = ScrapingConfig(clean_html=True, enable_cache=True)
    scraper = DoclingWebScraper(config)
    result = scraper.scrape_to_markdown("https://example.com")
"""

import warnings
from collections.abc import Callable
from typing import Any, Optional

__version__ = "0.0.21"
__author__ = "appserver_sdk_python_ai"

# Declarar variáveis com tipos apropriados
webscraping: Any | None = None
llm: Any | None = None
ocr: Any | None = None
shared: Any | None = None
get_token_count: Callable[[str], int] | None = None
get_token_count_with_model: Callable[..., Any] | None = None
list_available_models: Callable[..., Any] | None = None
get_portuguese_models: Callable[..., Any] | None = None
get_model_info: Callable[[str], Any] | None = None

# Importar módulos principais
try:
    from appserver_sdk_python_ai import webscraping as webscraping_module

    webscraping = webscraping_module
except ImportError as e:
    webscraping = None
    warnings.warn(f"Módulo webscraping não pôde ser importado: {e}", stacklevel=2)

try:
    from appserver_sdk_python_ai import ocr as ocr_module

    ocr = ocr_module
except ImportError as e:
    ocr = None
    warnings.warn(f"Módulo OCR não pôde ser importado: {e}", stacklevel=2)

try:
    from appserver_sdk_python_ai import llm as llm_module

    llm = llm_module

    # Importar funções principais do LLM
    from appserver_sdk_python_ai.llm.service.token_service import (
        get_model_info as _get_model_info,
    )
    from appserver_sdk_python_ai.llm.service.token_service import (
        get_portuguese_models as _get_portuguese_models,
    )
    from appserver_sdk_python_ai.llm.service.token_service import (
        get_token_count as _get_token_count,
    )
    from appserver_sdk_python_ai.llm.service.token_service import (
        get_token_count_with_model as _get_token_count_with_model,
    )
    from appserver_sdk_python_ai.llm.service.token_service import (
        list_available_models as _list_available_models,
    )

    # Atribuir às variáveis globais
    get_model_info = _get_model_info
    get_portuguese_models = _get_portuguese_models
    get_token_count = _get_token_count
    get_token_count_with_model = _get_token_count_with_model
    list_available_models = _list_available_models
except ImportError as e:
    llm = None
    warnings.warn(f"Módulo LLM não pôde ser importado: {e}", stacklevel=2)

try:
    from appserver_sdk_python_ai.webscraping.core.config import DEFAULT_USER_AGENT
except ImportError:
    DEFAULT_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

# Importar módulo shared
try:
    from appserver_sdk_python_ai import shared as shared_module
    from appserver_sdk_python_ai.shared import (
        BaseConfig,
        ConfigManager,
        DependencyChecker,
        HealthChecker,
        SDKLogger,
        VersionInfo,
    )

    shared = shared_module
except ImportError as e:
    shared = None
    warnings.warn(f"Módulo shared não pôde ser importado: {e}", stacklevel=2)


def get_user_agent():
    """Retorna o user agent padrão do SDK."""
    return DEFAULT_USER_AGENT


# Exportar módulos disponíveis
__all__ = [
    # Módulos
    "webscraping",
    "ocr",
    "llm",
    "shared",
    # Funções LLM
    "get_token_count",
    "get_token_count_with_model",
    "list_available_models",
    "get_portuguese_models",
    "get_model_info",
    # Funcionalidades comuns (se disponíveis)
    "SDKLogger",
    "DependencyChecker",
    "HealthChecker",
    "VersionInfo",
    "BaseConfig",
    "ConfigManager",
    # Utilitários
    "get_user_agent",
    "get_sdk_info",
    "print_sdk_status",
    "health_check_all",
    # Informações
    "__version__",
    "__author__",
]


# Informações do SDK
def get_sdk_info():
    """Retorna informações sobre o SDK."""
    modules = []

    # Módulo WebScraping
    if webscraping is not None:
        modules.append(
            {
                "name": "webscraping",
                "version": getattr(webscraping, "__version__", "unknown"),
                "available": True,
            }
        )
    else:
        modules.append({"name": "webscraping", "version": None, "available": False})

    # Módulo OCR
    if ocr is not None:
        modules.append(
            {
                "name": "ocr",
                "version": getattr(ocr, "__version__", "unknown"),
                "available": True,
            }
        )
    else:
        modules.append({"name": "ocr", "version": None, "available": False})

    # Módulo LLM
    if llm is not None:
        modules.append(
            {
                "name": "llm",
                "version": getattr(llm, "__version__", "unknown"),
                "available": True,
            }
        )
    else:
        modules.append({"name": "llm", "version": None, "available": False})

    return {"sdk_version": __version__, "author": __author__, "modules": modules}


def health_check_all():
    """Verifica a saúde de todos os módulos."""
    modules_health = {}
    overall_status = "OK"

    # Verificar cada módulo
    if webscraping and hasattr(webscraping, "health_check"):
        modules_health["webscraping"] = webscraping.health_check()
        if modules_health["webscraping"]["status"] == "ERROR":
            overall_status = "ERROR"
        elif (
            modules_health["webscraping"]["status"] == "WARNING"
            and overall_status == "OK"
        ):
            overall_status = "WARNING"

    if ocr and hasattr(ocr, "health_check"):
        modules_health["ocr"] = ocr.health_check()
        if modules_health["ocr"]["status"] == "ERROR":
            overall_status = "ERROR"
        elif modules_health["ocr"]["status"] == "WARNING" and overall_status == "OK":
            overall_status = "WARNING"

    if llm and hasattr(llm, "health_check"):
        modules_health["llm"] = llm.health_check()
        if modules_health["llm"]["status"] == "ERROR":
            overall_status = "ERROR"
        elif modules_health["llm"]["status"] == "WARNING" and overall_status == "OK":
            overall_status = "WARNING"

    return {
        "sdk_version": __version__,
        "overall_status": overall_status,
        "modules": modules_health,
    }


def print_sdk_status():
    """Imprime status do SDK."""
    info = get_sdk_info()

    print("=" * 80)
    print("APPSERVER SDK PYTHON AI - STATUS COMPLETO")
    print("=" * 80)
    print(f"Versão: {info['sdk_version']}")
    print(f"Autor: {info['author']}")
    if shared and hasattr(VersionInfo, "get_python_version"):
        print(f"Python: {VersionInfo.get_python_version()}")

    print("\n📦 Módulos:")
    for module in info["modules"]:
        status = "✅" if module["available"] else "❌"
        version = module["version"] if module["version"] else "NÃO DISPONÍVEL"
        print(f"  {status} {module['name']}: {version}")

    # Status detalhado de cada módulo (se disponível)
    print("\n📊 STATUS DETALHADO:")
    print()

    if webscraping and hasattr(webscraping, "print_status"):
        webscraping.print_status()
        print()

    if ocr and hasattr(ocr, "print_status"):
        ocr.print_status()
        print()

    if llm and hasattr(llm, "print_status"):
        llm.print_status()
        print()

    print("=" * 80)
