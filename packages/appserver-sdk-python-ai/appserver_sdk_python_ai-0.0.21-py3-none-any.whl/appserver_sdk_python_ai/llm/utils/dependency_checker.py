"""Utilitário para verificação de dependências do módulo LLM."""

import importlib
import sys
from typing import Any

from packaging import version


class DependencyChecker:
    """Verificador de dependências para o módulo LLM."""

    # Dependências principais obrigatórias
    REQUIRED_DEPENDENCIES = {
        "pydantic": "2.0.0",
        "httpx": "0.24.0",
        "structlog": "23.0.0",
        "psutil": "5.9.0",
        "typing_extensions": "4.0.0",
    }

    # Dependências opcionais por categoria
    OPTIONAL_DEPENDENCIES = {
        "analysis": {
            "pandas": "1.5.0",
            "matplotlib": "3.5.0",
            "seaborn": "0.11.0",
            "nltk": "3.8.0",
            "spacy": "3.4.0",
            "textblob": "0.17.0",
        },
        "local_models": {
            "transformers": "4.20.0",
            "torch": "1.12.0",
            "llama_cpp_python": "0.2.0",
            "onnxruntime": "1.12.0",
        },
        "dev": {
            "pytest": "7.0.0",
            "pytest_asyncio": "0.21.0",
            "pytest_cov": "4.0.0",
            "ruff": "0.1.0",
            "mypy": "1.0.0",
        },
        "docs": {"mkdocs": "1.4.0", "mkdocs_material": "8.5.0"},
    }

    def __init__(self):
        self.results = {
            "required": {},
            "optional": {},
            "missing": [],
            "outdated": [],
            "errors": [],
        }

    def _check_package(
        self, package_name: str, min_version: str | None = None
    ) -> dict[str, Any]:
        """Verifica se um pacote está instalado e sua versão.

        Args:
            package_name: Nome do pacote
            min_version: Versão mínima requerida

        Returns:
            Dict com informações do pacote
        """
        result = {
            "name": package_name,
            "installed": False,
            "version": None,
            "min_version": min_version,
            "compatible": False,
            "error": None,
        }

        try:
            # Tentar importar o módulo
            module = importlib.import_module(package_name)
            result["installed"] = True

            # Obter versão
            pkg_version = getattr(module, "__version__", None)
            if pkg_version:
                result["version"] = pkg_version

                # Verificar compatibilidade de versão
                if min_version:
                    try:
                        if version.parse(pkg_version) >= version.parse(min_version):
                            result["compatible"] = True
                        else:
                            result["compatible"] = False
                    except Exception as e:
                        result["error"] = f"Erro ao comparar versões: {e}"
                        result["compatible"] = None
                else:
                    result["compatible"] = True
            else:
                result["version"] = "unknown"
                result["compatible"] = None

        except ImportError:
            result["installed"] = False
            result["error"] = f"Pacote '{package_name}' não encontrado"
        except Exception as e:
            result["installed"] = False
            result["error"] = f"Erro ao verificar '{package_name}': {e}"

        return result

    def check_required_dependencies(self) -> dict[str, Any]:
        """Verifica todas as dependências obrigatórias.

        Returns:
            Dict com resultados da verificação
        """
        print("🔍 Verificando dependências obrigatórias...")

        for package, min_ver in self.REQUIRED_DEPENDENCIES.items():
            result = self._check_package(package, min_ver)
            self.results["required"][package] = result

            if not result["installed"]:
                self.results["missing"].append(package)
                print(f"❌ {package}: não instalado")
            elif result["compatible"] is False:
                self.results["outdated"].append(
                    {
                        "package": package,
                        "current": result["version"],
                        "required": min_ver,
                    }
                )
                print(f"⚠️  {package}: {result['version']} (requer >= {min_ver})")
            elif result["compatible"] is True:
                print(f"✅ {package}: {result['version']}")
            else:
                print(f"❓ {package}: {result['version']} (versão não verificável)")

        return dict(self.results["required"])

    def check_optional_dependencies(
        self, categories: list[str] | None = None
    ) -> dict[str, Any]:
        """Verifica dependências opcionais por categoria.

        Args:
            categories: Lista de categorias para verificar (None = todas)

        Returns:
            Dict com resultados da verificação
        """
        if categories is None:
            categories = list(self.OPTIONAL_DEPENDENCIES.keys())

        print("\n🔍 Verificando dependências opcionais...")

        for category in categories:
            if category not in self.OPTIONAL_DEPENDENCIES:
                print(f"⚠️  Categoria '{category}' não encontrada")
                continue

            print(f"\n📦 Categoria: {category}")
            self.results["optional"][category] = {}

            for package, min_ver in self.OPTIONAL_DEPENDENCIES[category].items():
                result = self._check_package(package, min_ver)
                self.results["optional"][category][package] = result

                if not result["installed"]:
                    print(f"❌ {package}: não instalado")
                elif result["compatible"] is False:
                    print(f"⚠️  {package}: {result['version']} (requer >= {min_ver})")
                elif result["compatible"] is True:
                    print(f"✅ {package}: {result['version']}")
                else:
                    print(f"❓ {package}: {result['version']} (versão não verificável)")

        return dict(self.results["optional"])

    def get_installation_commands(self) -> dict[str, list[str] | dict[str, str]]:
        """Gera comandos de instalação para dependências faltando.

        Returns:
            Dict com comandos de instalação
        """
        commands: dict[str, list[str] | dict[str, str]] = {
            "required": [],
            "optional": {},
        }

        # Comandos para dependências obrigatórias
        if self.results["missing"]:
            missing_packages = []
            for package in self.results["missing"]:
                min_ver = self.REQUIRED_DEPENDENCIES.get(package)
                if min_ver:
                    missing_packages.append(f"{package}>={min_ver}")
                else:
                    missing_packages.append(package)

            if missing_packages:
                if isinstance(commands["required"], list):
                    commands["required"].append(
                        f"pip install {' '.join(missing_packages)}"
                    )

        # Comandos para dependências desatualizadas
        if self.results["outdated"]:
            outdated_packages = []
            for item in self.results["outdated"]:
                package = item["package"]
                min_ver = item["required"]
                outdated_packages.append(f"{package}>={min_ver}")

            if outdated_packages:
                if isinstance(commands["required"], list):
                    commands["required"].append(
                        f"pip install --upgrade {' '.join(outdated_packages)}"
                    )

        # Comandos para dependências opcionais
        for category, packages in self.results["optional"].items():
            missing_optional = []
            for package, result in packages.items():
                if not result["installed"]:
                    min_ver = self.OPTIONAL_DEPENDENCIES[category].get(package)
                    if min_ver:
                        missing_optional.append(f"{package}>={min_ver}")
                    else:
                        missing_optional.append(package)

            if missing_optional:
                if isinstance(commands["optional"], dict):
                    commands["optional"][category] = (
                        f"pip install {' '.join(missing_optional)}"
                    )

        return commands

    def print_summary(self):
        """Imprime um resumo da verificação de dependências."""
        print("\n" + "=" * 60)
        print("📋 RESUMO DA VERIFICAÇÃO DE DEPENDÊNCIAS")
        print("=" * 60)

        # Dependências obrigatórias
        total_required = len(self.REQUIRED_DEPENDENCIES)
        installed_required = sum(
            1 for r in self.results["required"].values() if r["installed"]
        )
        compatible_required = sum(
            1 for r in self.results["required"].values() if r["compatible"] is True
        )

        print("\n🔧 Dependências Obrigatórias:")
        print(f"   Instaladas: {installed_required}/{total_required}")
        print(f"   Compatíveis: {compatible_required}/{total_required}")

        if self.results["missing"]:
            print(f"   ❌ Faltando: {', '.join(self.results['missing'])}")

        if self.results["outdated"]:
            print(f"   ⚠️  Desatualizadas: {len(self.results['outdated'])}")

        # Dependências opcionais
        if self.results["optional"]:
            print("\n📦 Dependências Opcionais:")
            for category, packages in self.results["optional"].items():
                total_cat = len(packages)
                installed_cat = sum(1 for r in packages.values() if r["installed"])
                print(f"   {category}: {installed_cat}/{total_cat} instaladas")

        # Comandos de instalação
        commands = self.get_installation_commands()
        if commands["required"] or commands["optional"]:
            print("\n💡 Comandos de Instalação:")

            if commands["required"]:
                print("\n   Dependências obrigatórias:")
                for cmd in commands["required"]:
                    print(f"   {cmd}")

            if commands["optional"]:
                print("\n   Dependências opcionais:")
                for category, cmd in commands["optional"].items():
                    print(f"   # {category}")
                    print(f"   {cmd}")

        # Status geral
        if not self.results["missing"] and not self.results["outdated"]:
            print(
                "\n✅ Todas as dependências obrigatórias estão instaladas e atualizadas!"
            )
        else:
            print("\n⚠️  Algumas dependências precisam de atenção.")


