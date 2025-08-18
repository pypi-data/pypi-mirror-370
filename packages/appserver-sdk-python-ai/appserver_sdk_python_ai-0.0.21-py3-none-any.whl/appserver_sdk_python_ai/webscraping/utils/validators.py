# appserver_sdk_python_ai/webscraping/utils/validators.py
"""
Validadores e utilitários para URLs e conteúdo.
"""

import ipaddress
import re
from urllib.parse import urljoin, urlparse

from appserver_sdk_python_ai.webscraping.exceptions import ValidationError


class URLValidator:
    """Validador de URLs para web scraping."""

    # Domínios comumente bloqueados para scraping
    BLOCKED_DOMAINS = {
        "localhost",
        "127.0.0.1",
        "0.0.0.0",
        "::1",
        "facebook.com",
        "www.facebook.com",
        "instagram.com",
        "www.instagram.com",
        "twitter.com",
        "www.twitter.com",
        "x.com",
        "www.x.com",
        "linkedin.com",
        "www.linkedin.com",
        "tiktok.com",
        "www.tiktok.com",
        "youtube.com",
        "www.youtube.com",
        "reddit.com",
        "www.reddit.com",
    }

    # Esquemas permitidos
    ALLOWED_SCHEMES = {"http", "https"}

    # Extensões de arquivo que não devem ser scrapadas
    BLOCKED_EXTENSIONS = {
        ".pdf",
        ".doc",
        ".docx",
        ".xls",
        ".xlsx",
        ".ppt",
        ".pptx",
        ".zip",
        ".rar",
        ".7z",
        ".tar",
        ".gz",
        ".jpg",
        ".jpeg",
        ".png",
        ".gif",
        ".bmp",
        ".svg",
        ".webp",
        ".mp3",
        ".mp4",
        ".avi",
        ".mov",
        ".wmv",
        ".flv",
        ".exe",
        ".msi",
        ".dmg",
        ".pkg",
    }

    @classmethod
    def validate_url(
        cls,
        url: str,
        allow_private: bool = False,
        custom_blocked: set[str] | None = None,
    ) -> bool:
        """
        Valida se uma URL é adequada para scraping.

        Args:
            url: URL a ser validada
            allow_private: Se deve permitir IPs privados
            custom_blocked: Conjunto adicional de domínios bloqueados

        Returns:
            bool: True se válida

        Raises:
            ValidationError: Se a URL for inválida
        """
        try:
            parsed = urlparse(url)

            # Verificar esquema
            if not parsed.scheme:
                raise ValidationError(
                    "URL deve ter esquema (http/https)", "scheme", url, url
                )

            if parsed.scheme.lower() not in cls.ALLOWED_SCHEMES:
                raise ValidationError(
                    f"Esquema não permitido: {parsed.scheme}",
                    "scheme",
                    parsed.scheme,
                    url,
                )

            # Verificar netloc
            if not parsed.netloc:
                raise ValidationError("URL deve ter domínio válido", "netloc", url, url)

            # Verificar extensões bloqueadas
            path = parsed.path.lower()
            for ext in cls.BLOCKED_EXTENSIONS:
                if path.endswith(ext):
                    raise ValidationError(
                        f"Extensão não suportada: {ext}", "extension", ext, url
                    )

            # Verificar domínios bloqueados
            domain = parsed.netloc.lower()

            blocked_domains = cls.BLOCKED_DOMAINS.copy()
            if custom_blocked:
                blocked_domains.update(custom_blocked)

            for blocked in blocked_domains:
                if blocked in domain:
                    raise ValidationError(
                        f"Domínio bloqueado: {blocked}", "domain", blocked, url
                    )

            # Verificar IPs privados se não permitido
            if not allow_private:
                cls._check_private_ip(parsed.netloc)

            return True

        except ValidationError:
            raise
        except Exception as e:
            raise ValidationError(f"URL inválida: {str(e)}", "url", url, url) from e

    @classmethod
    def _check_private_ip(cls, netloc: str):
        """Verifica se o netloc contém IP privado."""
        try:
            # Extrair IP se houver porta
            host = netloc.split(":")[0]

            # Tentar converter para IP
            ip = ipaddress.ip_address(host)

            if ip.is_private or ip.is_loopback:
                raise ValidationError(
                    f"IP privado/loopback não permitido: {host}", "ip", host
                )

        except ValueError:
            # Não é um IP, provavelmente um domínio
            pass

    @classmethod
    def normalize_url(cls, url: str, remove_tracking: bool = True) -> str:
        """
        Normaliza URL removendo parâmetros desnecessários.

        Args:
            url: URL original
            remove_tracking: Se deve remover parâmetros de tracking

        Returns:
            str: URL normalizada
        """
        try:
            parsed = urlparse(url)

            # Remover fragmentos
            normalized = parsed._replace(fragment="")

            # Remover parâmetros de tracking se solicitado
            if remove_tracking and normalized.query:
                tracking_params = {
                    "utm_source",
                    "utm_medium",
                    "utm_campaign",
                    "utm_term",
                    "utm_content",
                    "fbclid",
                    "gclid",
                    "msclkid",
                    "ref",
                    "source",
                    "_source",
                    "yclid",
                    "mc_cid",
                    "mc_eid",
                    "pk_source",
                    "pk_medium",
                    "pk_campaign",
                }

                params = []
                for param in normalized.query.split("&"):
                    if "=" in param:
                        param_name = param.split("=")[0].lower()
                        if param_name not in tracking_params:
                            params.append(param)
                    else:
                        params.append(param)

                normalized = normalized._replace(query="&".join(params))

            return normalized.geturl()

        except Exception:
            return url

    @classmethod
    def is_same_domain(cls, url1: str, url2: str) -> bool:
        """
        Verifica se duas URLs são do mesmo domínio.

        Args:
            url1: Primeira URL
            url2: Segunda URL

        Returns:
            bool: True se forem do mesmo domínio
        """
        try:
            domain1 = urlparse(url1).netloc.lower()
            domain2 = urlparse(url2).netloc.lower()

            # Remover www. para comparação
            domain1 = domain1.replace("www.", "", 1)
            domain2 = domain2.replace("www.", "", 1)

            return domain1 == domain2

        except Exception:
            return False

    @classmethod
    def extract_domain(cls, url: str) -> str:
        """
        Extrai o domínio de uma URL.

        Args:
            url: URL

        Returns:
            str: Domínio extraído
        """
        try:
            return urlparse(url).netloc.lower()
        except Exception:
            return ""

    @classmethod
    def is_absolute_url(cls, url: str) -> bool:
        """
        Verifica se a URL é absoluta.

        Args:
            url: URL a verificar

        Returns:
            bool: True se for absoluta
        """
        try:
            parsed = urlparse(url)
            return bool(parsed.netloc and parsed.scheme)
        except Exception:
            return False

    @classmethod
    def make_absolute_url(cls, url: str, base_url: str) -> str:
        """
        Converte URL relativa em absoluta.

        Args:
            url: URL que pode ser relativa
            base_url: URL base

        Returns:
            str: URL absoluta
        """
        try:
            if cls.is_absolute_url(url):
                return url
            return urljoin(base_url, url)
        except Exception:
            return url


