import json
from pathlib import Path
from typing import Dict, List, Optional
from srtify.core.models import PromptsCollection, PromptItem
from srtify.utils.paths import get_prompts_path


class PromptsManager:
    """Prompts manager class."""
    def __init__(self, file_path: str = None):
        self.file_path = Path(file_path) if file_path else get_prompts_path()
        self.collection = self._load_prompts()

    def _load_prompts(self) -> PromptsCollection:
        """Load prompts from file or create an empty collection."""
        self.file_path.parent.mkdir(exist_ok=True)

        if not self.file_path.exists():
            collection = PromptsCollection()
            self._save_prompts(collection)
            return collection

        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

                if isinstance(data, dict) and 'prompts' not in data:
                    print("Converting legacy prompts format...")
                    collection = PromptsCollection.from_legacy_dict(data)
                    self._save_prompts(collection)
                    return collection

                return PromptsCollection.from_dict(data)

        except (json.JSONDecodeError, KeyError, TypeError) as e:
            print(f"Error loading prompts file: {e}. Creating new collection.")

            backup_file = self.file_path.with_suffix('.json.backup')
            if self.file_path.exists():
                self.file_path.rename(backup_file)
                print(f"Backed up corrupt prompts file to {backup_file}")

            collection = PromptsCollection()
            self._save_prompts(collection)
            return collection

    def _save_prompts(self, collection: Optional[PromptsCollection] = None) -> bool:
        """Save current prompts to file."""
        if collection is None:
            collection = self.collection

        try:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(collection.to_dict(), f, indent=2, ensure_ascii=False)
            return True
        except (IOError, OSError) as e:
            print(f"Error saving prompts file: {e}")
            return False

    def reload(self) -> bool:
        """Reload prompts from file."""
        try:
            self.collection = self._load_prompts()
            return True
        except Exception as e:
            print(f"Error reloading prompts: {e}")
            return False

    def add_prompt(self, name: str, description: str) -> bool:
        """Add a new prompt."""
        if not name or not name.strip():
            raise ValueError("Prompt name cannot be empty.")
        if not description or not description.strip():
            raise ValueError("Prompt description cannot be empty.")

        name = name.strip()
        description = description.strip()

        if self.collection.add_prompt(name, description):
            if self._save_prompts():
                # print(f"✓ Prompt '{name}' added successfully.")
                return True
            else:
                self.collection.delete_prompt(name)
                # print(f"✗ Failed to save prompt '{name}'.")
                return False
        else:
            print(f"✗ Prompt '{name}' already exists.")
            return False

    def update_prompt(self, name: str, description: str) -> bool:
        """Update an existing prompt."""
        if not name or not name.strip():
            raise ValueError("Prompt name cannot be empty.")
        if not description or not description.strip():
            raise ValueError("Prompt description cannot be empty.")

        name = name.strip()
        description = description.strip()

        if self.collection.update_prompt(name, description):
            if self._save_prompts():
                print(f"✓ Prompt '{name}' updated successfully.")
                return True
            else:
                print(f"✗ Failed to save prompt '{name}'.")
                return False
        else:
            print(f"✗ Prompt '{name}' does not exist.")
            return False

    def delete_prompt(self, name: str) -> bool:
        """Delete a prompt."""
        if not name or not name.strip():
            raise ValueError("Prompt name cannot be empty.")

        name = name.strip()

        backup_prompt = self.collection.prompts.get(name)

        if self.collection.delete_prompt(name):
            if self._save_prompts():
                print(f"✓ Prompt '{name}' deleted successfully.")
                return True
            else:
                if backup_prompt:
                    self.collection.prompts[name] = backup_prompt
                print(f"✗ Failed to save prompt '{name}'.")
                return False
        else:
            print(f"✗ Prompt '{name}' does not exist.")
            return False

    def get_prompt(self, name: str) -> Optional[str]:
        """Get a specific prompt description by name."""
        if not name or name not in self.collection.prompts:
            return None

        self.collection.mark_used(name)
        self._save_prompts()

        return self.collection.prompts[name].description

    def prompt_exists(self, name: str) -> bool:
        """Check if a prompt exists by name."""
        return name in self.collection.prompts

    def get_all_prompts(self) -> Dict[str, str]:
        """Get all prompts as a dictionary of name -> description."""
        return self.collection.get_prompt_descriptions()

    def get_prompt_names(self) -> List[str]:
        return self.collection.get_prompt_names()

    def get_prompt_details(self, name: str) -> Optional[PromptItem]:
        """Get prompt details by name."""
        return self.collection.prompts.get(name)

    def search_prompts(self, query: str) -> Dict[str, str]:
        query = query.lower().strip()
        if not query:
            return self.get_all_prompts()

        results = {}
        for name, prompt in self.collection.prompts.items():
            if (query in name.lower() or
                query in prompt.description.lower()):
                results[name] = prompt.description

        return results

    def get_recently_used_prompts(self, limit: int = 5) -> Dict[str, str]:
        """Get a list of recently used prompts."""
        sorted_prompts = sorted(
            self.collection.prompts.items(),
            key=lambda x: x[1].last_used or "",
            reverse=True
        )

        results = {}
        for name, prompt in sorted_prompts[:limit]:
            if prompt.last_used:
                results[name] = prompt.description

        return results

    def count_prompts(self) -> int:
        return len(self.collection.prompts)

    def export_prompts(self, file_path: str, file_format: str = "json") -> bool:
        """Export prompts to file"""
        try:
            export_path = Path(file_path)

            if file_format.lower() == "json":
                with open(export_path, 'w', encoding='utf-8') as f:
                    json.dump(self.collection.to_dict(), f, indent=2, ensure_ascii=False)
            elif file_format.lower() == "txt":
                with open(export_path, 'w', encoding='utf-8') as f:
                    for name, prompt in self.collection.prompts.items():
                        f.write(f"=== {name} ===\n")
                        f.write(f"{prompt.description}\n")
                        f.write("-" * 50 + "\n\n")
            else:
                raise ValueError("Unsupported export format. Use 'json' or 'txt'.")
            print(f"✓ Prompts exported successfully to {export_path}")
            return True
        except Exception as e:
            print(f"✗ Error exporting prompts: {e}")
            return False

    def import_prompts(self, file_path: str, merge: bool = True) -> bool:
        """Import prompts from file"""
        try:
            import_path = Path(file_path)

            with open(import_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            imported_collection = PromptsCollection.from_dict(data)

            if merge:
                conflicts = []
                for name, prompt in imported_collection.prompts.items():
                    if name in self.collection.prompts:
                        conflicts.append(name)
                    else:
                        self.collection.prompts[name] = prompt

                if conflicts:
                    print(
                        f"⚠️ {len(conflicts)} Conflicts detected for prompts: {', '.join(conflicts)}. Skipping these.")

                print(
                    f"✓ Imported {len(imported_collection.prompts) - len(conflicts)} prompts with {len(conflicts)} conflicts.")
            else:
                self.collection = imported_collection
                print(f"✓ Imported {len(imported_collection.prompts)} prompts, replacing existing collection.")

            return self._save_prompts()
        except Exception as e:
            print(f"✗ Error importing prompts: {e}")
            return False

    def get_prompts_summary(self) -> dict:
        """Get a summary of current prompts."""
        recently_used = len(self.get_recently_used_prompts())
        total = self.count_prompts()

        return {
            "Total Prompts": total,
            "Recently Used": recently_used,
            "Unused": total - recently_used,
            "Collection Version": self.collection.version
        }