"""
Tests for Key Management Command

Tests key generation, validation, rotation, backup, and restoration.
"""

import pytest
import os
import tempfile
import shutil
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from datetime import datetime

from mcp_proxy_adapter.commands.key_management_command import KeyManagementCommand, KeyResult
from mcp_proxy_adapter.commands.result import CommandResult, SuccessResult
from mcp_proxy_adapter.core.certificate_utils import CertificateUtils


class TestKeyResult:
    """Test KeyResult class."""
    
    def test_key_result_initialization(self):
        """Test KeyResult initialization."""
        result = KeyResult(
            key_path="/path/to/key.pem",
            key_type="RSA",
            key_size=2048,
            status="valid"
        )
        
        assert result.key_path == "/path/to/key.pem"
        assert result.key_type == "RSA"
        assert result.key_size == 2048
        assert result.status == "valid"
        assert result.error is None
    
    def test_key_result_to_dict(self):
        """Test KeyResult to_dict method."""
        result = KeyResult(
            key_path="/path/to/key.pem",
            key_type="ECDSA",
            key_size=256,
            created_date="2024-01-01T00:00:00",
            expiry_date="2025-01-01T00:00:00",
            status="valid"
        )
        
        data = result.to_dict()
        
        assert data["key_path"] == "/path/to/key.pem"
        assert data["key_type"] == "ECDSA"
        assert data["key_size"] == 256
        assert data["created_date"] == "2024-01-01T00:00:00"
        assert data["expiry_date"] == "2025-01-01T00:00:00"
        assert data["status"] == "valid"
    
    def test_key_result_get_schema(self):
        """Test KeyResult get_schema method."""
        result = KeyResult(
            key_path="/path/to/key.pem",
            key_type="RSA",
            key_size=2048,
            status="valid"
        )
        schema = result.get_schema()
        
        assert schema["type"] == "object"
        assert "key_path" in schema["properties"]
        assert "key_type" in schema["properties"]
        assert "key_size" in schema["properties"]
        assert "status" in schema["properties"]


