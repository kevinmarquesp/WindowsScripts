from typing import Callable
from num2words import num2words
from random import choice
from os import system, name
from time import time
from datetime import datetime

EXCLUDE_DLMTR = ","
MAX_WORD_RESULT = 100
WORD_NUMS = [num2words(n, lang="ptbr").replace("ê", "e")  #removes the only accent mark from 'três'
             for n in range(MAX_WORD_RESULT + 1)]
LOG_FILE = r"C:\Users\kevin\Desktop\data\datasets\logger\multiplication_trainer.log.txt"

#todo: put the 'F'/'P' of the results.txt file into variables too


def display_all_results(log_file: str) -> None:
    with open(log_file, "r") as logf:
        for line in [l[:-1] for l in logf.readlines()]:
            timestamp, results, duration = line.split(" ")

            timestamp_str = f"\033[30m{timestamp}\033[m"
            results_str = results.replace("F", "\033[31m.\033[m")\
                                 .replace("P", "\033[32m#\033[m")
            duration_str = f"\033[30m{duration} secs\033[m"

            print(f"{timestamp_str} {results_str} {duration_str}")


def clear() -> None:
    if name == "nt":
        system("cls")
    else:
        system("clear")


def get_multiply_numbers(nums: list[int], exclude_func: Callable) -> tuple[int, int]:
    multiply_numbers = choice(nums), choice(nums)

    if exclude_func(multiply_numbers):
        return get_multiply_numbers(nums, exclude_func)

    return multiply_numbers


def main() -> None:
    exclude = "1,2,5,10"
    exclude_func = lambda c: c[0] == c[1]
    end = 10
    case_count = 25

    nums = [n for n in range(1, end + 1)
            if n not in (int(e) for e in exclude.split(EXCLUDE_DLMTR))]

    test_cases = []

    for _ in range(case_count):
        multiply_numbers = get_multiply_numbers(nums, exclude_func)
        correct_result = multiply_numbers[0] * multiply_numbers[1]
        possible_results = str(correct_result), num2words(correct_result, lang="ptbr")

        test_cases.append((multiply_numbers, possible_results))

    past_result_str = "\033[30m[----]\033[m"
    results_log = []
    timer_begin = time()

    clear()

    for test_case in test_cases:
        test_nums, possible_results = test_case
        prompt_str = f"{past_result_str} \033[32m$\033[m {test_nums[0]} * {test_nums[1]} \033[33m:\033[m "

        user_input = input(prompt_str)
        is_correct = user_input in possible_results

        if is_correct:
            past_result_str = "\033[32m[PASS]\033[m"
            results_log.append(True)
        else:
            past_result_str = "\033[31m[FAIL]\033[m"
            results_log.append(False)

        clear()

    timer_end = time()
    becnhmark = timer_end - timer_begin

    with open(LOG_FILE, "r+") as logf:
        logf.read()

        current_time = str(datetime.now()).replace(" ", "_")
        results_str = "".join(["P" if is_pass else "F" for is_pass in results_log])
        becnhmark_str = f"{becnhmark:.2f}"

        logf.write(f"{current_time} {results_str} {becnhmark_str}\n")

    display_all_results(LOG_FILE)
    input("\n\nPress any key to continue...")


if __name__ == "__main__":
    main()