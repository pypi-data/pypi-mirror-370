"""Documentação interativa para o módulo LLM."""

from .interactive_docs import (
    LLMDocumentation,
    docs_llm,
    get_llm_section,
    help_llm,
    list_llm_sections,
    search_llm_docs,
)

# Aliases para facilitar o uso
docs = docs_llm
help = help_llm
search = search_llm_docs

__all__ = [
    "LLMDocumentation",
    "help_llm",
    "docs_llm",
    "search_llm_docs",
    "list_llm_sections",
    "get_llm_section",
    "help",
    "docs",
    "search",
]
