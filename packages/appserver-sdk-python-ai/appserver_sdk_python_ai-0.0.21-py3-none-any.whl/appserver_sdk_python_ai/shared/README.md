# Módulo Shared - AppServer SDK Python AI

O módulo `shared` contém funcionalidades comuns e centralizadas utilizadas por todos os módulos do SDK, promovendo reutilização de código, consistência e eficiência entre os módulos. Este módulo foi expandido significativamente para incluir sistemas avançados de cache, validação, rede, gerenciamento de engines e processamento.

## 🚀 Funcionalidades Principais

### Funcionalidades Originais

#### 1. Sistema de Exceções (`exceptions.py`)

Classes de exceção padronizadas para todo o SDK.

#### 2. Sistema de Logging (`logging.py`)

Sistema de logging centralizado e configurável.

#### 3. Utilitários Comuns (`utils.py`)

Ferramentas como `DependencyChecker`, `HealthChecker` e `VersionInfo`.

#### 4. Sistema de Configuração (`config.py`)

Classes base para configurações e gerenciamento centralizado.

### 🆕 Novas Funcionalidades Centralizadas

#### 5. Sistema de Cache Unificado (`cache.py`)

Sistema de cache flexível com suporte a múltiplos backends:

```python
from appserver_sdk_python_ai.shared import UnifiedCacheManager, MemoryCacheBackend, FileCacheBackend

# Cache em memória
memory_cache = UnifiedCacheManager(backend=MemoryCacheBackend())
memory_cache.set("key", "value", ttl=300)
value = memory_cache.get("key")

# Cache em arquivo
file_cache = UnifiedCacheManager(backend=FileCacheBackend(cache_dir=".cache"))

# Decorador de cache
@file_cache.cached(ttl=600)
def expensive_function(param):
    return f"Resultado para {param}"
```

#### 6. Sistema de Validação (`validation.py`)

Validação robusta de dados e configurações:

```python
from appserver_sdk_python_ai.shared import DataValidator, ValidationSchema, ValidationRule, TypeValidator

# Validação de configuração de rede
network_config = {'timeout': 30, 'max_retries': 3}
DataValidator.validate_network_config(network_config)

# Schema personalizado
schema = ValidationSchema([
    ValidationRule('name', [TypeValidator(str)], required=True),
    ValidationRule('age', [TypeValidator(int)], required=True)
])
schema.validate_and_raise({'name': 'João', 'age': 25})
```

#### 7. Utilitários de Rede (`network.py`)

Clientes HTTP síncronos e assíncronos com recursos avançados:

```python
from appserver_sdk_python_ai.shared import HTTPClient, AsyncHTTPClient, NetworkConfig

# Cliente síncrono
config = NetworkConfig(timeout=30, max_retries=3, rate_limit=10)
client = HTTPClient(config=config)
response = client.get('https://api.example.com/data')

# Cliente assíncrono
async with AsyncHTTPClient(config=config) as async_client:
    response = await async_client.get('https://api.example.com/data')
```

#### 8. Gerenciamento de Engines (`engines.py`)

Sistema para gerenciar diferentes engines/provedores:

```python
from appserver_sdk_python_ai.shared import BaseEngine, EngineRegistry, EngineManager

class MyEngine(BaseEngine):
    @property
    def name(self) -> str:
        return "my_engine"
    
    def process(self, data):
        return f"Processado: {data}"

# Registrar e usar
registry = EngineRegistry()
registry.register('my_engine', MyEngine)

manager = EngineManager(registry)
engine = manager.get_best_engine()
result = engine.process("dados")
```

#### 9. Utilitários de Processamento (`processing.py`)

Ferramentas para processamento de texto, imagens e arquivos:

```python
from appserver_sdk_python_ai.shared import TextProcessor, ImageProcessor, FileProcessor

# Processamento de texto
text_processor = TextProcessor()
cleaned = text_processor.clean_text("  Texto com espaços  ")
keywords = text_processor.extract_keywords("Python é uma linguagem poderosa")

# Processamento de imagens (requer Pillow)
image_processor = ImageProcessor()
resized = image_processor.resize_image(image_data, (800, 600))

# Processamento de arquivos
file_processor = FileProcessor()
file_hash = file_processor.calculate_hash(file_data)
is_safe = file_processor.is_safe_file("document.pdf")
```

#### 10. Configurações Padronizadas (`standard_configs.py`)

Configuração unificada para diferentes tipos de módulos:

```python
from appserver_sdk_python_ai.shared import (
    create_webscraping_config,
    create_ocr_config,
    create_llm_config
)

# Configuração otimizada para web scraping
webscraping_config = create_webscraping_config(
    network={'timeout': 45},
    cache={'cache_ttl': 7200}
)

# Configuração otimizada para OCR
ocr_config = create_ocr_config(
    processing={'max_workers': 8}
)

# Configuração otimizada para LLM
llm_config = create_llm_config(
    security={'encryption_enabled': True}
)
```

