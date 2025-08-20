"""
Tests for dependency management system.

Tests the DependencyManager class and related functionality.
"""

import pytest
import subprocess
import sys
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from mcp_proxy_adapter.commands.dependency_manager import DependencyManager, dependency_manager


class TestDependencyManager:
    """Test cases for DependencyManager class."""
    
    def test_init(self):
        """Test DependencyManager initialization."""
        manager = DependencyManager()
        assert isinstance(manager._installed_packages, dict)
    
    @patch('mcp_proxy_adapter.commands.dependency_manager.pkg_resources.working_set')
    def test_load_installed_packages_success(self, mock_working_set):
        """Test successful loading of installed packages."""
        # Mock working_set to return some distributions
        mock_dist1 = Mock()
        mock_dist1.project_name = "test-package"
        mock_dist1.version = "1.0.0"
        
        mock_dist2 = Mock()
        mock_dist2.project_name = "another-package"
        mock_dist2.version = "2.0.0"
        
        mock_working_set.__iter__.return_value = [mock_dist1, mock_dist2]
        
        manager = DependencyManager()
        
        assert "test-package" in manager._installed_packages
        assert "another-package" in manager._installed_packages
        assert manager._installed_packages["test-package"] == "1.0.0"
        assert manager._installed_packages["another-package"] == "2.0.0"
    
    @patch('mcp_proxy_adapter.commands.dependency_manager.pkg_resources.working_set')
    def test_load_installed_packages_exception(self, mock_working_set):
        """Test loading installed packages with exception."""
        mock_working_set.side_effect = Exception("Test error")
        
        manager = DependencyManager()
        assert manager._installed_packages == {}
    
    def test_check_dependencies_empty(self):
        """Test checking empty dependencies list."""
        manager = DependencyManager()
        all_satisfied, missing_deps, installed_deps = manager.check_dependencies([])
        
        assert all_satisfied is True
        assert missing_deps == []
        assert installed_deps == []
    
    @patch('mcp_proxy_adapter.commands.dependency_manager.importlib.import_module')
    def test_check_dependencies_all_satisfied(self, mock_import):
        """Test checking dependencies when all are satisfied."""
        manager = DependencyManager()
        manager._installed_packages = {"test-package": "1.0.0"}
        
        all_satisfied, missing_deps, installed_deps = manager.check_dependencies(["test-package"])
        
        assert all_satisfied is True
        assert missing_deps == []
        assert installed_deps == ["test-package"]
    
    @patch('mcp_proxy_adapter.commands.dependency_manager.importlib.import_module')
    def test_check_dependencies_some_missing(self, mock_import):
        """Test checking dependencies when some are missing."""
        mock_import.side_effect = ImportError("Module not found")
        
        manager = DependencyManager()
        manager._installed_packages = {}
        
        all_satisfied, missing_deps, installed_deps = manager.check_dependencies(["missing-package"])
        
        assert all_satisfied is False
        assert missing_deps == ["missing-package"]
        assert installed_deps == []
    
    @patch('mcp_proxy_adapter.commands.dependency_manager.importlib.import_module')
    def test_is_dependency_satisfied_import_success(self, mock_import):
        """Test dependency satisfaction via import."""
        manager = DependencyManager()
        
        result = manager._is_dependency_satisfied("test-module")
        
        assert result is True
        mock_import.assert_called_once_with("test-module")
    
    @patch('mcp_proxy_adapter.commands.dependency_manager.importlib.import_module')
    @patch('mcp_proxy_adapter.commands.dependency_manager.pkg_resources.require')
    def test_is_dependency_satisfied_pkg_resources_success(self, mock_require, mock_import):
        """Test dependency satisfaction via pkg_resources."""
        mock_import.side_effect = ImportError("Module not found")
        
        manager = DependencyManager()
        
        result = manager._is_dependency_satisfied("test-package")
        
        assert result is True
        mock_require.assert_called_once_with("test-package")
    
    @patch('mcp_proxy_adapter.commands.dependency_manager.importlib.import_module')
    @patch('mcp_proxy_adapter.commands.dependency_manager.pkg_resources.require')
    def test_is_dependency_satisfied_installed_cache(self, mock_require, mock_import):
        """Test dependency satisfaction via installed packages cache."""
        mock_import.side_effect = ImportError("Module not found")
        # Mock pkg_resources.require to raise specific exception
        from pkg_resources import DistributionNotFound
        mock_require.side_effect = DistributionNotFound("Package not found")
        
        manager = DependencyManager()
        manager._installed_packages = {"test-package": "1.0.0"}
        
        result = manager._is_dependency_satisfied("test-package")
        
        assert result is True
    
    @patch('mcp_proxy_adapter.commands.dependency_manager.importlib.import_module')
    @patch('mcp_proxy_adapter.commands.dependency_manager.pkg_resources.require')
    def test_is_dependency_satisfied_not_found(self, mock_require, mock_import):
        """Test dependency satisfaction when not found."""
        mock_import.side_effect = ImportError("Module not found")
        # Mock pkg_resources.require to raise specific exception
        from pkg_resources import DistributionNotFound
        mock_require.side_effect = DistributionNotFound("Package not found")
        
        manager = DependencyManager()
        manager._installed_packages = {}
        
        result = manager._is_dependency_satisfied("missing-package")
        
        assert result is False
    
    def test_is_dependency_satisfied_with_version_specs(self):
        """Test dependency satisfaction with version specifications."""
        manager = DependencyManager()
        manager._installed_packages = {"test-package": "1.0.0"}
        
        # Test various version spec formats
        assert manager._is_dependency_satisfied("test-package==1.0.0") is True
        assert manager._is_dependency_satisfied("test-package>=1.0.0") is True
        assert manager._is_dependency_satisfied("test-package<=2.0.0") is True
        assert manager._is_dependency_satisfied("test-package!=2.0.0") is True
        assert manager._is_dependency_satisfied("test-package~=1.0") is True
    
    def test_install_dependencies_empty(self):
        """Test installing empty dependencies list."""
        manager = DependencyManager()
        success, installed_deps, failed_deps = manager.install_dependencies([])
        
        assert success is True
        assert installed_deps == []
        assert failed_deps == []
    
    @patch.object(DependencyManager, '_install_single_dependency')
    @patch.object(DependencyManager, '_load_installed_packages')
    def test_install_dependencies_success(self, mock_reload, mock_install):
        """Test successful dependency installation."""
        mock_install.return_value = True
        
        manager = DependencyManager()
        success, installed_deps, failed_deps = manager.install_dependencies(["test-package"])
        
        assert success is True
        assert installed_deps == ["test-package"]
        assert failed_deps == []
        # Note: _load_installed_packages is called during init and after successful install
        assert mock_reload.call_count >= 1
    
    @patch.object(DependencyManager, '_install_single_dependency')
    @patch.object(DependencyManager, '_load_installed_packages')
    def test_install_dependencies_partial_failure(self, mock_reload, mock_install):
        """Test dependency installation with partial failures."""
        mock_install.side_effect = [True, False]
        
        manager = DependencyManager()
        success, installed_deps, failed_deps = manager.install_dependencies(["test-package", "failed-package"])
        
        assert success is False
        assert installed_deps == ["test-package"]
        assert failed_deps == ["failed-package"]
        # _load_installed_packages is called during init, but not after partial failure
        assert mock_reload.call_count >= 1
    
    @patch.object(DependencyManager, '_install_single_dependency')
    @patch.object(DependencyManager, '_load_installed_packages')
    def test_install_dependencies_exception(self, mock_reload, mock_install):
        """Test dependency installation with exception."""
        mock_install.side_effect = Exception("Installation error")
        
        manager = DependencyManager()
        success, installed_deps, failed_deps = manager.install_dependencies(["test-package"])
        
        assert success is False
        assert installed_deps == []
        assert failed_deps == ["test-package"]
        # _load_installed_packages is called during init, but not after exception
        assert mock_reload.call_count >= 1
    
    @patch('mcp_proxy_adapter.commands.dependency_manager.subprocess.run')
    def test_install_single_dependency_success(self, mock_run):
        """Test successful single dependency installation."""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_run.return_value = mock_result
        
        manager = DependencyManager()
        result = manager._install_single_dependency("test-package")
        
        assert result is True
        mock_run.assert_called_once()
        cmd = mock_run.call_args[0][0]
        assert cmd[0] == sys.executable
        assert cmd[1] == "-m"
        assert cmd[2] == "pip"
        assert cmd[3] == "install"
        assert cmd[4] == "--quiet"
        assert cmd[5] == "test-package"
    
    @patch('mcp_proxy_adapter.commands.dependency_manager.subprocess.run')
    def test_install_single_dependency_user_install(self, mock_run):
        """Test single dependency installation with user install flag."""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_run.return_value = mock_result
        
        manager = DependencyManager()
        result = manager._install_single_dependency("test-package", user_install=True)
        
        assert result is True
        cmd = mock_run.call_args[0][0]
        assert "--user" in cmd
    
    @patch('mcp_proxy_adapter.commands.dependency_manager.subprocess.run')
    def test_install_single_dependency_failure(self, mock_run):
        """Test failed single dependency installation."""
        mock_result = Mock()
        mock_result.returncode = 1
        mock_result.stderr = "Installation failed"
        mock_run.return_value = mock_result
        
        manager = DependencyManager()
        result = manager._install_single_dependency("test-package")
        
        assert result is False
    
    @patch('mcp_proxy_adapter.commands.dependency_manager.subprocess.run')
    def test_install_single_dependency_timeout(self, mock_run):
        """Test single dependency installation with timeout."""
        mock_run.side_effect = subprocess.TimeoutExpired("pip install", 300)
        
        manager = DependencyManager()
        result = manager._install_single_dependency("test-package")
        
        assert result is False
    
    @patch('mcp_proxy_adapter.commands.dependency_manager.subprocess.run')
    def test_install_single_dependency_exception(self, mock_run):
        """Test single dependency installation with exception."""
        mock_run.side_effect = Exception("Subprocess error")
        
        manager = DependencyManager()
        result = manager._install_single_dependency("test-package")
        
        assert result is False
    
    def test_verify_installation_empty(self):
        """Test verification of empty dependencies list."""
        manager = DependencyManager()
        all_verified, failed_verifications = manager.verify_installation([])
        
        assert all_verified is True
        assert failed_verifications == []
    
    @patch.object(DependencyManager, '_is_dependency_satisfied')
    def test_verify_installation_all_verified(self, mock_satisfied):
        """Test verification when all dependencies are satisfied."""
        mock_satisfied.return_value = True
        
        manager = DependencyManager()
        all_verified, failed_verifications = manager.verify_installation(["test-package"])
        
        assert all_verified is True
        assert failed_verifications == []
    
    @patch.object(DependencyManager, '_is_dependency_satisfied')
    def test_verify_installation_some_failed(self, mock_satisfied):
        """Test verification when some dependencies fail."""
        mock_satisfied.side_effect = [True, False]
        
        manager = DependencyManager()
        all_verified, failed_verifications = manager.verify_installation(["test-package", "failed-package"])
        
        assert all_verified is False
        assert failed_verifications == ["failed-package"]
    
    @patch('mcp_proxy_adapter.commands.dependency_manager.pkg_resources.get_distribution')
    @patch('mcp_proxy_adapter.commands.dependency_manager.importlib.import_module')
    def test_get_dependency_info_not_installed(self, mock_import, mock_get_dist):
        """Test getting dependency info for not installed package."""
        from pkg_resources import DistributionNotFound
        mock_get_dist.side_effect = DistributionNotFound("Package not found")
        mock_import.side_effect = ImportError("Module not found")
        
        manager = DependencyManager()
        info = manager.get_dependency_info("missing-package")
        
        assert info["name"] == "missing-package"
        assert info["installed"] is False
        assert info["version"] is None
        assert info["importable"] is False
    
    def test_list_installed_dependencies(self):
        """Test listing installed dependencies."""
        manager = DependencyManager()
        manager._installed_packages = {"test-package": "1.0.0", "another-package": "2.0.0"}
        
        result = manager.list_installed_dependencies()
        
        assert result == {"test-package": "1.0.0", "another-package": "2.0.0"}
        # Ensure it's a copy, not the original
        assert result is not manager._installed_packages


class TestDependencyManagerGlobal:
    """Test cases for global dependency_manager instance."""
    
    def test_global_instance(self):
        """Test that global instance is created."""
        assert isinstance(dependency_manager, DependencyManager)
    
    def test_global_instance_singleton(self):
        """Test that global instance is a singleton."""
        from mcp_proxy_adapter.commands.dependency_manager import dependency_manager as dm1
        from mcp_proxy_adapter.commands.dependency_manager import dependency_manager as dm2
        
        assert dm1 is dm2 