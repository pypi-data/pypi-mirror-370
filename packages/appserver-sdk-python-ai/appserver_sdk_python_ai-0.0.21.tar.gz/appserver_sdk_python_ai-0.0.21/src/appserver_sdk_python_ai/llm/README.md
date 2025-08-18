# Módulo LLM - AppServer SDK Python AI

Um módulo profissional para integração com modelos de linguagem (LLM) e APIs de inteligência artificial.

## 🚀 Características

- **🔄 Cliente Assíncrono e Síncrono**: Suporte completo para operações síncronas e assíncronas
- **🛡️ Retry Automático**: Sistema robusto de retry com backoff exponencial
- **📊 Modelos Pydantic**: Validação de dados com type hints completos
- **🔌 Múltiplos Provedores**: Suporte para diferentes APIs de IA (OpenAI, Anthropic, etc.)
- **📝 Logging Estruturado**: Sistema de logs detalhado para debugging e monitoramento
- **⚡ Performance Otimizada**: Conexões reutilizáveis e pool de conexões
- **🔐 Segurança**: Gerenciamento seguro de API keys e autenticação
- **🎯 Interface Simples**: API intuitiva para uso básico e avançado

## 📁 Estrutura do Módulo

```
llm/
├── __init__.py                 # Inicialização e exports principais
├── README.md                   # Esta documentação
├── core/
│   ├── __init__.py
│   ├── model_manager.py       # Gerenciamento de modelos
│   └── token_counter.py       # Contagem de tokens
├── service/
│   ├── __init__.py
│   ├── ai_service.py          # Serviço principal de IA
│   └── providers/             # Provedores específicos
└── exceptions/
    └── llm_exceptions.py      # Exceções customizadas
```

## 📦 Instalação e Dependências

### Dependências Principais
- **Python**: >= 3.8
- **pydantic**: >= 2.0.0 - Validação de dados e modelos
- **httpx**: >= 0.24.0 - Cliente HTTP assíncrono
- **typing-extensions**: >= 4.0.0 - Extensões de tipagem
- **structlog**: >= 23.0.0 - Logging estruturado
- **psutil**: >= 5.9.0 - Métricas do sistema

### Instalação Básica
```bash
# Apenas funcionalidades core
pip install appserver-sdk-python-ai[llm]
```

### Instalação com Extras
```bash
# Com suporte a modelos locais
pip install appserver-sdk-python-ai[llm,local-models]

# Com ferramentas de análise
pip install appserver-sdk-python-ai[llm,analysis]

# Instalação completa para desenvolvimento
pip install appserver-sdk-python-ai[llm,dev,all]
```

### Dependências Opcionais

#### Para Modelos Locais
```bash
# Para modelos HuggingFace
pip install transformers>=4.20.0 torch>=1.12.0

# Para modelos Llama
pip install llama-cpp-python>=0.2.0

# Para modelos ONNX
pip install onnxruntime>=1.12.0
```

#### Para Análise Avançada
```bash
# Para análise de texto
pip install nltk>=3.8 spacy>=3.4.0

# Para processamento de linguagem natural
pip install textblob>=0.17.0
```

### Verificação de Dependências
```python
from appserver_sdk_python_ai.llm.utils.dependency_checker import check_dependencies

# Verificar dependências principais
result = check_dependencies()
if result['missing']:
    print(f"Dependências faltando: {result['missing']}")
else:
    print("✅ Todas as dependências principais estão instaladas")
```

## 🔥 Uso Rápido

### Cliente Básico
```python
from appserver_sdk_python_ai.llm import AIService

# Configurar cliente
ai_service = AIService(
    api_key="sua-api-key",
    base_url="https://api.appserver.com.br/ai/v1"
)

# Fazer requisição simples
response = ai_service.chat(
    prompt="Explique machine learning em termos simples",
    model="gpt-4",
    max_tokens=500
)

print(response.content)
print(f"Tokens utilizados: {response.usage.total_tokens}")
```

