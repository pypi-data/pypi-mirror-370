# Módulo OCR - AppServer SDK Python AI

Este módulo fornece funcionalidades avançadas de OCR (Optical Character Recognition) para extrair texto de imagens em diversos formatos.

## 🚀 Características

- **Múltiplos Engines**: Suporte para Tesseract, EasyOCR e PaddleOCR
- **Seleção Automática**: Escolha automática do melhor engine disponível
- **Formatos Suportados**: JPEG, PNG, GIF, TIFF, BMP, WEBP
- **Pré-processamento**: Melhoria automática da qualidade da imagem
- **Cache Inteligente**: Cache de resultados para melhor performance
- **Processamento em Lote**: Processamento paralelo de múltiplas imagens
- **Configuração Flexível**: Configurações detalhadas para cada engine
- **Integração com PDFs**: Processamento de documentos PDF com OCR
- **Detecção de Idiomas**: Suporte a múltiplos idiomas simultaneamente

## 📦 Instalação

### Usando Poetry (Recomendado)

Para instalar as dependências do OCR usando Poetry:

```bash
# Instalar dependências do grupo OCR
poetry install --with ocr
```

### Usando pip

Alternativamente, instale as dependências diretamente:

```bash
pip install pytesseract easyocr paddlepaddle paddleocr opencv-python-headless pillow
```

**Nota:** Usamos `opencv-python-headless` para evitar conflitos de dependências com outras bibliotecas.

### Configuração do Tesseract

**Windows:**
1. Baixe o instalador do Tesseract: https://github.com/UB-Mannheim/tesseract/wiki
2. Instale e adicione ao PATH do sistema
3. Configure a variável de ambiente `TESSERACT_CMD` se necessário

**Linux/macOS:**
```bash
# Ubuntu/Debian
sudo apt-get install tesseract-ocr

# macOS
brew install tesseract
```

### Pacotes de Idiomas

Para suporte a idiomas específicos:

```bash
# Português
sudo apt-get install tesseract-ocr-por

# Espanhol
sudo apt-get install tesseract-ocr-spa

# Francês
sudo apt-get install tesseract-ocr-fra
```

### Engines de OCR

#### Tesseract (Recomendado)
```bash
# Instalar biblioteca Python
pip install pytesseract

# Instalar Tesseract
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

## 🔧 Exemplos de Uso

### Uso Básico

```python
from appserver_sdk_python_ai.ocr import OCRProcessor

# Inicializar o processador
ocr = OCRProcessor()

# Extrair texto de uma imagem
result = ocr.extract_text("path/to/image.jpg")
print(f"Texto extraído: {result.text}")
print(f"Confiança: {result.confidence}")
```

### OCR com Engine Específico

```python
from appserver_sdk_python_ai.ocr import OCRProcessor, OCREngine

# Usar Tesseract especificamente
ocr = OCRProcessor(engine=OCREngine.TESSERACT)
result = ocr.extract_text("documento.png")

# Usar EasyOCR para melhor detecção de texto em imagens naturais
ocr_easy = OCRProcessor(engine=OCREngine.EASYOCR)
result_easy = ocr_easy.extract_text("foto_com_texto.jpg")

# Usar PaddleOCR para documentos complexos
ocr_paddle = OCRProcessor(engine=OCREngine.PADDLEOCR)
result_paddle = ocr_paddle.extract_text("documento_complexo.pdf")
```

### OCR com Múltiplos Idiomas

```python
from appserver_sdk_python_ai.ocr import OCRProcessor

# Configurar para português e inglês
ocr = OCRProcessor(
    languages=['por', 'eng'],
    engine=OCREngine.TESSERACT
)

result = ocr.extract_text("documento_multilingual.jpg")
print(f"Texto: {result.text}")
print(f"Idiomas detectados: {result.detected_languages}")
```

### Processamento em Lote

```python
from appserver_sdk_python_ai.ocr import OCRProcessor
import asyncio

async def processar_multiplas_imagens():
    ocr = OCRProcessor()
    
    imagens = [
        "documento1.jpg",
        "documento2.png",
        "documento3.pdf"
    ]
    
    # Processamento paralelo
    resultados = await ocr.extract_text_batch(imagens)
    
    for i, resultado in enumerate(resultados):
        print(f"Imagem {i+1}: {resultado.text[:100]}...")
        print(f"Confiança: {resultado.confidence}")
        print("-" * 50)

