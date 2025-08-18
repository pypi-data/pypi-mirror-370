# Módulo WebScraping - AppServer SDK Python AI

O módulo WebScraping fornece funcionalidades avançadas para extração de conteúdo de páginas web, processamento de documentos e OCR (Optical Character Recognition).

## 🚀 Características Principais

### Web Scraping
- **🔍 Scraping Robusto**: Requisições HTTP com retry automático, headers customizáveis e tratamento de erros
- **📄 Conversão Docling**: Utiliza a biblioteca Docling da IBM para conversão de alta qualidade
- **🧹 Limpeza Inteligente**: Remove automaticamente scripts, ads, navegação e outros elementos irrelevantes
- **🚀 Processamento Paralelo**: Suporte nativo para scraping de múltiplas URLs simultaneamente
- **💾 Sistema de Cache**: Cache automático em disco para otimizar performance
- **📊 Metadados Ricos**: Extração automática de título, descrição, autor, data e estatísticas
- **🛡️ Validação Robusta**: Validação de URLs, domínios bloqueados e verificação de robots.txt
- **⚡ Interface Simples**: API intuitiva para uso básico e avançado

### OCR (Optical Character Recognition)
- **Múltiplos Engines**: Tesseract, EasyOCR, PaddleOCR
- **Formatos Suportados**: JPEG, PNG, GIF, TIFF, BMP, WEBP
- **Pré-processamento**: Melhoria automática da qualidade da imagem
- **Processamento em Lote**: OCR paralelo de múltiplas imagens
- **Seleção Automática**: Escolha automática do melhor engine disponível

### Processamento de PDFs
- **OCR Avançado**: Processamento de PDFs com OCR usando Docling
- **Extração de Imagens**: Extração e catalogação de imagens em PDFs
- **Extração de Tabelas**: Reconhecimento e extração de tabelas
- **Processamento em Lote**: Processamento paralelo de múltiplos PDFs
- **Metadados Detalhados**: Informações completas sobre o processamento

## 📁 Estrutura do Módulo

```
webscraping/
├── __init__.py                 # Inicialização e exports principais
├── README.md                   # Esta documentação
├── core/
│   ├── config.py              # Configurações e constantes
│   ├── exceptions.py          # Exceções customizadas
│   └── models.py              # Modelos de dados
├── docling/
│   └── scraper.py            # Scraper principal com Docling
├── utils/
│   ├── cache.py              # Sistema de cache
│   ├── cleaner.py            # Limpeza de conteúdo
│   └── validators.py         # Validadores de URL e conteúdo
└── tests/
    └── test_basic.py         # Testes unitários
```

## 📦 Instalação

### Dependências Básicas
```bash
pip install requests beautifulsoup4 lxml
```

### Docling (Para conversão avançada e PDFs)
```bash
pip install docling
```

### OCR - Dependências Opcionais

#### Tesseract (Recomendado)
```bash
pip install pytesseract pillow

# Instalar Tesseract:
# Windows: https://github.com/UB-Mannheim/tesseract/wiki
# Linux: sudo apt install tesseract-ocr tesseract-ocr-por
# macOS: brew install tesseract
```

#### EasyOCR (Opcional)
```bash
pip install easyocr
```

#### PaddleOCR (Opcional)
```bash
pip install paddleocr
```

## 🔥 Uso Rápido

### Web Scraping Simples
```python
from appserver_sdk_python_ai.webscraping import quick_scrape

# Scraping básico
resultado = quick_scrape("https://example.com")
print(f"Título: {resultado.title}")
print(f"Conteúdo: {resultado.content}")
```

### Web Scraping com Configurações
```python
from appserver_sdk_python_ai.webscraping import DoclingWebScraper, ScrapingConfig

# Configurar scraper
config = ScrapingConfig(
    timeout=30,
    clean_html=True,
    include_images=True,
    enable_cache=True
)

scraper = DoclingWebScraper(config)
result = scraper.scrape_to_markdown("https://example.com")

if result.success:
    print(f"Título: {result.title}")
    print(f"Conteúdo: {result.content}")
    print(f"Metadados: {result.metadata}")
else:
    print(f"Erro: {result.error}")
```