### Chat com Contexto
```python
from appserver_sdk_python_ai.llm import AIService, Message

ai_service = AIService(api_key="sua-api-key")

# Conversa com contexto
messages = [
    Message(role="system", content="Você é um assistente especializado em Python."),
    Message(role="user", content="Como criar uma função recursiva?"),
    Message(role="assistant", content="Uma função recursiva é uma função que chama a si mesma..."),
    Message(role="user", content="Pode dar um exemplo prático?")
]

response = ai_service.chat_with_messages(
    messages=messages,
    model="gpt-4",
    temperature=0.7
)

print(response.content)
```

### Cliente Assíncrono
```python
import asyncio
from appserver_sdk_python_ai.llm import AsyncAIService

async def main():
    ai_service = AsyncAIService(api_key="sua-api-key")
    
    response = await ai_service.chat(
        prompt="O que é inteligência artificial?",
        model="gpt-3.5-turbo"
    )
    
    print(response.content)
    await ai_service.close()

asyncio.run(main())
```

## ⚙️ Configuração Avançada

### AIConfig - Todas as Opções
```python
from appserver_sdk_python_ai.llm import AIService, AIConfig

config = AIConfig(
    # Configurações de rede
    base_url="https://api.appserver.com.br/ai/v1",
    api_key="sua-api-key",
    timeout=30,                    # Timeout em segundos
    verify_ssl=True,               # Verificar certificados SSL
    
    # Configurações de retry
    max_retries=3,                 # Máximo de tentativas
    retry_delay=1.0,               # Delay inicial entre tentativas
    backoff_factor=2.0,            # Fator de backoff exponencial
    
    # Configurações de logging
    debug=False,                   # Modo debug
    log_requests=True,             # Log de requisições
    log_responses=False,           # Log de respostas (cuidado com dados sensíveis)
    
    # Headers customizados
    headers={
        "User-Agent": "AppServer-SDK/1.0",
        "Accept": "application/json"
    }
)

ai_service = AIService(config=config)
```

### Modelos de Dados

#### ChatRequest
```python
from appserver_sdk_python_ai.llm import ChatRequest

request = ChatRequest(
    prompt="Sua pergunta aqui",
    model="gpt-4",                 # Modelo a ser usado
    max_tokens=1000,               # Máximo de tokens na resposta
    temperature=0.7,               # Criatividade (0.0 a 1.0)
    top_p=1.0,                     # Nucleus sampling
    frequency_penalty=0.0,         # Penalidade de frequência
    presence_penalty=0.0,          # Penalidade de presença
    stop=["\n\n"],                # Tokens de parada
    stream=False                   # Streaming de resposta
)
```

#### ChatResponse
```python
# A resposta contém:
response.content          # Conteúdo da resposta
response.model           # Modelo usado
response.usage           # Informações de uso (tokens)
response.finish_reason   # Razão do fim da geração
response.created_at      # Timestamp da criação
response.id              # ID único da resposta
```

## 🎯 Casos de Uso Práticos

### 1. Análise de Sentimento
```python
from appserver_sdk_python_ai.llm import AIService

def analisar_sentimento(texto):
    ai_service = AIService(api_key="sua-api-key")
    
    prompt = f"""
    Analise o sentimento do seguinte texto e retorne apenas uma das opções:
    - POSITIVO
    - NEGATIVO
    - NEUTRO
    
    Texto: "{texto}"
    
    Sentimento:
    """
    
    response = ai_service.chat(
        prompt=prompt,
        model="gpt-3.5-turbo",
        max_tokens=10,
        temperature=0.1
    )
    
    return response.content.strip()

# Exemplo de uso
textos = [
    "Adorei o produto, superou minhas expectativas!",
    "O serviço foi terrível, não recomendo.",
    "O produto chegou no prazo esperado."
]

for texto in textos:
    sentimento = analisar_sentimento(texto)
    print(f"'{texto}' -> {sentimento}")
```

