# AppServer SDK Python AI

[![Python Version](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

SDK Python para integração com serviços de IA da AppServer.

## 🚀 Características

- Cliente HTTP assíncrono e síncrono
- Modelos Pydantic para validação de dados
- Retry automático com backoff exponencial  
- Type hints completos
- Suporte a múltiplos provedores de IA
- Logging estruturado
- Testes abrangentes

## 📦 Módulos Disponíveis

### 🤖 LLM (Large Language Models)
Módulo profissional para integração com modelos de linguagem e APIs de inteligência artificial.

**Características principais:**
- Cliente assíncrono e síncrono
- Retry automático com backoff exponencial
- Suporte a múltiplos provedores de IA
- Modelos Pydantic com type hints completos
- Sistema de logging estruturado
- Gerenciamento seguro de API keys

📖 **[Documentação completa do LLM](src/appserver_sdk_python_ai/llm/README.md)**

### 🔍 WebScraping
Módulo profissional de web scraping com conversão para markdown usando Docling.

**Características principais:**
- Scraping robusto com retry automático
- Conversão de alta qualidade usando Docling (IBM)
- Processamento paralelo de múltiplas URLs
- Sistema de cache inteligente
- Limpeza automática de conteúdo
- Extração de metadados ricos
- **OCR integrado**: Processamento de imagens e PDFs
- **Múltiplos engines**: Tesseract, EasyOCR, PaddleOCR

📖 **[Documentação completa do WebScraping](src/appserver_sdk_python_ai/webscraping/README.md)**

### 👁️ OCR (Optical Character Recognition)
Módulo especializado para extração de texto de imagens e documentos.

**Características principais:**
- Múltiplos engines de OCR (Tesseract, EasyOCR, PaddleOCR)
- Seleção automática do melhor engine disponível
- Formatos suportados: JPEG, PNG, GIF, TIFF, BMP, WEBP
- Pré-processamento automático de imagens
- Cache inteligente de resultados
- Processamento em lote paralelo
- Suporte a múltiplos idiomas
- Integração com processamento de PDFs

📖 **[Documentação completa do OCR](src/appserver_sdk_python_ai/ocr/README.md)**

## 📦 Instalação

### 🚀 Instalação da Biblioteca

A biblioteca está configurada para usar **wheels pré-compilados** automaticamente, evitando problemas de compilação em qualquer sistema operacional.

#### Instalação Básica
```bash
pip install appserver-sdk-python-ai
```
Inclui: `pydantic`, `httpx`, `structlog`, `typing-extensions`

### Instalação com Funcionalidades Específicas

#### Módulo LLM Básico
```bash
pip install appserver-sdk-python-ai[llm]
```
Adiciona: `psutil` para monitoramento de sistema

#### Modelos OpenAI
```bash
pip install appserver-sdk-python-ai[openai]
```
Adiciona: `tiktoken` para tokenização OpenAI

#### Modelos HuggingFace
```bash
pip install appserver-sdk-python-ai[huggingface]
```
Adiciona: `transformers`, `torch`

#### Modelos Locais
```bash
pip install appserver-sdk-python-ai[local-models]
```
Adiciona: `transformers`, `torch`, `llama-cpp-python`, `onnxruntime`

#### Análise Avançada
```bash
pip install appserver-sdk-python-ai[analysis]
```
Adiciona: `nltk`, `spacy`, `textblob`, `pandas`, `matplotlib`, `seaborn`

#### Instalação Completa
```bash
pip install appserver-sdk-python-ai[full]
```
Inclui as principais dependências para LLM e modelos

### Combinando Extras

Você pode combinar múltiplos extras:

```bash
# LLM + OpenAI + Análise
pip install appserver-sdk-python-ai[llm,openai,analysis]

# Instalação completa + desenvolvimento
pip install appserver-sdk-python-ai[full,dev]
```

### Via Poetry (Recomendado para Desenvolvimento)
```bash
# Instalação básica
poetry add appserver-sdk-python-ai

# Com extras
poetry add appserver-sdk-python-ai[full]
```

### Via GitHub (Desenvolvimento)
```bash
# Via Poetry
poetry add git+https://github.com/appserver/appserver-sdk-python-ai.git

# Via pip
pip install git+https://github.com/appserver/appserver-sdk-python-ai.git
```

### Resolução de Problemas

#### 🔧 Instalação Sem Problemas de Compilação

O projeto está configurado para usar **wheels pré-compilados** automaticamente, evitando problemas de compilação em qualquer sistema operacional.

**Instalação via pip:**
```bash
# Instalação básica
pip install appserver-sdk-python-ai[llm,openai,huggingface]

# Instalação completa
pip install appserver-sdk-python-ai[full]
```

**Se ainda encontrar problemas de compilação:**
```bash
# Forçar uso de wheels pré-compilados
pip install --only-binary=all appserver-sdk-python-ai[full]

# Ou usar Poetry com configuração específica
poetry config installer.prefer-binary true
poetry install --extras full
```

#### Erro de Importação
Se você receber erros de importação, verifique se instalou os extras necessários:

```python
# Verificar módulos disponíveis
from appserver_sdk_python_ai import health_check_all
health_check_all()
```

#### Dependências Conflitantes
Se houver conflitos de versão, use um ambiente virtual:

```bash
# Criar ambiente virtual
python -m venv venv

# Ativar (Windows)
venv\Scripts\activate

# Ativar (Linux/Mac)
source venv/bin/activate

# Instalar SDK
pip install appserver-sdk-python-ai[full]
```

#### Verificar Instalação
```python
# Teste básico
from appserver_sdk_python_ai.llm import get_token_count
print(get_token_count("Hello world"))

# Teste completo
# python examples/llm/complete_features_demo.py
```

## 🔧 Uso Básico

### Verificação da Instalação

```python
from appserver_sdk_python_ai import get_sdk_info, print_sdk_status

# Informações do SDK
info = get_sdk_info()
print(info)

# Status dos módulos
print_sdk_status()
```

### Tratamento de Dependências Opcionais

O SDK foi projetado para funcionar mesmo sem dependências opcionais:

```python
from appserver_sdk_python_ai import llm

if llm is not None:
    # Módulo LLM disponível
    from appserver_sdk_python_ai.llm import get_token_count
    tokens = get_token_count("Texto de exemplo")
else:
    print("Módulo LLM não disponível")
    print("Instale com: pip install appserver-sdk-python-ai[llm]")
```

### Módulo WebScraping

```python
from appserver_sdk_python_ai.webscraping import quick_scrape

# Scraping simples
markdown = quick_scrape("https://example.com")
print(markdown)
```

### Módulo OCR

```python
from appserver_sdk_python_ai.ocr import quick_ocr

# OCR simples de uma imagem
texto = quick_ocr("documento.png")
print(texto)

# OCR com configurações específicas
from appserver_sdk_python_ai.ocr import OCRProcessor, OCRConfig

config = OCRConfig(
    languages=["por", "eng"],
    engine="tesseract"
)

processor = OCRProcessor(config)
resultado = processor.process_image("imagem.jpg")
print(resultado.text)
print(f"Confiança: {resultado.confidence}%")
```

### Módulo LLM - Uso Básico

```python
try:
    from appserver_sdk_python_ai.llm import (
        get_token_count,
        list_available_models,
        get_portuguese_models
    )
    
    # Contar tokens
    tokens = get_token_count("Olá, mundo!")
    print(f"Tokens: {tokens}")
    
    # Listar modelos
    models = list_available_models()
    print(f"Modelos disponíveis: {len(models)}")
    
except ImportError as e:
    print(f"Módulo LLM não disponível: {e}")
    print("Instale com: pip install appserver-sdk-python-ai[llm]")
```

### Módulo LLM - Cliente Síncrono

```python
from appserver_sdk_python_ai.llm import AIService

# Configurar cliente
ai_service = AIService(
    api_key="sua-api-key",
    base_url="https://api.appserver.com.br/ai/v1"
)

# Fazer requisição
response = ai_service.chat(
    prompt="Explique machine learning em termos simples",
    model="gpt-4",
    max_tokens=500
)

print(response.content)
print(f"Tokens utilizados: {response.usage.total_tokens}")
```

### Módulo LLM - Cliente Assíncrono

```python
import asyncio
from appserver_sdk_python_ai.llm import AsyncAIService

async def main():
    ai_service = AsyncAIService(
        api_key="sua-api-key",
        base_url="https://api.appserver.com.br/ai/v1"
    )
    
    response = await ai_service.chat(
        prompt="O que é inteligência artificial?",
        model="gpt-3.5-turbo",
        max_tokens=500
    )
    
    print(response.content)
    await ai_service.close()

asyncio.run(main())
```

### Módulo LLM - Configuração Avançada

```python
from appserver_sdk_python_ai.llm import AIService, AIConfig

config = AIConfig(
    base_url="https://api.appserver.com.br/ai/v1",
    api_key="sua-api-key",
    timeout=30,
    max_retries=3,
    retry_delay=1.0,
    debug=True
)

ai_service = AIService(config=config)
```

## 🛠️ Desenvolvimento

### Pré-requisitos

- Python 3.11+
- Poetry

### Configuração do Ambiente

```bash
# Clonar repositório
git clone https://github.com/appserver/appserver-sdk-python-ai.git
cd appserver-sdk-python-ai

# Instalar dependências
poetry install

# Configurar pre-commit hooks
poetry run pre-commit install

# Ativar ambiente virtual
poetry shell
```

### Executar Testes

```bash
# Todos os testes
poetry run pytest

# Com cobertura
poetry run pytest --cov=appserver_sdk_python_ai --cov-report=html

# Apenas testes unitários
poetry run pytest -m unit

# Apenas testes de integração
poetry run pytest -m integration
```

### Linting e Formatação

```bash
# Verificar e corrigir código
poetry run ruff check . --fix
poetry run ruff format .

# Verificar tipos
poetry run mypy src/

# Verificar segurança
poetry run bandit -r src/
poetry run safety check
```

### Executar Exemplo

```bash
# Exemplos básicos
poetry run python examples/basic_usage.py
poetry run python examples/async_usage.py

# Exemplos do módulo LLM
poetry run python examples/llm/custom_model_example.py
poetry run python examples/llm/metrics_example.py

# Demonstrações completas do módulo LLM
poetry run python examples/llm/features_demo.py
poetry run python examples/llm/improvements_demo.py
poetry run python examples/llm/medium_priority_demo.py
```

## 📚 Documentação

### 📖 Documentação Principal

- **[🏗️ Arquitetura](ARCHITECTURE.md)** - Visão geral da arquitetura e padrões de design
- **[🤝 Contribuição](CONTRIBUTING.md)** - Guia completo para contribuidores
- **[📋 Changelog](CHANGELOG.md)** - Histórico de mudanças e versões
- **[📄 Licença](LICENSE)** - Termos de uso e licenciamento

### 📦 Documentação dos Módulos

- **[🤖 LLM](src/appserver_sdk_python_ai/llm/README.md)** - Guia completo do módulo de modelos de linguagem
- **[🔍 WebScraping](src/appserver_sdk_python_ai/webscraping/README.md)** - Guia completo do módulo de web scraping
- **[👁️ OCR](src/appserver_sdk_python_ai/ocr/README.md)** - Guia completo do módulo de reconhecimento óptico de caracteres
- **[🔧 Shared](src/appserver_sdk_python_ai/shared/README.md)** - Utilitários e funcionalidades compartilhadas

### Estrutura do Projeto

```
appserver-sdk-python-ai/
├── src/
│   └── appserver_sdk_python_ai/
│       ├── __init__.py
│       ├── py.typed                # Marcador de tipos Python
│       ├── llm/                    # Módulo LLM
│       │   ├── __init__.py
│       │   ├── README.md           # Documentação do LLM
│       │   ├── core/               # Funcionalidades principais
│       │   ├── service/            # Serviços e clientes
│       │   ├── exceptions/         # Exceções específicas
│       │   ├── docs/               # Documentação interativa
│       │   └── utils/              # Utilitários do módulo
│       ├── webscraping/            # Módulo WebScraping
│       │   ├── __init__.py
│       │   ├── README.md           # Documentação do WebScraping
│       │   ├── core/               # Funcionalidades principais
│       │   ├── docling/            # Integração com Docling
│       │   ├── utils/              # Utilitários do módulo
│       │   └── exceptions/         # Exceções específicas
│       ├── ocr/                    # Módulo OCR
│       │   ├── __init__.py
│       │   ├── README.md           # Documentação do OCR
│       │   ├── core/               # Funcionalidades principais
│       │   └── exceptions/         # Exceções específicas
│       └── shared/                 # Utilitários compartilhados
│           ├── __init__.py
│           ├── README.md           # Documentação dos utilitários
│           ├── exceptions.py       # Exceções base
│           ├── core/               # Funcionalidades compartilhadas
│           ├── utils/              # Utilitários comuns
│           └── examples/           # Exemplos de uso
├── tests/                          # Testes automatizados
│   ├── test_llm/                   # Testes do módulo LLM
│   ├── test_webscraping/           # Testes do módulo WebScraping
│   ├── test_ocr/                   # Testes do módulo OCR
│   ├── test_shared/                # Testes dos utilitários
│   └── integration/                # Testes de integração
├── examples/                       # Exemplos de uso e demonstrações
│   ├── llm/                        # Exemplos do módulo LLM
│   └── output/                     # Saídas dos exemplos
├── scripts/                        # Scripts de desenvolvimento
├── .github/                        # Configurações do GitHub
└── pyproject.toml                  # Configuração do Poetry
```

### Modelos e Configurações Disponíveis

- `AIConfig`: Configuração do cliente LLM
- `ChatResponse`: Modelo de resposta do chat
- `Message`: Modelo de mensagem para conversas
- `LLMConfig`: Configuração específica do módulo LLM

### Exceções

- `LLMError`: Exceção base do módulo LLM
- `LLMProviderError`: Erro específico do provedor
- `LLMAuthenticationError`: Erro de autenticação
- `LLMRateLimitError`: Erro de limite de taxa
- `LLMTimeoutError`: Erro de timeout

## 🤖 Módulo LLM

O módulo LLM oferece funcionalidades avançadas para interação com modelos de linguagem:

### 🚀 Funcionalidades Principais

- **Cliente LLM**: Interface unificada para diferentes provedores
- **Cache Inteligente**: Sistema de cache LRU thread-safe para otimização
- **Validação Robusta**: Validação de entrada e saída com múltiplos níveis
- **Logging Estruturado**: Sistema de logging avançado com contexto
- **Métricas e Monitoramento**: Coleta automática de métricas de performance
- **Configuração Centralizada**: Gerenciamento unificado de configurações

### 📊 Sistema de Métricas

O módulo inclui um sistema abrangente de métricas:

```python
from appserver_sdk_python_ai.llm import (
    get_metrics_summary,
    export_metrics,
    record_operation_metric
)

# Coleta automática durante operações
summary = get_metrics_summary()
print(f"Operações realizadas: {len(summary['operation_stats'])}")

# Exportação para análise
export_metrics(format_type="json", file_path="metrics.json")
export_metrics(format_type="prometheus", file_path="metrics.prom")
```

**Tipos de Métricas Coletadas:**
- ⏱️ Latência e duração de operações
- 📈 Contadores de sucesso/erro
- 💾 Uso de memória e CPU
- 🔢 Estatísticas de tokens processados
- 📊 Histogramas de performance

### 📖 Documentação Completa

Para documentação detalhada do módulo LLM, consulte:
- **[📚 README do Módulo LLM](src/appserver_sdk_python_ai/llm/README.md)** - Documentação completa e consolidada
- **[🔧 Documentação Interativa](src/appserver_sdk_python_ai/llm/docs/interactive_docs.py)** - Acesso dinâmico à documentação
- **[💡 Exemplos Práticos](examples/llm/)** - Exemplos de uso organizados por funcionalidade
- **[📊 Métricas e Outputs](examples/output/)** - Arquivos de métricas e relatórios
- **[📝 Logs do Sistema](examples/output/)** - Logs estruturados da aplicação

> **Nota**: A documentação do módulo LLM foi consolidada em um único local para evitar redundância. O sistema de documentação interativa carrega dinamicamente o conteúdo do README.md do módulo.

## 🤝 Contribuindo

Contribuições são muito bem-vindas! Este projeto segue padrões rigorosos de qualidade e documentação.

### 🚀 Início Rápido para Contribuidores

1. **Fork** o projeto no GitHub
2. **Clone** seu fork localmente
3. **Configure** o ambiente de desenvolvimento
4. **Crie** uma branch para sua feature
5. **Desenvolva** seguindo nossos padrões
6. **Teste** suas mudanças
7. **Submeta** um Pull Request

### 📚 Documentação Completa

Para informações detalhadas sobre como contribuir, consulte nosso **[Guia de Contribuição](CONTRIBUTING.md)**, que inclui:

- 🛠️ Configuração do ambiente de desenvolvimento
- 📏 Padrões de código e convenções
- 🧪 Como escrever e executar testes
- 📝 Convenções de commit e documentação
- 🔄 Processo completo de Pull Request
- 🐛 Como reportar bugs e sugerir funcionalidades

### ⚡ Contribuições Rápidas

- **🐛 Bug Reports**: [Abrir Issue](https://github.com/appserver/appserver-sdk-python-ai/issues/new?template=bug_report.md)
- **💡 Feature Requests**: [Sugerir Funcionalidade](https://github.com/appserver/appserver-sdk-python-ai/issues/new?template=feature_request.md)
- **📝 Documentação**: Melhorias sempre bem-vindas
- **🧪 Testes**: Aumente nossa cobertura de testes

### Convenções de Documentação

#### Nomenclatura de Arquivos
- **Preferência**: Documentação no `README.md` do próprio módulo
- **Formato alternativo**: `{modulo}-{tipo}.md` (apenas quando necessário)

#### Estrutura dos Documentos
1. **Título e Descrição**
2. **Índice** (se necessário)
3. **Conteúdo Principal**
4. **Exemplos Práticos**
5. **Referências e Links**

#### Adicionando Nova Documentação
1. **Criar Arquivo**: Use a convenção `{modulo}-{tipo}.md`
2. **Seguir Estrutura**: Mantenha consistência com documentos existentes
3. **Atualizar README**: Adicione referência neste arquivo
4. **Links Cruzados**: Atualize links relevantes em outros documentos

#### Manutenção da Documentação
- **Revisão Regular**: Mensal ou a cada release
- **Verificações**: Links funcionais, informações atualizadas, exemplos válidos
- **Sincronização**: Manter sincronizado com mudanças no código
- **Versionamento**: Indicar mudanças significativas

## 📄 Licença

Este projeto está licenciado sob a **Licença MIT** - veja o arquivo **[LICENSE](LICENSE)** para detalhes completos.

### 🔓 Resumo da Licença

- ✅ **Uso comercial** permitido
- ✅ **Modificação** permitida
- ✅ **Distribuição** permitida
- ✅ **Uso privado** permitido
- ❌ **Sem garantias** ou responsabilidades

## 📞 Suporte e Comunidade

### 🆘 Canais de Suporte

- **🐛 Issues**: [GitHub Issues](https://github.com/appserver/appserver-sdk-python-ai/issues) - Para bugs e problemas
- **💬 Discussões**: [GitHub Discussions](https://github.com/appserver/appserver-sdk-python-ai/discussions) - Para perguntas e ideias
- **📧 Email**: suporte@appserver.com - Para suporte direto
- **📚 Documentação**: Consulte os READMEs específicos de cada módulo

### 🤝 Comunidade

- **🌟 Star** o projeto se ele foi útil
- **🍴 Fork** para contribuir
- **👀 Watch** para acompanhar atualizações
- **📢 Share** com outros desenvolvedores

## 🚀 Status e Roadmap

### 📊 Status Atual

- ✅ **Estável**: Módulo LLM (v0.0.20)
- 🚧 **Em Desenvolvimento**: Módulos WebScraping e OCR
- 📋 **Planejado**: Módulos de análise de dados e automação
- 🔄 **Contínuo**: Melhorias de performance e documentação

### 🗺️ Roadmap

- **Q1 2024**: Estabilização completa dos módulos WebScraping e OCR
- **Q2 2024**: Módulo de análise de dados
- **Q3 2024**: Módulo de automação e workflows
- **Q4 2024**: Integração com mais provedores de IA

---

<div align="center">

**Desenvolvido com ❤️ pela equipe AppServer**

[🌐 Website](https://appserver.com) • [📧 Contato](mailto:suporte@appserver.com) • [📱 LinkedIn](https://linkedin.com/company/appserver)

</div>
