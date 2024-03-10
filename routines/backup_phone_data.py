from typing import Any, Literal, Optional, Callable
from argparse import Namespace, ArgumentParser
from json import loads, load
from ftplib import FTP
from time import sleep, time
from sys import argv
from concurrent.futures import ThreadPoolExecutor
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


DEFAULT_CREDENTIALS_JSON: str = r"C:\Users\kevin\Desktop\data\datasets\fsinfo\android.credential.json"\
                                if os.name == "nt" else\
                                r"/mnt/c/Users/kevin/Desktop/data/datasets/fsinfo/android.credential.json"
                                #only works for wsl for now...
DEFAULT_TARGETS_JSON: str = r"C:\Users\kevin\Desktop\data\datasets\fsinfo\android-snapshot.backup.json"\
                            if os.name == "nt" else\
                            r"/mnt/c/Users/kevin/Desktop/data/datasets/fsinfo/android-snapshot.backup.json"
                            #only works for wsl for now...

class DefaultArguments:
    r"""
    Class for managing default arguments for synchronization. Some of the default values will depends on a local json
    file stored in the DEFAULT_TARGETS_JSON and DEFAULT_CREDENTIALS_JSON paths!

    :ivar target:
        List of target directories.
    :ivar host:
        FTP server hostname or IP address.
    :ivar port:
        Port number for the FTP server.
    :ivar username:
        Username for FTP login.
    :ivar password:
        Password for FTP login.
    :ivar sync_config_file:
        Path to the synchronization configuration file.
    :ivar timeout:
        Timeout duration for FTP operations.
    """

    target: list[str]
    host: str
    port: int
    username: str
    password: str
    sync_config_file: str
    timeout: int

    def __init__(self):
        r"""
        Initializes the DefaultArguments object and sets default values for target, host, port, username, password,
        sync_config_file, and timeout attributes based on the operating system.
        """

        os_key: str = "Windows" if os.name == "nt" else "Linux"
        default_targets: dict[str, Any]
        default_credentials: dict[str, str | int]

        with open(DEFAULT_CREDENTIALS_JSON, "r") as f:
            default_credentials = load(f)

        with open(DEFAULT_TARGETS_JSON, "r") as f:
            default_targets = load(f)

        self.timeout = 3
        self.target = default_targets[os_key]["Targets"]
        self.host = default_credentials["Host"]
        self.port = default_credentials["Port"]
        self.username = default_credentials["Username"]
        self.password = default_credentials["Password"]
        self.sync_config_file = default_targets["SyncConfigFile"]
        

def parse_user_arguments(usr_args: list[str]) -> Namespace:
    r"""
    Parses user arguments for a script that connects to an FTP server and backs up selected directories/files.

    :param usr_args:
        User arguments

    :return:
        Parsed arguments
    """

    parser: ArgumentParser = ArgumentParser(description="This script will connect to a FTP server, normaly your phone,\
                                            and use a backup json data stored in that server to backup the selected\
                                            directorys/files to a destination on this computer.")
    defaults: DefaultArguments = DefaultArguments()

    parser.add_argument("-t", "--targets", type=str, nargs="+", default=defaults.target, help="This argument can have\
                        multiple values, each value should be a valid path for a directory on the system.")
    parser.add_argument("-H", "--host", type=str, default=defaults.host, help="The IP address or domain of you server,\
                        assuming that the server is running localy on your own network.")
    parser.add_argument("-p", "--port", type=int, default=defaults.port, help="Port to connect to that host.")
    parser.add_argument("-u", "--username", type=str, default=defaults.username, help="Username to login.")
    parser.add_argument("-P", "--password", type=str, default=defaults.password, help="Password to login.")
    parser.add_argument("-s", "--sync-config-file", type=str, default=defaults.sync_config_file, help="Path, in the\
                        FTP server storage, for the JSON config file, this program will use that file to know what\
                        directories/files it should mirror.")
    parser.add_argument("-T", "--timeout", type=int, default=defaults.timeout, help="Timeout span, in seconds, that\
                        will be used to throw an error on the FTP connection related code.")

    return parser.parse_args()


def retry_on_exception(func: Callable):
    r"""
    A decorator that allows a function to retry when an exception occurs.

    :param func:
        The function to be retried upon an exception.

    :return:
        The wrapper function that handles the retry logic.

    This decorator wraps a function such that if the function raises an exception, it will keep retrying indefinitely.
    After each failed attempt, it waits for 0.5 seconds before trying again. If the function call is successful, it
    returns the result.
    """

    def __wrapper(*args, **key_args):
        while True:
            try:
                return func(*args, **key_args)
            except Exception as e:
                cprint(f"[r]Func Call Error[/]: {e} [B]{func}[/]")
                sleep(.5)
    
    return __wrapper