### Web Scraping em Lote
```python
from appserver_sdk_python_ai.webscraping import batch_scrape_simple

urls = [
    "https://example1.com",
    "https://example2.com",
    "https://example3.com"
]

# Scraping em lote
resultados = batch_scrape_simple(urls, max_workers=3)
for resultado in resultados:
    if resultado.success:
        print(f"✓ {resultado.url}: {resultado.title}")
    else:
        print(f"✗ {resultado.url}: {resultado.error}")
```

### OCR de Imagens
```python
from appserver_sdk_python_ai.webscraping import quick_ocr, batch_ocr

# OCR simples
texto = quick_ocr("imagem.png")
print(texto)

# OCR em lote
resultados = batch_ocr(["img1.png", "img2.jpg", "img3.gif"])
for resultado in resultados:
    if resultado["success"]:
        print(f"{resultado['image_path']}: {resultado['text']}")
```

### Processamento de PDFs
```python
from appserver_sdk_python_ai.webscraping import process_pdf_with_ocr, batch_process_pdfs

# PDF único
resultado = process_pdf_with_ocr(
    pdf_path="documento.pdf",
    extract_images=True,
    extract_tables=True
)

print(f"Páginas: {resultado.metadata['pages_processed']}")
print(f"Imagens: {resultado.metadata['images_count']}")
print(f"Tabelas: {resultado.metadata['tables_count']}")

# Múltiplos PDFs
resultados = batch_process_pdfs(
    pdf_paths=["doc1.pdf", "doc2.pdf"],
    output_dir="resultados",
    extract_images=True,
    extract_tables=True
)
```

## ⚙️ Configuração Avançada

### ScrapingConfig - Todas as Opções
```python
from appserver_sdk_python_ai.webscraping import ScrapingConfig

config = ScrapingConfig(
    # Configurações de rede
    timeout=30,                        # Timeout em segundos
    max_content_length=50*1024*1024,   # Tamanho máximo (50MB)
    follow_redirects=True,             # Seguir redirecionamentos
    max_redirects=5,                   # Máximo de redirecionamentos
    verify_ssl=True,                   # Verificar certificados SSL
    encoding=None,                     # Encoding (auto-detect)
    
    # Configurações de retry
    retry_attempts=3,                  # Tentativas de retry
    retry_delay=1.0,                   # Delay entre tentativas
    
    # Configurações de conteúdo
    clean_html=True,                   # Limpar HTML
    include_images=True,               # Incluir imagens
    include_links=True,                # Incluir links
    
    # Sistema de cache
    enable_cache=False,                # Habilitar cache
    cache_ttl=3600,                   # TTL do cache (1 hora)
    cache_dir=".webscraping_cache",   # Diretório do cache
    
    # Headers customizados
    user_agent="Meu Bot 1.0",
    headers={
        "Accept": "text/html",
        "Accept-Language": "pt-BR"
    },
    cookies={"session": "abc123"}
)
```

### DoclingWebScraper Avançado
```python
from appserver_sdk_python_ai.webscraping import DoclingWebScraper

scraper = DoclingWebScraper(
    cache_enabled=True,
    cache_ttl=3600,
    request_delay=1.0,
    max_retries=3,
    timeout=30
)

resultado = scraper.scrape("https://example.com")
```

### OCR Customizado
```python
from appserver_sdk_python_ai.webscraping import create_custom_ocr_processor

processor = create_custom_ocr_processor(
    engine="tesseract",
    languages=["pt", "en"],
    confidence_threshold=0.8,
    preprocessing={
        "resize_factor": 2.0,
        "denoise": True,
        "enhance_contrast": True
    }
)

resultado = processor.process_image("imagem.png")
```

## 📊 Status e Verificações

### Verificar Status do Módulo
```python
from appserver_sdk_python_ai.webscraping import print_status, health_check

# Status detalhado
print_status()

# Health check
status = health_check()
print(f"Docling disponível: {status['dependencies']['docling']}")
print(f"OCR disponível: {status['features']['ocr_processing']}")
```

