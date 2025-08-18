from re import Pattern
from cpplint_fix.config import CPPLFixConfig


def test_cppl_fix_config():
    """Test the CPPLFixConfig model."""
    
    content = r"""{
        "exclude_rules": ["whitespace/line_length", "build/include_order"],
        "exclude_files": [".*test.*\\.cpp", ".*example.*\\.h"]
    }"""
    
    config = CPPLFixConfig.model_validate_json(content)
    
    assert config.exclude_rules == ["whitespace/line_length", "build/include_order"]
    assert len(config.exclude_files) == 2
    assert all(isinstance(pattern, Pattern) for pattern in config.exclude_files)
    assert config.exclude_files[0].match("path/test_file.cpp")  # Should match
    assert config.exclude_files[1].match("example_file.h")  # Should match
    assert not config.exclude_files[0].match("other_file.cpp")  # Should not match
    
    # Test that extra fields are forbidden
    try:
        CPPLFixConfig(extra_field="should_fail") # type: ignore
    except ValueError as e:
        assert "Extra inputs are not permitted" in str(e)
        
def test_cppl_fix_config_yaml():
    """Test the CPPLFixConfig model with YAML content."""
    
    content = """
    exclude_rules:
      - whitespace/line_length
      - build/include_order
    exclude_files:
      - '.*test.*\\.cpp'
      - '.*example.*\\.h'
    """
    
    config = CPPLFixConfig.model_validate_yaml(content)
    
    assert config.exclude_rules == ["whitespace/line_length", "build/include_order"]
    assert len(config.exclude_files) == 2
    assert all(isinstance(pattern, Pattern) for pattern in config.exclude_files)
    assert config.exclude_files[0].match("test_file.cpp")  # Should match
    assert config.exclude_files[1].match("example_file.h")  # Should match
    assert not config.exclude_files[0].match("other_file.cpp")  # Should not match