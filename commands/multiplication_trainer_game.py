from typing import Any, Never
import curses
from sys import argv
from argparse import ArgumentParser, Namespace
from random import choice
from num2words import num2words
from dataclasses import dataclass
from time import time
import os
from datetime import datetime


class ScriptUtils:
    class Color:
        class Bg:
            BLACK: str = "\033[40m"
            RED: str = "\033[41m"
            GREEN: str = "\033[42m"
            YELLOW: str = "\033[43m"
            BLUE: str = "\033[44m"
            MAGENTA: str = "\033[45m"
            CYAN: str = "\033[46m"
            WHITE: str = "\033[47m"
            RESET: str = "\033[m"

        class Fg:
            BLACK: str = "\033[30m"
            RED: str = "\033[31m"
            GREEN: str = "\033[32m"
            YELLOW: str = "\033[33m"
            BLUE: str = "\033[34m"
            MAGENTA: str = "\033[35m"
            CYAN: str = "\033[36m"
            WHITE: str = "\033[37m"
            RESET: str = "\033[m"

    @staticmethod
    def clear_screen() -> None:
        os.system("cls" if os.name == "nt" else "clear")

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


def parse_user_arguments(usr_args: list[str]) -> Namespace:
    r"""
    ...todo: add a documentation for this function...
    """

    parser: ArgumentParser = ArgumentParser(description="Simple script that uses a TUI interface that let you train\
                                            your multiplication skills, if you have some issue with that. Have fun!")

    parser.add_argument("-c", "--count", type=int, default=25, help="How manny chalenge cases the game will create for\
                        you, consider using a number lesser than 30 for 'easy to display' propurses...")
    parser.add_argument("-s", "--start", type=int, default=0, help="The min value that the multiplication cases can\
                        have, the multiplication table will start with the number specified.")
    parser.add_argument("-e", "--end", type=int, default=10, help="The max value that the multiplication cases can\
                        have, the  multiplication table wil end with the number specified.")
    parser.add_argument("-i", "--ignore-squares", action="store_true", help="Use this option to tell the game to skipt\
                        the cases where x == y; a.k.a: the square cases.")
    parser.add_argument("-E", "--exclude", type=str, default="0", help="String (separeted by the ',' without spaces)\
                        with the number that the game will ignore.")

    return parser.parse_args()


def get_difference_between_two_lists(l1: list[Any], l2: list[Any]) -> list[Any]:
    return [i for i in l1 if i not in l2]


Challenge = tuple[tuple[int, int], list[int, str]]

def generate_chalenges(start: int, end: int, ignore_squares: bool, excluded_numbers: list[int]) -> Challenge:
    valid_cases: int = get_difference_between_two_lists(range(start, end + 1), excluded_numbers)
    x: int = choice(valid_cases)
    y: int = choice(valid_cases)
    r: int = x * y

    if x == y and ignore_squares:
        return generate_chalenges(start, end, ignore_squares, excluded_numbers)

    valid_results: list[int, str] = [r, f"{r}", num2words(r), num2words(r, lang="ptbr"),
                                     num2words(r, lang="ptbr").replace("ê", "e")]
    
    return ((x, y), valid_results)


def validate_excluded_numbers(start: int, end: int, excluded_numbers: list[int]) -> Never | None:
    fg: ScriptUtils.Color.Fg = ScriptUtils.Color.Fg
    bg: ScriptUtils.Color.Bg = ScriptUtils.Color.Bg

    user_range: list[int] = list(range(start, end + 1))
    difference: list[int] = get_difference_between_two_lists(user_range, excluded_numbers)
    
    if len(difference) < 2:
        print(f"{bg.RED}  ERRO  {bg.RESET} {fg.RED}Wait! You've excluded most of the numbers, that's not fair!{fg.RESET}")
        raise "Cannot generate the challenge cases, not enough options"


def convert_number_list_string_to_number_list(num_list_str: list[str]) -> list[int]:
    return [int(n) for n in set(num_list_str.replace(" ", "").split(","))]


@dataclass
class ChallengeResult:
    x: int
    y: int
    expected_results: list[int, str]
    user_result: str
    is_correct: bool


