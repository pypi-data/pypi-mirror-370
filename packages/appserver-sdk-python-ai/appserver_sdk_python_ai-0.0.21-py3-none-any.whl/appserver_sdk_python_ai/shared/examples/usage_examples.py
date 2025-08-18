"""Exemplos de uso das funcionalidades centralizadas do módulo shared."""

import asyncio
from typing import Any

# Importações das funcionalidades centralizadas
from appserver_sdk_python_ai.shared.core.cache import (
    FileCacheBackend,
    MemoryCacheBackend,
    UnifiedCacheManager,
)
from appserver_sdk_python_ai.shared.core.engines import (
    BaseEngine,
    EngineManager,
    EngineRegistry,
)
from appserver_sdk_python_ai.shared.core.network import (
    AsyncHTTPClient,
    HTTPClient,
    NetworkConfig,
)
from appserver_sdk_python_ai.shared.core.standard_configs import (
    create_llm_config,
    create_ocr_config,
    create_webscraping_config,
)
from appserver_sdk_python_ai.shared.core.validation import (
    DataValidator,
    TypeValidator,
    ValidationRule,
    ValidationSchema,
)
from appserver_sdk_python_ai.shared.utils.processing import FileProcessor, TextProcessor


def example_cache_usage():
    """Exemplo de uso do sistema de cache unificado."""
    print("=== Exemplo: Sistema de Cache Unificado ===")

    # Cache em memória
    memory_backend = MemoryCacheBackend(max_entries=100)
    memory_cache = UnifiedCacheManager(backend=memory_backend)

    # Armazenar dados
    memory_cache.set("user:123", {"name": "João", "email": "joao@example.com"}, ttl=600)

    # Recuperar dados
    user_data = memory_cache.get("user:123")
    print(f"Dados do usuário: {user_data}")

    # Cache em arquivo
    file_backend = FileCacheBackend(cache_dir=".cache", max_size_mb=50)
    file_cache = UnifiedCacheManager(backend=file_backend)

    # Usar decorador de cache
    @file_cache.cached(ttl=300)
    def expensive_operation(param1: str, param2: int) -> str:
        """Operação custosa que será cacheada."""
        print(f"Executando operação custosa com {param1}, {param2}")
        return f"Resultado para {param1}-{param2}"

    # Primeira chamada - executa a função
    result1 = expensive_operation("test", 42)
    print(f"Resultado 1: {result1}")

    # Segunda chamada - usa cache
    result2 = expensive_operation("test", 42)
    print(f"Resultado 2: {result2}")

    print()


def example_validation_usage():
    """Exemplo de uso do sistema de validação."""
    print("=== Exemplo: Sistema de Validação ===")

    # Validação de configuração de rede
    network_config = {
        "timeout": 30,
        "max_retries": 3,
        "user_agent": "MyApp/1.0",
        "verify_ssl": True,
    }

    try:
        DataValidator.validate_network_config(network_config)
        print("✓ Configuração de rede válida")
    except Exception as e:
        print(f"✗ Erro na configuração de rede: {e}")

    # Validação personalizada
    schema = ValidationSchema(
        [
            ValidationRule("name", [TypeValidator(str)], required=True),
            ValidationRule("age", [TypeValidator(int)], required=True),
            ValidationRule("email", [TypeValidator(str)], required=False),
        ]
    )

    valid_data = {"name": "Maria", "age": 25, "email": "maria@example.com"}
    invalid_data = {"name": "João", "age": "vinte e cinco"}  # age deve ser int

    try:
        schema.validate_and_raise(valid_data)
        print("✓ Dados válidos")
    except Exception as e:
        print(f"✗ Erro nos dados: {e}")

    try:
        schema.validate_and_raise(invalid_data)
        print("✓ Dados inválidos passaram (não deveria acontecer)")
    except Exception as e:
        print(f"✓ Erro esperado nos dados inválidos: {e}")

    print()


def example_network_usage():
    """Exemplo de uso dos utilitários de rede."""
    print("=== Exemplo: Utilitários de Rede ===")

    # Configuração de rede
    config = NetworkConfig(
        timeout=30,
        max_retries=3,
        user_agent="SDK-Example/1.0",
        rate_limit=10,  # 10 requisições por minuto
        rate_limit_window=60,
    )

    # Cliente HTTP
    client = HTTPClient(config=config)

    try:
        # Fazer uma requisição GET
        response = client.get("https://httpbin.org/get")
        print(f"✓ GET request successful: {response.status_code}")

        # Fazer uma requisição POST
        data = {"key": "value", "message": "Hello from SDK"}
        response = client.post("https://httpbin.org/post", json=data)
        print(f"✓ POST request successful: {response.status_code}")

    except Exception as e:
        print(f"✗ Erro na requisição: {e}")

    print()


async def example_async_network_usage():
    """Exemplo de uso do cliente HTTP assíncrono."""
    print("=== Exemplo: Cliente HTTP Assíncrono ===")

    config = NetworkConfig(timeout=30, max_retries=2)

    async with AsyncHTTPClient(config=config) as client:
        try:
            # Requisição GET assíncrona
            response = await client.get("https://httpbin.org/get")
            print(f"✓ Async GET successful: {response.status}")

            # Requisição POST assíncrona
            data = {"async": True, "message": "Hello async world"}
            response = await client.post("https://httpbin.org/post", json=data)
            print(f"✓ Async POST successful: {response.status}")

        except Exception as e:
            print(f"✗ Erro na requisição assíncrona: {e}")

    print()