### Verificar Engines de OCR
```python
from appserver_sdk_python_ai.webscraping import (
    get_available_ocr_engines,
    check_ocr_dependencies,
    OCR_AVAILABLE
)

if OCR_AVAILABLE:
    engines = get_available_ocr_engines()
    print(f"Engines disponíveis: {engines}")
    
    deps = check_ocr_dependencies()
    for dep, status in deps.items():
        print(f"{dep}: {'✓' if status else '✗'}")
```

## 🎯 Casos de Uso Práticos

### 1. Verificação de Status e Dependências
```python
from appserver_sdk_python_ai.webscraping import (
    print_status,
    check_ocr_dependencies,
    get_available_ocr_engines,
    OCR_AVAILABLE
)

# Verificar status completo do módulo
print_status()

# Verificar dependências de OCR
deps = check_ocr_dependencies()
for dep, status in deps.items():
    status_text = "✓ Disponível" if status else "✗ Não disponível"
    print(f"{dep}: {status_text}")

# Listar engines de OCR disponíveis
if OCR_AVAILABLE:
    engines = get_available_ocr_engines()
    print(f"Engines disponíveis: {engines}")
else:
    print("OCR não disponível. Instale as dependências.")
```

### 2. OCR de Imagem Individual
```python
from appserver_sdk_python_ai.webscraping import (
    quick_ocr,
    OCRNotAvailableError,
    OCRError
)

try:
    # OCR simples
    texto = quick_ocr("documento.png")
    print(f"Texto extraído: {texto}")
    
    # OCR com idiomas específicos
    texto_pt = quick_ocr("documento.png", languages=["pt", "en"])
    print(f"Texto (PT/EN): {texto_pt}")
    
except OCRNotAvailableError:
    print("OCR não disponível. Instale as dependências.")
except OCRError as e:
    print(f"Erro no OCR: {e}")
```

### 3. OCR Customizado com Pré-processamento
```python
from appserver_sdk_python_ai.webscraping import create_custom_ocr_processor

# Criar processador customizado
processor = create_custom_ocr_processor(
    engine="auto",  # Seleciona automaticamente o melhor
    languages=["pt", "en"],
    confidence_threshold=0.7,
    preprocessing={
        "resize_factor": 2.0,
        "denoise": True,
        "enhance_contrast": True
    },
    cache_enabled=True
)

# Processar imagem
resultado = processor.process_image("documento.png")
print(f"Engine usado: {resultado['engine']}")
print(f"Confiança: {resultado['confidence']:.2f}")
print(f"Texto: {resultado['text']}")
print(f"Tempo: {resultado['processing_time']:.2f}s")
```

### 4. OCR em Lote com Callback de Progresso
```python
from appserver_sdk_python_ai.webscraping import batch_ocr
import os

# Encontrar todas as imagens
imagens = []
for arquivo in os.listdir("documentos_escaneados"):
    if arquivo.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
        imagens.append(os.path.join("documentos_escaneados", arquivo))

# Callback para acompanhar progresso
def progress_callback(current, total, image_path, success):
    status = "✓" if success else "✗"
    print(f"[{current}/{total}] {status} {os.path.basename(image_path)}")

# Processar em lote
resultados = batch_ocr(
    image_paths=imagens,
    max_workers=2,
    languages=["pt", "en"],
    progress_callback=progress_callback
)

# Salvar resultados
for resultado in resultados:
    if resultado["success"]:
        nome_arquivo = os.path.splitext(resultado["image_path"])[0] + ".txt"
        with open(nome_arquivo, "w", encoding="utf-8") as f:
            f.write(resultado["text"])
        print(f"✓ Salvo: {nome_arquivo}")
    else:
        print(f"✗ Erro em {resultado['image_path']}: {resultado['error']}")
```

