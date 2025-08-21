"""
Testes para o sistema de detecção
"""

from unittest.mock import MagicMock, patch

import pytest

from jtech_installer.core.models import OSType
from jtech_installer.detector.system import SystemDetector


class TestSystemDetector:
    """Testes para SystemDetector"""

    def test_detect_returns_system_info(self):
        """Testa se detect() retorna SystemInfo válido"""
        detector = SystemDetector()
        system_info = detector.detect()

        assert system_info.os_type in [
            OSType.LINUX,
            OSType.MACOS,
            OSType.WINDOWS,
        ]
        assert system_info.python_version
        assert system_info.current_directory.exists()
        assert system_info.architecture

    @patch("platform.system")
    def test_detect_os_linux(self, mock_system):
        """Testa detecção do Linux"""
        mock_system.return_value = "Linux"
        detector = SystemDetector()

        os_type = detector._detect_os()
        assert os_type == OSType.LINUX

    @patch("platform.system")
    def test_detect_os_macos(self, mock_system):
        """Testa detecção do macOS"""
        mock_system.return_value = "Darwin"
        detector = SystemDetector()

        os_type = detector._detect_os()
        assert os_type == OSType.MACOS

    @patch("platform.system")
    def test_detect_os_windows(self, mock_system):
        """Testa detecção do Windows"""
        mock_system.return_value = "Windows"
        detector = SystemDetector()

        os_type = detector._detect_os()
        assert os_type == OSType.WINDOWS

    @patch("platform.system")
    def test_detect_os_unsupported(self, mock_system):
        """Testa erro para SO não suportado"""
        mock_system.return_value = "FreeBSD"
        detector = SystemDetector()

        with pytest.raises(
            ValueError, match="Sistema operacional não suportado"
        ):
            detector._detect_os()

    @patch("subprocess.run")
    def test_check_git_available(self, mock_run):
        """Testa detecção de Git disponível"""
        mock_run.return_value = MagicMock()
        detector = SystemDetector()

        assert detector._check_git() is True
        mock_run.assert_called_with(
            ["git", "--version"], check=True, capture_output=True, text=True
        )

    @patch("subprocess.run")
    def test_check_git_not_available(self, mock_run):
        """Testa detecção de Git não disponível"""
        mock_run.side_effect = FileNotFoundError()
        detector = SystemDetector()

        assert detector._check_git() is False
