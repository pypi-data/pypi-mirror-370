"""Analisador avançado de ambiente para JTECH™ Core."""

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from ..core.models import InstallationConfig, TeamType


class ProjectType(Enum):
    """Tipos de projeto detectados."""

    UNKNOWN = "unknown"
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    JAVA = "java"
    CSHARP = "csharp"
    GO = "go"
    RUST = "rust"
    PHP = "php"
    RUBY = "ruby"
    MIXED = "mixed"


class FrameworkType(Enum):
    """Tipos de framework detectados."""

    NONE = "none"
    DJANGO = "django"
    FLASK = "flask"
    FASTAPI = "fastapi"
    REACT = "react"
    VUE = "vue"
    ANGULAR = "angular"
    NEXTJS = "nextjs"
    EXPRESS = "express"
    SPRING = "spring"
    DOTNET = "dotnet"
    LARAVEL = "laravel"
    RAILS = "rails"


@dataclass
class ConflictInfo:
    """Informações sobre um conflito detectado."""

    type: str
    severity: str  # "low", "medium", "high", "critical"
    description: str
    affected_files: List[str]
    recommendation: str


@dataclass
class ProjectStructure:
    """Estrutura de projeto detectada."""

    root_path: Path
    project_type: ProjectType
    frameworks: List[FrameworkType]
    languages: Set[str]
    build_tools: Set[str]
    dependencies: Dict[str, Any]
    existing_configs: List[str]
    git_info: Optional[Dict[str, Any]]


@dataclass
class EnvironmentAnalysis:
    """Resultado completo da análise de ambiente."""

    project_structure: ProjectStructure
    is_brownfield: bool
    conflicts: List[ConflictInfo]
    recommendations: List[str]
    suggested_team_type: TeamType
    compatibility_score: float
    warnings: List[str]


