import shutil
from typing import Optional
from .menu import MainMenu, PromptMenu, SettingsMenu
from srtify.core.prompts import PromptsManager
from srtify.core.settings import SettingsManager
from srtify.utils.utils import clear_screen, fancy_headline
from ..core.translator import TranslatorApp


class CliHandler:
    def __init__(self, settings_manager: SettingsManager, prompts_manager: PromptsManager):
        self.settings_manager = settings_manager
        self.prompts_manager = prompts_manager
        self.settings_menu = SettingsMenu()

    def handle_main_menu(self):
        """Handle the main menu."""
        main_menu = MainMenu()


        while True:
            clear_screen()
            print(fancy_headline("Gemini SRT Translator", "rounded"))
            summary = self.settings_manager.get_settings_summary()
            print(f"API Key: {summary['API Key']}")
            print(f"Target Language: {summary['Language']}")
            print(f"Input Directory: {summary['Input Directory']}")
            print(f"Output Directory: {summary['Output Directory']}")
            print(f"Batch Size: {summary['Batch Size']}")

            choice = main_menu.select()

            if choice is None or choice == "exit":
                print(fancy_headline("Goodbye!", "rounded"))
                return None

            try:
                match choice:
                    case "translate":
                        self.interactive_translation()
                    case "prompts":
                        self.handle_prompts_menu()
                    case "settings":
                        self.handle_settings_menu()
                    case "quick":
                        # TODO: Implement quick translation
                        pass
            except KeyboardInterrupt:
                print("\nReturning to main menu...")
            except Exception as e:
                print(f"❌ Error in Main Menu: {e}")
                input("Press Enter to continue...")

    def interactive_translation(self):
        clear_screen()
        print(fancy_headline("Start Translation", "rounded"))

        input_dir, output_dir = self.settings_manager.get_directories()
        lang, batch_size = self.settings_manager.get_translation_config()
        api_key = self.settings_manager.get_api_key()

        if not api_key:
            print("❌ No API key found. Use 'subtitle-translator settings' to configure.")
            input("Press Enter to continue...")
            return

        print("\nSelect a prompt to use for translation:")
        prompt = self.select_prompt_for_translation()
        print(f"Selected prompt: {prompt}")

        app = TranslatorApp(self.settings_manager, self.prompts_manager)

        options = {
            'input': input_dir,
            'output': output_dir,
            'language': lang,
            'batch_size': batch_size,
            'prompt': prompt
        }

        try:
            app.run_translation(options)
            print("✅ Translation completed successfully!")
        except Exception as e:
            print(f"❌ Error during translation: {e}")
        finally:
            input("Press Enter to continue...")

    def select_prompt_for_translation(self) -> Optional[str]:
        """ Let the user select a prompt for translation
        :return: str: prompt
        """
        all_prompts = self.prompts_manager.get_all_prompts()
        for i, (name, prompt) in enumerate(all_prompts.items()):
            print(f"{i+1} - {name}: {prompt[:100]}")
        choice = input("Enter the number of the prompt you want to use: ")
        try:
            return list(all_prompts.keys())[int(choice) - 1]
        except (IndexError, ValueError):
            print("Invalid choice. Please enter a number between 1 and", len(all_prompts))

    def handle_prompts_menu(self):
        while True:
            try:
                # print(fancy_headline("Prompts Menu", "rounded"))

                prompts = self.prompts_manager.get_all_prompts()
                prompts_menu = PromptMenu(prompts)
                name, choice = prompts_menu.select(clear_screen=True)

                if choice == 'new':
                    self.add_prompt()
                elif choice == 'main':
                    break
                else:
                    # print(f"Selected prompt: {name}: {choice}")
                    self.select_prompt(name, choice)

            except KeyboardInterrupt:
                print("\nReturning to main menu...")
            except Exception as e:
                print(f"❌ Error in Prompts Menu: {e}")
                input("Press Enter to continue...")

    def add_prompt(self, prompt_name: str = None, prompt_description: str = None):
        """Add a new prompt."""
        if not prompt_name:
            prompt_name = input("Enter prompt name: ").strip()
            if not prompt_name:
                print("❌ Prompt name cannot be empty!")
                input("Press Enter to continue...")
                return
            if self.prompts_manager.prompt_exists(prompt_name):
                print(f"❌ Prompt '{prompt_name}' already exists!")
                input("Press Enter to continue...")
                return

        if not prompt_description:
            prompt_description = input("Enter prompt description: ").strip()
            if not prompt_description:
                print("❌ Prompt description cannot be empty!")
                return

        try:
            if self.prompts_manager.add_prompt(prompt_name, prompt_description):
                print(f"✓ Prompt '{prompt_name}' added successfully!")
            else:
                print(f"❌ Failed to add prompt '{prompt_name}'!")
        except ValueError as e:
            print(f"❌ Error: {e}")

        input("Press Enter to continue...")

    def select_prompt(self, *prompt):
        """Select a prompt."""
        prompt_menu = PromptMenu()
        choice = prompt_menu.prompt_options()

        if choice is None:
            print("❌ No option selected!")
            return

        if choice == "show":
            print(f"Prompt name: {prompt[0]}")
            print(f"Prompt description: {prompt[1]}")
            input("Press Enter to continue...")
        elif choice == "edit":
            self.edit_prompt(*prompt)
        elif choice == "delete":
            self.delete_prompt(*prompt)
        elif choice == "back":
            return

    def edit_prompt(self, *prompt):
        """Edit a prompt."""
        print(f"Prompt: {prompt[0]}")
        print('-' * (len(prompt[0]) + 8))
        print(f"Description: {prompt[1]}")

        try:
            print("=" * shutil.get_terminal_size().columns)
            new_prompt = input("Enter new description: ").strip()
            if new_prompt and self.prompts_manager.update_prompt(prompt[0], new_prompt):
                print(f"✓ Prompt '{prompt[0]}' updated successfully!")
            else:
                print(f"❌ Failed to update prompt '{prompt[0]}'!")
        except (ValueError, IndexError) as e:
            print(f"❌ Error: {e}")

    def delete_prompt(self, *prompt):
        """Delete a prompt."""
        try:
            if input(f"Are you sure you want to delete prompt '{prompt[0]}'? (y/n) ").strip().lower().endswith('y'):
                if self.prompts_manager.delete_prompt(prompt[0]):
                    print(f"✓ Prompt '{prompt[0]}' deleted successfully!")
                else:
                    print(f"❌ Failed to delete prompt '{prompt[0]}'!")
        except (ValueError, IndexError) as e:
            print(f"❌ Error: {e}")

    def search_prompts(self, search_term):
        """Search for prompts."""
        if not search_term:
            search_term = input("Enter search term: ").strip()
            if not search_term:
                print("❌ Search term cannot be empty!")
                exit()

        results = self.prompts_manager.search_prompts(search_term)
        if results:
            if len(results) > 1:
                print(f"Found {len(results)} prompts matching '{search_term}':")
                print("=" * shutil.get_terminal_size().columns)
                for i, name, description in enumerate(results.items()):
                    print(f"{i+1} - {name}: {description}")
                print("=" * shutil.get_terminal_size().columns)
                choice = input("Enter the number of the prompt you want to select: ").strip()
                if choice.isdigit() and 1 <= int(choice) <= len(results):
                    prompt_name = list(results.keys())[int(choice) - 1]
                    print(f"Selected prompt: {prompt_name}")
                    return results[prompt_name]
                else:
                    print("❌ Invalid choice!")
                    exit()
            else:
                for name, description in results.items():
                    print(f"Found prompt '{name}':\n{description}")
                    return results[name]

        return None

    def handle_settings_menu(self):
        """Handle the settings menu."""
        while True:
            summary = self.settings_manager.get_settings_summary()
            choice = self.settings_menu.select()

            if choice is None:
                print("Settings selection cancelled.")
                break

            try:
                match choice:
                    case 'view':
                        print(fancy_headline("Settings Summary"))
                        for key, value in summary.items():
                            print(f"  {key}: {value}")
                        print("=" * 50)
                        input("Press Enter to continue...")
                    case 'api':
                        self.set_api_key()
                    case 'dirs':
                        self.set_directories()
                    case 'translation':
                        self.set_translation_preferences()
                    case 'reset':
                        if input("Reset all settings to default? (y/N) ").strip().lower().endswith('y'):
                            print("Resetting settings...")
                            if self.settings_manager.reset_to_defaults():
                                print("✓ Settings reset to default successfully!")
                            else:
                                print("❌ Failed to reset settings to default!")
                        else:
                            print("Settings reset cancelled.")
                        input("Press Enter to continue...")
                    case 'back':
                        break
            except KeyboardInterrupt:
                print("\nReturning to main menu...")
            except Exception as e:
                print(f"❌ Error in Settings Menu: {e}")
                input("Press Enter to continue...")

    def set_api_key(self, new_key: str = None):
        """Set API key."""
        current_key = self.settings_manager.get_api_key()
        if current_key:
            masked_key = f"...{current_key[-6:]}" if len(current_key) > 6 else "Set"
            print(f"Current API Key: {masked_key}")

        if not new_key:
            new_key = input("Enter new API key: ").strip()
        if new_key:
            try:
                if self.settings_manager.set_api_key(new_key):
                    print("✓ API key set successfully!")
                else:
                    print("❌ Failed to set API key!")
            except ValueError as e:
                print(f"❌ Error setting API key: {e}")

    def set_directories(self):
        """Set input and output directories."""
        current_input, current_output = self.settings_manager.get_directories()
        print(f"Current Input Directory: {current_input}")
        print(f"Current Output Directory: {current_output}")

        new_input = input("Enter new input directory: ").strip()
        new_output = input("Enter new output directory: ").strip()

        if new_input or new_output:
            try:
                if self.settings_manager.set_directories(
                    new_input or current_input,
                    new_output or current_output
                ):
                    print("✓ Directories set successfully!")
                else:
                    print("❌ Failed to set directories!")
            except ValueError as e:
                print(f"❌ Error setting directories: {e}")

    def set_translation_preferences(self, language: str = None, batch_size: int = None):
        """Set translation preferences."""
        current_lang = self.settings_manager.get_translation_language()
        current_batch = self.settings_manager.get_translation_batch_size()

        print(f"Current Language: {current_lang}")
        print(f"Current Batch Size: {current_batch}")

        new_lang = input("Enter new language (or leave blank to keep current): ").strip()
        new_batch = input("Enter new batch size (or leave blank to keep current): ").strip()

        try:
            batch_size = int(new_batch) if new_batch else current_batch
            language = new_lang if new_lang else current_lang

            if self.set_language(language):
                print("✓ Translation language set successfully!")
            else:
                print("❌ Failed to set translation language!")

            if self.set_batch_size(batch_size):
                print("✓ Translation batch size set successfully!")
            else:
                print("❌ Failed to set translation batch size!")
        except ValueError as e:
            print(f"❌ Error setting translation preferences: {e}")

    def set_language(self, language: str = None):
        if not language or not language.strip():
            language = self.settings_manager.get_translation_language()
        self.settings_manager.set_translation_language(language)

    def set_batch_size(self, batch_size: int = None):
        if not batch_size or batch_size <= 0:
            batch_size = self.settings_manager.get_translation_batch_size()
        self.settings_manager.set_translation_batch_size(batch_size)