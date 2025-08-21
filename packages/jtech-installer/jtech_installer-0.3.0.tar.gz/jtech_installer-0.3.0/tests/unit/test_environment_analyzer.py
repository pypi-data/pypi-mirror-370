"""Testes para o analisador avançado de ambiente."""

import shutil
import tempfile
from pathlib import Path
from unittest.mock import mock_open, patch

import pytest

from jtech_installer.analyzer.environment import (
    AdvancedEnvironmentAnalyzer,
    ConflictInfo,
    EnvironmentAnalysis,
    FrameworkType,
    ProjectStructure,
    ProjectType,
)
from jtech_installer.core.models import InstallationConfig, InstallationType, TeamType


class TestAdvancedEnvironmentAnalyzer:
    """Testes para o AdvancedEnvironmentAnalyzer."""

    @pytest.fixture
    def temp_project_dir(self):
        """Fixture para diretório temporário de projeto."""
        temp_dir = Path(tempfile.mkdtemp())
        yield temp_dir
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def sample_config(self, temp_project_dir):
        """Fixture para configuração de teste."""
        return InstallationConfig(
            project_path=temp_project_dir,
            install_type=InstallationType.GREENFIELD,
            team_type=TeamType.FULLSTACK,
            vs_code_integration=True,
            custom_config={},
            framework_source_path=None,
        )

    @pytest.fixture
    def analyzer(self, sample_config):
        """Fixture para analisador."""
        return AdvancedEnvironmentAnalyzer(sample_config)

    def test_analyzer_initialization(self, analyzer, sample_config):
        """Testa inicialização do analisador."""
        assert analyzer.config == sample_config
        assert analyzer.project_path == sample_config.project_path
        assert isinstance(analyzer.language_patterns, dict)
        assert isinstance(analyzer.framework_patterns, dict)

    def test_detect_python_project(self, analyzer, temp_project_dir):
        """Testa detecção de projeto Python."""
        # Criar arquivos Python
        (temp_project_dir / "main.py").write_text("print('hello')")
        (temp_project_dir / "requirements.txt").write_text(
            "flask==2.0.1\ndjango==4.0"
        )

        structure = analyzer._detect_project_structure()

        assert structure.project_type == ProjectType.PYTHON
        assert "python" in structure.languages
        assert FrameworkType.FLASK in structure.frameworks
        assert FrameworkType.DJANGO in structure.frameworks

    def test_detect_javascript_project(self, analyzer, temp_project_dir):
        """Testa detecção de projeto JavaScript."""
        # Criar arquivos JavaScript
        (temp_project_dir / "index.js").write_text("console.log('hello');")
        package_json = {
            "name": "test-project",
            "dependencies": {"react": "^18.0.0", "express": "^4.18.0"},
        }

        with patch("builtins.open", mock_open(read_data=str(package_json))):
            with patch("json.load", return_value=package_json):
                structure = analyzer._detect_project_structure()

        assert structure.project_type == ProjectType.JAVASCRIPT
        assert "javascript" in structure.languages

    def test_detect_mixed_project(self, analyzer, temp_project_dir):
        """Testa detecção de projeto misto."""
        # Criar arquivos de múltiplas linguagens
        (temp_project_dir / "main.py").write_text("print('hello')")
        (temp_project_dir / "index.js").write_text("console.log('hello');")
        (temp_project_dir / "main.go").write_text("package main")

        structure = analyzer._detect_project_structure()

        assert structure.project_type == ProjectType.MIXED
        assert len(structure.languages) >= 2

    def test_is_brownfield_detection(self, analyzer, temp_project_dir):
        """Testa detecção de projeto brownfield."""
        # Projeto vazio (greenfield)
        structure = ProjectStructure(
            root_path=temp_project_dir,
            project_type=ProjectType.UNKNOWN,
            frameworks=[],
            languages=set(),
            build_tools=set(),
            dependencies={},
            existing_configs=[],
            git_info=None,
        )

        assert not analyzer._is_brownfield_project(structure)

        # Projeto com código (brownfield)
        structure.project_type = ProjectType.PYTHON
        structure.languages = {"python"}
        structure.existing_configs = ["requirements.txt"]

        assert analyzer._is_brownfield_project(structure)

    def test_detect_config_conflicts(self, analyzer, temp_project_dir):
        """Testa detecção de conflitos de configuração."""
        # Criar core-config.yml existente
        jtech_dir = temp_project_dir / ".jtech-core"
        jtech_dir.mkdir()
        (jtech_dir / "core-config.yml").write_text("existing: config")

        structure = ProjectStructure(
            root_path=temp_project_dir,
            project_type=ProjectType.PYTHON,
            frameworks=[],
            languages={"python"},
            build_tools=set(),
            dependencies={},
            existing_configs=["sphinx.conf"],
            git_info=None,
        )

        conflicts = analyzer._detect_config_conflicts(structure)

        # Deve detectar conflito de core-config.yml
        config_conflicts = [
            c for c in conflicts if c.type == "config_override"
        ]
        assert len(config_conflicts) == 1
        assert config_conflicts[0].severity == "medium"

        # Deve detectar conflito de documentação
        doc_conflicts = [
            c for c in conflicts if c.type == "documentation_conflict"
        ]
        assert len(doc_conflicts) == 1

    def test_detect_directory_conflicts(self, analyzer, temp_project_dir):
        """Testa detecção de conflitos de diretório."""
        # Criar diretório .jtech-core existente
        jtech_dir = temp_project_dir / ".jtech-core"
        jtech_dir.mkdir()

        # Criar workflows GitHub existentes
        github_dir = temp_project_dir / ".github" / "workflows"
        github_dir.mkdir(parents=True)
        (github_dir / "ci.yml").write_text("name: CI")

        structure = ProjectStructure(
            root_path=temp_project_dir,
            project_type=ProjectType.PYTHON,
            frameworks=[],
            languages={"python"},
            build_tools=set(),
            dependencies={},
            existing_configs=[],
            git_info=None,
        )

        conflicts = analyzer._detect_directory_conflicts(structure)

        # Deve detectar conflito de diretório
        dir_conflicts = [c for c in conflicts if c.type == "directory_exists"]
        assert len(dir_conflicts) == 1
        assert dir_conflicts[0].severity == "high"

        # Deve detectar conflito de workflows
        workflow_conflicts = [
            c for c in conflicts if c.type == "github_workflows"
        ]
        assert len(workflow_conflicts) == 1

    def test_detect_vscode_conflicts(self, analyzer, temp_project_dir):
        """Testa detecção de conflitos do VS Code."""
        # Criar configurações VS Code existentes
        vscode_dir = temp_project_dir / ".vscode"
        vscode_dir.mkdir()
        (vscode_dir / "settings.json").write_text('{"editor.tabSize": 4}')
        (vscode_dir / "extensions.json").write_text('{"recommendations": []}')

        structure = ProjectStructure(
            root_path=temp_project_dir,
            project_type=ProjectType.PYTHON,
            frameworks=[],
            languages={"python"},
            build_tools=set(),
            dependencies={},
            existing_configs=[],
            git_info=None,
        )

        conflicts = analyzer._detect_vscode_conflicts(structure)

        assert len(conflicts) == 1
        assert conflicts[0].type == "vscode_config_exists"
        assert conflicts[0].severity == "medium"
        assert ".vscode/settings.json" in conflicts[0].affected_files
        assert ".vscode/extensions.json" in conflicts[0].affected_files

    def test_suggest_team_type(self, analyzer, temp_project_dir):
        """Testa sugestão de tipo de equipe."""
        # Projeto frontend
        frontend_structure = ProjectStructure(
            root_path=temp_project_dir,
            project_type=ProjectType.JAVASCRIPT,
            frameworks=[FrameworkType.REACT],
            languages={"javascript"},
            build_tools=set(),
            dependencies={},
            existing_configs=[],
            git_info=None,
        )

        assert (
            analyzer._suggest_team_type(frontend_structure)
            == TeamType.FULLSTACK
        )

        # Projeto backend
        backend_structure = ProjectStructure(
            root_path=temp_project_dir,
            project_type=ProjectType.PYTHON,
            frameworks=[FrameworkType.DJANGO],
            languages={"python"},
            build_tools=set(),
            dependencies={},
            existing_configs=[],
            git_info=None,
        )

        assert analyzer._suggest_team_type(backend_structure) == TeamType.NO_UI

        # Projeto multi-linguagem
        mixed_structure = ProjectStructure(
            root_path=temp_project_dir,
            project_type=ProjectType.MIXED,
            frameworks=[],
            languages={"python", "javascript", "go"},
            build_tools=set(),
            dependencies={},
            existing_configs=[],
            git_info=None,
        )

        assert analyzer._suggest_team_type(mixed_structure) == TeamType.ALL

    def test_calculate_compatibility_score(self, analyzer, temp_project_dir):
        """Testa cálculo do score de compatibilidade."""
        structure = ProjectStructure(
            root_path=temp_project_dir,
            project_type=ProjectType.PYTHON,
            frameworks=[FrameworkType.DJANGO],
            languages={"python"},
            build_tools=set(),
            dependencies={},
            existing_configs=[],
            git_info={"has_git": True},
        )

        # Sem conflitos
        conflicts = []
        score = analyzer._calculate_compatibility_score(structure, conflicts)
        assert score == 100.0  # Base + bonificações

        # Com conflitos
        conflicts = [
            ConflictInfo("test", "high", "Test conflict", [], "Fix it"),
            ConflictInfo("test2", "medium", "Test conflict 2", [], "Fix it"),
        ]
        score = analyzer._calculate_compatibility_score(structure, conflicts)
        assert score < 100.0

    def test_generate_recommendations(self, analyzer, temp_project_dir):
        """Testa geração de recomendações."""
        # Projeto Python
        python_structure = ProjectStructure(
            root_path=temp_project_dir,
            project_type=ProjectType.PYTHON,
            frameworks=[],
            languages={"python"},
            build_tools=set(),
            dependencies={},
            existing_configs=[],
            git_info=None,
        )

        conflicts = [
            ConflictInfo("test", "high", "High severity", [], "Fix it")
        ]

        recommendations = analyzer._generate_recommendations(
            python_structure, conflicts
        )

        # Deve incluir recomendação para projeto Python
        python_rec = any("python" in rec.lower() for rec in recommendations)
        assert python_rec

        # Deve incluir recomendação de backup para conflitos high
        backup_rec = any("backup" in rec.lower() for rec in recommendations)
        assert backup_rec

        # Deve incluir recomendação de Git
        git_rec = any("git" in rec.lower() for rec in recommendations)
        assert git_rec

    def test_full_environment_analysis(self, analyzer, temp_project_dir):
        """Testa análise completa do ambiente."""
        # Criar projeto Python com algumas configurações
        (temp_project_dir / "main.py").write_text("print('hello')")
        (temp_project_dir / "requirements.txt").write_text("django==4.0")

        # Criar .jtech-core existente
        jtech_dir = temp_project_dir / ".jtech-core"
        jtech_dir.mkdir()
        (jtech_dir / "core-config.yml").write_text("existing: config")

        analysis = analyzer.analyze_environment()

        assert isinstance(analysis, EnvironmentAnalysis)
        assert analysis.project_structure.project_type == ProjectType.PYTHON
        assert analysis.is_brownfield
        assert len(analysis.conflicts) > 0
        assert len(analysis.recommendations) > 0
        assert isinstance(analysis.suggested_team_type, TeamType)
        assert 0 <= analysis.compatibility_score <= 100

    def test_should_ignore_file(self, analyzer, temp_project_dir):
        """Testa se arquivos devem ser ignorados."""
        # Arquivos que devem ser ignorados
        ignored_files = [
            temp_project_dir / "node_modules" / "package.js",
            temp_project_dir / ".git" / "config",
            temp_project_dir / "__pycache__" / "module.pyc",
            temp_project_dir / "venv" / "lib" / "python3.9",
            temp_project_dir / "dist" / "bundle.js",
        ]

        for file_path in ignored_files:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.touch()
            assert analyzer._should_ignore_file(file_path)

        # Arquivos que NÃO devem ser ignorados
        normal_files = [
            temp_project_dir / "src" / "main.py",
            temp_project_dir / "tests" / "test_main.py",
            temp_project_dir / "package.json",
        ]

        for file_path in normal_files:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.touch()
            assert not analyzer._should_ignore_file(file_path)

    def test_is_config_file(self, analyzer):
        """Testa detecção de arquivos de configuração."""
        config_files = [
            Path("package.json"),
            Path("requirements.txt"),
            Path("config.yml"),
            Path("settings.toml"),
            Path(".gitignore"),
            Path("README.md"),
        ]

        for file_path in config_files:
            assert analyzer._is_config_file(file_path)

        non_config_files = [
            Path("main.py"),
            Path("index.js"),
            Path("style.css"),
            Path("image.png"),
        ]

        for file_path in non_config_files:
            assert not analyzer._is_config_file(file_path)

    def test_analyze_git_info(self, analyzer, temp_project_dir):
        """Testa análise de informações do Git."""
        # Projeto sem Git
        git_info = analyzer._analyze_git_info()
        assert git_info is None

        # Criar estrutura Git básica
        git_dir = temp_project_dir / ".git"
        git_dir.mkdir()
        (git_dir / "HEAD").write_text("ref: refs/heads/main")

        git_info = analyzer._analyze_git_info()
        assert git_info is not None
        assert git_info["has_git"] is True
        assert git_info["initialized"] is True

    def test_parse_package_json(self, analyzer, temp_project_dir):
        """Testa parsing de package.json."""
        package_json = temp_project_dir / "package.json"
        package_data = {
            "name": "test-project",
            "dependencies": {"react": "^18.0.0"},
            "devDependencies": {"jest": "^29.0.0"},
        }

        with patch("builtins.open", mock_open(read_data="mock")):
            with patch("json.load", return_value=package_data):
                result = analyzer._parse_package_json(package_json)

        assert result == package_data

        # Teste com arquivo inválido
        with patch("builtins.open", side_effect=FileNotFoundError):
            result = analyzer._parse_package_json(package_json)
            assert result == {}

    def test_parse_requirements_txt(self, analyzer, temp_project_dir):
        """Testa parsing de requirements.txt."""
        req_file = temp_project_dir / "requirements.txt"
        req_content = "django==4.0.0\nflask>=2.0.0\n# comment\npytest"
        req_file.write_text(req_content)

        result = analyzer._parse_requirements_txt(req_file)

        expected = ["django==4.0.0", "flask>=2.0.0", "pytest"]
        assert result == expected

        # Teste com arquivo que não existe
        missing_file = temp_project_dir / "missing.txt"
        result = analyzer._parse_requirements_txt(missing_file)
        assert result == []