def challenge_user(challenge_data: Challenge, key: int) -> ChallengeResult:
    fg: ScriptUtils.Color.Fg = ScriptUtils.Color.Fg
    bg: ScriptUtils.Color.Bg = ScriptUtils.Color.Bg

    x: int; y: int; expected_result: list[int, str]
    (x, y), expected_results = challenge_data

    print(f"\n  {fg.BLACK}--- {fg.GREEN}~{fg.CYAN} {x} * {y}")

    user_input: str = input(f"  {fg.BLACK}{key:>3} {fg.GREEN}${fg.RESET} ").strip()
    is_correct: bool = user_input in expected_results

    ScriptUtils.clear_screen()

    if is_correct:
        print(f"\n  {bg.GREEN}  PASS  {bg.RESET}{fg.GREEN} You're correct! {x} * {y} is equal to '{user_input}'{fg.RESET}")
    else:
        print(f"\n  {bg.RED}  FAIL  {bg.RESET}{fg.RED} You're wrong! {x} * {y} should be '{expected_results}'{fg.RESET}")

    return ChallengeResult(x, y, expected_results, user_input, is_correct)


def display_current_game_results(challenge_results: list[ChallengeResult], benchmark: float) -> None:
    TABLE_SEPARATOR: str = f"  {fg.BLACK}|{fg.RESET}  "
    TABLE_SEPARATOR_LN: str = f"\n  {fg.BLACK}|{fg.RESET}  "

    fg: ScriptUtils.Color.Fg = ScriptUtils.Color.Fg
    challenge_results_strings: list[str] = [f"{c.x} * {c.y} == {c.is_correct and fg.GREEN or fg.RED}{c.user_result}{fg.RESET} {TABLE_SEPARATOR}"
                                            for c in challenge_results]
    max_result_string_length: int = max(list(map(len, challenge_results_strings)))
    challenges_length: int = len(challenge_results)
    correct_results: int = len(list(filter(lambda c: c.is_correct, challenge_results)))
    incorrect_results: int = len(list(filter(lambda c: not c.is_correct, challenge_results)))

    print(end=TABLE_SEPARATOR_LN)
    for key, challenge_result_string in enumerate(challenge_results_strings):
        challenge_string_length: int = len(challenge_result_string)
        padding_difference: int = max_result_string_length - challenge_string_length

        print(f"{' ' * padding_difference}{challenge_result_string}",
              end=TABLE_SEPARATOR_LN if (key + 1) % 5 == 0 and key != len(challenge_results_strings) - 1 else "  ")

    print(f"\n\n  {fg.CYAN}benchmark{fg.RESET}:  {fg.YELLOW}{benchmark:.3f} secs{fg.RESET}")
    print(f"  {fg.CYAN}date{fg.RESET}:       {fg.YELLOW}{datetime.now()}{fg.RESET}")
    print(f"  {fg.CYAN}logger{fg.RESET}:     {fg.GREEN}{correct_results}{fg.RESET} {fg.YELLOW}/ {challenges_length}, {fg.RED}{incorrect_results}{fg.RESET}\n")


def start_playing(args: Namespace) -> None:
    fg: ScriptUtils.Color.Fg = ScriptUtils.Color.Fg
    excluded_numbers: list[int] = convert_number_list_string_to_number_list(args.exclude)

    validate_excluded_numbers(args.start, args.end, excluded_numbers)  #to be sure that it's possible to generate a random string quickly
    
    challenges: list[Challenge] = [generate_chalenges(args.start, args.end, args.ignore_squares, excluded_numbers)
                                   for _ in range(args.count)]

    ScriptUtils.clear_screen()

    benchmark_begin: float = time()
    challenge_results: list[ChallengeResult] = [challenge_user(challenge_data, key + 1)
                                                for key, challenge_data in enumerate(challenges)]
    benchmark: float = time() - benchmark_begin

    input(f"\n  {fg.GREEN}!!!{fg.RESET} Press any key to check the {fg.YELLOW}summary{fg.RESET}...")
    ScriptUtils.clear_screen()
    display_current_game_results(challenge_results, benchmark)
    input()



def main(usr_args: list[str]) -> None:
    args: Namespace = parse_user_arguments(usr_args)

    user_choice: tuple[int, str, str] = ScriptUtils.display_options_menu("Multiplication Game", {
        "start_playing": "Start Game!",
        "exit": "Quit Script"
    })

    match user_choice:
        case (_, "start_playing", _):
            start_playing(args)
            main(usr_args)

        case (_, "exit", _):
            pass

    
if __name__ == "__main__":
    main(argv[1:])