class ContentValidator:
    """Validador de conteúdo extraído."""

    MIN_CONTENT_LENGTH = 100  # Mínimo de caracteres
    MIN_WORD_COUNT = 20  # Mínimo de palavras

    @classmethod
    def is_valid_content(
        cls,
        content: str,
        min_length: int | None = None,
        min_words: int | None = None,
    ) -> bool:
        """
        Valida se o conteúdo extraído é adequado.

        Args:
            content: Conteúdo a validar
            min_length: Comprimento mínimo (opcional)
            min_words: Número mínimo de palavras (opcional)

        Returns:
            bool: True se válido
        """
        if not content or not isinstance(content, str):
            return False

        content = content.strip()

        # Verificar comprimento
        min_len = min_length or cls.MIN_CONTENT_LENGTH
        if len(content) < min_len:
            return False

        # Verificar número de palavras
        words = content.split()
        min_word_count = min_words or cls.MIN_WORD_COUNT
        if len(words) < min_word_count:
            return False

        # Verificar se não é apenas espaços ou caracteres especiais
        clean_content = re.sub(r"[^\w\s]", "", content)
        if len(clean_content.strip()) < min_len * 0.5:
            return False

        return True

    @classmethod
    def detect_content_language(cls, content: str) -> str | None:
        """
        Detecta o idioma do conteúdo (implementação básica).

        Args:
            content: Conteúdo a analisar

        Returns:
            Optional[str]: Código do idioma detectado
        """
        if not content:
            return None

        # Palavras comuns em português
        portuguese_words = {
            "de",
            "da",
            "do",
            "das",
            "dos",
            "a",
            "o",
            "as",
            "os",
            "um",
            "uma",
            "e",
            "ou",
            "mas",
            "que",
            "para",
            "com",
            "em",
            "por",
            "é",
            "são",
            "foi",
            "está",
            "estão",
            "tem",
            "têm",
            "não",
            "sim",
            "mais",
            "muito",
        }

        # Palavras comuns em inglês
        english_words = {
            "the",
            "be",
            "to",
            "of",
            "and",
            "a",
            "in",
            "that",
            "have",
            "i",
            "it",
            "for",
            "not",
            "on",
            "with",
            "he",
            "as",
            "you",
            "do",
            "at",
            "this",
            "but",
            "his",
            "by",
            "from",
            "they",
        }

        # Palavras comuns em espanhol
        spanish_words = {
            "de",
            "la",
            "que",
            "el",
            "en",
            "y",
            "a",
            "es",
            "se",
            "no",
            "te",
            "lo",
            "le",
            "da",
            "su",
            "por",
            "son",
            "con",
            "para",
            "al",
            "del",
            "los",
            "las",
            "un",
            "una",
            "está",
            "están",
        }

        words = re.findall(r"\b\w+\b", content.lower())
        if not words:
            return None

        # Contar ocorrências
        pt_count = sum(1 for word in words if word in portuguese_words)
        en_count = sum(1 for word in words if word in english_words)
        es_count = sum(1 for word in words if word in spanish_words)

        total_words = len(words)

        # Calcular porcentagens
        pt_ratio = pt_count / total_words
        en_ratio = en_count / total_words
        es_ratio = es_count / total_words

        # Determinar idioma mais provável
        if pt_ratio > 0.1 and pt_ratio >= en_ratio and pt_ratio >= es_ratio:
            return "pt"
        elif en_ratio > 0.1 and en_ratio >= pt_ratio and en_ratio >= es_ratio:
            return "en"
        elif es_ratio > 0.1 and es_ratio >= pt_ratio and es_ratio >= en_ratio:
            return "es"

        return None

    @classmethod
    def calculate_readability_score(cls, content: str) -> float:
        """
        Calcula uma pontuação simples de legibilidade.

        Args:
            content: Conteúdo a analisar

        Returns:
            float: Pontuação de 0.0 a 1.0 (1.0 = mais legível)
        """
        if not content:
            return 0.0

        # Métricas básicas
        sentences = re.split(r"[.!?]+", content)
        sentences = [s.strip() for s in sentences if s.strip()]

        words = content.split()

        if not sentences or not words:
            return 0.0

        # Cálculos
        avg_sentence_length = len(words) / len(sentences)
        avg_word_length = sum(len(word) for word in words) / len(words)

        # Pontuação baseada em métricas ideais
        # Sentenças ideais: 15-20 palavras
        sentence_score = 1.0 - abs(avg_sentence_length - 17.5) / 17.5
        sentence_score = max(0.0, min(1.0, sentence_score))

        # Palavras ideais: 4-6 caracteres
        word_score = 1.0 - abs(avg_word_length - 5.0) / 5.0
        word_score = max(0.0, min(1.0, word_score))

        # Pontuação combinada
        return (sentence_score + word_score) / 2


class RobotsTxtChecker:
    """Verificador de robots.txt."""

    @classmethod
    def can_scrape_url(cls, url: str, user_agent: str = "*") -> bool:
        """
        Verifica se é permitido fazer scraping da URL baseado em robots.txt.

        Args:
            url: URL a verificar
            user_agent: User agent a verificar

        Returns:
            bool: True se permitido
        """
        try:
            from urllib.robotparser import RobotFileParser

            parsed_url = urlparse(url)
            robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"

            rp = RobotFileParser()
            rp.set_url(robots_url)
            rp.read()

            return rp.can_fetch(user_agent, url)

        except Exception:
            # Se não conseguir verificar, assumir que é permitido
            return True
