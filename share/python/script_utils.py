from typing import Any
import curses


class ScriptUtils:
    @staticmethod
    def display_options_menu(title: str, options: dict[Any, str], default_option: int = 0,
                             up_keys: list[int] = [curses.KEY_UP, ord("k")],
                             down_keys: list[int] = [curses.KEY_DOWN, ord("j")],
                             select_keys: list[int] = [curses.KEY_ENTER, 10, 13, ord("o")]) -> Any:
        r"""
        This function displays an interactive options menu in the terminal. The menu is navigable using specified keys
        for moving the selection up and down, and for selecting an option.

        :param title:
            The title displayed at the top of the options menu.
        :param options:
            A dictionary where each key-value pair represents an option. The keys are option identifiers and the
            values are the prompts displayed for each option.
        :param default_option:
            The index of the option that is selected by default when the menu is displayed. If not provided, the first
            option is selected by default.
        :param up_keys:
            A list of key codes that, when pressed, move the selection up in the menu. By default, these are the up
            arrow key and the 'k' key.
        :param down_keys:
            A list of key codes that, when pressed, move the selection down in the menu. By default, these are the
            down arrow key and the 'j' key.
        :param select_keys:
            A list of key codes that, when pressed, select the currently highlighted option. By default, these are the
            enter key and the 'o' key.

        :return:
            A tuple containing three elements: the index of the selected option, the key of the selected option, and
            the value of the selected option. This allows the calling code to know which option was selected by the
            user.
        """

        TITLE_PADDING_START: int = 1
        PROMPT_PADDING_START: int = 2

        option_keys: list[Any] = list(options.keys())
        option_values: list[str] = list(options.values())

        #variables related to formating the style of the menu, size of each option, paddings, etc.

        max_prompt_length: int = max(list(map(len, option_values)))
        title_lines: list[str] = title.split("\n")
        title_padding_top: int = len(title_lines) - 1
        menu_list_padding_top: int = title_padding_top + len(title_lines) + 1

        #variables that the wrapper function will use to know witch option is selected

        selected_index: int = default_option
        selected_key: Any = option_keys[selected_index]
        selected_value: str = option_values[selected_index]

        user_input: int = 0

        def __display_options_menu_wrapper(stdscr: "curses._CursesWindow"):
            r"""
            This function displays an options menu in a curses window. It allows the user to navigate through the
            options using the up and down keys.

            :param stdscr:
                The curses window in which the options menu will be displayed.
            :type stdscr:
                curses._CursesWindow
            """

            nonlocal title_lines, option_keys, option_values, selected_key, selected_index, selected_value, user_input

            stdscr.refresh()

            while user_input not in select_keys:  #only stops the event listener when the enter key is pressed
                stdscr.clear()

                for key, title_line in enumerate(title_lines):  #logic to write the title lines
                    stdscr.addstr(title_padding_top + key, TITLE_PADDING_START + PROMPT_PADDING_START, title_line)

                for key, option_value in enumerate(option_values):  #logic to write the menu options formated in a beaty way
                    option_length: int = len(option_value)
                    option_length_difference: int = max_prompt_length - option_length
                    option_prompt: str = f"  {option_value.strip()}  " + " " * option_length_difference

                    stdscr.addstr(key + menu_list_padding_top, PROMPT_PADDING_START, option_prompt,
                                  curses.A_REVERSE if key == selected_index else 0)

                    if key == len(option_values) - 1:
                        stdscr.addstr(key + menu_list_padding_top + 2, 0, "")

                #user event listeners section

                stdscr.refresh()
                user_input = stdscr.getch()

                if user_input in up_keys:
                    selected_index = (selected_index - 1) % len(option_keys)
                elif user_input in down_keys:
                    selected_index = (selected_index + 1) % len(option_keys)

                selected_key = option_keys[selected_index]
                selected_value = option_values[selected_index]

        curses.wrapper(__display_options_menu_wrapper)
        return (selected_index, selected_key, selected_value)
#end: ScriptUtils