# appserver_sdk_python_ai/ocr/processor.py
"""
Processador principal de OCR
===========================

Este módulo implementa o processador de OCR que suporta múltiplos engines
para extração de texto de imagens.
"""

import hashlib
import logging
import os
import time
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import TimeoutError as FutureTimeoutError
from pathlib import Path
from typing import Any

from appserver_sdk_python_ai.ocr.core.config import (
    DEFAULT_OCR_CONFIG,
    OCRConfig,
    OCREngine,
)
from appserver_sdk_python_ai.ocr.exceptions import (
    OCREngineError,
    OCRError,
    OCRFormatNotSupportedError,
    OCRImageError,
    OCRLowConfidenceError,
    OCRNotAvailableError,
    OCRTimeoutError,
)

# Configurar logging
logger = logging.getLogger(__name__)


class OCRResult:
    """Resultado do processamento de OCR."""

    def __init__(
        self,
        text: str,
        confidence: float,
        engine: str,
        processing_time: float,
        file_path: str | None = None,
        metadata: dict[str, Any] | None = None,
    ):
        self.text = text
        self.confidence = confidence
        self.engine = engine
        self.processing_time = processing_time
        self.file_path = file_path
        self.metadata = metadata or {}
        self._cached_at: float | None = None

    def __str__(self) -> str:
        return f"OCRResult(engine={self.engine}, confidence={self.confidence:.2f}, chars={len(self.text)})"

    def to_dict(self) -> dict[str, Any]:
        """Converte resultado para dicionário."""
        return {
            "text": self.text,
            "confidence": self.confidence,
            "engine": self.engine,
            "processing_time": self.processing_time,
            "file_path": self.file_path,
            "metadata": self.metadata,
        }