### 2. Geração de Resumos
```python
from appserver_sdk_python_ai.llm import AIService

def gerar_resumo(texto, max_palavras=100):
    ai_service = AIService(api_key="sua-api-key")
    
    prompt = f"""
    Crie um resumo conciso do seguinte texto em no máximo {max_palavras} palavras.
    Mantenha os pontos principais e informações essenciais.
    
    Texto:
    {texto}
    
    Resumo:
    """
    
    response = ai_service.chat(
        prompt=prompt,
        model="gpt-4",
        max_tokens=max_palavras * 2,  # Margem de segurança
        temperature=0.3
    )
    
    return response.content.strip()

# Exemplo de uso
texto_longo = """
A inteligência artificial (IA) é uma área da ciência da computação que se concentra 
no desenvolvimento de sistemas capazes de realizar tarefas que normalmente requerem 
inteligência humana. Isso inclui aprendizado, raciocínio, percepção, compreensão 
de linguagem natural e resolução de problemas. A IA tem aplicações em diversos 
setores, desde saúde e educação até transporte e entretenimento.
"""

resumo = gerar_resumo(texto_longo, max_palavras=50)
print(f"Resumo: {resumo}")
```

### 3. Chatbot com Memória
```python
from appserver_sdk_python_ai.llm import AIService, Message

class ChatBot:
    def __init__(self, api_key, system_prompt="Você é um assistente útil."):
        self.ai_service = AIService(api_key=api_key)
        self.messages = [Message(role="system", content=system_prompt)]
    
    def chat(self, user_input):
        # Adicionar mensagem do usuário
        self.messages.append(Message(role="user", content=user_input))
        
        # Obter resposta
        response = self.ai_service.chat_with_messages(
            messages=self.messages,
            model="gpt-3.5-turbo",
            max_tokens=500,
            temperature=0.7
        )
        
        # Adicionar resposta do assistente ao histórico
        self.messages.append(Message(role="assistant", content=response.content))
        
        return response.content
    
    def reset(self):
        # Manter apenas a mensagem do sistema
        self.messages = self.messages[:1]

# Exemplo de uso
bot = ChatBot(
    api_key="sua-api-key",
    system_prompt="Você é um especialista em Python. Responda de forma didática."
)

print("ChatBot iniciado! Digite 'sair' para encerrar.")
while True:
    user_input = input("Você: ")
    if user_input.lower() == 'sair':
        break
    
    response = bot.chat(user_input)
    print(f"Bot: {response}")
```

### 4. Processamento em Lote Assíncrono
```python
import asyncio
from appserver_sdk_python_ai.llm import AsyncAIService

async def processar_textos_em_lote(textos, prompt_template):
    ai_service = AsyncAIService(api_key="sua-api-key")
    
    async def processar_texto(texto):
        prompt = prompt_template.format(texto=texto)
        response = await ai_service.chat(
            prompt=prompt,
            model="gpt-3.5-turbo",
            max_tokens=200
        )
        return {"texto_original": texto, "resultado": response.content}
    
    # Processar todos os textos em paralelo
    tasks = [processar_texto(texto) for texto in textos]
    resultados = await asyncio.gather(*tasks)
    
    await ai_service.close()
    return resultados

# Exemplo de uso
async def main():
    textos = [
        "Python é uma linguagem de programação.",
        "Machine learning é um subcampo da IA.",
        "APIs facilitam a integração entre sistemas."
    ]
    
    prompt_template = """
    Traduza o seguinte texto para inglês:
    
    Texto: {texto}
    
    Tradução:
    """
    
    resultados = await processar_textos_em_lote(textos, prompt_template)
    
    for resultado in resultados:
        print(f"Original: {resultado['texto_original']}")
        print(f"Tradução: {resultado['resultado']}")
        print("-" * 50)

# asyncio.run(main())
```

