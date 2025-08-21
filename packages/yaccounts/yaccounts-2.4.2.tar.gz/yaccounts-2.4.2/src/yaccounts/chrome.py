import pathlib
import platform
import shutil
import subprocess

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from .config import get_new_chrome_tabs
from .yutils import TermColors, get_app_data_dir


def get_default_chrome_path():
    system = platform.system()
    if system == "Windows":
        return pathlib.Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe")
    elif system == "Darwin":
        return pathlib.Path(
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        )
    elif system == "Linux":
        return pathlib.Path(
            shutil.which("google-chrome")
            or shutil.which("chromium")
            or shutil.which("chromium-browser")
        )
    else:
        raise RuntimeError(f"Unsupported platform: {system}")


# def get_default_chrome_user_data_dir():
#     system = platform.system()
#     if system == "Windows":
#         return os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\User Data")
#     elif system == "Darwin":
#         return os.path.expanduser("~/Library/Application Support/Google/Chrome")
#     elif system == "Linux":
#         return os.path.expanduser("~/.config/google-chrome")
#     else:
#         raise RuntimeError(f"Unsupported platform: {system}")


def run_chrome(port=9222):
    chrome_path = get_default_chrome_path()
    if not chrome_path.exists():
        raise RuntimeError(f"Chrome executable not found at {chrome_path}")

    chrome_profile_path = get_app_data_dir() / "chrome-user-data"
    subprocess.Popen(
        [
            chrome_path,
            f"--remote-debugging-port={port}",
            f"--user-data-dir={chrome_profile_path}",
            "--no-first-run",
            "--no-default-browser-check",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    chrome_options = Options()
    chrome_options.debugger_address = f"127.0.0.1:{port}"

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    goto_workday_page(driver)

    print(
        f"Chrome launched with remote debugging on port {port}, using profile {chrome_profile_path}"
    )
    input(
        f"{TermColors.YELLOW}Please log in to workday and then press Enter.{TermColors.END}"
    )


def get_chrome_webdriver(profile_name="Default", remote_debugging_port=9222):
    # Connect to running Chrome
    chrome_options = Options()
    chrome_options.debugger_address = f"127.0.0.1:{remote_debugging_port}"

    driver = webdriver.Chrome(options=chrome_options)

    return driver


def goto_workday_page(dr):
    url = "https://www.myworkday.com/byu/d/home.htmld"

    if get_new_chrome_tabs():
        # Open a new tab and switch to it
        script = f"window.open('{url}', '_blank');"
        dr.execute_script(script)
        dr.switch_to.window(dr.window_handles[-1])

    dr.get(url)
