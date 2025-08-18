from re import Pattern
from yaml import safe_load
from pydantic import BaseModel, Field, ConfigDict


class CPPLFixConfig(BaseModel):
    """Configuration for CPPLint Fix."""
    
    model_config = ConfigDict(
        extra='forbid',  # Forbid extra fields
        validate_assignment=True,  # Validate assignments to fields
    )
    
    exclude_rules: list[str] = Field(
        default_factory=list,
        description="List of CPPLint rules to exclude from fixing."
    )
    
    exclude_files: list[Pattern] = Field(
        default_factory=list,
        description="List of regex patterns for file paths to exclude from fixing."
    )
    
    @classmethod
    def model_validate_yaml(cls, content: str) -> "CPPLFixConfig":
        """Validate and parse YAML content into a CPPLFixConfig instance."""
        data = safe_load(content)
        return cls.model_validate(data)