class TestKeyManagementCommand:
    """Test KeyManagementCommand class."""
    
    @pytest.fixture
    def key_command(self):
        """Create KeyManagementCommand instance."""
        return KeyManagementCommand()
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir
    
    @pytest.fixture
    def mock_key_files(self, temp_dir):
        """Create mock key files."""
        old_key_file = os.path.join(temp_dir, "old.key")
        new_key_file = os.path.join(temp_dir, "new.key")
        
        # Create mock files
        with open(old_key_file, 'w') as f:
            f.write("MOCK OLD PRIVATE KEY")
        with open(new_key_file, 'w') as f:
            f.write("MOCK NEW PRIVATE KEY")
        
        return old_key_file, new_key_file
    
    @pytest.mark.asyncio
    async def test_key_generate_invalid_key_type(self, key_command, temp_dir):
        """Test key generation with invalid key type."""
        output_path = os.path.join(temp_dir, "test.key")
        
        result = await key_command.key_generate("INVALID", 2048, output_path)
        
        assert result.to_dict()["success"] is False
        assert "Key type must be RSA or ECDSA" in result.to_dict()["error"]["message"]
    
    @pytest.mark.asyncio
    async def test_key_generate_invalid_key_size(self, key_command, temp_dir):
        """Test key generation with invalid key size."""
        output_path = os.path.join(temp_dir, "test.key")
        
        result = await key_command.key_generate("RSA", 512, output_path)
        
        assert result.to_dict()["success"] is False
        assert "Key size must be at least 1024 bits" in result.to_dict()["error"]["message"]
    
    @pytest.mark.asyncio
    async def test_key_generate_invalid_ecdsa_key_size(self, key_command, temp_dir):
        """Test ECDSA key generation with invalid key size."""
        output_path = os.path.join(temp_dir, "test.key")
        
        result = await key_command.key_generate("ECDSA", 512, output_path)
        
        assert result.to_dict()["success"] is False
        assert "ECDSA key size must be 256, 384, or 521 bits" in result.to_dict()["error"]["message"]
    
    @pytest.mark.asyncio
    @patch.object(CertificateUtils, 'generate_private_key')
    async def test_key_generate_success(self, mock_generate, key_command, temp_dir):
        """Test successful key generation."""
        output_path = os.path.join(temp_dir, "test.key")
        
        # Mock certificate utils
        mock_generate.return_value = {
            "success": True,
            "key_type": "RSA",
            "key_size": 2048
        }
        
        result = await key_command.key_generate("RSA", 2048, output_path)
        
        assert result.to_dict()["success"] is True
        assert "key" in result.to_dict()["data"]
        assert result.to_dict()["data"]["key"]["key_type"] == "RSA"
        assert result.to_dict()["data"]["key"]["key_size"] == 2048
        assert result.to_dict()["data"]["key"]["status"] == "valid"
    
    @pytest.mark.asyncio
    @patch.object(CertificateUtils, 'generate_private_key')
    async def test_key_generate_failure(self, mock_generate, key_command, temp_dir):
        """Test key generation failure."""
        output_path = os.path.join(temp_dir, "test.key")
        
        # Mock certificate utils failure
        mock_generate.return_value = {
            "success": False,
            "error": "Key generation failed"
        }
        
        result = await key_command.key_generate("RSA", 2048, output_path)
        
        assert result.to_dict()["success"] is False
        assert "Key generation failed" in result.to_dict()["error"]["message"]
    
    @pytest.mark.asyncio
    async def test_key_validate_missing_file(self, key_command):
        """Test key validation with missing file."""
        result = await key_command.key_validate("/nonexistent/key.pem")
        
        assert result.to_dict()["success"] is False
        assert "Key file not found" in result.to_dict()["error"]["message"]
    
    @pytest.mark.asyncio
    @patch.object(CertificateUtils, 'validate_private_key')
    async def test_key_validate_success(self, mock_validate, key_command, mock_key_files):
        """Test successful key validation."""
        old_key_file, _ = mock_key_files
        
        # Mock certificate utils
        mock_validate.return_value = {
            "success": True,
            "key_type": "RSA",
            "key_size": 2048,
            "created_date": "2024-01-01T00:00:00"
        }
        
        result = await key_command.key_validate(old_key_file)
        
        assert result.to_dict()["success"] is True
        assert "key" in result.to_dict()["data"]
        assert result.to_dict()["data"]["key"]["key_type"] == "RSA"
        assert result.to_dict()["data"]["key"]["key_size"] == 2048
        assert result.to_dict()["data"]["key"]["status"] == "valid"
    
    @pytest.mark.asyncio
    @patch.object(CertificateUtils, 'validate_private_key')
    async def test_key_validate_failure(self, mock_validate, key_command, mock_key_files):
        """Test key validation failure."""
        old_key_file, _ = mock_key_files
        
        # Mock certificate utils failure
        mock_validate.return_value = {
            "success": False,
            "error": "Key validation failed"
        }
        
        result = await key_command.key_validate(old_key_file)
        
        assert result.to_dict()["success"] is False
        assert "Key validation failed" in result.to_dict()["error"]["message"]
    
    @pytest.mark.asyncio
    async def test_key_rotate_missing_old_key(self, key_command, mock_key_files):
        """Test key rotation with missing old key."""
        _, new_key_file = mock_key_files
        
        result = await key_command.key_rotate("/nonexistent/old.key", new_key_file)
        
        assert result.to_dict()["success"] is False
        assert "Old key file not found" in result.to_dict()["error"]["message"]
    
    @pytest.mark.asyncio
    async def test_key_rotate_missing_new_key(self, key_command, mock_key_files):
        """Test key rotation with missing new key."""
        old_key_file, _ = mock_key_files
        
        result = await key_command.key_rotate(old_key_file, "/nonexistent/new.key")
        
        assert result.to_dict()["success"] is False
        assert "New key file not found" in result.to_dict()["error"]["message"]
    
    @pytest.mark.asyncio
    @patch.object(CertificateUtils, 'validate_private_key')
    async def test_key_rotate_old_key_validation_failed(self, mock_validate, key_command, mock_key_files):
        """Test key rotation with old key validation failure."""
        old_key_file, new_key_file = mock_key_files
        
        # Mock certificate utils for old key validation failure
        mock_validate.side_effect = [
            {"success": False, "error": "Old key validation failed"},  # old key
            {"success": True, "key_type": "RSA", "key_size": 2048}     # new key
        ]
        
        result = await key_command.key_rotate(old_key_file, new_key_file)
        
        assert result.to_dict()["success"] is False
        assert "Old key validation failed" in result.to_dict()["error"]["message"]
    
    @pytest.mark.asyncio
    @patch.object(CertificateUtils, 'validate_private_key')
    async def test_key_rotate_new_key_validation_failed(self, mock_validate, key_command, mock_key_files):
        """Test key rotation with new key validation failure."""
        old_key_file, new_key_file = mock_key_files
        
        # Mock certificate utils for new key validation failure
        mock_validate.side_effect = [
            {"success": True, "key_type": "RSA", "key_size": 2048},    # old key
            {"success": False, "error": "New key validation failed"}   # new key
        ]
        
        result = await key_command.key_rotate(old_key_file, new_key_file)
        
        assert result.to_dict()["success"] is False
        assert "New key validation failed" in result.to_dict()["error"]["message"]
    
    @pytest.mark.asyncio
    @patch.object(CertificateUtils, 'validate_private_key')
    async def test_key_rotate_success(self, mock_validate, key_command, mock_key_files):
        """Test successful key rotation."""
        old_key_file, new_key_file = mock_key_files
        
        # Mock certificate utils for successful validation
        mock_validate.return_value = {
            "success": True,
            "key_type": "RSA",
            "key_size": 2048
        }
        
        result = await key_command.key_rotate(old_key_file, new_key_file)
        
        assert result.to_dict()["success"] is True
        assert result.to_dict()["data"]["old_key_path"] == old_key_file
        assert result.to_dict()["data"]["new_key_path"] == new_key_file
        assert result.to_dict()["data"]["backup_path"] is not None
        assert "Key rotation completed successfully" in result.to_dict()["data"]["message"]
    
    @pytest.mark.asyncio
    async def test_key_backup_missing_file(self, key_command, temp_dir):
        """Test key backup with missing file."""
        backup_path = os.path.join(temp_dir, "backup.key")
        
        result = await key_command.key_backup("/nonexistent/key.pem", backup_path)
        
        assert result.to_dict()["success"] is False
        assert "Key file not found" in result.to_dict()["error"]["message"]
    
    @pytest.mark.asyncio
    @patch.object(CertificateUtils, 'validate_private_key')
    async def test_key_backup_key_validation_failed(self, mock_validate, key_command, mock_key_files, temp_dir):
        """Test key backup with key validation failure."""
        old_key_file, _ = mock_key_files
        backup_path = os.path.join(temp_dir, "backup.key")
        
        # Mock certificate utils failure
        mock_validate.return_value = {
            "success": False,
            "error": "Key validation failed"
        }
        
        result = await key_command.key_backup(old_key_file, backup_path)
        
        assert result.to_dict()["success"] is False
        assert "Key validation failed before backup" in result.to_dict()["error"]["message"]
    
    @pytest.mark.asyncio
    @patch.object(CertificateUtils, 'validate_private_key')
    @patch.object(CertificateUtils, 'create_encrypted_backup')
    async def test_key_backup_encrypted_success(self, mock_create_backup, mock_validate, key_command, mock_key_files, temp_dir):
        """Test successful encrypted key backup."""
        old_key_file, _ = mock_key_files
        backup_path = os.path.join(temp_dir, "backup.key")
        
        # Mock certificate utils
        mock_validate.return_value = {
            "success": True,
            "key_type": "RSA",
            "key_size": 2048
        }
        
        def mock_create_backup_func(key_path, backup_path, password):
            # Create a mock backup file
            with open(backup_path, 'w') as f:
                f.write("MOCK ENCRYPTED BACKUP")
            return {"success": True}
        
        mock_create_backup.side_effect = mock_create_backup_func
        
        # Mock key_validate method
        with patch.object(key_command, 'key_validate') as mock_key_validate:
            mock_key_validate.return_value = SuccessResult(
                data={
                    "key": {
                        "key_path": old_key_file,
                        "key_type": "RSA",
                        "key_size": 2048,
                        "status": "valid"
                    }
                }
            )
        
        result = await key_command.key_backup(old_key_file, backup_path, encrypt_backup=True, password="testpass")
        
        assert result.to_dict()["success"] is True
        assert result.to_dict()["data"]["key_path"] == old_key_file
        assert result.to_dict()["data"]["backup_path"] == backup_path
        assert result.to_dict()["data"]["encrypted"] is True
        assert "backup_date" in result.to_dict()["data"]
    
    @pytest.mark.asyncio
    @patch.object(CertificateUtils, 'validate_private_key')
    @patch.object(CertificateUtils, 'create_encrypted_backup')
    async def test_key_backup_encrypted_failure(self, mock_create_backup, mock_validate, key_command, mock_key_files, temp_dir):
        """Test encrypted key backup failure."""
        old_key_file, _ = mock_key_files
        backup_path = os.path.join(temp_dir, "backup.key")
        
        # Mock certificate utils
        mock_validate.return_value = {
            "success": True,
            "key_type": "RSA",
            "key_size": 2048
        }
        mock_create_backup.return_value = {
            "success": False,
            "error": "Encryption failed"
        }
        
        result = await key_command.key_backup(old_key_file, backup_path, encrypt_backup=True, password="testpass")
        
        assert result.to_dict()["success"] is False
        assert "Encrypted backup failed" in result.to_dict()["error"]["message"]
    
    @pytest.mark.asyncio
    @patch.object(CertificateUtils, 'validate_private_key')
    async def test_key_backup_simple_success(self, mock_validate, key_command, mock_key_files, temp_dir):
        """Test successful simple key backup."""
        old_key_file, _ = mock_key_files
        backup_path = os.path.join(temp_dir, "backup.key")
        
        # Mock certificate utils
        mock_validate.return_value = {
            "success": True,
            "key_type": "RSA",
            "key_size": 2048
        }
        
        result = await key_command.key_backup(old_key_file, backup_path, encrypt_backup=False)
        
        assert result.to_dict()["success"] is True
        assert result.to_dict()["data"]["key_path"] == old_key_file
        assert result.to_dict()["data"]["backup_path"] == backup_path
        assert result.to_dict()["data"]["encrypted"] is False
        assert "backup_date" in result.to_dict()["data"]
        assert os.path.exists(backup_path)
    
    @pytest.mark.asyncio
    async def test_key_restore_missing_backup(self, key_command, temp_dir):
        """Test key restore with missing backup file."""
        key_path = os.path.join(temp_dir, "restored.key")
        
        result = await key_command.key_restore("/nonexistent/backup.key", key_path)
        
        assert result.to_dict()["success"] is False
        assert "Backup file not found" in result.to_dict()["error"]["message"]
    
    @pytest.mark.asyncio
    @patch.object(CertificateUtils, 'restore_encrypted_backup')
    @patch.object(CertificateUtils, 'validate_private_key')
    async def test_key_restore_encrypted_success(self, mock_validate, mock_restore, key_command, mock_key_files, temp_dir):
        """Test successful encrypted key restore."""
        old_key_file, _ = mock_key_files
        backup_path = os.path.join(temp_dir, "backup.key")
        restored_key_path = os.path.join(temp_dir, "restored.key")
        
        # Copy old key as backup
        shutil.copy2(old_key_file, backup_path)
        
        # Mock certificate utils
        def mock_restore_func(backup_path, key_path, password):
            # Create a mock restored key file
            with open(key_path, 'w') as f:
                f.write("MOCK RESTORED KEY")
            return {"success": True}
        
        mock_restore.side_effect = mock_restore_func
        mock_validate.return_value = {
            "success": True,
            "key_type": "RSA",
            "key_size": 2048
        }
        
        # Mock key_validate method
        with patch.object(key_command, 'key_validate') as mock_key_validate:
            mock_key_validate.return_value = SuccessResult(
                data={
                    "key": {
                        "key_path": restored_key_path,
                        "key_type": "RSA",
                        "key_size": 2048,
                        "status": "valid"
                    }
                }
            )
        
        result = await key_command.key_restore(backup_path, restored_key_path, password="testpass")
        
        assert result.to_dict()["success"] is True
        assert result.to_dict()["data"]["backup_path"] == backup_path
        assert result.to_dict()["data"]["key_path"] == restored_key_path
        assert "restore_date" in result.to_dict()["data"]
    
    @pytest.mark.asyncio
    @patch.object(CertificateUtils, 'restore_encrypted_backup')
    async def test_key_restore_encrypted_failure(self, mock_restore, key_command, mock_key_files, temp_dir):
        """Test encrypted key restore failure."""
        old_key_file, _ = mock_key_files
        backup_path = os.path.join(temp_dir, "backup.key")
        restored_key_path = os.path.join(temp_dir, "restored.key")
        
        # Copy old key as backup
        shutil.copy2(old_key_file, backup_path)
        
        # Mock certificate utils failure
        mock_restore.return_value = {
            "success": False,
            "error": "Decryption failed"
        }
        
        result = await key_command.key_restore(backup_path, restored_key_path, password="testpass")
        
        assert result.to_dict()["success"] is False
        assert "Encrypted restore failed" in result.to_dict()["error"]["message"]
    
    @pytest.mark.asyncio
    @patch.object(CertificateUtils, 'validate_private_key')
    async def test_key_restore_simple_success(self, mock_validate, key_command, mock_key_files, temp_dir):
        """Test successful simple key restore."""
        old_key_file, _ = mock_key_files
        backup_path = os.path.join(temp_dir, "backup.key")
        restored_key_path = os.path.join(temp_dir, "restored.key")
        
        # Copy old key as backup
        shutil.copy2(old_key_file, backup_path)
        
        # Mock certificate utils
        mock_validate.return_value = {
            "success": True,
            "key_type": "RSA",
            "key_size": 2048
        }
        
        result = await key_command.key_restore(backup_path, restored_key_path)
        
        assert result.to_dict()["success"] is True
        assert result.to_dict()["data"]["backup_path"] == backup_path
        assert result.to_dict()["data"]["key_path"] == restored_key_path
        assert "restore_date" in result.to_dict()["data"]
        assert os.path.exists(restored_key_path)
    
    @pytest.mark.asyncio
    @patch.object(CertificateUtils, 'validate_private_key')
    async def test_key_restore_validation_failed(self, mock_validate, key_command, mock_key_files, temp_dir):
        """Test key restore with validation failure."""
        old_key_file, _ = mock_key_files
        backup_path = os.path.join(temp_dir, "backup.key")
        restored_key_path = os.path.join(temp_dir, "restored.key")
        
        # Copy old key as backup
        shutil.copy2(old_key_file, backup_path)
        
        # Mock certificate utils
        mock_validate.return_value = {
            "success": False,
            "error": "Restored key validation failed"
        }
        
        result = await key_command.key_restore(backup_path, restored_key_path)
        
        assert result.to_dict()["success"] is False
        assert "Restored key validation failed" in result.to_dict()["error"]["message"]
    
    @pytest.mark.asyncio
    @patch.object(CertificateUtils, 'generate_private_key')
    async def test_key_generate_exception_handling(self, mock_generate, key_command, temp_dir):
        """Test key generation exception handling."""
        output_path = os.path.join(temp_dir, "test.key")
        
        mock_generate.side_effect = Exception("Test exception")
        result = await key_command.key_generate("RSA", 2048, output_path)
        
        assert result.to_dict()["success"] is False
        assert "Key generation failed" in result.to_dict()["error"]["message"]
    
    @pytest.mark.asyncio
    @patch.object(CertificateUtils, 'validate_private_key')
    async def test_key_validate_exception_handling(self, mock_validate, key_command, mock_key_files):
        """Test key validation exception handling."""
        old_key_file, _ = mock_key_files
        
        mock_validate.side_effect = Exception("Test exception")
        result = await key_command.key_validate(old_key_file)
        
        assert result.to_dict()["success"] is False
        assert "Key validation failed" in result.to_dict()["error"]["message"]
    
    @pytest.mark.asyncio
    @patch.object(CertificateUtils, 'validate_private_key')
    async def test_key_rotate_exception_handling(self, mock_validate, key_command, mock_key_files):
        """Test key rotation exception handling."""
        old_key_file, new_key_file = mock_key_files
        
        mock_validate.side_effect = Exception("Test exception")
        result = await key_command.key_rotate(old_key_file, new_key_file)
        
        assert result.to_dict()["success"] is False
        assert "Old key validation failed" in result.to_dict()["error"]["message"]
    
    @pytest.mark.asyncio
    @patch.object(CertificateUtils, 'validate_private_key')
    async def test_key_backup_exception_handling(self, mock_validate, key_command, mock_key_files, temp_dir):
        """Test key backup exception handling."""
        old_key_file, _ = mock_key_files
        backup_path = os.path.join(temp_dir, "backup.key")
        
        mock_validate.side_effect = Exception("Test exception")
        result = await key_command.key_backup(old_key_file, backup_path)
        
        assert result.to_dict()["success"] is False
        assert "Key validation failed before backup" in result.to_dict()["error"]["message"]
    
    @pytest.mark.asyncio
    @patch.object(CertificateUtils, 'validate_private_key')
    async def test_key_restore_exception_handling(self, mock_validate, key_command, mock_key_files, temp_dir):
        """Test key restore exception handling."""
        old_key_file, _ = mock_key_files
        backup_path = os.path.join(temp_dir, "backup.key")
        restored_key_path = os.path.join(temp_dir, "restored.key")
        
        # Copy old key as backup
        shutil.copy2(old_key_file, backup_path)
        
        mock_validate.side_effect = Exception("Test exception")
        result = await key_command.key_restore(backup_path, restored_key_path)
        
        assert result.to_dict()["success"] is False
        assert "Restored key validation failed" in result.to_dict()["error"]["message"] 