@retry_on_exception
def ftp_connect(host: str, port: int, username: str, password: str, timeout: int = 120) -> FTP:
    r"""
    Connects to an FTP server with the provided host, port, username, and password.

    :param host:
        The IP address or domain of the server.
    :param port:
        Port to connect to the host.
    :param username:
        Username to login.
    :param password:
        Password to login.
    :param timeout:
        Timeout span, in seconds, that will be used to throw an error on the FTP connection related code. Default is 120
        seconds.

    :return:
        An FTP object representing the connection to the server.

    This function attempts to connect to an FTP server using the provided host, port, username, and password.  If the
    connection or login attempt raises an exception, the function will keep retrying indefinitely, waiting for 0.5
    seconds after each failed attempt. If the connection and login are successful, it logs a success message and returns
    the FTP object.
    """

    ftp: FTP = FTP()

    ftp.connect(host, port=port, timeout=timeout)
    ftp.login(username, password)

    logger(f"Successfully connect to ftp://{username}@{host}:{port}", ptype="good")

    return ftp


BackupProfile = dict[Literal["Exclude", "Data"], list[dict[Literal["Path", "Delete?"], str | bool]]]
SyncConfig = dict[str, BackupProfile]

def get_json_config_content(ftp: FTP, config_path: str) -> SyncConfig:
    r"""
    Retrieves the content of a JSON configuration file from an FTP server.

    :param ftp:
        An FTP object representing the connection to the server.
    :param config_path:
        The path to the configuration file on the FTP server.

    :return:
        The content of the JSON configuration file.

    This function changes the current directory on the FTP server to the directory of the configuration file, retrieves
    the content of the file, and returns it as a dictionary. If the file does not exist, it logs an error message and
    raises an exception.
    """

    dir_path: str = os.path.dirname(config_path) or "/"
    config_file: str = os.path.basename(config_path)

    ftp.cwd(dir_path)

    if config_file not in ftp.nlst():
        error: str = f"Could not find the {config_path} on the system"

        logger(error, ptype="error", padding="bottom")
        raise error

    content_lines: list[bytes] = []

    ftp.retrbinary(f"RETR {config_file}", lambda line: content_lines.append(line))

    content: str = "".join([line.decode() for line in content_lines])

    return loads(content)


def is_ftp_dir(ftp_path: str, ftp: FTP) -> bool:
    r"""
    Checks if a given path on an FTP server is a directory.

    :param ftp_path:
        The path to check on the FTP server.
    :param ftp:
        An FTP object representing the connection to the server.

    :return:
        True if the path is a directory, False otherwise.

    This function attempts to change the current directory on the FTP server to the given path and then back to the
    parent directory. If this operation is successful, the function returns True, indicating that the path is a
    directory. If an exception is raised during this operation, the function returns False, indicating that the path is
    not a directory.
    """

    try:
        ftp.cwd(ftp_path)
        ftp.cwd("..")
        return True

    except Exception as _:  #todo: specify the non existing directory error!
        return False


@retry_on_exception
def mirror_ftp_file(ftp_path: str, target: str, host: str, port: int, username: str, password: str,
                    timeout: int) -> None:
    r"""
    Mirrors a file from an FTP server to a local target.

    :param ftp_path:
        The path of the file on the FTP server.
    :param target:
        The local target where the file will be mirrored.
    :param host:
        The host of the FTP server.
    :param port:
        The port of the FTP server.
    :param username:
        The username to connect to the FTP server.
    :param password:
        The password to connect to the FTP server.
    :param timeout:
        The timeout for the FTP connection.

    If the ftp_path is a directory, it will be skipped and a warning will be logged. If the mirroring is successful, a
    success message will be logged.
    """

    cprint(f"Mirroing [c]{ftp_path}[/] to [c]{target}[/]")

    with ftp_connect(host, port, username, password, timeout=timeout) as ftp:
        if not is_ftp_dir(ftp_path, ftp):
            with open(target, "wb") as target_file:
                ftp.retrbinary(f"RETR {ftp_path}", target_file.write)
        else:
            logger(f"Could not mirror a directory, skiping {ftp_path}", ptype="warning")

    logger(f"Successfuly mirroed {ftp_path} to {target}!", ptype="pass")