## 📁 Estrutura Expandida do Módulo

```
shared/
├── __init__.py              # Exportações principais
├── README.md               # Documentação
├── core/                   # Funcionalidades centrais
│   ├── __init__.py
│   ├── config.py          # Sistema de configuração
│   ├── cache.py           # Sistema de cache unificado
│   ├── validation.py      # Sistema de validação
│   ├── network.py         # Utilitários de rede
│   ├── engines.py         # Gerenciamento de engines
│   └── standard_configs.py # Configurações padronizadas
├── utils/                  # Utilitários auxiliares
│   ├── __init__.py
│   ├── common.py          # Utilitários comuns
│   ├── logging.py         # Sistema de logging
│   └── processing.py      # Utilitários de processamento
└── examples/              # Exemplos de uso
    ├── __init__.py
    └── usage_examples.py  # Exemplos práticos
```

## Funcionalidades Detalhadas

### 1. Sistema de Exceções (`exceptions.py`)

Classes de exceção padronizadas para todo o SDK:

```python
from appserver_sdk_python_ai.shared import (
    SDKError,
    ConfigurationError,
    ValidationError,
    NetworkError,
    TimeoutError,
    AuthenticationError,
    RateLimitError
)

# Exemplo de uso
try:
    # código que pode falhar
    pass
except NetworkError as e:
    print(f"Erro de rede: {e}")
```

### 2. Sistema de Logging (`logging.py`)

Sistema de logging centralizado e configurável:

```python
from appserver_sdk_python_ai.shared import SDKLogger

# Configurar logging
SDKLogger.setup_logging(level="INFO", format="detailed")

# Obter logger para um módulo
logger = SDKLogger.get_logger("meu_modulo")
logger.info("Mensagem de log")

# Controlar nível de logging
SDKLogger.set_level("DEBUG")

# Desabilitar/habilitar logging
SDKLogger.disable_logging()
SDKLogger.enable_logging()
```

### 3. Utilitários Comuns (`utils.py`)

#### DependencyChecker

Verificação padronizada de dependências:

```python
from appserver_sdk_python_ai.shared import DependencyChecker

# Verificar dependências
deps = DependencyChecker.check_dependencies(["requests", "beautifulsoup4"])
print(deps)  # {'requests': '2.28.1', 'beautifulsoup4': 'NOT_INSTALLED'}
```

#### HealthChecker

Criação de relatórios de saúde padronizados:

```python
from appserver_sdk_python_ai.shared import HealthChecker

# Criar relatório de saúde
health = HealthChecker.create_health_report(
    module_name="meu_modulo",
    version="1.0.0",
    dependencies={"requests": "2.28.1"},
    features={"feature1": True, "feature2": False},
    critical_deps=["requests"],
    optional_deps=["beautifulsoup4"]
)

# Imprimir status formatado
HealthChecker.print_health_status(health)
```

#### VersionInfo

Informações de versão do Python e módulos:

```python
from appserver_sdk_python_ai.shared import VersionInfo

# Obter versão do Python
python_version = VersionInfo.get_python_version()
print(f"Python: {python_version}")

# Obter informações detalhadas
info = VersionInfo.get_version_info("1.0.0")
print(info)
```

### 4. Sistema de Configuração (`config.py`)

#### BaseConfig

Classe base para configurações:

```python
from appserver_sdk_python_ai.shared import BaseConfig

class MinhaConfig(BaseConfig):
    def __init__(self):
        super().__init__()
        self.minha_opcao = "valor"
```

#### ConfigManager

Gerenciamento centralizado de configurações:

```python
from appserver_sdk_python_ai.shared import ConfigManager, BaseConfig

# Registrar configuração
config = BaseConfig()
ConfigManager.register_config("meu_modulo", config)

# Obter configuração
config = ConfigManager.get_config("meu_modulo")

# Listar configurações
configs = ConfigManager.list_configs()
```

## Integração com Módulos

Todos os módulos do SDK (`webscraping`, `ocr`, `llm`) foram refatorados para utilizar as funcionalidades do módulo `shared`, garantindo:

- **Consistência**: Mesmo comportamento em todos os módulos
- **Manutenibilidade**: Código centralizado e reutilizável
- **Padronização**: Interfaces e formatos uniformes
- **Eficiência**: Redução de código duplicado

## Exemplo de Uso Completo

```python
from appserver_sdk_python_ai.shared import (
    SDKLogger,
    DependencyChecker,
    HealthChecker,
    VersionInfo,
    ConfigManager,
    BaseConfig
)

# Configurar logging
SDKLogger.setup_logging(level="INFO")
logger = SDKLogger.get_logger("exemplo")

# Verificar dependências
deps = DependencyChecker.check_dependencies(["requests"])
logger.info(f"Dependências: {deps}")

# Criar relatório de saúde
health = HealthChecker.create_health_report(
    module_name="exemplo",
    version="1.0.0",
    dependencies=deps,
    features={"feature1": True}
)

# Imprimir status
HealthChecker.print_health_status(health)

# Informações de versão
logger.info(f"Python: {VersionInfo.get_python_version()}")
```