# Executar
asyncio.run(processar_multiplas_imagens())
```

### OCR com Pré-processamento

```python
from appserver_sdk_python_ai.ocr import OCRProcessor, PreprocessingConfig

# Configurar pré-processamento para melhorar qualidade
preprocess_config = PreprocessingConfig(
    enhance_contrast=True,
    denoise=True,
    deskew=True,
    resize_factor=2.0
)

ocr = OCRProcessor(preprocessing=preprocess_config)
result = ocr.extract_text("imagem_baixa_qualidade.jpg")

print(f"Texto melhorado: {result.text}")
print(f"Melhoria na confiança: {result.confidence}")
```

### OCR Simples
```python
from appserver_sdk_python_ai.ocr import quick_ocr

# OCR básico
texto = quick_ocr("imagem.png")
print(texto)

# OCR com idiomas específicos
texto = quick_ocr("imagem.png", languages=["pt", "en"])
print(texto)
```

## 🎯 Casos de Uso Práticos

### Extração de Dados de Documentos

```python
from appserver_sdk_python_ai.ocr import OCRProcessor
import re

def extrair_dados_rg(imagem_rg):
    ocr = OCRProcessor(engine=OCREngine.TESSERACT)
    result = ocr.extract_text(imagem_rg)
    
    # Extrair número do RG
    rg_pattern = r'\b\d{1,2}\.\d{3}\.\d{3}-\d{1}\b'
    rg_match = re.search(rg_pattern, result.text)
    
    # Extrair CPF
    cpf_pattern = r'\b\d{3}\.\d{3}\.\d{3}-\d{2}\b'
    cpf_match = re.search(cpf_pattern, result.text)
    
    return {
        'rg': rg_match.group() if rg_match else None,
        'cpf': cpf_match.group() if cpf_match else None,
        'texto_completo': result.text,
        'confianca': result.confidence
    }

# Usar
dados = extrair_dados_rg("rg_frente.jpg")
print(f"RG: {dados['rg']}")
print(f"CPF: {dados['cpf']}")
```

### Digitalização de Notas Fiscais

```python
from appserver_sdk_python_ai.ocr import OCRProcessor
from decimal import Decimal
import re

def processar_nota_fiscal(imagem_nf):
    ocr = OCRProcessor(
        engine=OCREngine.PADDLEOCR,
        preprocessing=PreprocessingConfig(
            enhance_contrast=True,
            deskew=True
        )
    )
    
    result = ocr.extract_text(imagem_nf)
    
    # Extrair valor total
    valor_pattern = r'TOTAL.*?R\$\s*(\d+,\d{2})'
    valor_match = re.search(valor_pattern, result.text, re.IGNORECASE)
    
    # Extrair CNPJ
    cnpj_pattern = r'\b\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}\b'
    cnpj_match = re.search(cnpj_pattern, result.text)
    
    return {
        'valor_total': valor_match.group(1) if valor_match else None,
        'cnpj': cnpj_match.group() if cnpj_match else None,
        'texto_completo': result.text
    }

# Processar nota fiscal
nf_dados = processar_nota_fiscal("nota_fiscal.jpg")
print(f"Valor: R$ {nf_dados['valor_total']}")
print(f"CNPJ: {nf_dados['cnpj']}")
```

### OCR em Lote
```python
from appserver_sdk_python_ai.ocr import batch_ocr

def progress_callback(current, total, image_path, success):
    print(f"[{current}/{total}] {'✓' if success else '✗'} {image_path}")

resultados = batch_ocr(
    image_paths=["img1.png", "img2.jpg", "img3.gif"],
    max_workers=3,
    progress_callback=progress_callback
)

for resultado in resultados:
    if resultado["success"]:
        print(f"{resultado['image_path']}: {resultado['text']}")
    else:
        print(f"Erro em {resultado['image_path']}: {resultado['error']}")
```

### OCR Customizado
```python
from appserver_sdk_python_ai.ocr import create_custom_ocr_processor

# Criar processador customizado
processor = create_custom_ocr_processor(
    engine="tesseract",
    languages=["pt", "en"],
    confidence_threshold=0.8,
    preprocessing={
        "resize_factor": 2.0,
        "denoise": True,
        "enhance_contrast": True
    },
    cache_enabled=True
)

# Processar imagem
resultado = processor.process_image("imagem.png")
print(f"Texto: {resultado['text']}")
print(f"Confiança: {resultado['confidence']}")
print(f"Engine: {resultado['engine']}")
```

## 🔗 Integração com Outros Módulos

### Integração com WebScraping

```python
from appserver_sdk_python_ai.webscraping import WebScraper
from appserver_sdk_python_ai.ocr import OCRProcessor
import requests
from io import BytesIO

