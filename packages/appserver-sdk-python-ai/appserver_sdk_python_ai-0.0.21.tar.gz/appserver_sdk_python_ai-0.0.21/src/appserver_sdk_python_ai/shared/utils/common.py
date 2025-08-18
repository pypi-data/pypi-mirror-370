"""Utilitários comuns para todos os módulos do SDK."""

import sys
from collections.abc import Sequence
from typing import Any


class DependencyChecker:
    """Verificador de dependências comum."""

    @staticmethod
    def check_dependencies(dependencies: Sequence[str]) -> dict[str, str]:
        """
        Verifica se as dependências estão instaladas.

        Args:
            dependencies: Lista de nomes de pacotes para verificar

        Returns:
            Dicionário com status de cada dependência
        """
        result = {}

        for dep in dependencies:
            try:
                # Mapeamento de nomes especiais
                import_name = dep
                if dep == "beautifulsoup4":
                    import_name = "bs4"
                elif dep == "pillow":
                    import_name = "PIL"

                module = __import__(import_name)
                version = getattr(module, "__version__", "installed")
                result[dep] = version
            except ImportError:
                result[dep] = "NOT_INSTALLED"

        return result

    @staticmethod
    def check_optional_dependencies(dependencies: Sequence[str]) -> dict[str, bool]:
        """
        Verifica dependências opcionais retornando apenas status booleano.

        Args:
            dependencies: Lista de nomes de pacotes para verificar

        Returns:
            Dicionário com status booleano de cada dependência
        """
        result = {}
        deps_status = DependencyChecker.check_dependencies(dependencies)

        for dep, status in deps_status.items():
            result[dep] = status != "NOT_INSTALLED"

        return result


class HealthChecker:
    """Verificador de saúde comum para módulos."""

    @staticmethod
    def create_health_report(
        module_name: str,
        version: str,
        dependencies: dict[str, str],
        features: dict[str, bool],
        critical_deps: list[str] | None = None,
        optional_deps: list[str] | None = None,
    ) -> dict[str, Any]:
        """
        Cria um relatório de saúde padronizado.

        Args:
            module_name: Nome do módulo
            version: Versão do módulo
            dependencies: Status das dependências
            features: Status dos recursos
            critical_deps: Lista de dependências críticas
            optional_deps: Lista de dependências opcionais

        Returns:
            Relatório de saúde padronizado
        """
        critical_deps = critical_deps or []
        optional_deps = optional_deps or []

        issues: list[str] = []
        warnings: list[str] = []

        health = {
            "module": module_name,
            "status": "OK",
            "version": version,
            "dependencies": dependencies,
            "features": features,
            "issues": issues,
            "warnings": warnings,
        }

        # Verificar dependências críticas
        for dep in critical_deps:
            if dep in dependencies and dependencies[dep] == "NOT_INSTALLED":
                health["status"] = "ERROR"
                issues.append(f"{dep} não está instalado (crítico)")

        # Verificar dependências opcionais
        for dep in optional_deps:
            if dep in dependencies and dependencies[dep] == "NOT_INSTALLED":
                if health["status"] == "OK":
                    health["status"] = "WARNING"
                warnings.append(f"{dep} não está instalado (opcional)")

        return health

    @staticmethod
    def print_health_status(
        health: dict[str, Any],
        show_dependencies: bool = True,
        show_features: bool = True,
    ):
        """
        Imprime o status de saúde de forma formatada.

        Args:
            health: Relatório de saúde
            show_dependencies: Se deve mostrar dependências
            show_features: Se deve mostrar recursos
        """
        module_name = health.get("module", "SDK").upper()
        print("=" * 60)
        print(f"MÓDULO {module_name} - appserver_sdk_python_ai")
        print("=" * 60)
        print(f"Versão: {health['version']}")
        print(f"Status: {health['status']}")

        if show_dependencies and "dependencies" in health:
            print("\n📦 Dependências:")
            deps = health["dependencies"]
            for dep, status in deps.items():
                icon = "✅" if status != "NOT_INSTALLED" else "❌"
                version_str = status if status != "NOT_INSTALLED" else "NÃO INSTALADO"
                print(f"  {icon} {dep}: {version_str}")

        if show_features and "features" in health:
            print("\n🚀 Recursos disponíveis:")
            for feature, available in health["features"].items():
                icon = "✅" if available else "❌"
                feature_name = feature.replace("_", " ").title()
                print(f"  {icon} {feature_name}")

        if health.get("issues"):
            print("\n❌ Problemas críticos:")
            for issue in health["issues"]:
                print(f"  • {issue}")

        if health.get("warnings"):
            print("\n⚠️ Avisos:")
            for warning in health["warnings"]:
                print(f"  • {warning}")

        print("=" * 60)


class VersionInfo:
    """Utilitários para informações de versão."""

    @staticmethod
    def get_python_version() -> str:
        """Retorna a versão do Python."""
        return f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"

    @staticmethod
    def create_version_info(
        module_name: str,
        module_version: str,
        dependencies: dict[str, str] | None = None,
        additional_info: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Cria informações de versão padronizadas.

        Args:
            module_name: Nome do módulo
            module_version: Versão do módulo
            dependencies: Dependências e suas versões
            additional_info: Informações adicionais

        Returns:
            Dicionário com informações de versão
        """
        info: dict[str, Any] = {
            "module": module_name,
            "version": module_version,
            "python_version": VersionInfo.get_python_version(),
        }

        if dependencies:
            info["dependencies"] = dependencies

        if additional_info:
            for key, value in additional_info.items():
                info[key] = value

        return info