class ExampleEngine(BaseEngine):
    """Engine de exemplo para demonstrar o sistema de gerenciamento."""

    def __init__(self, name: str, config: dict[str, Any] | None = None):
        super().__init__(name, config)

    def check_availability(self) -> bool:
        """Verifica se a engine está disponível."""
        return True  # Sempre disponível para exemplo

    def initialize(self) -> None:
        """Inicializa a engine."""
        print(f"Inicializando engine {self.name}")
        # Simulação de inicialização

    def get_version(self) -> str | None:
        """Retorna versão da engine."""
        return "1.0.0"

    def get_capabilities(self) -> list[str]:
        """Retorna lista de capacidades da engine."""
        return ["text_processing", "batch_processing"]

    def validate_config(self) -> None:
        """Valida configuração da engine."""
        # Implementação básica de validação
        if not self.name:
            raise ValueError("Nome da engine é obrigatório")
        if not isinstance(self.config, dict):
            raise ValueError("Configuração deve ser um dicionário")

    def process(self, data: Any) -> Any:
        """Processa dados usando esta engine."""
        return f"Processado por {self.name}: {data}"


def example_engine_management():
    """Exemplo de uso do sistema de gerenciamento de engines."""
    print("=== Exemplo: Gerenciamento de Engines ===")

    # Criar registry e manager
    registry = EngineRegistry()
    manager = EngineManager(registry)

    # Registrar engines
    registry.register(ExampleEngine, "engine1")
    registry.register(ExampleEngine, "engine2")
    registry.register(ExampleEngine, "engine3")

    # Definir ordem de preferência
    manager.set_preferred_engines(["engine1", "engine2", "engine3"])

    # Obter melhor engine disponível
    best_engine = manager.get_best_engine()
    if best_engine:
        print(f"✓ Melhor engine: {best_engine.name}")

        # Processar dados
        result = best_engine.process("dados de teste")
        print(f"✓ Resultado: {result}")
    else:
        print("✗ Nenhuma engine disponível")

    # Executar com fallback
    try:
        result = manager.execute_with_fallback(
            lambda engine: engine.process("dados importantes")
        )
        print(f"✓ Resultado com fallback: {result}")
    except Exception as e:
        print(f"✗ Erro na execução com fallback: {e}")

    print()


def example_processing_utilities():
    """Exemplo de uso dos utilitários de processamento."""
    print("=== Exemplo: Utilitários de Processamento ===")

    # Processamento de texto
    text_processor = TextProcessor()

    raw_text = "  Este é um TEXTO com espaços extras e MAIÚSCULAS!  "
    cleaned_text = text_processor.clean_text(raw_text)
    print(f"Texto limpo: '{cleaned_text}'")

    # Extrair palavras
    words = text_processor.extract_words(
        "Python é uma linguagem de programação poderosa e versátil"
    )
    print(f"Palavras extraídas: {words[:5]}")  # Mostrar apenas as primeiras 5

    # Processamento de arquivos
    file_processor = FileProcessor()

    # Simular dados de arquivo
    test_data = b"Dados de teste para hash"
    temp_file = file_processor.create_temp_file(test_data, suffix=".txt")
    file_hash = file_processor.calculate_file_hash(temp_file)
    print(f"Hash do arquivo: {file_hash}")

    # Limpar arquivo temporário
    file_processor.cleanup_temp_files([temp_file])

    # Obter informações do arquivo temporário criado
    temp_file2 = file_processor.create_temp_file("Conteúdo de teste", suffix=".txt")
    file_info = file_processor.get_file_info(temp_file2)
    print(f"Informações do arquivo: {file_info['name']} ({file_info['size_mb']} MB)")
    file_processor.cleanup_temp_files([temp_file2])

    print()


def example_standard_configs():
    """Exemplo de uso das configurações padronizadas."""
    print("=== Exemplo: Configurações Padronizadas ===")

    # Configuração para web scraping
    webscraping_config = create_webscraping_config(
        network={"default_timeout": 45, "max_retries": 5}, cache={"cache_ttl": 7200}
    )

    print("Configuração WebScraping:")
    print(f"  - Timeout: {webscraping_config.network.default_timeout}s")
    print(f"  - Cache TTL: {webscraping_config.cache.cache_ttl}s")
    print(f"  - User Agent: {webscraping_config.network.user_agent}")

    # Configuração para OCR
    ocr_config = create_ocr_config(processing={"max_workers": 8, "batch_size": 20})

    print("\nConfiguração OCR:")
    print(f"  - Max Workers: {ocr_config.processing.max_workers}")
    print(f"  - Batch Size: {ocr_config.processing.batch_size}")
    print(f"  - Engines Preferidas: {ocr_config.engines.preferred_engines}")

    # Configuração para LLM
    llm_config = create_llm_config(
        security={"encryption_enabled": True},
        engines={"preferred_engines": ["openai", "anthropic"]},
    )

    print("\nConfiguração LLM:")
    print(f"  - Encryption: {llm_config.security.encryption_enabled}")
    print(f"  - Rate Limit: {llm_config.network.rate_limit}")
    print(f"  - Engines Preferidas: {llm_config.engines.preferred_engines}")

    # Validar todas as configurações
    try:
        webscraping_config.validate_all()
        ocr_config.validate_all()
        llm_config.validate_all()
        print("\n✓ Todas as configurações são válidas")
    except Exception as e:
        print(f"\n✗ Erro na validação: {e}")

    print()


def main():
    """Executa todos os exemplos."""
    print("🚀 Demonstração das Funcionalidades Centralizadas do SDK\n")

    # Exemplos síncronos
    example_cache_usage()
    example_validation_usage()
    example_network_usage()
    example_engine_management()
    example_processing_utilities()
    example_standard_configs()

    # Exemplo assíncrono
    print("Executando exemplo assíncrono...")
    asyncio.run(example_async_network_usage())

    print("✅ Todos os exemplos executados com sucesso!")


if __name__ == "__main__":
    main()
