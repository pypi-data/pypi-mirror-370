import argparse
from datetime import datetime
import pathlib

from .xlsx import xlsx_merge
from .config import DEFAULT_CHROME_PORT, set_new_chrome_tabs, set_verbose
from .account import Account
from .chrome import get_chrome_webdriver, run_chrome
from .yutils import error


def run_chrome_command(args):
    run_chrome(port=args.port)


def report_actuals_command(args):
    if args.verbose:
        set_verbose(True)
    if args.tabs:
        set_new_chrome_tabs(True)

    dr = get_chrome_webdriver(remote_debugging_port=args.port)

    account = Account(
        args.account,
        args.year,
        args.transactions_xlsx_out,
        args.payroll_xlsx_out,
        args.journals_xlsx_out,
    )
    account.get_workday_data(dr)

    account.to_excel(args.xlsx_out)


def xlsx_merge_command(args):
    if not args.input_files or len(args.input_files) < 2:
        error("You must specify at least two input files to merge.")
    xlsx_merge(args.input_files, args.output_file)


def main():
    parser = argparse.ArgumentParser(description="YAccounts Workday CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    #################### Run Chrome Command ####################
    launch_chrome_parser = subparsers.add_parser(
        "run-chrome", help="Launch Chrome browser"
    )
    launch_chrome_parser.add_argument(
        "--port",
        type=int,
        default=DEFAULT_CHROME_PORT,
        help=f"Port to use for Chrome remote debugging (default: {DEFAULT_CHROME_PORT})",
    )
    launch_chrome_parser.set_defaults(func=run_chrome_command)

    #################### Report Actuals Command ####################
    report_actuals_parser = subparsers.add_parser(
        "report-actuals", help="Run the budget and actuals report"
    )
    report_actuals_parser.add_argument(
        "account",
        type=str,
        help="Workday account ID (e.g., GR00227)",
    )
    report_actuals_parser.add_argument(
        "--year",
        type=int,
        default=datetime.now().year,
        help="Year for the budget report (default: current year)",
    )
    report_actuals_parser.add_argument(
        "--xlsx-out",
        type=pathlib.Path,
        help="Path to save the output Excel file (default: ./<account>_<year>.xlsx)",
    )
    report_actuals_parser.add_argument(
        "--transactions-xlsx-out",
        type=pathlib.Path,
        help="Path to save the transaction data as an Excel file. Only applicable to GR accounts. (optional, default: None)",
    )
    report_actuals_parser.add_argument(
        "--journals-xlsx-out",
        type=pathlib.Path,
        help="Path to save the journal data as an Excel file. Only applicable to non-GR accounts. (optional, default: None)",
    )
    report_actuals_parser.add_argument(
        "--payroll-xlsx-out",
        type=pathlib.Path,
        help="Path to save the payroll data as an Excel file. Only applicable to non-GR accounts. (optional, default: None)",
    )
    report_actuals_parser.add_argument(
        "--port",
        type=int,
        default=DEFAULT_CHROME_PORT,
        help=f"Port Chrome is running on (default: {DEFAULT_CHROME_PORT})",
    )
    report_actuals_parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose output",
    )
    report_actuals_parser.add_argument(
        "--tabs",
        action="store_true",
        help="Open new Chrome tabs for each operation (default: False)",
    )
    report_actuals_parser.set_defaults(func=report_actuals_command)

    #################### XLSX Merge Command #####################
    xlsx_merge_parser = subparsers.add_parser(
        "xlsx-merge", help="Merge multiple Excel files into one"
    )
    xlsx_merge_parser.add_argument(
        "output_file",
        type=pathlib.Path,
        help="Path to the output Excel file where merged data will be saved",
    )
    xlsx_merge_parser.add_argument(
        "input_files",
        nargs="+",
        type=pathlib.Path,
        help="Paths to the input Excel files to merge",
    )
    xlsx_merge_parser.set_defaults(func=xlsx_merge_command)

    args = parser.parse_args()

    # Automatically call the right function!
    args.func(args)
