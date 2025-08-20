from typing import Dict
from simple_term_menu import TerminalMenu


class Menu:
    def __init__(self, title, style=None):
        self.title = title
        self.style = style or {
            "menu_highlight_style": ("bg_green", "fg_black"),
            "search_highlight_style": ("bg_red", "fg_black"),
            "cycle_cursor": True,
            "search_key": '/'
        }

    def show(self, items, clear_screen=False):
        return TerminalMenu(
            items,
            clear_screen=clear_screen,
            title=self.title,
            **self.style
        )


class MainMenu(Menu):
    def __init__(self):
        super().__init__("====== Gemini SRT Translator ======")
        self.options = {
            "Start Translation": "translate",
            "Prompts Menu": "prompts",
            "Settings Menu": "settings",
            "Quick Translation (Default Settings)":  "quick",
            "Exit": "exit"
        }

    def select(self):
        option_names = list(self.options.keys())
        menu = self.show(option_names, clear_screen=False)
        selected_index = menu.show()

        if selected_index is not None:
            selected_key = option_names[selected_index]
            return self.options[selected_key]

        return None


class PromptMenu(Menu):
    def __init__(self, prompts_list: Dict[str, str] = None):
        super().__init__("====== Prompt Menu ======")
        self.prompts_list = prompts_list if prompts_list is not None else {}
        self.options = {
            "Add New Prompt": "new",
            "Back to Main Menu": "main"
        }
        # if prompts_list:
        self.prompts_list.update(self.options)

    def select(self, clear_screen=False):
        prompts_list = list(self.prompts_list.keys())
        menu = self.show(prompts_list, clear_screen)
        selected_index = menu.show()

        if selected_index is not None:
            selected_key = prompts_list[selected_index]
            selected_value = self.prompts_list[selected_key]
            return selected_key, selected_value

        print("No option selected.")
        return None

    def prompt_options(self):
        options = {
            "Show": "show",
            "Edit": "edit",
            "Delete": "delete",
            "Back": "back"
        }
        options_list = list(options.keys())
        menu = self.show(options_list, clear_screen=True)
        selected_index = menu.show()

        if selected_index is not None:
            selected_key = options_list[selected_index]
            return options[selected_key]

        print("No option selected.")
        return None


class SettingsMenu(Menu):
    def __init__(self):
        super().__init__("====== Settings Menu ======")
        self.options = {
            "View Current Settings": "view",
            "Set API Key": "api",
            "Set Input/Output Directories": "dirs",
            "Set Translation Preferences": "translation",
            "Reset to Default": "reset",
            "Back to Main Menu": "back"
        }

    def select(self):
        option_names = list(self.options.keys())
        menu = self.show(option_names, clear_screen=True)
        selected_index = menu.show()

        if selected_index is not None:
            return self.options[option_names[selected_index]]
        print("Settings selection cancelled.")
        return None