def extrair_texto_de_imagens_web(url):
    # Fazer scraping da página
    scraper = WebScraper()
    page_data = scraper.scrape(url)
    
    # Encontrar todas as imagens
    image_urls = page_data.find_all_images()
    
    ocr = OCRProcessor()
    textos_extraidos = []
    
    for img_url in image_urls:
        # Baixar imagem
        response = requests.get(img_url)
        img_bytes = BytesIO(response.content)
        
        # Extrair texto
        result = ocr.extract_text(img_bytes)
        if result.confidence > 0.7:
            textos_extraidos.append({
                'url': img_url,
                'texto': result.text,
                'confianca': result.confidence
            })
    
    return textos_extraidos

# Usar
textos = extrair_texto_de_imagens_web('https://exemplo.com')
for texto in textos:
    print(f"Imagem: {texto['url']}")
    print(f"Texto: {texto['texto'][:100]}...")
```

### Integração com LLM

```python
from appserver_sdk_python_ai.ocr import OCRProcessor
from appserver_sdk_python_ai.llm import LLMClient

def analisar_documento_com_ia(imagem_path):
    # Extrair texto com OCR
    ocr = OCRProcessor()
    ocr_result = ocr.extract_text(imagem_path)
    
    # Analisar com LLM
    llm = LLMClient()
    
    prompt = f"""
    Analise o seguinte texto extraído de um documento:
    
    {ocr_result.text}
    
    Extraia as seguintes informações:
    1. Tipo de documento
    2. Dados pessoais (nome, CPF, RG, etc.)
    3. Datas importantes
    4. Valores monetários
    5. Resumo do conteúdo
    
    Formate a resposta em JSON.
    """
    
    analysis = llm.chat(prompt)
    
    return {
        'texto_original': ocr_result.text,
        'confianca_ocr': ocr_result.confidence,
        'analise_ia': analysis.content
    }

# Usar
analise = analisar_documento_com_ia('contrato.pdf')
print(f"Análise: {analise['analise_ia']}")
```

## ⚙️ Configuração Avançada

### Classe OCRConfig
```python
from appserver_sdk_python_ai.ocr import OCRConfig, OCRProcessor

config = OCRConfig(
    engine="auto",  # tesseract, easyocr, paddleocr, auto
    languages=["pt", "en"],
    confidence_threshold=0.7,
    
    # Configurações específicas do Tesseract
    tesseract_config={
        "psm": 6,  # Page Segmentation Mode
        "oem": 3,  # OCR Engine Mode
        "custom_config": "--psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz "
    },
    
    # Configurações do EasyOCR
    easyocr_config={
        "gpu": False,
        "detail": 1,
        "paragraph": False
    },
    
    # Configurações do PaddleOCR
    paddleocr_config={
        "use_angle_cls": True,
        "use_gpu": False,
        "show_log": False
    },
    
    # Pré-processamento de imagem
    preprocessing={
        "resize_factor": 1.5,
        "denoise": True,
        "enhance_contrast": True,
        "convert_to_grayscale": True,
        "threshold_type": "adaptive"  # binary, adaptive, otsu
    },
    
    # Pós-processamento de texto
    postprocessing={
        "remove_extra_whitespace": True,
        "fix_line_breaks": True,
        "remove_special_chars": False,
        "min_word_length": 1
    },
    
    # Cache
    cache_enabled=True,
    cache_ttl=3600,  # 1 hora
    
    # Processamento em lote
    batch_size=10,
    max_workers=3
)

processor = OCRProcessor(config)
```

### Configuração de Engine

```python
from appserver_sdk_python_ai.ocr import OCRProcessor, OCREngine

# Usar engine específico
ocr_tesseract = OCRProcessor(engine=OCREngine.TESSERACT)
ocr_easyocr = OCRProcessor(engine=OCREngine.EASYOCR)
ocr_paddle = OCRProcessor(engine=OCREngine.PADDLEOCR)
```

### Configuração de Idiomas

```python
# Múltiplos idiomas
ocr = OCRProcessor(
    engine=OCREngine.TESSERACT,
    languages=["por", "eng", "spa"]
)
```

### Configuração de Pré-processamento

```python
from appserver_sdk_python_ai.ocr import PreprocessingConfig

config = PreprocessingConfig(
    resize_factor=2.0,
    enhance_contrast=True,
    denoise=True,
    deskew=True,
    threshold_method="adaptive"
)