@retry_on_exception
def mirror_ftp_dir_structure(ftp_path: str, target: str, exclude: list[str], ftp: FTP) -> None:
    r"""
    Mirrors the directory structure from an FTP server to a local target.

    :param ftp_path:
        The path of the directory on the FTP server.
    :param target:
        The local target where the directory structure will be mirrored.
    :param exclude:
        A list of FTP paths to exclude from the mirroring.
    :param ftp:
        The FTP object representing the connection to the FTP server.

    This function recursively mirrors the directory structure. If the ftp_path is in the exclude list or is not a
    directory, it will be skipped.
    """

    if not os.path.exists(target):
        os.makedirs(target)

    if is_ftp_dir(ftp_path, ftp):
        ftp.cwd(ftp_path)

    for item in ftp.nlst():
        ftp_item_path: str = f"{ftp_path}/{item}"
        target_item_path: str = os.path.join(target, item)
        
        if ftp_item_path in exclude or not is_ftp_dir(ftp_item_path, ftp):
            continue

        mirror_ftp_dir_structure(ftp_item_path, target_item_path, exclude, ftp)


@retry_on_exception
def mirror_ftp_files(ftp_path: str, target: str, exclude: list[str], executor: ThreadPoolExecutor,
                             host: str, port: int, username: str, password: str, timeout: int) -> None:
    r"""
    Mirrors the files from an FTP server to a local target.

    :param ftp_path:
        The path of the directory on the FTP server.
    :param target:
        The local target where the files will be mirrored.
    :param exclude:
        A list of FTP paths to exclude from the mirroring.
    :param executor:
        The ThreadPoolExecutor that will be used for concurrent file mirroring.
    :param host:
        The host of the FTP server.
    :param port:
        The port of the FTP server.
    :param username:
        The username to connect to the FTP server.
    :param password:
        The password to connect to the FTP server.
    :param timeout:
        The timeout for the FTP connection.

    This function recursively mirrors the files. If the ftp_path is in the exclude list or is a directory, it will be
    skipped. Files are mirrored concurrently using the provided executor.
    """

    if not os.path.exists(target):
        os.makedirs(target)

    with ftp_connect(host, port, username, password, timeout=timeout) as ftp:
        if is_ftp_dir(ftp_path, ftp):
            ftp.cwd(ftp_path)

        for file in ftp.nlst():
            ftp_file_path: str = f"{ftp_path}/{file}"
            target_file_path: str = os.path.join(target, file)
            
            if ftp_file_path in exclude:
                continue

            if is_ftp_dir(ftp_file_path, ftp):
                mirror_ftp_files(ftp_file_path, target_file_path, exclude, executor, host, port, username,
                                        password, timeout)
                continue

            executor.submit(mirror_ftp_file, ftp_file_path, target_file_path, host, port, username, password, timeout)


def main(usr_args: list[str]) -> None:
    args: Namespace = parse_user_arguments(usr_args)
    config: SyncConfig = {}
    ftp_root: str = "/"

    with ftp_connect(args.host, args.port, args.username, args.password, timeout=args.timeout) as ftp:
        config = get_json_config_content(ftp, args.sync_config_file)
        ftp_root = ftp.pwd()

    menu: dict[str, str] = {}

    for profile_name, profile in config.items():
        menu[profile_name] = profile["Title"]

    profile_name: str
    _, profile_name, _ = display_options_menu("ANDROID FTP BACKUP\n- select a backup profile", menu)
    profile: BackupProfile = config[profile_name]
    exclude: list[str] = [item["Path"] for item in profile["Exclude"]]

    clear()

    for key, path in enumerate([data["Path"] for data in profile["Data"]]):
        logger("Normalizing the data path strings...")

        norm_path: str = path.replace("./", ftp_root)
        norm_path = ("/" if norm_path[0] != "/" else "") + norm_path
        profile["Data"][key]["Path"] = norm_path

    for key, path in enumerate([data["Path"] for data in profile["Exclude"]]):
        logger("Normalizing the exclude path strings...")

        norm_path: str = path.replace("./", ftp_root)
        norm_path = ("/" if norm_path[0] != "/" else "") + norm_path
        profile["Exclude"][key]["Path"] = norm_path

    benchmark_start: float = time()

    with ThreadPoolExecutor(max_workers=os.cpu_count() // 2) as executor:
        logger("Mirroring all files in parallel tasks...")

        for data in profile["Data"]:
            for target in args.targets:
                mirror_ftp_files(data["Path"], os.path.join(target, data["Path"].lstrip("/")), exclude,
                                         executor, args.host, args.port, args.username, args.password, args.timeout)

    benchmark: float = time() - benchmark_start

    cprint(f"\n[B]{benchmark} seconds[/]\n\n")
    input()


if __name__ == "__main__":
    clear()
    main(argv[1:])