### 5. Extração de Informações Estruturadas
```python
from appserver_sdk_python_ai.llm import AIService
import json

def extrair_informacoes_contato(texto):
    ai_service = AIService(api_key="sua-api-key")
    
    prompt = f"""
    Extraia as informações de contato do seguinte texto e retorne em formato JSON.
    Se alguma informação não estiver disponível, use null.
    
    Formato esperado:
    {{
        "nome": "string",
        "email": "string",
        "telefone": "string",
        "empresa": "string",
        "cargo": "string"
    }}
    
    Texto:
    {texto}
    
    JSON:
    """
    
    response = ai_service.chat(
        prompt=prompt,
        model="gpt-4",
        max_tokens=300,
        temperature=0.1
    )
    
    try:
        return json.loads(response.content)
    except json.JSONDecodeError:
        return None

# Exemplo de uso
texto_contato = """
Olá, meu nome é João Silva e trabalho como Desenvolvedor Senior na TechCorp.
Você pode me contatar pelo email joao.silva@techcorp.com ou pelo telefone (11) 99999-9999.
Estou interessado em discutir oportunidades de parceria.
"""

info = extrair_informacoes_contato(texto_contato)
if info:
    print(json.dumps(info, indent=2, ensure_ascii=False))
else:
    print("Não foi possível extrair as informações.")
```

## 🔄 Streaming de Respostas

```python
from appserver_sdk_python_ai.llm import AsyncAIService

async def chat_com_streaming():
    ai_service = AsyncAIService(api_key="sua-api-key")
    
    prompt = "Conte uma história interessante sobre inteligência artificial"
    
    print("Resposta: ", end="", flush=True)
    
    async for chunk in ai_service.chat_stream(
        prompt=prompt,
        model="gpt-4",
        max_tokens=500
    ):
        print(chunk.content, end="", flush=True)
    
    print()  # Nova linha no final
    await ai_service.close()

# asyncio.run(chat_com_streaming())
```

## 📊 Métricas e Monitoramento

O módulo LLM inclui um sistema abrangente de métricas para monitoramento de performance e uso:

### Coleta Automática de Métricas

```python
from appserver_sdk_python_ai.llm import (
    get_metrics_summary,
    get_metrics_collector,
    export_metrics
)
from appserver_sdk_python_ai.llm.service.client import MockLLMClient

# As métricas são coletadas automaticamente durante operações
client = MockLLMClient()
client.authenticate()

# Operações são automaticamente monitoradas
models = client.list_models()
response = client.generate_text("Hello world", models[0])

# Visualizar resumo das métricas
summary = get_metrics_summary()
print(f"Total de operações: {summary['operation_stats']}")
print(f"Métricas do sistema: {summary['system']}")
```

### Métricas Customizadas

```python
from appserver_sdk_python_ai.llm import (
    record_operation_metric,
    increment_counter,
    set_gauge,
    OperationStatus
)
import time

# Registrar operação customizada
start_time = time.time()
# ... sua operação aqui ...
duration_ms = (time.time() - start_time) * 1000

record_operation_metric(
    operation_type="custom_processing",
    duration_ms=duration_ms,
    status=OperationStatus.SUCCESS,
    model_name="custom-model",
    token_count=1500
)

# Incrementar contadores
increment_counter("api_requests", 1, {"endpoint": "/chat"})

# Definir gauges
set_gauge("active_connections", 25.0)
```

### Exportação de Métricas

```python
# Exportar para diferentes formatos
export_metrics(format_type="json", file_path="metrics.json")
export_metrics(format_type="csv", file_path="metrics.csv")
export_metrics(format_type="prometheus", file_path="metrics.prom")

# Obter métricas em tempo real
collector = get_metrics_collector()
stats = collector.get_histogram_stats("operation_duration_ms")
print(f"Latência P95: {stats['p95']:.2f}ms")
```

### Monitoramento de Performance

```python
# Visualizar estatísticas de performance
summary = get_metrics_summary(include_system=True)

for op_type, stats in summary['operation_stats'].items():
    success_rate = (stats['success_count'] / stats['count']) * 100
    print(f"{op_type}:")
    print(f"  Taxa de sucesso: {success_rate:.1f}%")
    print(f"  Duração média: {stats['avg_duration_ms']:.2f}ms")

# Métricas do sistema
sys_metrics = summary['system']
print(f"Uso de memória: {sys_metrics['memory']['percent']:.1f}%")
print(f"Uso de CPU: {sys_metrics['cpu']['percent']:.1f}%")
```

