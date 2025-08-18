# appserver_sdk_python_ai/webscraping/utils/cleaner.py
"""
Utilitários para limpeza e processamento de conteúdo HTML.
"""

import logging
import re
from urllib.parse import urljoin

from bs4 import BeautifulSoup, Comment

from appserver_sdk_python_ai.webscraping.core.config import ScrapingConfig

logger = logging.getLogger(__name__)


class ContentCleaner:
    """Classe para limpeza de conteúdo HTML."""

    # Tags a serem removidas completamente
    REMOVE_TAGS = [
        "script",
        "style",
        "meta",
        "link",
        "noscript",
        "iframe",
        "object",
        "embed",
        "applet",
        "form",
        "input",
        "button",
        "select",
        "textarea",
        "nav",
        "header",
        "footer",
        "aside",
        "advertisement",
        "ads",
    ]

    # Atributos a manter para tags específicas
    KEEP_ATTRIBUTES = {
        "a": ["href", "title"],
        "img": ["src", "alt", "title", "width", "height"],
        "table": ["summary"],
        "th": ["scope"],
        "td": ["colspan", "rowspan"],
        "blockquote": ["cite"],
        "q": ["cite"],
        "video": ["src", "poster"],
        "audio": ["src"],
        "source": ["src", "type"],
    }

    # Classes e IDs comumente usados para conteúdo irrelevante
    NOISE_CLASSES = {
        "ad",
        "ads",
        "advertisement",
        "banner",
        "popup",
        "modal",
        "sidebar",
        "widget",
        "social",
        "share",
        "comment",
        "comments",
        "footer",
        "header",
        "navigation",
        "nav",
        "menu",
        "breadcrumb",
        "related",
        "recommended",
        "trending",
        "popular",
    }

    # Seletores CSS para remoção
    NOISE_SELECTORS = [
        ".advertisement",
        ".ads",
        ".ad",
        ".sidebar",
        ".widget",
        ".social-share",
        ".share-buttons",
        ".comments",
        ".comment-section",
        ".related-posts",
        ".recommended",
        '[id*="ad"]',
        '[class*="ad"]',
        '[id*="banner"]',
        '[class*="banner"]',
    ]

    @classmethod
    def clean_html(
        cls, html_content: str, base_url: str, config: ScrapingConfig
    ) -> str:
        """
        Limpa conteúdo HTML removendo elementos desnecessários.

        Args:
            html_content: Conteúdo HTML original
            base_url: URL base para resolver links relativos
            config: Configurações de scraping

        Returns:
            str: HTML limpo
        """
        try:
            soup = BeautifulSoup(html_content, "lxml")

            # Remover comentários
            cls._remove_comments(soup)

            # Remover tags desnecessárias
            cls._remove_unwanted_tags(soup)

            # Remover elementos com classes/IDs de ruído
            cls._remove_noise_elements(soup)

            # Limpar atributos
            cls._clean_attributes(soup)

            # Resolver URLs relativos
            if config.include_links or config.include_images:
                cls._resolve_relative_urls(soup, base_url, config)

            # Remover elementos baseado na configuração
            if not config.include_images:
                cls._remove_images(soup)

            if not config.include_links:
                cls._remove_links(soup)

            # Remover tags vazias
            cls._remove_empty_tags(soup)

            # Limpar texto
            cls._clean_text_content(soup)

            return str(soup)

        except Exception as e:
            logger.warning(f"Erro na limpeza do HTML: {e}")
            return html_content

    @classmethod
    def _remove_comments(cls, soup: BeautifulSoup):
        """Remove comentários HTML."""
        comments = soup.find_all(string=lambda text: isinstance(text, Comment))
        for comment in comments:
            comment.extract()

    @classmethod
    def _remove_unwanted_tags(cls, soup: BeautifulSoup):
        """Remove tags indesejadas."""
        for tag_name in cls.REMOVE_TAGS:
            for tag in soup.find_all(tag_name):
                tag.decompose()

    @classmethod
    def _remove_noise_elements(cls, soup: BeautifulSoup):
        """Remove elementos com classes/IDs de ruído."""
        # Remover por seletores CSS
        for selector in cls.NOISE_SELECTORS:
            try:
                for element in soup.select(selector):
                    element.decompose()
            except Exception as e:
                logger.debug(f"Erro ao aplicar seletor {selector}: {e}")

        # Remover por classes de ruído
        for element in soup.find_all():  # type: ignore
            element_classes = element.get("class")
            if element_classes:
                classes = [c.lower() for c in element_classes if isinstance(c, str)]
                if any(noise in " ".join(classes) for noise in cls.NOISE_CLASSES):
                    element.decompose()  # type: ignore
                    continue

            element_id = element.get("id")
            if element_id and isinstance(element_id, str):
                element_id_lower = element_id.lower()
                if any(noise in element_id_lower for noise in cls.NOISE_CLASSES):
                    element.decompose()  # type: ignore

    @classmethod
    def _clean_attributes(cls, soup: BeautifulSoup):
        """Limpa atributos dos elementos."""
        for tag in soup.find_all():
            if tag.name in cls.KEEP_ATTRIBUTES:  # type: ignore
                allowed_attrs = cls.KEEP_ATTRIBUTES[tag.name]  # type: ignore
                tag.attrs = {k: v for k, v in tag.attrs.items() if k in allowed_attrs}  # type: ignore
            else:
                # Para outros elementos, manter apenas atributos essenciais
                essential_attrs = []
                if tag.name in [  # type: ignore
                    "div",
                    "span",
                    "section",
                    "article",
                    "p",
                    "h1",
                    "h2",
                    "h3",
                    "h4",
                    "h5",
                    "h6",
                ]:
                    essential_attrs = ["id", "class"]

                tag.attrs = {k: v for k, v in tag.attrs.items() if k in essential_attrs}  # type: ignore

    @classmethod
    def _resolve_relative_urls(
        cls, soup: BeautifulSoup, base_url: str, config: ScrapingConfig
    ):
        """Resolve URLs relativos."""
        if config.include_links:
            for link in soup.find_all("a", href=True):
                link["href"] = urljoin(base_url, link["href"])  # type: ignore

        if config.include_images:
            for img in soup.find_all("img", src=True):
                img["src"] = urljoin(base_url, img["src"])  # type: ignore

    @classmethod
    def _remove_images(cls, soup: BeautifulSoup):
        """Remove todas as imagens."""
        for img in soup.find_all(["img", "picture", "figure"]):
            img.decompose()

    @classmethod
    def _remove_links(cls, soup: BeautifulSoup):
        """Remove links mas mantém o texto."""
        for link in soup.find_all("a"):
            link.unwrap()  # type: ignore

    @classmethod
    def _remove_empty_tags(cls, soup: BeautifulSoup):
        """Remove tags vazias recursivamente."""
        # Tags que são naturalmente vazias
        self_closing_tags = {
            "br",
            "hr",
            "img",
            "input",
            "meta",
            "link",
            "area",
            "base",
            "col",
            "embed",
            "source",
            "track",
            "wbr",
        }

        # Múltiplas passadas para remover tags aninhadas vazias
        for _ in range(3):
            empty_tags = soup.find_all(
                lambda tag: tag.name not in self_closing_tags
                and not tag.get_text(strip=True)
                and not tag.find_all(self_closing_tags)
                and len(tag.find_all()) == 0
            )

            if not empty_tags:
                break

            for tag in empty_tags:
                tag.decompose()

    @classmethod
    def _clean_text_content(cls, soup: BeautifulSoup):
        """Limpa o conteúdo de texto."""
        # Normalizar espaços em branco
        for element in soup.find_all(string=True):
            if element.parent.name not in ["script", "style", "pre", "code"]:  # type: ignore
                # Normalizar espaços múltiplos
                cleaned_text = re.sub(r"\s+", " ", str(element))
                element.replace_with(cleaned_text)  # type: ignore

    @classmethod
    def extract_main_content(cls, soup: BeautifulSoup) -> BeautifulSoup:
        """
        Extrai o conteúdo principal da página.

        Args:
            soup: BeautifulSoup object

        Returns:
            BeautifulSoup: Conteúdo principal extraído
        """
        # Tentar diferentes estratégias para encontrar conteúdo principal
        main_content_selectors = [
            "main",
            "article",
            '[role="main"]',
            ".main-content",
            ".content",
            ".post-content",
            ".entry-content",
            ".article-content",
            "#main",
            "#content",
            "#post-content",
        ]

        for selector in main_content_selectors:
            try:
                main_element = soup.select_one(selector)
                if main_element and main_element.get_text(strip=True):
                    logger.info(
                        f"Conteúdo principal encontrado usando seletor: {selector}"
                    )
                    return main_element  # type: ignore
            except Exception as e:
                logger.debug(f"Erro ao aplicar seletor {selector}: {e}")

        # Se não encontrar conteúdo principal específico, tentar body
        body = soup.find("body")
        if body:
            return body  # type: ignore

        # Último recurso: retornar todo o soup
        return soup

    @classmethod
    def calculate_content_density(cls, element) -> float:
        """
        Calcula a densidade de conteúdo de um elemento.
        Útil para identificar conteúdo principal vs navegação/ads.

        Args:
            element: Elemento BeautifulSoup

        Returns:
            float: Densidade de conteúdo (0.0 a 1.0)
        """
        try:
            text_length = len(element.get_text(strip=True))
            if text_length == 0:
                return 0.0

            # Contar links e elementos de navegação
            links = element.find_all("a")
            nav_elements = element.find_all(["nav", "menu"])

            link_text_length = sum(len(link.get_text(strip=True)) for link in links)
            nav_text_length = sum(len(nav.get_text(strip=True)) for nav in nav_elements)

            # Calcular densidade
            content_text_length = text_length - link_text_length - nav_text_length
            density = max(0.0, content_text_length / text_length)

            return min(1.0, density)

        except Exception:
            return 0.0

    @classmethod
    def remove_low_quality_content(
        cls, soup: BeautifulSoup, min_density: float = 0.3
    ) -> BeautifulSoup:
        """
        Remove elementos com baixa densidade de conteúdo.

        Args:
            soup: BeautifulSoup object
            min_density: Densidade mínima para manter o elemento

        Returns:
            BeautifulSoup: Soup com conteúdo de baixa qualidade removido
        """
        # Elementos a verificar
        check_elements = soup.find_all(["div", "section", "aside"])

        for element in check_elements:
            density = cls.calculate_content_density(element)
            if density < min_density and len(element.get_text(strip=True)) < 200:
                logger.debug(f"Removendo elemento com baixa densidade: {density:.2f}")
                element.decompose()

        return soup