ocr = OCRProcessor(preprocessing=config)
```

## 🔍 Exemplos Avançados

### OCR com Validação

```python
from appserver_sdk_python_ai.ocr import OCRProcessor, ValidationConfig

# Configurar validação
validation = ValidationConfig(
    min_confidence=0.8,
    required_patterns=[r"\d{3}\.\d{3}\.\d{3}-\d{2}"],  # CPF
    forbidden_chars=["@", "#", "$"]
)

ocr = OCRProcessor(validation=validation)
result = ocr.extract_text("document.jpg")

if result.is_valid:
    print(f"Texto válido: {result.text}")
else:
    print(f"Problemas encontrados: {result.validation_errors}")
```

### OCR com Callback de Progresso

```python
def progress_callback(current, total, filename):
    percentage = (current / total) * 100
    print(f"Processando {filename}: {percentage:.1f}%")

ocr = OCRProcessor(progress_callback=progress_callback)
results = ocr.extract_text_batch(["img1.jpg", "img2.png", "img3.pdf"])
```

## 🎯 Engines de OCR

### Tesseract
- **Prós**: Maduro, preciso, muitos idiomas
- **Contras**: Requer instalação separada
- **Melhor para**: Documentos, texto limpo

### EasyOCR
- **Prós**: Fácil instalação, boa para texto em cena
- **Contras**: Modelos grandes, menos idiomas
- **Melhor para**: Imagens naturais, placas, sinais

### PaddleOCR
- **Prós**: Rápido, boa precisão, suporte a chinês
- **Contras**: Documentação em chinês
- **Melhor para**: Documentos asiáticos, texto misto

## 📊 Formatos Suportados

| Formato | Extensões | Suporte |
|---------|-----------|----------|
| JPEG | .jpg, .jpeg | ✅ |
| PNG | .png | ✅ |
| GIF | .gif | ✅ |
| TIFF | .tiff, .tif | ✅ |
| BMP | .bmp | ✅ |
| WEBP | .webp | ✅ |

## 🔍 Verificação de Status

```python
from appserver_sdk_python_ai.ocr import (
    get_available_ocr_engines,
    check_ocr_dependencies,
    OCR_AVAILABLE
)

# Verificar se OCR está disponível
if OCR_AVAILABLE:
    print("OCR está disponível!")
else:
    print("OCR não está disponível")

# Listar engines disponíveis
engines = get_available_ocr_engines()
print(f"Engines disponíveis: {engines}")

# Verificar dependências
deps = check_ocr_dependencies()
for dep, status in deps.items():
    print(f"{dep}: {'✓' if status else '✗'}")
```

## 🚨 Tratamento de Erros

```python
from appserver_sdk_python_ai.ocr import (
    OCRError,
    OCRNotAvailableError,
    OCREngineError,
    OCRImageError,
    OCRFormatNotSupportedError,
    OCRTimeoutError,
    OCRLowConfidenceError
)

try:
    texto = quick_ocr("imagem.png")
except OCRNotAvailableError:
    print("OCR não está disponível. Instale as dependências.")
except OCRImageError as e:
    print(f"Erro na imagem: {e}")
except OCREngineError as e:
    print(f"Erro no engine: {e}")
except OCRLowConfidenceError as e:
    print(f"Baixa confiança no resultado: {e}")
except OCRError as e:
    print(f"Erro geral de OCR: {e}")
```

### Tratamento Avançado de Erros

```python
from appserver_sdk_python_ai.ocr import OCRProcessor, OCREngine, EngineNotAvailableError

try:
    ocr = OCRProcessor(engine=OCREngine.TESSERACT)
    result = ocr.extract_text("documento.jpg")
    
    if result.confidence < 0.5:
        print("Aviso: Baixa confiança na extração")
        
except EngineNotAvailableError as e:
    print(f"Engine não disponível: {e}")
    # Fallback para outro engine
    ocr = OCRProcessor(engine=OCREngine.EASYOCR)
    result = ocr.extract_text("documento.jpg")
    
except OCRError as e:
    print(f"Erro no OCR: {e}")
    # Log do erro ou notificação
    
except FileNotFoundError:
    print("Arquivo não encontrado")
    
except Exception as e:
    print(f"Erro inesperado: {e}")
```

## 🧪 Testes

### Executar Testes

```bash
# Executar todos os testes
pytest tests/ocr/

# Executar testes específicos
pytest tests/ocr/test_ocr_processor.py