## 🚨 Tratamento de Erros

```python
from appserver_sdk_python_ai.llm import (
    AIService,
    AIException,
    AIConnectionError,
    AIAuthenticationError,
    AIRateLimitError,
    AITimeoutError,
    AIModelNotFoundError
)

def chat_com_tratamento_erro(prompt):
    ai_service = AIService(api_key="sua-api-key")
    
    try:
        response = ai_service.chat(
            prompt=prompt,
            model="gpt-4",
            max_tokens=500
        )
        return response.content
        
    except AIAuthenticationError:
        return "Erro: API key inválida ou expirada"
    except AIRateLimitError as e:
        return f"Erro: Limite de taxa excedido. Tente novamente em {e.retry_after} segundos"
    except AIModelNotFoundError:
        return "Erro: Modelo especificado não encontrado"
    except AITimeoutError:
        return "Erro: Timeout na requisição"
    except AIConnectionError:
        return "Erro: Problema de conexão com a API"
    except AIException as e:
        return f"Erro geral da API: {e}"
    except Exception as e:
        return f"Erro inesperado: {e}"

# Exemplo de uso
resultado = chat_com_tratamento_erro("Explique quantum computing")
print(resultado)
```

## 📊 Monitoramento e Métricas

### Contagem de Tokens
```python
from appserver_sdk_python_ai.llm import TokenCounter

# Contar tokens antes de enviar
counter = TokenCounter()

prompt = "Explique machine learning em detalhes"
tokens_prompt = counter.count_tokens(prompt, model="gpt-4")
print(f"Tokens no prompt: {tokens_prompt}")

# Estimar custo
custo_estimado = counter.estimate_cost(
    prompt_tokens=tokens_prompt,
    completion_tokens=500,  # Estimativa
    model="gpt-4"
)
print(f"Custo estimado: ${custo_estimado:.4f}")
```

### Logging Personalizado
```python
import logging
from appserver_sdk_python_ai.llm import AIService

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger("meu_app")

ai_service = AIService(
    api_key="sua-api-key",
    debug=True  # Habilita logs detalhados
)

# Os logs serão automaticamente gerados
response = ai_service.chat(
    prompt="Teste de logging",
    model="gpt-3.5-turbo"
)
```

## 🚀 Melhorias e Funcionalidades Avançadas

O módulo LLM foi aprimorado com diversas funcionalidades avançadas para melhor performance, robustez e usabilidade:

### ✅ Sistema de Cache Inteligente
- **Cache LRU thread-safe** com TTL configurável
- **Decorador @cache_result** para fácil aplicação
- **Estatísticas de performance** (hits/misses)
- **Monitoramento de uso de memória**
- **Limpeza automática** de entradas expiradas

```python
from appserver_sdk_python_ai.llm import get_cache_stats, clear_cache

# Verificar estatísticas do cache
stats = get_cache_stats()
print(f"Taxa de acerto: {stats['hit_rate']:.2%}")

# Limpar cache se necessário
clear_cache()
```

### ✅ Validação Robusta
- **Múltiplos níveis de validação** (LENIENT, MODERATE, STRICT)
- **Validadores específicos** para modelos, tokens, configurações e texto
- **Mensagens de erro descritivas** e categorizadas
- **Separação entre warnings e errors**

```python
from appserver_sdk_python_ai.llm import validate_model_name, ValidationLevel

result = validate_model_name("gpt-4", ValidationLevel.MODERATE)
if result.is_valid:
    print("Modelo válido!")
else:
    print(f"Erro: {result.error_message}")
```

### ✅ Logging Estruturado
- **Logs em formato JSON** para análise automatizada
- **Contexto de operação** com metadata
- **Métricas de performance** automáticas
- **Rotação automática** de arquivos de log
- **Decorador @log_function_call** para logging automático