def check_dependencies(
    include_optional: bool = False, optional_categories: list[str] | None = None
) -> dict[str, Any]:
    """Função principal para verificação de dependências.

    Args:
        include_optional: Se deve verificar dependências opcionais
        optional_categories: Categorias específicas para verificar

    Returns:
        Dict com resultados completos da verificação
    """
    checker = DependencyChecker()

    # Verificar dependências obrigatórias
    checker.check_required_dependencies()

    # Verificar dependências opcionais se solicitado
    if include_optional:
        checker.check_optional_dependencies(optional_categories)

    # Imprimir resumo
    checker.print_summary()

    return dict(checker.results)


def check_python_version() -> bool:
    """Verifica se a versão do Python é compatível.

    Returns:
        True se a versão for compatível
    """
    min_python = (3, 8)
    current_python = sys.version_info[:2]

    print(f"🐍 Python: {sys.version.split()[0]}")

    if current_python >= min_python:
        print(f"✅ Versão do Python compatível (>= {min_python[0]}.{min_python[1]})")
        return True
    else:
        print(
            f"❌ Versão do Python incompatível (requer >= {min_python[0]}.{min_python[1]})"
        )
        return False


if __name__ == "__main__":
    # Verificação completa quando executado diretamente
    print("🔍 Verificação Completa de Dependências do Módulo LLM")
    print("=" * 60)

    # Verificar versão do Python
    python_ok = check_python_version()

    if python_ok:
        # Verificar todas as dependências
        results = check_dependencies(include_optional=True)

        # Código de saída baseado no resultado
        if results["missing"] or results["outdated"]:
            sys.exit(1)
        else:
            sys.exit(0)
    else:
        sys.exit(1)