class AdvancedEnvironmentAnalyzer:
    """Analisador avançado de ambiente para detectar projetos existentes."""

    def __init__(self, config: InstallationConfig):
        """
        Inicializa o analisador.

        Args:
            config: Configuração de instalação
        """
        self.config = config
        self.project_path = config.project_path

        # Padrões de detecção
        self.language_patterns = {
            ProjectType.PYTHON: [
                "*.py",
                "requirements.txt",
                "setup.py",
                "pyproject.toml",
                "Pipfile",
                "environment.yml",
                "conda.yml",
            ],
            ProjectType.JAVASCRIPT: [
                "*.js",
                "package.json",
                "yarn.lock",
                "npm-shrinkwrap.json",
            ],
            ProjectType.TYPESCRIPT: [
                "*.ts",
                "*.tsx",
                "tsconfig.json",
                "tslint.json",
            ],
            ProjectType.JAVA: ["*.java", "pom.xml", "build.gradle", "gradlew"],
            ProjectType.CSHARP: [
                "*.cs",
                "*.csproj",
                "*.sln",
                "packages.config",
            ],
            ProjectType.GO: ["*.go", "go.mod", "go.sum", "Gopkg.toml"],
            ProjectType.RUST: ["*.rs", "Cargo.toml", "Cargo.lock"],
            ProjectType.PHP: ["*.php", "composer.json", "composer.lock"],
            ProjectType.RUBY: ["*.rb", "Gemfile", "Gemfile.lock", "Rakefile"],
        }

        self.framework_patterns = {
            FrameworkType.DJANGO: ["manage.py", "settings.py", "wsgi.py"],
            FrameworkType.FLASK: ["app.py", "application.py", "flask"],
            FrameworkType.FASTAPI: ["main.py", "fastapi"],
            FrameworkType.REACT: ["react", "jsx", "package.json"],
            FrameworkType.VUE: ["vue", "vue.config.js"],
            FrameworkType.ANGULAR: ["angular.json", "@angular"],
            FrameworkType.NEXTJS: ["next.config.js", "pages/"],
            FrameworkType.EXPRESS: ["express", "app.js", "server.js"],
            FrameworkType.SPRING: ["pom.xml", "@SpringBootApplication"],
            FrameworkType.DOTNET: [".csproj", "Program.cs", "Startup.cs"],
            FrameworkType.LARAVEL: ["artisan", "composer.json", "laravel"],
            FrameworkType.RAILS: ["Gemfile", "config/application.rb"],
        }

    def analyze_environment(self) -> EnvironmentAnalysis:
        """
        Executa análise completa do ambiente.

        Returns:
            Resultado da análise de ambiente
        """
        # Detectar estrutura do projeto
        project_structure = self._detect_project_structure()

        # Verificar se é brownfield
        is_brownfield = self._is_brownfield_project(project_structure)

        # Detectar conflitos
        conflicts = self._detect_conflicts(project_structure)

        # Gerar recomendações
        recommendations = self._generate_recommendations(
            project_structure, conflicts
        )

        # Sugerir tipo de equipe
        suggested_team_type = self._suggest_team_type(project_structure)

        # Calcular score de compatibilidade
        compatibility_score = self._calculate_compatibility_score(
            project_structure, conflicts
        )

        # Gerar warnings
        warnings = self._generate_warnings(project_structure, conflicts)

        return EnvironmentAnalysis(
            project_structure=project_structure,
            is_brownfield=is_brownfield,
            conflicts=conflicts,
            recommendations=recommendations,
            suggested_team_type=suggested_team_type,
            compatibility_score=compatibility_score,
            warnings=warnings,
        )

    def _detect_project_structure(self) -> ProjectStructure:
        """Detecta a estrutura do projeto."""
        languages = set()
        detected_types = []
        frameworks = []
        build_tools = set()
        dependencies = {}
        existing_configs = []

        # Analisar arquivos no diretório
        for file_path in self.project_path.rglob("*"):
            if file_path.is_file() and not self._should_ignore_file(file_path):
                # Detectar linguagens
                for project_type, patterns in self.language_patterns.items():
                    if any(file_path.match(pattern) for pattern in patterns):
                        detected_types.append(project_type)
                        languages.add(project_type.value)

                # Detectar frameworks
                frameworks.extend(self._detect_frameworks_in_file(file_path))

                # Detectar build tools
                build_tools.update(self._detect_build_tools(file_path))

                # Detectar configs existentes
                if self._is_config_file(file_path):
                    rel_path = str(file_path.relative_to(self.project_path))
                    existing_configs.append(rel_path)

        # Analisar dependências
        dependencies = self._analyze_dependencies()

        # Determinar tipo principal do projeto
        if len(detected_types) == 0:
            main_type = ProjectType.UNKNOWN
        elif len(detected_types) == 1:
            main_type = detected_types[0]
        else:
            # Para projeto misto, verificar se há realmente múltiplas linguagens
            # diferentes ou apenas frameworks da mesma linguagem
            unique_lang_count = len(languages)
            if unique_lang_count == 1:
                # Se só há uma linguagem, usar o tipo dessa linguagem
                main_type = (
                    list(detected_types)[0]
                    if detected_types
                    else ProjectType.UNKNOWN
                )
            else:
                main_type = ProjectType.MIXED

        # Remover duplicatas de frameworks
        unique_frameworks = list(set(frameworks))

        # Detectar informações do Git
        git_info = self._analyze_git_info()

        return ProjectStructure(
            root_path=self.project_path,
            project_type=main_type,
            frameworks=unique_frameworks,
            languages=languages,
            build_tools=build_tools,
            dependencies=dependencies,
            existing_configs=existing_configs,
            git_info=git_info,
        )

    def _is_brownfield_project(self, structure: ProjectStructure) -> bool:
        """Determina se é um projeto brownfield."""
        indicators = [
            len(structure.languages) > 0,
            len(structure.existing_configs) > 0,
            structure.project_type != ProjectType.UNKNOWN,
            len(structure.frameworks) > 0,
            structure.git_info is not None,
        ]

        return sum(indicators) >= 2

    def _detect_conflicts(
        self, structure: ProjectStructure
    ) -> List[ConflictInfo]:
        """Detecta conflitos potenciais."""
        conflicts = []

        # Conflitos de configuração existente
        conflicts.extend(self._detect_config_conflicts(structure))

        # Conflitos de estrutura de diretório
        conflicts.extend(self._detect_directory_conflicts(structure))

        # Conflitos de dependências
        conflicts.extend(self._detect_dependency_conflicts(structure))

        # Conflitos de VS Code
        if self.config.vs_code_integration:
            conflicts.extend(self._detect_vscode_conflicts(structure))

        return conflicts

    def _detect_config_conflicts(
        self, structure: ProjectStructure
    ) -> List[ConflictInfo]:
        """Detecta conflitos de configuração."""
        conflicts = []

        # Verificar se já existe core-config.yml
        core_config_path = (
            self.project_path / ".jtech-core" / "core-config.yml"
        )
        if core_config_path.exists():
            conflicts.append(
                ConflictInfo(
                    type="config_override",
                    severity="medium",
                    description="Arquivo core-config.yml já existe",
                    affected_files=[
                        str(core_config_path.relative_to(self.project_path))
                    ],
                    recommendation="O arquivo existente será preservado e mesclado",
                )
            )

        # Verificar conflitos com outros frameworks de documentação
        doc_conflicts = []
        for config_file in structure.existing_configs:
            if any(
                doc_tool in config_file.lower()
                for doc_tool in ["sphinx", "mkdocs", "gitbook", "docusaurus"]
            ):
                doc_conflicts.append(config_file)

        if doc_conflicts:
            conflicts.append(
                ConflictInfo(
                    type="documentation_conflict",
                    severity="low",
                    description="Sistema de documentação existente detectado",
                    affected_files=doc_conflicts,
                    recommendation="Considere integrar com o sistema existente",
                )
            )

        return conflicts

    def _detect_directory_conflicts(
        self, structure: ProjectStructure
    ) -> List[ConflictInfo]:
        """Detecta conflitos de estrutura de diretório."""
        conflicts = []

        # Verificar se .jtech-core já existe
        jtech_dir = self.project_path / ".jtech-core"
        if jtech_dir.exists():
            conflicts.append(
                ConflictInfo(
                    type="directory_exists",
                    severity="high",
                    description="Diretório .jtech-core já existe",
                    affected_files=[".jtech-core/"],
                    recommendation="Conteúdo existente será preservado quando possível",
                )
            )

        # Verificar conflitos com .github
        github_dir = self.project_path / ".github"
        if github_dir.exists():
            existing_workflows = list(github_dir.glob("workflows/*.yml"))
            if existing_workflows:
                conflicts.append(
                    ConflictInfo(
                        type="github_workflows",
                        severity="medium",
                        description="GitHub workflows existentes detectados",
                        affected_files=[
                            str(f.relative_to(self.project_path))
                            for f in existing_workflows
                        ],
                        recommendation="Chatmodes serão adicionados sem afetar workflows",
                    )
                )

        return conflicts

    def _detect_dependency_conflicts(
        self, structure: ProjectStructure
    ) -> List[ConflictInfo]:
        """Detecta conflitos de dependências."""
        conflicts = []

        # Verificar conflitos Python
        if (
            ProjectType.PYTHON in [structure.project_type]
            or "python" in structure.languages
        ):
            python_conflicts = self._check_python_conflicts(structure)
            conflicts.extend(python_conflicts)

        # Verificar conflitos JavaScript/TypeScript
        if any(
            lang in structure.languages
            for lang in ["javascript", "typescript"]
        ):
            js_conflicts = self._check_js_conflicts(structure)
            conflicts.extend(js_conflicts)

        return conflicts

    def _detect_vscode_conflicts(
        self, structure: ProjectStructure
    ) -> List[ConflictInfo]:
        """Detecta conflitos do VS Code."""
        conflicts = []

        vscode_dir = self.project_path / ".vscode"
        if vscode_dir.exists():
            existing_files = []
            for vscode_file in [
                "settings.json",
                "extensions.json",
                "tasks.json",
                "launch.json",
            ]:
                if (vscode_dir / vscode_file).exists():
                    existing_files.append(f".vscode/{vscode_file}")

            if existing_files:
                conflicts.append(
                    ConflictInfo(
                        type="vscode_config_exists",
                        severity="medium",
                        description="Configurações VS Code existentes detectadas",
                        affected_files=existing_files,
                        recommendation="Configurações serão mescladas preservando as existentes",
                    )
                )

        return conflicts

    def _generate_recommendations(
        self, structure: ProjectStructure, conflicts: List[ConflictInfo]
    ) -> List[str]:
        """Gera recomendações baseadas na análise."""
        recommendations = []

        # Recomendações baseadas no tipo de projeto
        if structure.project_type == ProjectType.PYTHON:
            recommendations.append(
                "Considere usar o tipo de equipe 'fullstack' ou 'no-ui' para projetos Python"
            )

        elif (
            structure.project_type == ProjectType.JAVASCRIPT
            or structure.project_type == ProjectType.TYPESCRIPT
        ):
            if (
                FrameworkType.REACT in structure.frameworks
                or FrameworkType.VUE in structure.frameworks
            ):
                recommendations.append(
                    "Tipo de equipe 'fullstack' recomendado para projetos frontend"
                )
            else:
                recommendations.append(
                    "Considere o tipo 'no-ui' para projetos backend JavaScript"
                )

        elif structure.project_type == ProjectType.MIXED:
            recommendations.append(
                "Projeto multi-linguagem detectado - tipo 'all' recomendado"
            )

        # Recomendações baseadas em conflitos
        high_severity_conflicts = [
            c for c in conflicts if c.severity == "high"
        ]
        if high_severity_conflicts:
            recommendations.append(
                "Execute backup antes da instalação devido a conflitos de alta prioridade"
            )

        medium_severity_conflicts = [
            c for c in conflicts if c.severity == "medium"
        ]
        if len(medium_severity_conflicts) > 2:
            recommendations.append(
                "Considere revisar configurações existentes antes da instalação"
            )

        # Recomendações específicas
        if not structure.git_info:
            recommendations.append(
                "Considere inicializar repositório Git antes da instalação"
            )

        if ".gitignore" not in [
            Path(f).name for f in structure.existing_configs
        ]:
            recommendations.append(
                "Adicione .gitignore apropriado para seu tipo de projeto"
            )

        return recommendations

    def _suggest_team_type(self, structure: ProjectStructure) -> TeamType:
        """Sugere tipo de equipe baseado na estrutura."""
        # Lógica de sugestão baseada em frameworks e linguagens
        frontend_frameworks = {
            FrameworkType.REACT,
            FrameworkType.VUE,
            FrameworkType.ANGULAR,
            FrameworkType.NEXTJS,
        }
        backend_frameworks = {
            FrameworkType.DJANGO,
            FrameworkType.FLASK,
            FrameworkType.FASTAPI,
            FrameworkType.EXPRESS,
        }

        has_frontend = any(
            fw in structure.frameworks for fw in frontend_frameworks
        )
        has_backend = any(
            fw in structure.frameworks for fw in backend_frameworks
        )

        if has_frontend and has_backend:
            return TeamType.FULLSTACK
        elif has_frontend:
            return (
                TeamType.FULLSTACK
            )  # Frontend ainda precisa de capacidades full-stack
        elif has_backend:
            return TeamType.NO_UI
        elif len(structure.languages) > 2:
            return TeamType.ALL
        else:
            return TeamType.IDE_MINIMAL

    def _calculate_compatibility_score(
        self, structure: ProjectStructure, conflicts: List[ConflictInfo]
    ) -> float:
        """Calcula score de compatibilidade (0-100)."""
        base_score = 100.0

        # Penalizar por conflitos
        for conflict in conflicts:
            if conflict.severity == "critical":
                base_score -= 25
            elif conflict.severity == "high":
                base_score -= 15
            elif conflict.severity == "medium":
                base_score -= 10
            elif conflict.severity == "low":
                base_score -= 5

        # Bonificar por indicadores positivos
        if structure.git_info:
            base_score += 5

        if structure.project_type != ProjectType.UNKNOWN:
            base_score += 10

        if len(structure.frameworks) > 0:
            base_score += 5

        return max(0.0, min(100.0, base_score))

    def _generate_warnings(
        self, structure: ProjectStructure, conflicts: List[ConflictInfo]
    ) -> List[str]:
        """Gera warnings baseados na análise."""
        warnings = []

        # Warnings para conflitos críticos
        critical_conflicts = [c for c in conflicts if c.severity == "critical"]
        for conflict in critical_conflicts:
            warnings.append(f"CRÍTICO: {conflict.description}")

        # Warnings para estrutura
        if structure.project_type == ProjectType.UNKNOWN:
            warnings.append(
                "Tipo de projeto não identificado - instalação pode não ser otimizada"
            )

        if not structure.existing_configs:
            warnings.append(
                "Nenhum arquivo de configuração detectado - verifique se está no diretório correto"
            )

        return warnings

    # Métodos auxiliares
    def _should_ignore_file(self, file_path: Path) -> bool:
        """Verifica se arquivo deve ser ignorado na análise."""
        ignore_patterns = [
            "*/node_modules/*",
            "*/.git/*",
            "*/__pycache__/*",
            "*/venv/*",
            "*/.venv/*",
            "*/.env/*",
            "*/dist/*",
            "*/build/*",
            "*/env/*",
        ]

        # Verificar se alguma parte do caminho contém termos a ignorar
        ignore_terms = [
            "node_modules",
            ".git",
            "__pycache__",
            "venv",
            ".venv",
            ".env",
            "dist",
            "build",
            "env",
        ]

        # Verificar padrões diretos
        if any(file_path.match(pattern) for pattern in ignore_patterns):
            return True

        # Verificar se algum componente do path contém termos a ignorar
        path_parts = file_path.parts
        for part in path_parts:
            if any(term in part for term in ignore_terms):
                return True

        return False

    def _detect_frameworks_in_file(
        self, file_path: Path
    ) -> List[FrameworkType]:
        """Detecta frameworks baseado em um arquivo."""
        frameworks = []

        # Análise baseada em nome/estrutura de arquivo
        for framework, patterns in self.framework_patterns.items():
            if any(pattern in str(file_path).lower() for pattern in patterns):
                frameworks.append(framework)

        # Análise de conteúdo para alguns casos específicos
        if file_path.name == "package.json":
            frameworks.extend(self._analyze_package_json(file_path))
        elif file_path.name in ["requirements.txt", "pyproject.toml"]:
            frameworks.extend(self._analyze_python_deps(file_path))

        return frameworks

    def _detect_build_tools(self, file_path: Path) -> Set[str]:
        """Detecta ferramentas de build."""
        build_tools = set()

        build_indicators = {
            "webpack.config.js": "webpack",
            "vite.config.js": "vite",
            "rollup.config.js": "rollup",
            "gulpfile.js": "gulp",
            "Gruntfile.js": "grunt",
            "Makefile": "make",
            "CMakeLists.txt": "cmake",
            "build.gradle": "gradle",
            "pom.xml": "maven",
        }

        for indicator, tool in build_indicators.items():
            if file_path.name == indicator:
                build_tools.add(tool)

        return build_tools

    def _is_config_file(self, file_path: Path) -> bool:
        """Verifica se é um arquivo de configuração."""
        config_extensions = {
            ".json",
            ".yml",
            ".yaml",
            ".toml",
            ".ini",
            ".cfg",
            ".conf",
        }
        config_names = {
            "package.json",
            "composer.json",
            "Cargo.toml",
            "pyproject.toml",
            "requirements.txt",
            "Gemfile",
            "go.mod",
            ".gitignore",
            "README.md",
        }

        return (
            file_path.suffix in config_extensions
            or file_path.name in config_names
        )

    def _analyze_dependencies(self) -> Dict[str, Any]:
        """Analisa dependências do projeto."""
        dependencies = {}

        # Python
        req_file = self.project_path / "requirements.txt"
        if req_file.exists():
            dependencies["python"] = self._parse_requirements_txt(req_file)

        # Node.js
        package_file = self.project_path / "package.json"
        if package_file.exists():
            dependencies["nodejs"] = self._parse_package_json(package_file)

        return dependencies

    def _analyze_git_info(self) -> Optional[Dict[str, Any]]:
        """Analisa informações do Git."""
        git_dir = self.project_path / ".git"
        if not git_dir.exists():
            return None

        git_info = {"has_git": True}

        # Verificar se há commits
        try:
            # Verificação simples de estrutura Git
            if (git_dir / "HEAD").exists():
                git_info["initialized"] = True

            # Verificar branches remotos
            refs_dir = git_dir / "refs" / "remotes"
            if refs_dir.exists():
                git_info["has_remotes"] = True
        except Exception:
            pass

        return git_info

    def _check_python_conflicts(
        self, structure: ProjectStructure
    ) -> List[ConflictInfo]:
        """Verifica conflitos específicos do Python."""
        conflicts = []

        # Verificar múltiplos gerenciadores de dependência
        dep_files = [
            "requirements.txt",
            "Pipfile",
            "pyproject.toml",
            "environment.yml",
        ]
        existing_dep_files = [
            f for f in dep_files if (self.project_path / f).exists()
        ]

        if len(existing_dep_files) > 1:
            conflicts.append(
                ConflictInfo(
                    type="multiple_dependency_managers",
                    severity="medium",
                    description="Múltiplos gerenciadores de dependência Python detectados",
                    affected_files=existing_dep_files,
                    recommendation="Considere padronizar em um único gerenciador",
                )
            )

        return conflicts

    def _check_js_conflicts(
        self, structure: ProjectStructure
    ) -> List[ConflictInfo]:
        """Verifica conflitos específicos do JavaScript."""
        conflicts = []

        # Verificar múltiplos lock files
        lock_files = ["package-lock.json", "yarn.lock", "pnpm-lock.yaml"]
        existing_locks = [
            f for f in lock_files if (self.project_path / f).exists()
        ]

        if len(existing_locks) > 1:
            conflicts.append(
                ConflictInfo(
                    type="multiple_package_managers",
                    severity="medium",
                    description="Múltiplos gerenciadores de pacote JavaScript detectados",
                    affected_files=existing_locks,
                    recommendation="Use apenas um gerenciador de pacotes",
                )
            )

        return conflicts

    def _analyze_package_json(self, file_path: Path) -> List[FrameworkType]:
        """Analisa package.json para detectar frameworks."""
        frameworks = []
        try:
            import json

            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            deps = {
                **data.get("dependencies", {}),
                **data.get("devDependencies", {}),
            }

            if "react" in deps:
                frameworks.append(FrameworkType.REACT)
            if "vue" in deps:
                frameworks.append(FrameworkType.VUE)
            if "@angular/core" in deps:
                frameworks.append(FrameworkType.ANGULAR)
            if "next" in deps:
                frameworks.append(FrameworkType.NEXTJS)
            if "express" in deps:
                frameworks.append(FrameworkType.EXPRESS)

        except Exception:
            pass

        return frameworks

    def _analyze_python_deps(self, file_path: Path) -> List[FrameworkType]:
        """Analisa dependências Python para detectar frameworks."""
        frameworks = []
        try:
            content = file_path.read_text(encoding="utf-8").lower()

            # Usar regex para correspondências exatas de pacotes
            import re

            if re.search(r"\bdjango\b", content):
                frameworks.append(FrameworkType.DJANGO)
            if re.search(r"\bflask\b", content):
                frameworks.append(FrameworkType.FLASK)
            if re.search(r"\bfastapi\b", content):
                frameworks.append(FrameworkType.FASTAPI)

        except Exception:
            pass

        return frameworks

    def _parse_requirements_txt(self, file_path: Path) -> List[str]:
        """Parse requirements.txt."""
        try:
            return [
                line.strip()
                for line in file_path.read_text().splitlines()
                if line.strip() and not line.startswith("#")
            ]
        except Exception:
            return []

    def _parse_package_json(self, file_path: Path) -> Dict[str, Any]:
        """Parse package.json."""
        try:
            import json

            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
