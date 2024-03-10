from typing import Any, Literal, Optional, Callable, Any
from time import sleep
import curses, os


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


def cprint(message: str) -> None:
    r"""
    Prints a colored message to the console based on color tags within the message.

    :param message: The message to print with color tags.
    """

    clr_tags: list[tuple[str, str]] = [
        ("[B]", "\033[;;30m"), ("[^B]", "\033[;;40m"),
        ("[r]", "\033[;;31m"), ("[^r]", "\033[;;41m"),
        ("[g]", "\033[;;32m"), ("[^g]", "\033[;;42m"),
        ("[y]", "\033[;;33m"), ("[^y]", "\033[;;43m"),
        ("[b]", "\033[;;34m"), ("[^b]", "\033[;;44m"),
        ("[m]", "\033[;;35m"), ("[^m]", "\033[;;45m"),
        ("[c]", "\033[;;36m"), ("[^c]", "\033[;;46m"),
        ("[w]", "\033[;;37m"), ("[^w]", "\033[;;47m"),
        ("[/]", "\033[m"),
    ]

    for clr_tag, clr_code in clr_tags:
        message = message.replace(clr_tag, clr_code)

    print(message)


logger_msg_type = Literal["warning", "info", "todo", "error", "fail", "good", "pass"]
logger_pad_type = Literal["top", "bottom", "both"]

def logger(message: str, ptype: logger_msg_type = "info", padding: Optional[logger_pad_type] = None) -> None:
    r"""
    Logs a message with a specified type and optional padding.

    :param message:
        The message to log.
    :param ptype:
        The type of the log message. Defaults to "info".
    :param padding:
        The type of padding to apply. Can be "top", "bottom", or "both". Defaults to None.
    """

    prefix: dict[logger_msg_type, str] = {
        "warning": "\033[43m WARN \033[;;33m",
        "info":    "\033[46m INFO \033[;;36m",
        "todo":    "\033[44m TODO \033[;;34m",
        "error":   "\033[41m ERRO \033[;;31m",
        "fail":    "\033[41m FAIL \033[;;31m",
        "good":    "\033[42m GOOD \033[;;32m",
        "pass":    "\033[42m PASS \033[;;32m"
    }

    padding_top: str = "\n" if padding in ["top", "both"] else ""
    padding_bottom: str = "\n" if padding in ["bottom", "both"] else ""

    print(f"{padding_top}{prefix[ptype]} {message}\033[m{padding_bottom}")


def clear() -> None:
    r"""
    Clears the stdout screen.
    """

    os.system("cls" if os.name == "nt" else "clear")


def retry(expected_err: Exception = Exception, delay_sec: int = 1) -> Callable:
    r"""
    A decorator for retrying a function execution upon encountering specified exceptions.

    This decorator wraps a function such that if the function raises an exception of the type `expected_err`, it will
    retry executing the function after a delay specified by `delay_sec`. If the function raises an exception that is not
    of the type `expected_err`, it will print an error message and raise that error too.

    :param expected_err:
        The type of the exceptions upon which the function should be retried. Default is `Exception`, which means the
        function will be retried for any exception.
    :param delay_sec:
        The number of seconds to wait before retrying the function. Default is 1.

    :returns:
        A callable that takes a function and returns a wrapped version of the function.
    :raises Exception:
        If the function raises an exception that is not of the type `expected_err`.

    :Example:

    .. code-block:: python

        @retry(expected_err=ConnectionError, delay_sec=5)
        def fetch_data():
            # Function implementation here...
    """

    def decorator(function: Callable) -> Callable:
        def wrapper(*args, **key_args) -> Any:
            while True:
                try:
                    return function(*args, **key_args)

                except Exception as err:
                    if not isinstance(err, expected_err):
                        cprint(f"[r]Unexpected Error[/]: [B][retry][/] {err} at {function}")
                        raise err

                    sleep(delay_sec)

        return wrapper

    return decorator