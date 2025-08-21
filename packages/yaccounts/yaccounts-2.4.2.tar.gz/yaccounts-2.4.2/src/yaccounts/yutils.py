import pathlib
import appdirs

from .config import get_verbose


class TermColors:
    NONE = ""
    PURPLE = "\033[95m"
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    END = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


def error(msg):
    print_color(TermColors.RED, f"ERROR: {msg}")
    assert False, "Exiting due to error"


def warn(msg):
    print_color(TermColors.YELLOW, f"Warning: {msg}")


def print_color(color, msg, end="\n"):
    print(f"{color}{msg}{TermColors.END}", end=end, flush=True)


def retry(func, retries=3, exception=Exception, *args, **kwargs):
    for attempt in range(1, retries + 1):
        try:
            return func(*args, **kwargs)  # Pass arguments to the function
        except exception as e:
            warn(f"Warning: Attempt {attempt} failed")
            if attempt == retries:
                raise  # Re-raise the last exception after all retries


def workday_str_amount_to_float(val):
    """Clean financial amounts."""
    if isinstance(val, str):
        val = val.replace("$", "").replace(",", "").strip()
        val = val.strip()
        if val.startswith("(") and val.endswith(")"):
            val = "-" + val[1:-1]  # Convert (292.53) -> -292.53
        val = val.replace(",", "")  # Remove thousands separator
    return float(val)


def get_app_data_dir(app_name="yaccounts"):
    data_dir = appdirs.user_data_dir(appname=app_name)
    path = pathlib.Path(data_dir)
    path.mkdir(parents=True, exist_ok=True)
    return path


def print_progress(message):
    """Print a progress message if VERBOSE, otherwise print '.'"""
    if get_verbose():
        print(message)
    else:
        print(".", end="", flush=True)