class OCRProcessor:
    """Processador principal de OCR."""

    def __init__(self, config: OCRConfig | None = None):
        self.config = config or DEFAULT_OCR_CONFIG
        self._cache: dict[str, OCRResult] = {}
        self._available_engines = self._detect_available_engines()

        if not self._available_engines:
            raise OCRNotAvailableError(
                "Nenhuma biblioteca de OCR está disponível. "
                "Instale pelo menos uma: pytesseract, easyocr, paddleocr"
            )

        logger.info(f"OCRProcessor inicializado com engines: {self._available_engines}")

    def _detect_available_engines(self) -> list[str]:
        """Detecta engines de OCR disponíveis."""
        available = []

        # Tesseract
        try:
            import importlib.util

            if importlib.util.find_spec("pytesseract") and importlib.util.find_spec(
                "PIL"
            ):
                available.append(OCREngine.TESSERACT.value)
        except ImportError:
            logger.debug("Tesseract não disponível")

        # EasyOCR
        try:
            import importlib.util

            if importlib.util.find_spec("easyocr"):
                available.append(OCREngine.EASYOCR.value)
        except ImportError:
            logger.debug("EasyOCR não disponível")

        # PaddleOCR
        try:
            import importlib.util

            if importlib.util.find_spec("paddleocr"):
                available.append(OCREngine.PADDLEOCR.value)
        except ImportError:
            logger.debug("PaddleOCR não disponível")

        return available

    def _get_cache_key(self, file_path: str, config_hash: str) -> str:
        """Gera chave de cache para arquivo e configuração."""
        file_stat = os.stat(file_path)
        file_info = f"{file_path}_{file_stat.st_mtime}_{file_stat.st_size}"
        return hashlib.md5(f"{file_info}_{config_hash}".encode()).hexdigest()

    def _get_config_hash(self) -> str:
        """Gera hash da configuração atual."""
        config_str = f"{self.config.engine.value}_{self.config.languages}_{self.config.tesseract_config}"
        return hashlib.md5(config_str.encode()).hexdigest()

    def _is_cache_valid(self, cache_key: str) -> bool:
        """Verifica se entrada do cache ainda é válida."""
        if not self.config.enable_cache or cache_key not in self._cache:
            return False

        result = self._cache[cache_key]
        cached_at = getattr(result, "_cached_at", None)
        if cached_at is not None:
            return bool((time.time() - cached_at) < self.config.cache_ttl)

        return False

    def _select_engine(self) -> str:
        """Seleciona engine de OCR baseado na configuração."""
        if self.config.engine == OCREngine.AUTO:
            # Prioridade: Tesseract > EasyOCR > PaddleOCR
            for preferred in [
                OCREngine.TESSERACT.value,
                OCREngine.EASYOCR.value,
                OCREngine.PADDLEOCR.value,
            ]:
                if preferred in self._available_engines:
                    return str(preferred)

        engine_value = self.config.engine.value
        if engine_value not in self._available_engines:
            raise OCREngineError(
                f"Engine '{engine_value}' não está disponível. "
                f"Engines disponíveis: {self._available_engines}",
                engine_value,
            )

        return str(engine_value)

    def _preprocess_image(self, image_path: str) -> str:
        """Pré-processa imagem para melhorar OCR."""
        if not self.config.preprocess_image:
            return image_path

        try:
            from PIL import Image, ImageEnhance, ImageFilter

            with Image.open(image_path) as img:
                # Converter para RGB se necessário
                if img.mode != "RGB":
                    img = img.convert("RGB")

                # Redimensionar
                if self.config.resize_factor != 1.0:
                    new_size = (
                        int(img.width * self.config.resize_factor),
                        int(img.height * self.config.resize_factor),
                    )
                    img = img.resize(new_size, Image.Resampling.LANCZOS)

                # Melhorar contraste
                if self.config.enhance_contrast:
                    enhancer = ImageEnhance.Contrast(img)
                    img = enhancer.enhance(1.5)

                # Reduzir ruído
                if self.config.denoise:
                    img = img.filter(ImageFilter.MedianFilter(size=3))

                # Salvar imagem processada temporariamente
                temp_path = f"{image_path}_processed.png"
                img.save(temp_path, "PNG")
                return temp_path

        except Exception as e:
            logger.warning(f"Erro no pré-processamento da imagem: {e}")
            return image_path

    def _process_with_tesseract(self, image_path: str) -> OCRResult:
        """Processa imagem com Tesseract."""
        try:
            import pytesseract
            from PIL import Image

            start_time = time.time()

            # Configurar idiomas
            lang = self.config.get_tesseract_languages()

            # Processar imagem
            with Image.open(image_path) as img:
                # Extrair texto com dados de confiança
                data = pytesseract.image_to_data(
                    img,
                    lang=lang,
                    config=self.config.tesseract_config,
                    timeout=self.config.tesseract_timeout,
                    output_type=pytesseract.Output.DICT,
                )

                # Extrair texto simples
                text = pytesseract.image_to_string(
                    img,
                    lang=lang,
                    config=self.config.tesseract_config,
                    timeout=self.config.tesseract_timeout,
                )

                # Calcular confiança média
                confidences = [int(conf) for conf in data["conf"] if int(conf) > 0]
                avg_confidence = (
                    sum(confidences) / len(confidences) if confidences else 0
                )
                confidence = avg_confidence / 100.0  # Normalizar para 0-1

            processing_time = time.time() - start_time

            return OCRResult(
                text=text.strip(),
                confidence=confidence,
                engine="tesseract",
                processing_time=processing_time,
                file_path=image_path,
                metadata={"raw_data": data},
            )

        except Exception as e:
            raise OCREngineError(f"Erro no Tesseract: {str(e)}", "tesseract", e) from e

    def _process_with_easyocr(self, image_path: str) -> OCRResult:
        """Processa imagem com EasyOCR."""
        try:
            import easyocr

            start_time = time.time()

            # Inicializar reader
            languages = self.config.get_easyocr_languages()
            reader = easyocr.Reader(
                languages,
                gpu=self.config.easyocr_gpu,
                model_storage_directory=self.config.easyocr_model_storage_directory,
            )

            # Processar imagem
            results = reader.readtext(image_path)

            # Extrair texto e confiança
            texts = []
            confidences = []

            for _bbox, text, confidence in results:
                texts.append(text)
                confidences.append(confidence)

            full_text = "\n".join(texts)
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0

            processing_time = time.time() - start_time

            return OCRResult(
                text=full_text,
                confidence=avg_confidence,
                engine="easyocr",
                processing_time=processing_time,
                file_path=image_path,
                metadata={"raw_results": results},
            )

        except Exception as e:
            raise OCREngineError(f"Erro no EasyOCR: {str(e)}", "easyocr", e) from e

    def _process_with_paddleocr(self, image_path: str) -> OCRResult:
        """Processa imagem com PaddleOCR."""
        try:
            from paddleocr import PaddleOCR

            start_time = time.time()

            # Inicializar OCR
            ocr = PaddleOCR(
                use_angle_cls=self.config.paddleocr_use_angle_cls,
                lang=self.config.paddleocr_lang,
                use_gpu=self.config.paddleocr_use_gpu,
                show_log=False,
            )

            # Processar imagem
            results = ocr.ocr(image_path, cls=self.config.paddleocr_use_angle_cls)

            # Extrair texto e confiança
            texts = []
            confidences = []

            if results and results[0]:
                for line in results[0]:
                    if line:
                        bbox, (text, confidence) = line
                        texts.append(text)
                        confidences.append(confidence)

            full_text = "\n".join(texts)
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0

            processing_time = time.time() - start_time

            return OCRResult(
                text=full_text,
                confidence=avg_confidence,
                engine="paddleocr",
                processing_time=processing_time,
                file_path=image_path,
                metadata={"raw_results": results},
            )

        except Exception as e:
            raise OCREngineError(f"Erro no PaddleOCR: {str(e)}", "paddleocr", e) from e

    def _clean_text(self, text: str) -> str:
        """Limpa e normaliza texto extraído."""
        if not self.config.clean_text:
            return text

        # Remover espaços extras
        if self.config.remove_extra_whitespace:
            import re

            text = re.sub(r"\s+", " ", text)
            text = re.sub(r"\n\s*\n", "\n\n", text)

        return text.strip()

    # def extract_text_from_image(
    #     self, image_path: str | Path, engine: OCREngine | None = None
    # ) -> OCRResult:
    #     """Extrai texto de uma imagem usando OCR.

    #     Args:
    #         image_path: Caminho para a imagem
    #         engine: Engine específico para usar (opcional)

    #     Returns:
    #         OCRResult com texto extraído e metadados

    #     Raises:
    #         OCRImageError: Erro no processamento da imagem
    #         OCRFormatNotSupportedError: Formato não suportado
    #         OCRTimeoutError: Timeout no processamento
    #         OCRLowConfidenceError: Confiança abaixo do mínimo
    #     """
    #     image_path = str(image_path)

    #     # Verificar se arquivo existe
    #     if not os.path.exists(image_path):
    #         raise OCRImageError(f"Arquivo não encontrado: {image_path}", image_path)

    #     # Verificar formato
    #     file_ext = Path(image_path).suffix.lower().lstrip(".")
    #     if not self.config.is_format_supported(file_ext):
    #         raise OCRFormatNotSupportedError(image_path, file_ext)

    #     # Verificar cache
    #     config_hash = self._get_config_hash()
    #     cache_key = self._get_cache_key(image_path, config_hash)

    #     if self._is_cache_valid(cache_key):
    #         logger.debug(f"Resultado encontrado no cache para {image_path}")
    #         return self._cache[cache_key]

    #     # Selecionar engine
    #     selected_engine = engine.value if engine else self._select_engine()

    #     try:
    #         # Pré-processar imagem
    #         processed_path = self._preprocess_image(image_path)

    #         # Processar com timeout
    #         with ThreadPoolExecutor(max_workers=1) as executor:
    #             if selected_engine == "tesseract":
    #                 future = executor.submit(
    #                     self._process_with_tesseract, processed_path
    #                 )
    #             elif selected_engine == "easyocr":
    #                 future = executor.submit(self._process_with_easyocr, processed_path)
    #             elif selected_engine == "paddleocr":
    #                 future = executor.submit(
    #                     self._process_with_paddleocr, processed_path
    #                 )
    #             else:
    #                 raise OCREngineError(
    #                     f"Engine não suportado: {selected_engine}", selected_engine
    #                 )

    #             try:
    #                 result = future.result(timeout=self.config.processing_timeout)
    #             except FutureTimeoutError as timeout_err:
    #                 raise OCRTimeoutError(
    #                     image_path, self.config.processing_timeout, selected_engine
    #                 ) from timeout_err

    #         # Limpar arquivo temporário se foi criado
    #         if processed_path != image_path and os.path.exists(processed_path):
    #             try:
    #                 os.remove(processed_path)
    #             except OSError:
    #                 pass

    #         # Limpar texto
    #         result.text = self._clean_text(result.text)

    #         # Verificar confiança mínima
    #         if result.confidence < self.config.min_confidence:
    #             raise OCRLowConfidenceError(
    #                 image_path,
    #                 result.confidence,
    #                 self.config.min_confidence,
    #                 selected_engine,
    #             )

    #         # Armazenar no cache
    #         if self.config.enable_cache:
    #             setattr(result, "_cached_at", time.time())
    #             self._cache[cache_key] = result

    #         logger.info(
    #             f"OCR concluído: {image_path} | Engine: {selected_engine} | "
    #             f"Confiança: {result.confidence:.2f} | Tempo: {result.processing_time:.2f}s"
    #         )

    #         return result

    #     except (OCRError, OCREngineError, OCRTimeoutError, OCRLowConfidenceError):
    #         raise
    #     except Exception as e:
    #         raise OCRImageError(
    #             f"Erro inesperado no processamento: {str(e)}", image_path, e
    #         ) from e

    def extract_text_from_image(
        self, image_path: str | Path, engine: OCREngine | None = None
    ) -> OCRResult:
        """Extrai texto de uma imagem usando OCR.

        Args:
            image_path: Caminho para a imagem
            engine: Engine específico para usar (opcional)

        Returns:
            OCRResult com texto extraído e metadados

        Raises:
            OCRImageError: Erro no processamento da imagem
            OCRFormatNotSupportedError: Formato não suportado
            OCRTimeoutError: Timeout no processamento
            OCRLowConfidenceError: Confiança abaixo do mínimo
        """
        image_path = str(image_path)

        # Verificar se arquivo existe
        if not os.path.exists(image_path):
            raise OCRImageError(f"Arquivo não encontrado: {image_path}", image_path)

        # Verificar formato
        file_ext = Path(image_path).suffix.lower().lstrip(".")
        if not self.config.is_format_supported(file_ext):
            raise OCRFormatNotSupportedError(image_path, file_ext)

        # Verificar cache
        config_hash = self._get_config_hash()
        cache_key = self._get_cache_key(image_path, config_hash)

        if self._is_cache_valid(cache_key):
            logger.debug(f"Resultado encontrado no cache para {image_path}")
            return self._cache[cache_key]

        # Selecionar engine
        selected_engine = engine.value if engine else self._select_engine()

        try:
            # Pré-processar imagem
            processed_path = self._preprocess_image(image_path)

            # Processar com timeout
            with ThreadPoolExecutor(max_workers=1) as executor:
                if selected_engine == "tesseract":
                    future = executor.submit(
                        self._process_with_tesseract, processed_path
                    )
                elif selected_engine == "easyocr":
                    future = executor.submit(self._process_with_easyocr, processed_path)
                elif selected_engine == "paddleocr":
                    future = executor.submit(
                        self._process_with_paddleocr, processed_path
                    )
                else:
                    raise OCREngineError(
                        f"Engine não suportado: {selected_engine}", selected_engine
                    )

                try:
                    result = future.result(timeout=self.config.processing_timeout)
                except FutureTimeoutError as timeout_err:
                    raise OCRTimeoutError(
                        image_path, self.config.processing_timeout, selected_engine
                    ) from timeout_err

            # Limpar arquivo temporário se foi criado
            if processed_path != image_path and os.path.exists(processed_path):
                try:
                    os.remove(processed_path)
                except OSError:
                    logger.debug(
                        f"Não foi possível remover arquivo temporário: {processed_path}",
                        exc_info=True,
                    )

            # Limpar texto
            result.text = self._clean_text(result.text)

            # Verificar confiança mínima
            if result.confidence < self.config.min_confidence:
                raise OCRLowConfidenceError(
                    image_path,
                    result.confidence,
                    self.config.min_confidence,
                    selected_engine,
                )

            # Armazenar no cache (atribuição direta do timestamp — MyPy-friendly)
            if self.config.enable_cache:
                result._cached_at = time.time()
                self._cache[cache_key] = result

            logger.info(
                f"OCR concluído: {image_path} | Engine: {selected_engine} | "
                f"Confiança: {result.confidence:.2f} | Tempo: {result.processing_time:.2f}s"
            )

            return result

        except (OCRError, OCREngineError, OCRTimeoutError, OCRLowConfidenceError):
            raise
        except Exception as e:
            raise OCRImageError(
                f"Erro inesperado no processamento: {str(e)}", image_path, e
            ) from e

    def extract_text_from_images(
        self, image_paths: list[str | Path], engine: OCREngine | None = None
    ) -> list[OCRResult]:
        """Extrai texto de múltiplas imagens em paralelo.

        Args:
            image_paths: Lista de caminhos para imagens
            engine: Engine específico para usar (opcional)

        Returns:
            Lista de OCRResult para cada imagem
        """
        results = []

        # Processar em lotes
        for i in range(0, len(image_paths), self.config.batch_size):
            batch = image_paths[i : i + self.config.batch_size]

            with ThreadPoolExecutor(max_workers=self.config.max_workers) as executor:
                futures = {
                    executor.submit(self.extract_text_from_image, path, engine): path
                    for path in batch
                }

                for future in futures:
                    try:
                        result = future.result()
                        results.append(result)
                    except Exception as e:
                        # Criar resultado de erro
                        error_result = OCRResult(
                            text="",
                            confidence=0.0,
                            engine="error",
                            processing_time=0.0,
                            file_path=str(futures[future]),
                            metadata={"error": str(e)},
                        )
                        results.append(error_result)
                        logger.error(f"Erro ao processar {futures[future]}: {e}")

        return results

    def get_available_engines(self) -> list[str]:
        """Retorna lista de engines disponíveis."""
        return self._available_engines.copy()

    def clear_cache(self) -> None:
        """Limpa cache de resultados."""
        self._cache.clear()
        logger.info("Cache de OCR limpo")
