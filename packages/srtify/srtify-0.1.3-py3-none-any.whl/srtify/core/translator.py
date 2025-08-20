import shutil
from pathlib import Path
from typing import Dict, List, Optional, Any
import gemini_srt_translator as gst
from .file_encoding import detect_and_fix_encoding
from srtify.core.settings import SettingsManager
from srtify.core.prompts import PromptsManager
from srtify.utils.utils import fancy_headline


class TranslatorApp:
    """ Main Application class for handling translation operations. """
    def __init__(self, settings_manager: SettingsManager, prompts_manager: PromptsManager):
        self.settings = settings_manager
        self.prompts = prompts_manager

    def translate_single_file(
        self,
        input_path: Path,
        output_path: Path,
        srt_file: str,
        language: str,
        prompt: str,
        batch_size: int,
        api_key: str
    ) -> bool:
        """ Translate a single SRT file. """
        input_file = input_path / srt_file
        output_file = output_path / srt_file

        print(f"Translating:    {srt_file}")
        print(f"Language:       {language}")
        print(f"Batch Size:     {batch_size}")
        if prompt:
            print(f"Prompt:         {prompt[:100]}{'...' if len(prompt) > 100 else ''}")

        if not api_key:
            print("❌ No API key found. Configure settings first.")
            return False

        output_file.parent.mkdir(parents=True, exist_ok=True)

        # Configure gemini_srt_translator
        gst.gemini_api_key = api_key
        gst.target_language = language.lower()
        gst.input_file = str(input_file)
        gst.output_file = str(output_file)
        gst.batch_size = batch_size
        if prompt:
            gst.description = prompt

        try:
            gst.translate()
            print("✅ Translation successful.")
            return True
        except Exception as e:
            print(f"❌ Translation failed for {srt_file}: {e}")
            return False

    def get_srt_file(self, input_path: Path, specific_file: Optional[str] = None) -> List[str]:
        """ Get list of SRT files to process. """
        if specific_file:
            file_name = specific_file.strip()
            if not file_name.endswith(".srt"):
                file_name = f"{file_name}.srt"

            file_path = input_path / file_name
            if file_path.exists():
                return [file_name]
            else:
                print(f"❌ File {file_name} not found in {input_path}")
                return []

        else:
            str_files = [file.name for file in input_path.glob("*.srt")]
            return str_files

    def validate_files_encoding(self, input_path: Path, srt_files: List[str]) -> List[str]:
        """ Validate and fix file encoding for all SRT files. """
        print("Checking file encoding...")
        valid_files = []

        for srt_file in srt_files:
            if detect_and_fix_encoding(str(input_path), srt_file):
                valid_files.append(srt_file)
            else:
                print(f"❌ Failed to fix encoding for file {srt_file}. Skipping...")

        return valid_files

    def resolve_prompt(self, options: Dict[str, Any]) -> Optional[str]:
        """ Resolve which prompt to use based on options """
        if options.get('custom_prompt'):
            return options['custom_prompt'].strip()
        elif options.get('prompt'):
            results = self.prompts.search_prompts(options['prompt'].strip())
            if results:
                if len(results) == 1:
                    return list(results.values())[0]
                else:
                    print(f"Found {len(results)} prompts matching '{options['prompt']}'")
                    for name, desc in results.items():
                        print(f" - {name}: {desc[:100]}{'...' if len(desc) > 100 else ''}")
                    return None
            else:
                print(f"No prompts found matching '{options['prompt']}'")
                return None
        elif options.get('quick'):
            return "Translate naturally and accurately"
        else:
            return "Translate naturally and accurately"

    def run_translation(self, options: Dict[str, Any]) -> None:
        """ Main translation runner. """
        input_dir, output_dir = self.settings.get_directories()
        default_lang = self.settings.get_translation_language()
        default_batch_size = self.settings.get_translation_batch_size()
        api_key = self.settings.get_api_key()

        input_path = Path(options.get('input_path') or input_dir)
        output_path = Path(options.get('output_path') or output_dir)
        language = options.get('language') or default_lang
        batch_size = options.get('batch_size') or default_batch_size

        if not api_key:
            print("❌ No API key found. Use 'subtitle-translator settings' to configure.")
            return

        selected_prompt = self.resolve_prompt(options)
        if selected_prompt is None:
            print("❌ No prompt selected. Exiting.")
            return

        # Print configuration
        print("Translation Settings:")
        print("=" * 30)
        print(f"- Target Language:  {language}")
        print(f"- Input Directory:  {input_path}")
        print(f"- Output Directory: {output_path}")
        print(f"- Batch Size:       {batch_size}")
        print(f"- API Key:          {'Set' if api_key else 'Not Set'}")
        print("=" * 30)

        srt_files = self.get_srt_file(input_path, options.get('file'))
        if not srt_files:
            print("❌ No SRT files found. Exiting.")
            return

        print(f"Found {len(srt_files)} SRT files.")

        valid_files = self.validate_files_encoding(input_path, srt_files)
        if not valid_files:
            print("❌ No valid SRT files found after encoding check. Exiting.")
            return

        print(f"Found {len(valid_files)} valid SRT files.")
        print(f"\nStarting translation to {language}...")
        print("=" * shutil.get_terminal_size().columns)

        successful = 0
        failed = 0

        for srt_file in valid_files:
            if self.translate_single_file(
                input_path, output_path, srt_file,
                language, selected_prompt, batch_size, api_key
            ):
                successful += 1
            else:
                failed += 1

        print("=" * shutil.get_terminal_size().columns)
        print(fancy_headline("TRANSLATION SUMMARY", "rounded"))
        print(f"Successful: {successful}")
        print(f"Failed: {failed}")
        print(f"Output Directory: {output_path}")