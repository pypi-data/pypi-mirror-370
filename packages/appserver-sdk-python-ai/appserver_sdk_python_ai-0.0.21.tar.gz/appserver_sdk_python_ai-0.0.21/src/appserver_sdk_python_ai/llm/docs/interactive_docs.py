"""Documentação interativa para o módulo LLM.

Este módulo fornece acesso à documentação da API em tempo de desenvolvimento.
Pode ser usado diretamente em prompts de projetos que utilizam esta biblioteca.
A documentação é carregada dinamicamente do README.md do módulo.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any


class LLMDocumentation:
    """Classe para acessar documentação da API LLM em tempo de desenvolvimento."""

    @staticmethod
    def _get_readme_content() -> str:
        """Carrega o conteúdo do README.md do módulo LLM."""
        try:
            # Caminho para o README.md do módulo LLM
            current_dir = Path(__file__).parent.parent
            readme_path = current_dir / "README.md"

            if readme_path.exists():
                with open(readme_path, encoding="utf-8") as f:
                    return f.read()
            else:
                return "README.md não encontrado no módulo LLM."
        except Exception as e:
            return f"Erro ao carregar README.md: {e}"

    @staticmethod
    def get_quick_start_guide() -> str:
        """Retorna guia de início rápido extraído do README.md."""
        readme_content = LLMDocumentation._get_readme_content()

        # Extrair seção de uso rápido do README
        lines = readme_content.split("\n")
        quick_start_lines = []
        in_quick_start = False

        for line in lines:
            if "## 🔥 Uso Rápido" in line:
                in_quick_start = True
                quick_start_lines.append(
                    "🚀 GUIA DE INÍCIO RÁPIDO - AppServer SDK Python AI (LLM)"
                )
                quick_start_lines.append("=" * 60)
                continue
            elif in_quick_start and line.startswith("## "):
                break
            elif in_quick_start:
                quick_start_lines.append(line)

        if quick_start_lines:
            return "\n".join(quick_start_lines)
        else:
            return "Seção de uso rápido não encontrada no README.md"

    @staticmethod
    def get_full_documentation() -> str:
        """Retorna a documentação completa do README.md."""
        return LLMDocumentation._get_readme_content()

    @staticmethod
    def get_section(section_title: str) -> str:
        """Extrai uma seção específica do README.md."""
        readme_content = LLMDocumentation._get_readme_content()
        lines = readme_content.split("\n")
        section_lines = []
        in_section = False

        for line in lines:
            if section_title in line and line.startswith("#"):
                in_section = True
                section_lines.append(line)
                continue
            elif in_section and line.startswith("#") and not line.startswith("###"):
                break
            elif in_section:
                section_lines.append(line)

        return (
            "\n".join(section_lines)
            if section_lines
            else f"Seção '{section_title}' não encontrada."
        )

    @staticmethod
    def get_api_reference() -> dict[str, Any]:
        """Retorna referência da API extraída do README.md."""
        # Extrair informações da API do README
        api_section = LLMDocumentation.get_section("⚙️ Configuração Avançada")
        examples_section = LLMDocumentation.get_section("🔥 Uso Rápido")
        installation_section = LLMDocumentation.get_section(
            "📦 Instalação e Dependências"
        )

        return {
            "installation": installation_section,
            "configuration": api_section,
            "examples": examples_section,
            "full_docs": "Use get_full_documentation() para ver toda a documentação",
        }

    @staticmethod
    def get_examples() -> str:
        """Retorna exemplos práticos extraídos do README.md."""
        return LLMDocumentation.get_section("🎯 Casos de Uso Práticos")

    @staticmethod
    def get_troubleshooting() -> str:
        """Retorna guia de solução de problemas extraído do README.md."""
        return LLMDocumentation.get_section("🚨 Tratamento de Erros")

    @staticmethod
    def search_documentation(query: str) -> str:
        """Busca por um termo na documentação."""
        readme_content = LLMDocumentation._get_readme_content()
        lines = readme_content.split("\n")
        matching_lines = []

        for i, line in enumerate(lines):
            if query.lower() in line.lower():
                # Adicionar contexto (linha anterior e posterior)
                start = max(0, i - 1)
                end = min(len(lines), i + 2)
                context = lines[start:end]
                matching_lines.extend(context)
                matching_lines.append("---")

        if matching_lines:
            return "\n".join(matching_lines)
        else:
            return f"Termo '{query}' não encontrado na documentação."

    @staticmethod
    def get_available_sections() -> list[str]:
        """Retorna lista de seções disponíveis no README.md."""
        readme_content = LLMDocumentation._get_readme_content()
        lines = readme_content.split("\n")
        sections = []

        for line in lines:
            if line.startswith("## "):
                sections.append(line.replace("## ", "").strip())

        return sections


# Funções de conveniência para acesso rápido
def help_llm() -> str:
    """Ajuda rápida do módulo LLM."""
    return LLMDocumentation.get_quick_start_guide()


def docs_llm() -> str:
    """Documentação completa do módulo LLM."""
    return LLMDocumentation.get_full_documentation()


def search_llm_docs(query: str) -> str:
    """Busca na documentação do módulo LLM."""
    return LLMDocumentation.search_documentation(query)


def list_llm_sections() -> list[str]:
    """Lista seções disponíveis na documentação."""
    return LLMDocumentation.get_available_sections()


def get_llm_section(section_title: str) -> str:
    """Obtém uma seção específica da documentação."""
    return LLMDocumentation.get_section(section_title)