## 🎯 Benefícios da Centralização Expandida

### ✅ Consistência
- Comportamento uniforme entre módulos
- Padrões de configuração consistentes
- Tratamento de erros padronizado
- Interfaces uniformes para cache, rede e processamento

### ✅ Reutilização
- Eliminação de código duplicado
- Funcionalidades testadas e otimizadas
- Manutenção centralizada
- Componentes modulares e intercambiáveis

### ✅ Flexibilidade
- Configuração modular por tipo de módulo
- Suporte a múltiplos backends (cache, engines)
- Extensibilidade através de interfaces bem definidas
- Fallbacks automáticos para engines

### ✅ Performance
- Cache inteligente com TTL e limpeza automática
- Rate limiting automático para requisições
- Processamento otimizado com suporte a paralelização
- Backends de cache eficientes (memória e arquivo)

### ✅ Segurança
- Validação rigorosa de dados de entrada
- Configurações de segurança padronizadas
- Tratamento seguro de credenciais e dados sensíveis
- Verificação SSL e sanitização de URLs

### ✅ Facilidade de Uso
- Configurações pré-definidas para casos comuns
- Instâncias padrão prontas para uso
- Exemplos práticos e documentação abrangente
- APIs intuitivas e bem documentadas

## 🔄 Migração de Código Existente

### Antes (código duplicado em cada módulo)
```python
# Em webscraping/cache.py
class MemoryCache:
    def __init__(self):
        self.cache = {}
    def get(self, key): pass
    def set(self, key, value): pass

# Em ocr/utils.py  
class ImageProcessor:
    def resize_image(self, image, size): pass

# Em llm/http_client.py
class HTTPClient:
    def __init__(self):
        self.session = requests.Session()
    def get(self, url): pass
```

### Depois (usando funcionalidades centralizadas)
```python
# Em qualquer módulo
from appserver_sdk_python_ai.shared import (
    default_cache,
    default_http_client,
    ImageProcessor,
    create_webscraping_config
)

# Usar funcionalidades centralizadas
config = create_webscraping_config()
cache = default_cache
client = default_http_client
image_processor = ImageProcessor()
```

## 📚 Exemplos Práticos Completos

Veja o arquivo `examples/usage_examples.py` para exemplos completos de uso de todas as funcionalidades:

```python
# Executar todos os exemplos
from appserver_sdk_python_ai.shared.examples import usage_examples
usage_examples.main()

# Executar exemplos específicos
usage_examples.example_cache_usage()
usage_examples.example_network_usage()
usage_examples.example_validation_usage()
```

## 🚦 Compatibilidade e Migração Segura

Todas as funcionalidades foram implementadas mantendo **100% de compatibilidade** com o código existente:

- ✅ **Não quebra APIs existentes**: Funcionalidades antigas continuam funcionando
- ✅ **Funcionalidades opcionais**: Novos recursos são opt-in
- ✅ **Configuração flexível**: Suporte a configurações customizadas
- ✅ **Fallbacks automáticos**: Comportamento padrão quando configuração não especificada
- ✅ **Migração gradual**: Módulos podem adotar funcionalidades incrementalmente

## 📈 Próximos Passos Recomendados

1. **Integração Gradual**: 
   - Migrar módulos existentes para usar cache unificado
   - Adotar configurações padronizadas
   - Utilizar utilitários de rede centralizados

2. **Testes Abrangentes**: 
   - Implementar testes unitários para novas funcionalidades
   - Testes de integração entre módulos
   - Testes de performance e stress

3. **Documentação e Exemplos**:
   - Expandir exemplos de uso
   - Guias de migração específicos por módulo
   - Documentação de APIs detalhada

4. **Monitoramento e Métricas**:
   - Adicionar logging de performance
   - Métricas de uso de cache
   - Monitoramento de rate limiting

5. **Otimizações Baseadas em Uso Real**:
   - Ajustar configurações padrão
   - Otimizar backends de cache
   - Melhorar algoritmos de fallback

## 🤝 Contribuição e Desenvolvimento

Para contribuir com o módulo shared:

1. **Compatibilidade**: Sempre manter compatibilidade com código existente
2. **Testes**: Adicionar testes para novas funcionalidades
3. **Documentação**: Documentar mudanças e exemplos de uso
4. **Padrões**: Seguir os padrões de código estabelecidos
5. **Impacto**: Considerar impacto em todos os módulos dependentes
6. **Performance**: Avaliar impacto na performance
7. **Segurança**: Revisar implicações de segurança

---

**Nota Importante**: Este módulo é a **base fundamental** para todos os outros módulos do SDK. Mudanças aqui devem ser cuidadosamente testadas e validadas para evitar quebras em funcionalidades dependentes. A arquitetura foi projetada para ser extensível e compatível, permitindo evolução contínua sem impacto negativo.