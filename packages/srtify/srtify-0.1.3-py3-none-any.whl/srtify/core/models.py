import os
from dataclasses import dataclass, field, asdict
from typing import Dict, Optional, Any
from pathlib import Path
from datetime import datetime


@dataclass
class ApiConfig:
    """API Configuration settings."""
    gemini_key: str = ""

    def is_valid(self) -> bool:
        return bool(self.gemini_key.strip())


@dataclass
class DirectoryConfig:
    """Directory configuration settings."""
    input_dir: str = ""
    output_dir: str = ""

    def __post_init__(self):
        """Expand user paths after initialization."""
        if self.input_dir:
            self.input_dir = os.path.expanduser(self.input_dir)
        if self.output_dir:
            self.output_dir = os.path.expanduser(self.output_dir)

    def validate(self) -> bool:
        """Validate directory paths."""
        if not self.input_dir or not self.output_dir:
            return False

        try:
            Path(self.input_dir).mkdir(parents=True, exist_ok=True)
            Path(self.output_dir).mkdir(parents=True, exist_ok=True)
            return True
        except (OSError, PermissionError):
            return False


@dataclass
class TranslationConfig:
    """Translation configuration settings."""
    default_language: str = "Persian"
    batch_size: int = 300

    def __post_init__(self):
        if self.batch_size <= 0:
            self.batch_size = 300


@dataclass
class AppSettings:
    api: ApiConfig = field(default_factory=ApiConfig)
    directories: DirectoryConfig = field(default_factory=DirectoryConfig)
    translation: TranslationConfig = field(default_factory=TranslationConfig)

    def to_dict(self) -> Dict[str, Any]:
        """Convert settings to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AppSettings':
        api_data = data.get('api', {})
        dir_data = data.get('directories', {})
        trans_data = data.get('translation', {})

        return cls(
            api=ApiConfig(**api_data),
            directories=DirectoryConfig(**dir_data),
            translation=TranslationConfig(**trans_data)
        )

    def validate(self) -> bool:
        return (self.api.is_valid() and
                self.directories.validate() and
                self.translation.batch_size > 0)


@dataclass
class PromptItem:
    """Individual prompt item."""
    name: str
    description: str
    created_at: Optional[str] = None
    last_used: Optional[str] = None

    def __post_init__(self):
        """Set creation item if not provided."""
        if not self.created_at:
            self.created_at = datetime.now().isoformat()


@dataclass
class PromptsCollection:
    """Collection of prompts with metadata."""
    prompts: Dict[str, PromptItem] = field(default_factory=dict)
    version: str = "1.0"

    def add_prompt(self, name: str, description: str) -> bool:
        """Add a new prompt."""
        if name in self.prompts:
            return False

        self.prompts[name] = PromptItem(name=name, description=description)
        return True

    def update_prompt(self, name: str, description: str) -> bool:
        """Update an existing prompt."""
        if name not in self.prompts:
            return False

        self.prompts[name].description = description
        return True

    def delete_prompt(self, name: str) -> bool:
        """Delete a prompt."""
        if name not in self.prompts:
            return False

        del self.prompts[name]
        return True

    def get_prompt_names(self) -> list[str]:
        """Get a list of prompt names."""
        return list(self.prompts.keys())

    def get_prompt_descriptions(self) -> Dict[str, str]:
        """Get dictionary of name -> description mapping."""
        return {name: prompt.description for name, prompt in self.prompts.items()}

    def mark_used(self, name: str):
        """Mark prompt as recently used."""
        if name in self.prompts:
            self.prompts[name].last_used = datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """Convert dictionary from JSON serialization."""
        return {
            'prompts': {name: asdict(prompt) for name, prompt in self.prompts.items()},
            'version': self.version
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PromptsCollection':
        """Create instance from dictionary."""
        prompts_data = data.get('prompts', {})
        prompts = {}

        for name, prompt_data in prompts_data.items():
            prompts[name] = PromptItem(**prompt_data)

        return cls(
            prompts=prompts,
            version=data.get('version', '1.0')
        )

    @classmethod
    def from_legacy_dict(cls, data: Dict[str, str]) -> 'PromptsCollection':
        """Create instance from legacy dictionary."""
        collection = cls()
        for name, description in data.items():
            collection.add_prompt(name, description)
        return collection