### 5. Processamento de PDF Individual
```python
from appserver_sdk_python_ai.webscraping import process_pdf_with_ocr
from pathlib import Path

# Processar PDF com extração completa
resultado = process_pdf_with_ocr(
    pdf_path="relatorio.pdf",
    output_file="relatorio_processado.md",
    extract_images=True,
    extract_tables=True
)

if resultado.success:
    print("✓ PDF processado com sucesso!")
    print(f"Título: {resultado.title}")
    print(f"Páginas: {resultado.metadata.get('pages_processed', 0)}")
    print(f"Imagens: {resultado.metadata.get('images_count', 0)}")
    print(f"Tabelas: {resultado.metadata.get('tables_count', 0)}")
    print(f"Tempo: {resultado.processing_time:.2f}s")
    
    # Mostrar informações sobre imagens encontradas
    if resultado.metadata.get("images"):
        print("\nImagens encontradas:")
        for i, img in enumerate(resultado.metadata["images"][:3]):
            print(f"  {i+1}. Página {img['page']}: {img['caption']}")
    
    # Mostrar informações sobre tabelas encontradas
    if resultado.metadata.get("tables"):
        print("\nTabelas encontradas:")
        for i, table in enumerate(resultado.metadata["tables"][:3]):
            print(f"  {i+1}. Página {table['page']}: {table['rows']}x{table['cols']}")
else:
    print(f"✗ Erro: {resultado.error}")
```

### 6. Processamento em Lote de PDFs
```python
from appserver_sdk_python_ai.webscraping import batch_process_pdfs
import glob
from pathlib import Path

# Encontrar todos os PDFs
pdfs = glob.glob("relatorios/*.pdf")

def callback_progresso(atual, total, arquivo, sucesso):
    status = "✓" if sucesso else "✗"
    nome = Path(arquivo).name
    print(f"[{atual}/{total}] {status} {nome}")

# Processar todos os PDFs
resultados = batch_process_pdfs(
    pdf_paths=pdfs,
    output_dir="relatorios_processados",
    max_workers=2,  # PDFs são intensivos
    extract_images=True,
    extract_tables=True,
    progress_callback=callback_progresso
)

# Gerar relatório detalhado
print("\n=== RELATÓRIO DE PROCESSAMENTO ===")
sucessos = sum(1 for r in resultados if r.success)
print(f"Total processado: {len(resultados)}")
print(f"Sucessos: {sucessos}")
print(f"Falhas: {len(resultados) - sucessos}")

# Estatísticas agregadas
total_paginas = sum(r.metadata.get('pages_processed', 0) for r in resultados if r.success)
total_imagens = sum(r.metadata.get('images_count', 0) for r in resultados if r.success)
total_tabelas = sum(r.metadata.get('tables_count', 0) for r in resultados if r.success)

print(f"\nEstatísticas:")
print(f"- Total de páginas: {total_paginas}")
print(f"- Total de imagens: {total_imagens}")
print(f"- Total de tabelas: {total_tabelas}")

# Detalhes por arquivo
print("\nDetalhes por arquivo:")
for resultado in resultados:
    if resultado.success:
        nome = Path(resultado.url.replace('file://', '')).name
        paginas = resultado.metadata.get('pages_processed', 0)
        imagens = resultado.metadata.get('images_count', 0)
        tabelas = resultado.metadata.get('tables_count', 0)
        print(f"✓ {nome}: {paginas}p, {imagens}img, {tabelas}tab")
    else:
        nome = Path(resultado.url.replace('file://', '')).name
        print(f"✗ {nome}: {resultado.error}")
```

### 7. Extração de Conteúdo de Notícias
```python
from appserver_sdk_python_ai.webscraping import DoclingWebScraper

scraper = DoclingWebScraper()
urls_noticias = [
    "https://site-noticias1.com/artigo1",
    "https://site-noticias2.com/artigo2"
]

resultados = scraper.batch_scrape(urls_noticias)
for resultado in resultados:
    if resultado.success:
        print(f"Título: {resultado.title}")
        print(f"Resumo: {resultado.content[:200]}...")
        print(f"Palavras-chave: {resultado.metadata.get('keywords', [])}")
```