```python
from appserver_sdk_python_ai.llm import get_logger, OperationType

logger = get_logger()
logger.info("Operação executada", operation_type=OperationType.TOKEN_COUNT)
```

### ✅ Sistema de Métricas Completo
- **Coleta automática** de métricas de performance
- **Tipos de métricas**: contadores, gauges, histogramas, timers
- **Exportação** para JSON, CSV e Prometheus
- **Monitoramento** de sistema (CPU, memória, disco)
- **Métricas de operação** com contexto detalhado

### ✅ Documentação Interativa
- **Sistema de ajuda integrado** (`help_llm()`, `docs_llm()`)
- **Busca na documentação** (`search_llm_docs()`)
- **Exemplos práticos** e guias de solução de problemas
- **Referência da API** em tempo de desenvolvimento

### ✅ Utilitários Avançados
- **Listagem de modelos** organizados por provedor
- **Registro de modelos customizados** com validação
- **Modelos otimizados** para português e multilíngues
- **Análise de compatibilidade** de dependências

### 🎯 Arquitetura Melhorada
- **Separação clara de responsabilidades** entre módulos
- **Extensibilidade** para novos provedores e modelos
- **Testabilidade** com estrutura modular
- **Performance otimizada** com cache integrado
- **Robustez** com validação e logging estruturado

### 📊 Exemplo de Uso Integrado

```python
from appserver_sdk_python_ai.llm import (
    get_metrics_summary,
    help_llm,
    docs_llm,
    list_available_models
)
from appserver_sdk_python_ai.llm.service.client import MockLLMClient

# Documentação interativa
help_llm()  # Ajuda rápida
docs_llm()  # Documentação completa

# Listar modelos disponíveis
models = list_available_models()
print(f"Modelos disponíveis: {len(models)}")

# Cliente com métricas automáticas
client = MockLLMClient()
client.authenticate()

# Operações monitoradas automaticamente
response = client.generate_text("Hello world", "gpt-4")

# Visualizar métricas coletadas
summary = get_metrics_summary(include_system=True)
print(f"Operações realizadas: {len(summary['operation_stats'])}")
print(f"Uso de memória: {summary['system']['memory']['percent']:.1f}%")
```

## 🔐 Segurança e Boas Práticas

### Gerenciamento Seguro de API Keys
```python
import os
from appserver_sdk_python_ai.llm import AIService

# Usar variáveis de ambiente
ai_service = AIService(
    api_key=os.getenv("APPSERVER_API_KEY"),
    base_url=os.getenv("APPSERVER_BASE_URL", "https://api.appserver.com.br/ai/v1")
)

# Verificar se a API key está configurada
if not os.getenv("APPSERVER_API_KEY"):
    raise ValueError("API key não configurada. Defina a variável APPSERVER_API_KEY")
```

### Validação de Entrada
```python
from appserver_sdk_python_ai.llm import AIService
import re

def validar_prompt(prompt):
    """Valida e sanitiza o prompt antes de enviar"""
    if not prompt or not prompt.strip():
        raise ValueError("Prompt não pode estar vazio")
    
    if len(prompt) > 10000:  # Limite de caracteres
        raise ValueError("Prompt muito longo")
    
    # Remover caracteres potencialmente problemáticos
    prompt_limpo = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', prompt)
    
    return prompt_limpo.strip()

def chat_seguro(prompt):
    try:
        prompt_validado = validar_prompt(prompt)
        ai_service = AIService(api_key=os.getenv("APPSERVER_API_KEY"))
        
        response = ai_service.chat(
            prompt=prompt_validado,
            model="gpt-3.5-turbo",
            max_tokens=500
        )
        
        return response.content
        
    except ValueError as e:
        return f"Erro de validação: {e}"
    except Exception as e:
        return f"Erro: {e}"
```

## 🚀 Performance e Otimização

### Pool de Conexões
```python
from appserver_sdk_python_ai.llm import AsyncAIService

# Cliente com pool de conexões otimizado
ai_service = AsyncAIService(
    api_key="sua-api-key",
    max_connections=100,
    max_keepalive_connections=20,
    timeout=30
)
```