# Executar com cobertura
pytest tests/ocr/ --cov=appserver_sdk_python_ai.ocr
```

### Exemplo de Teste

```python
import pytest
from appserver_sdk_python_ai.ocr import OCRProcessor
from pathlib import Path

def test_ocr_basic_extraction():
    ocr = OCRProcessor()
    test_image = Path("tests/fixtures/sample_text.jpg")
    
    result = ocr.extract_text(test_image)
    
    assert result.text is not None
    assert len(result.text) > 0
    assert result.confidence > 0.0
    
def test_ocr_batch_processing():
    ocr = OCRProcessor()
    test_images = [
        "tests/fixtures/doc1.jpg",
        "tests/fixtures/doc2.png"
    ]
    
    results = ocr.extract_text_batch(test_images)
    
    assert len(results) == 2
    for result in results:
        assert result.text is not None
```

## 📈 Performance e Otimização

### Dicas de Performance

```python
# 1. Use cache para imagens repetidas
ocr = OCRProcessor(cache_enabled=True)

# 2. Processe em lote quando possível
results = ocr.extract_text_batch(image_list)

# 3. Configure workers para processamento paralelo
ocr = OCRProcessor(max_workers=4)

# 4. Use pré-processamento apenas quando necessário
preprocess_config = PreprocessingConfig(
    enhance_contrast=False,  # Desabilitar se não necessário
    denoise=False,
    deskew=True  # Manter apenas o essencial
)

# 5. Escolha o engine adequado para cada caso
# Tesseract: Documentos com texto limpo
# EasyOCR: Imagens naturais com texto
# PaddleOCR: Documentos complexos ou multilíngues
```

## 🎨 Pré-processamento de Imagem

O módulo inclui várias técnicas de pré-processamento para melhorar a qualidade do OCR:

- **Redimensionamento**: Aumenta a resolução para melhor reconhecimento
- **Remoção de Ruído**: Remove artefatos que podem confundir o OCR
- **Melhoria de Contraste**: Aumenta a diferença entre texto e fundo
- **Conversão para Escala de Cinza**: Simplifica o processamento
- **Binarização**: Converte para preto e branco puro

## 📈 Performance

### Dicas para Melhor Performance

1. **Use cache**: Habilite o cache para imagens processadas frequentemente
2. **Processamento em lote**: Use `batch_ocr` para múltiplas imagens
3. **Pré-processamento**: Configure adequadamente para seu tipo de imagem
4. **Engine apropriado**: Escolha o engine mais adequado para seu caso
5. **Resolução**: Imagens com DPI 300+ têm melhor precisão

### Benchmarks Típicos

| Engine | Velocidade | Precisão | Uso de Memória |
|--------|------------|----------|----------------|
| Tesseract | Médio | Alto | Baixo |
| EasyOCR | Lento | Alto | Alto |
| PaddleOCR | Rápido | Médio | Médio |

## 🔗 Integração com PDFs

Para processamento de PDFs com OCR, use as funções específicas que utilizam o Docling:

```python
from appserver_sdk_python_ai.ocr import (
    process_pdf_with_ocr,
    batch_process_pdfs
)

# Processar PDF único
resultado = process_pdf_with_ocr(
    pdf_path="documento.pdf",
    extract_images=True,
    extract_tables=True
)

# Processar múltiplos PDFs
resultados = batch_process_pdfs(
    pdf_paths=["doc1.pdf", "doc2.pdf"],
    output_dir="resultados",
    extract_images=True,
    extract_tables=True
)
```

## 🤝 Contribuição

Para contribuir com o módulo OCR:

1. **Fork** o repositório
2. **Clone** seu fork localmente
3. **Instale** as dependências de desenvolvimento:
   ```bash
   pip install -e ".[dev]"
   ```
4. **Execute** os testes:
   ```bash
   pytest tests/ocr/
   ```
5. **Implemente** suas mudanças
6. **Adicione** testes para novas funcionalidades
7. **Execute** o linting:
   ```bash
   flake8 src/appserver_sdk_python_ai/ocr/
   black src/appserver_sdk_python_ai/ocr/
   ```
8. **Submeta** um Pull Request

## 📄 Licença

Este módulo é parte do AppServer SDK Python AI e está licenciado sob os termos da licença do projeto principal.

## 🆘 Suporte

Para suporte e dúvidas:
- Abra uma **issue** no repositório
- Consulte a **documentação** completa
- Entre em contato com a **equipe de desenvolvimento**