### 8. Monitoramento de Sites
```python
from appserver_sdk_python_ai.webscraping import DoclingWebScraper
import time
import hashlib

def monitorar_mudancas(url, intervalo=300):  # 5 minutos
    """Monitora mudanças em uma página web"""
    scraper = DoclingWebScraper(cache_enabled=False)
    hash_anterior = None
    
    while True:
        try:
            resultado = scraper.scrape(url)
            if resultado.success:
                # Calcular hash do conteúdo
                hash_atual = hashlib.md5(resultado.content.encode()).hexdigest()
                
                if hash_anterior and hash_atual != hash_anterior:
                    print(f"🔔 Mudança detectada em {url}")
                    print(f"Novo título: {resultado.title}")
                    # Aqui você pode enviar notificação, email, etc.
                
                hash_anterior = hash_atual
                print(f"✓ Verificação OK - {time.strftime('%H:%M:%S')}")
            else:
                print(f"✗ Erro ao verificar: {resultado.error}")
                
        except Exception as e:
            print(f"✗ Erro inesperado: {e}")
        
        time.sleep(intervalo)

# Usar o monitor
# monitorar_mudancas("https://example.com/noticias")
```

## 🚨 Tratamento de Erros

```python
from appserver_sdk_python_ai.webscraping import (
    WebScrapingError,
    ConversionError,
    ValidationError,
    CacheError,
    OCRError,
    OCRNotAvailableError
)

try:
    resultado = quick_scrape("https://example.com")
except ValidationError as e:
    print(f"URL inválida: {e}")
except ConversionError as e:
    print(f"Erro na conversão: {e}")
except WebScrapingError as e:
    print(f"Erro geral: {e}")

try:
    texto = quick_ocr("imagem.png")
except OCRNotAvailableError:
    print("OCR não disponível. Instale as dependências.")
except OCRError as e:
    print(f"Erro no OCR: {e}")
```

## 📈 Performance e Otimização

### Dicas de Performance

1. **Use Cache**: Habilite o cache para URLs e imagens processadas frequentemente
2. **Processamento em Lote**: Use funções batch para múltiplos itens
3. **Configuração de Workers**: Ajuste `max_workers` baseado no seu hardware
4. **Timeout Adequado**: Configure timeouts apropriados para seu caso
5. **Pré-processamento**: Configure OCR adequadamente para seu tipo de imagem

### Configurações Recomendadas

```python
# Para web scraping intensivo
scraper = DoclingWebScraper(
    cache_enabled=True,
    cache_ttl=7200,  # 2 horas
    request_delay=0.5,  # Respeitar servidores
    max_retries=3,
    timeout=30
)

# Para OCR de documentos
processor = create_custom_ocr_processor(
    engine="tesseract",
    languages=["pt", "en"],
    preprocessing={
        "resize_factor": 2.0,
        "denoise": True,
        "enhance_contrast": True
    },
    cache_enabled=True
)

# Para processamento de PDFs
resultados = batch_process_pdfs(
    pdf_paths=pdfs,
    max_workers=2,  # PDFs são intensivos
    extract_images=True,
    extract_tables=True
)
```

## 🔗 Integração com Outros Módulos

O módulo WebScraping pode ser integrado com outros componentes do AppServer SDK:

```python
# Exemplo de integração com processamento de IA
from appserver_sdk_python_ai.webscraping import quick_scrape
from appserver_sdk_python_ai.llm import process_text  # Exemplo

# Extrair conteúdo
resultado = quick_scrape("https://artigo-tecnico.com")

if resultado.success:
    # Processar com IA
    resumo = process_text(resultado.content, task="summarize")
    print(f"Resumo: {resumo}")
```

## 📋 Exemplo Completo de OCR e Processamento

Baseado no arquivo `examples/webscraping_ocr_example.py`, aqui está um exemplo completo que demonstra todas as funcionalidades:

```python
#!/usr/bin/env python3
"""
Exemplo completo de uso das funcionalidades de OCR do módulo webscraping.

Este exemplo demonstra:
1. Verificação de status e dependências
2. OCR de imagens individuais (JPEG, PNG, GIF)
3. OCR em lote de múltiplas imagens
4. Processamento de PDFs com OCR e extração de imagens/tabelas
5. Processamento em lote de PDFs
6. Configuração customizada de OCR
"""

import os
from pathlib import Path

from appserver_sdk_python_ai.webscraping import (
    # Status do módulo
    OCR_AVAILABLE,
    OCRError,
    OCRNotAvailableError,
    # Funções de OCR
    quick_ocr,
    batch_ocr,
    create_custom_ocr_processor,
    # Funções de PDF
    process_pdf_with_ocr,
    batch_process_pdfs,
    # Utilitários
    print_status,
    check_ocr_dependencies,
    get_available_ocr_engines,
)

def main():
    """Função principal que executa todos os exemplos."""
    print("🔍 EXEMPLOS DE OCR E PROCESSAMENTO DE DOCUMENTOS")
    print("=" * 50)
    print()

    # 1. Verificar status do módulo
    print("=== STATUS DO MÓDULO WEBSCRAPING ===")
    print_status()
    print()

    print("=== VERIFICAÇÃO DE DEPENDÊNCIAS OCR ===")
    deps = check_ocr_dependencies()
    for dep, status in deps.items():
        status_text = "✓ Disponível" if status else "✗ Não disponível"
        print(f"{dep}: {status_text}")
    print()

    print("=== ENGINES DE OCR DISPONÍVEIS ===")
    engines = get_available_ocr_engines()
    if engines:
        for engine in engines:
            print(f"- {engine}")
    else:
        print("Nenhum engine de OCR disponível")
    print()

    if not OCR_AVAILABLE:
        print("⚠️  OCR não está disponível. Instale as dependências:")
        print("   pip install pytesseract pillow")
        print("   pip install easyocr  # opcional")
        print("   pip install paddleocr  # opcional")
        print()
        print("   Também instale o Tesseract:")
        print("   - Windows: https://github.com/UB-Mannheim/tesseract/wiki")
        print("   - Linux: sudo apt install tesseract-ocr")
        print("   - macOS: brew install tesseract")
        return

    # 2. OCR de imagem individual
    print("=== OCR DE IMAGEM INDIVIDUAL ===")
    image_path = "exemplo_imagem.png"
    
    if os.path.exists(image_path):
        try:
            # OCR simples
            texto = quick_ocr(image_path)
            print(f"Texto extraído: {texto}")
            
            # OCR com idiomas específicos
            texto_pt = quick_ocr(image_path, languages=["pt", "en"])
            print(f"Texto (PT/EN): {texto_pt}")
            
        except OCRNotAvailableError:
            print("OCR não disponível.")
        except OCRError as e:
            print(f"Erro no OCR: {e}")
    else:
        print(f"Arquivo de exemplo não encontrado: {image_path}")
    print()

    # 3. OCR customizado
    print("=== OCR CUSTOMIZADO ===")
    if os.path.exists(image_path):
        try:
            processor = create_custom_ocr_processor(
                engine="auto",
                languages=["pt", "en"],
                confidence_threshold=0.7,
                preprocessing={
                    "resize_factor": 2.0,
                    "denoise": True,
                    "enhance_contrast": True,
                },
                cache_enabled=True,
            )
            
            resultado = processor.process_image(image_path)
            print(f"Engine usado: {resultado['engine']}")
            print(f"Confiança: {resultado['confidence']:.2f}")
            print(f"Texto: {resultado['text']}")
            print(f"Tempo: {resultado['processing_time']:.2f}s")
            
        except Exception as e:
            print(f"Erro no OCR customizado: {e}")
    print()

    # 4. OCR em lote
    print("=== OCR EM LOTE ===")
    image_paths = ["imagem1.png", "imagem2.jpg", "imagem3.gif"]
    existing_images = [img for img in image_paths if os.path.exists(img)]
    
    if existing_images:
        def progress_callback(current, total, image_path, success):
            status = "✓" if success else "✗"
            print(f"[{current}/{total}] {status} {image_path}")
        
        resultados = batch_ocr(
            image_paths=existing_images,
            max_workers=2,
            progress_callback=progress_callback,
        )
        
        for resultado in resultados:
            if resultado["success"]:
                print(f"- {resultado['image_path']}: {resultado['text'][:100]}...")
            else:
                print(f"- {resultado['image_path']}: ERRO - {resultado['error']}")
    else:
        print("Nenhuma imagem de exemplo encontrada.")
    print()

    # 5. Processamento de PDF
    print("=== PROCESSAMENTO DE PDF ===")
    pdf_path = "exemplo_documento.pdf"
    
    if os.path.exists(pdf_path):
        try:
            resultado = process_pdf_with_ocr(
                pdf_path=pdf_path,
                output_file="resultado_pdf.md",
                extract_images=True,
                extract_tables=True,
            )
            
            if resultado.success:
                print("✓ PDF processado com sucesso!")
                print(f"Páginas: {resultado.metadata.get('pages_processed', 0)}")
                print(f"Imagens: {resultado.metadata.get('images_count', 0)}")
                print(f"Tabelas: {resultado.metadata.get('tables_count', 0)}")
            else:
                print(f"✗ Erro: {resultado.error}")
                
        except Exception as e:
            print(f"Erro no processamento: {e}")
    else:
        print(f"Arquivo PDF não encontrado: {pdf_path}")
    print()

    print("✅ Exemplos executados!")
    print()
    print("📝 Notas importantes:")
    print("- Substitua os caminhos de exemplo por arquivos reais")
    print("- Para PDFs, o Docling oferece OCR avançado sem dependências extras")
    print("- Para imagens, instale pytesseract, easyocr ou paddleocr")
    print("- Use configurações de pré-processamento para melhorar a precisão")

if __name__ == "__main__":
    main()
```