### Cache de Respostas
```python
from appserver_sdk_python_ai.llm import AIService
import hashlib
import json
from functools import lru_cache

class CachedAIService:
    def __init__(self, api_key):
        self.ai_service = AIService(api_key=api_key)
        self._cache = {}
    
    def _get_cache_key(self, prompt, model, **kwargs):
        """Gera chave única para o cache"""
        cache_data = {
            "prompt": prompt,
            "model": model,
            **kwargs
        }
        cache_str = json.dumps(cache_data, sort_keys=True)
        return hashlib.md5(cache_str.encode()).hexdigest()
    
    def chat(self, prompt, model="gpt-3.5-turbo", **kwargs):
        cache_key = self._get_cache_key(prompt, model, **kwargs)
        
        # Verificar cache
        if cache_key in self._cache:
            print("Cache hit!")
            return self._cache[cache_key]
        
        # Fazer requisição
        response = self.ai_service.chat(
            prompt=prompt,
            model=model,
            **kwargs
        )
        
        # Armazenar no cache
        self._cache[cache_key] = response
        return response

# Uso
cached_ai = CachedAIService(api_key="sua-api-key")
response1 = cached_ai.chat("O que é Python?")  # Requisição à API
response2 = cached_ai.chat("O que é Python?")  # Cache hit!
```

## 🧪 Testes

```python
import pytest
from unittest.mock import Mock, patch
from appserver_sdk_python_ai.llm import AIService, ChatResponse

@pytest.fixture
def ai_service():
    return AIService(api_key="test-key")

def test_chat_success(ai_service):
    # Mock da resposta
    mock_response = ChatResponse(
        content="Resposta de teste",
        model="gpt-3.5-turbo",
        usage={"total_tokens": 50}
    )
    
    with patch.object(ai_service, 'chat', return_value=mock_response):
        response = ai_service.chat("Teste")
        assert response.content == "Resposta de teste"
        assert response.model == "gpt-3.5-turbo"

def test_chat_error(ai_service):
    with patch.object(ai_service, 'chat', side_effect=Exception("API Error")):
        with pytest.raises(Exception):
            ai_service.chat("Teste")

# Executar testes
# pytest src/appserver_sdk_python_ai/llm/tests/ -v
```

## 🤝 Contribuição

Para contribuir com o módulo LLM:

1. **Novos Provedores**: Adicione suporte a novos provedores de IA
2. **Otimizações**: Melhore performance e eficiência
3. **Funcionalidades**: Adicione novos recursos e capacidades
4. **Testes**: Expanda a cobertura de testes
5. **Documentação**: Melhore exemplos e documentação

```bash
# Executar testes do módulo LLM
python -m pytest src/appserver_sdk_python_ai/llm/tests/ -v

# Verificar cobertura
python -m pytest src/appserver_sdk_python_ai/llm/tests/ --cov=llm --cov-report=html
```

## 📚 Recursos Adicionais

- **[📚 Documentação da API](https://docs.appserver.com.br/ai/)** - Documentação oficial online
- **[💡 Exemplos Práticos](../../../examples/llm/)** - Exemplos de uso organizados por funcionalidade
- **[🔧 Documentação Interativa](docs/interactive_docs.py)** - Acesso dinâmico a esta documentação
- **[📋 Changelog](../../../CHANGELOG.md)** - Histórico de versões e mudanças
- **[🆘 Issues e Suporte](https://github.com/appserver/appserver-sdk-python-ai/issues)** - Reportar problemas e solicitar ajuda

> **Nota**: Esta documentação é a fonte única e consolidada para o módulo LLM. A documentação interativa carrega dinamicamente o conteúdo deste arquivo para evitar redundância.

## 📄 Licença

Este módulo faz parte do AppServer SDK Python AI e segue a mesma licença do projeto principal.

---

**Versão**: 1.0.0  
**Última atualização**: 2024  
**Compatibilidade**: Python 3.8+  
**Desenvolvido com ❤️ pela equipe AppServer**