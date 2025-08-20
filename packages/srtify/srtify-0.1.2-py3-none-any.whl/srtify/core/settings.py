import json
from pathlib import Path
from platformdirs import user_documents_path
from typing import Tuple, Optional
from srtify.core.models import AppSettings, ApiConfig, DirectoryConfig, TranslationConfig
from srtify.utils.paths import get_config_path


home_dir = Path.home()
DEFAULT_INPUT_DIR = str(user_documents_path() / "Subtitles")
DEFAULT_OUTPUT_DIR = str(user_documents_path() / "Subtitles" / "Translated")


class SettingsManager:
    """Settings manager with dataclass-based configuration."""

    def __init__(self, config_file: str = None):
        self.config_file = Path(config_file) if config_file else get_config_path()
        self.settings = self._load_settings()

    def _load_settings(self) -> AppSettings:
        """Load settings from file or create defaults."""
        self.config_file.parent.mkdir(exist_ok=True)

        default_settings = AppSettings(
            api=ApiConfig(),
            directories=DirectoryConfig(
                input_dir=DEFAULT_INPUT_DIR,
                output_dir=DEFAULT_OUTPUT_DIR
            ),
            translation=TranslationConfig()
        )

        if not self.config_file.exists():
            self._save_settings(default_settings)
            return default_settings

        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return AppSettings.from_dict(data)
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            print(f"Error loading settings: {e}. Using defaults.")
            backup_file = self.config_file.with_suffix('.json.backup')
            if self.config_file.exists():
                self.config_file.rename(backup_file)
                print(f"Backed up corrupted config to {backup_file}")

            self._save_settings(default_settings)
            return default_settings

    def _save_settings(self, settings: Optional[AppSettings] = None):
        """Save current settings to file."""
        if settings is None:
            settings = self.settings

        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(settings.to_dict(), f, indent=2, ensure_ascii=False)
            return True
        except (IOError, OSError) as e:
            print(f"Error saving configuration: {e}")
            return False

    def reload(self) -> bool:
        """Reload settings from file."""
        try:
            self.settings = self._load_settings()
            return True
        except Exception as e:
            print(f"Error reloading settings: {e}")
            return False

    def get_api_key(self) -> str:
        """Get the API key."""
        return self.settings.api.gemini_key

    def set_api_key(self, api_key: str) -> bool:
        """Set the API key with validation."""
        if not api_key or not api_key.strip():
            raise ValueError("API key cannot be empty.")

        self.settings.api.gemini_key = api_key.strip()
        return self._save_settings()

    def is_api_key_valid(self) -> bool:
        """Check if the API key is valid."""
        return self.settings.api.is_valid()

    def get_directories(self) -> Tuple[str, str]:
        """Get input and output directories."""
        return (
            self.settings.directories.input_dir,
            self.settings.directories.output_dir
        )

    def set_directories(self, input_dir: str, output_dir: str) -> bool:
        """Set input and output directories with validation."""
        if not input_dir or not input_dir.strip():
            raise ValueError("Input directory cannot be empty.")
        if not output_dir or not output_dir.strip():
            raise ValueError("Output directory cannot be empty.")

        new_dirs = DirectoryConfig(
            input_dir=input_dir.strip(),
            output_dir=output_dir.strip()
        )

        if not new_dirs.validate():
            raise ValueError("One or both directories are invalid or inaccessible.")

        self.settings.directories = new_dirs
        return self._save_settings()

    def ensure_directories_exist(self) -> bool:
        """Ensure input and output directories exist."""
        return self.settings.directories.validate()

    # def get_translation_config(self) -> Tuple[str, int]:
    #     """Get translation configuration."""
    #     return (
    #         self.settings.translation.default_language,
    #         self.settings.translation.batch_size
    #     )

    def get_translation_language(self) -> str:
        return self.settings.translation.default_language

    def get_translation_batch_size(self) -> int:
        return self.settings.translation.batch_size

    # def set_translation_config(self, language: str, batch_size: int) -> bool:
    #     """Set translation configuration with validation."""
    #     if not language or not language.strip():
    #         raise ValueError("Default language cannot be empty.")
    #
    #     if batch_size <= 0:
    #         raise ValueError("Batch size must be a positive integer.")
    #
    #     self.settings.translation.default_language = language.strip()
    #     self.settings.translation.batch_size = batch_size
    #     return self._save_settings()

    def set_translation_language(self, language: str) -> bool:
        if not language or not language.strip():
            raise ValueError("Default language cannot be empty.")

        self.settings.translation.default_language = language.strip()
        return self._save_settings()

    def set_translation_batch_size(self, batch_size: int) -> bool:
        if batch_size <= 0:
            raise ValueError("Batch size must be a positive integer.")

        self.settings.translation.batch_size = batch_size
        return self._save_settings()

    def validate_all(self) -> bool:
        """Validate all settings."""
        return self.settings.validate()

    def reset_to_defaults(self) -> bool:
        """Reset all settings to defaults."""
        self.settings = AppSettings(
            api=ApiConfig(),
            directories=DirectoryConfig(
                input_dir=DEFAULT_INPUT_DIR,
                output_dir=DEFAULT_OUTPUT_DIR
            ),
            translation=TranslationConfig()
        )
        return self._save_settings()

    def export_settings(self, file_path: str) -> bool:
        """Export settings to a file."""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.settings.to_dict(), f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error exporting settings: {e}")
            return False

    def import_settings(self, file_path: str) -> bool:
        """Import settings from a file."""

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                new_settings = AppSettings.from_dict(data)

                if new_settings.validate():
                    self.settings = new_settings
                    return self._save_settings()
                else:
                    print("Imported settings are invalid.")
                    return False
        except Exception as e:
            print(f"Error importing settings: {e}")
            return False

    def get_settings_summary(self) -> dict:
        """Get a summary of current settings."""
        return {
            "API Key": "Set" if self.is_api_key_valid() else "Not Set",
            "Input Directory": self.settings.directories.input_dir,
            "Output Directory": self.settings.directories.output_dir,
            "Language": self.settings.translation.default_language,
            "Batch Size": self.settings.translation.batch_size,
            "Directories Valid": self.settings.directories.validate()
        }