### Executando o Exemplo

1. **Prepare os arquivos de teste**:
   ```bash
   # Crie algumas imagens com texto para testar
   # exemplo_imagem.png, imagem1.png, imagem2.jpg, etc.
   
   # Crie um PDF com texto e imagens
   # exemplo_documento.pdf
   ```

2. **Execute o exemplo**:
   ```bash
   python examples/webscraping_ocr_example.py
   ```

3. **Verifique os resultados**:
   - Textos extraídos das imagens
   - Arquivo `resultado_pdf.md` com conteúdo do PDF
   - Imagens e tabelas extraídas (se houver)

## 🧪 Testes

```bash
# Executar todos os testes
python -m pytest tests/test_webscraping/ -v

# Executar testes específicos
python -m pytest tests/test_webscraping/test_scraper.py -v

# Com cobertura
python -m pytest tests/test_webscraping/ --cov=webscraping --cov-report=html
```

## 🔧 Troubleshooting e Dicas Avançadas

### Problemas Comuns com OCR

#### OCR não disponível
```python
from appserver_sdk_python_ai.webscraping import OCR_AVAILABLE, check_ocr_dependencies

if not OCR_AVAILABLE:
    print("OCR não disponível. Verificando dependências...")
    deps = check_ocr_dependencies()
    for dep, status in deps.items():
        if not status:
            print(f"❌ {dep} não instalado")
```

**Soluções**:
- **Tesseract**: Instale o binário do sistema + `pip install pytesseract pillow`
- **EasyOCR**: `pip install easyocr` (requer CUDA para GPU)
- **PaddleOCR**: `pip install paddleocr` (mais pesado, melhor precisão)

#### Baixa qualidade de OCR
```python
# Use pré-processamento para melhorar a qualidade
processor = create_custom_ocr_processor(
    preprocessing={
        "resize_factor": 3.0,      # Aumentar imagem
        "denoise": True,           # Remover ruído
        "enhance_contrast": True,  # Melhorar contraste
        "sharpen": True,          # Aumentar nitidez
        "binarize": True          # Converter para preto e branco
    },
    confidence_threshold=0.8       # Filtrar texto com baixa confiança
)
```

#### Problemas de idioma
```python
# Especifique idiomas corretos
texto = quick_ocr(
    "documento.png",
    languages=["pt", "en"],  # Português e inglês
    engine="tesseract"        # Tesseract tem melhor suporte a idiomas
)
```

### Problemas com PDFs

#### PDFs protegidos ou corrompidos
```python
try:
    resultado = process_pdf_with_ocr("documento.pdf")
except Exception as e:
    if "password" in str(e).lower():
        print("PDF protegido por senha")
    elif "corrupt" in str(e).lower():
        print("PDF corrompido")
    else:
        print(f"Erro desconhecido: {e}")
```

#### PDFs muito grandes
```python
# Processe em lote com menos workers
resultados = batch_process_pdfs(
    pdf_paths=pdfs_grandes,
    max_workers=1,  # Reduzir para economizar memória
    extract_images=False,  # Desabilitar se não precisar
    extract_tables=False
)
```

### Otimização de Performance

#### Cache Inteligente
```python
# Configure cache para diferentes cenários
scraper = DoclingWebScraper(
    cache_enabled=True,
    cache_ttl=7200,  # 2 horas para conteúdo dinâmico
    cache_dir=".cache_webscraping"
)

# Para OCR, use cache por hash da imagem
processor = create_custom_ocr_processor(
    cache_enabled=True,
    cache_by_content_hash=True  # Cache baseado no conteúdo
)
```

#### Processamento Paralelo Otimizado
```python
import multiprocessing

# Calcular workers ideais
max_workers = min(multiprocessing.cpu_count(), len(arquivos), 4)

# Para OCR (CPU intensivo)
resultados_ocr = batch_ocr(
    image_paths=imagens,
    max_workers=max_workers
)

# Para web scraping (I/O intensivo)
resultados_web = batch_scrape_simple(
    urls=urls,
    max_workers=max_workers * 2  # Pode ser maior para I/O
)
```

### Monitoramento e Logging

```python
import logging
from appserver_sdk_python_ai.webscraping import DoclingWebScraper

# Configurar logging detalhado
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def processar_com_monitoramento(urls):
    scraper = DoclingWebScraper()
    sucessos = 0
    falhas = 0
    
    for i, url in enumerate(urls, 1):
        try:
            resultado = scraper.scrape(url)
            if resultado.success:
                sucessos += 1
                logger.info(f"[{i}/{len(urls)}] ✓ {url}")
            else:
                falhas += 1
                logger.warning(f"[{i}/{len(urls)}] ✗ {url}: {resultado.error}")
        except Exception as e:
            falhas += 1
            logger.error(f"[{i}/{len(urls)}] ❌ {url}: {e}")
    
    logger.info(f"Processamento concluído: {sucessos} sucessos, {falhas} falhas")
    return sucessos, falhas
```

### Integração com Outros Sistemas

#### Salvamento em Banco de Dados
```python
import sqlite3
from datetime import datetime

def salvar_resultado_ocr(resultado, db_path="ocr_results.db"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ocr_results (
            id INTEGER PRIMARY KEY,
            image_path TEXT,
            text_content TEXT,
            confidence REAL,
            engine TEXT,
            processing_time REAL,
            created_at TIMESTAMP
        )
    """)
    
    cursor.execute("""
        INSERT INTO ocr_results 
        (image_path, text_content, confidence, engine, processing_time, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        resultado['image_path'],
        resultado['text'],
        resultado['confidence'],
        resultado['engine'],
        resultado['processing_time'],
        datetime.now()
    ))
    
    conn.commit()
    conn.close()
```

#### API REST para OCR
```python
from flask import Flask, request, jsonify
from appserver_sdk_python_ai.webscraping import quick_ocr

app = Flask(__name__)

@app.route('/ocr', methods=['POST'])
def api_ocr():
    if 'image' not in request.files:
        return jsonify({'error': 'Nenhuma imagem enviada'}), 400
    
    file = request.files['image']
    languages = request.form.get('languages', 'pt,en').split(',')
    
    try:
        # Salvar temporariamente
        temp_path = f"/tmp/{file.filename}"
        file.save(temp_path)
        
        # Processar OCR
        texto = quick_ocr(temp_path, languages=languages)
        
        return jsonify({
            'success': True,
            'text': texto,
            'languages': languages
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True)
```

## 🤝 Contribuição

Para contribuir com o módulo:

1. **Web Scraping**: Melhore a extração de metadados, adicione suporte a novos sites
2. **OCR**: Adicione novos engines, melhore pré-processamento
3. **PDFs**: Otimize processamento, adicione novos tipos de extração
4. **Performance**: Otimize algoritmos, melhore cache
5. **Documentação**: Adicione exemplos, melhore documentação
6. **Testes**: Adicione testes para novos recursos
7. **Exemplos**: Crie exemplos práticos para casos de uso específicos

## 📄 Licença

Este módulo faz parte do AppServer SDK Python AI e segue a mesma licença do projeto principal.

---

**Versão**: 1.0.0  
**Última atualização**: 2024  
**Compatibilidade**: Python 3.8+
**Desenvolvido com ❤️ pela equipe AppServer**