import time
from datetime import datetime

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from .config import (
    WAIT_TIME_GRANT,
    WAIT_TIME_MENU_BUTTON,
    WAIT_TIME_PERIOD,
    WAIT_TIME_BASE,
    WAIT_TIME_TABLE,
    get_verbose,
)
from .chrome import goto_workday_page
from .table import (
    extract_actuals_from_activity_table,
    extract_actuals_from_grant_table,
    extract_journal_data_from_table,
    extract_payroll_data_from_table,
    extract_transaction_data_from_table,
)
from .yutils import TermColors, print_color, print_progress


################################################################################
############################# Report Functions #################################
################################################################################
def run_grant_report(dr, account, month_year):
    _configure_account_report(dr, "grant", account, month_year)
    _run_report(dr)
    _wait_for_data_table(dr, "div.wd-DataGrid")
    ret = extract_actuals_from_grant_table(dr, month_year)
    print("Done")
    return ret


def run_activity_report(dr, account, month_year):
    _configure_account_report(dr, "activity", account, month_year)
    _run_report(dr)
    _wait_for_data_table(dr, "div.wd-DataGrid")
    ret = extract_actuals_from_activity_table(dr, month_year)
    print("Done")
    return ret


def run_gift_report(dr, account, month_year):
    _configure_account_report(dr, "gift", account, month_year)
    _run_report(dr)
    _wait_for_data_table(dr, "div.wd-DataGrid")
    ret = extract_actuals_from_activity_table(dr, month_year)
    print("Done")
    return ret


def run_journal_report(dr, account, month_year):
    _configure_account_report(dr, "journal", account, month_year)
    _run_report(dr)
    _wait_for_data_table(dr, 'table[data-testid="table"]')
    ret = extract_journal_data_from_table(dr)
    print("Done")
    return ret


def run_transactions_report(dr, account, year):
    _configure_account_report(dr, "transaction", account, datetime(year, 1, 1))
    _run_report(dr, click_filter_first=False)
    _wait_for_data_table(dr, 'table[data-testid="table"]')
    ret = extract_transaction_data_from_table(dr)
    print(f"Done. Extracted {len(ret)} rows.")
    return ret


def run_payroll_report(dr, account, year):
    _configure_account_report(dr, "payroll", account, datetime(year, 1, 1))

    _run_report(dr)
    _wait_for_data_table(dr, 'table[data-testid="table"]')

    ret = extract_payroll_data_from_table(dr)
    print("Done")
    return ret


################################################################################
############################# Internal Helpers #################################
################################################################################


def _wait_for_data_table(dr, selector):
    # Wait for the data table to be present and visible
    WebDriverWait(dr, WAIT_TIME_TABLE).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, selector))
    )
    print_progress("Data table is visible.")


def _configure_account_report(dr, type, account, month_year):
    if type in ("transaction", "payroll"):
        month_year_str = month_year.strftime("%Y")
    else:
        month_year_str = month_year.strftime("%b %Y")

    print_color(
        TermColors.BLUE,
        f"Running {type} report for {account} {month_year_str}",
        end="\n" if get_verbose() else "",
    )
    goto_workday_page(dr)
    _goto_finance_reports(dr)

    if type == "journal":
        _click_finance_report(dr, "BYU Find Journal Lines")
    elif type == "transaction":
        _click_finance_report(dr, "BYU Grants Transactions")
    elif type == "payroll":
        _click_finance_report(dr, "BYU Payroll Details By Worktag")
    else:
        _click_finance_report(
            dr, f"BYU Budget Vs Actuals Overview by {type.capitalize()}"
        )

    # Set the grant or account in the search input
    if type in ("gift", "journal", "grant", "activity"):
        _set_report_input_box(dr, "Organization", account, sleep=WAIT_TIME_GRANT)
    elif type in ("transaction"):
        _set_report_input_box(dr, "Grant", account, sleep=WAIT_TIME_GRANT)

    # For payroll report, click the 'Exclude Grant' checkbox
    if type == "payroll":
        checkbox_panel = WebDriverWait(dr, 10).until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    "//label[contains(text(), 'Exclude Grant')]/ancestor::li//div[@data-automation-id='checkboxPanel']",
                )
            )
        )
        checkbox_panel.click()

    if type == "transaction":
        _set_date_by_label(dr, "Start Date", 1, 1, month_year.year)
        _set_date_by_label(dr, "End Date", 12, 31, month_year.year)
    elif type == "payroll":
        _set_date_by_label(dr, "Starting Accounting_Date", 1, 1, month_year.year)
        _set_date_by_label(dr, "Ending Accounting_Date", 12, 31, month_year.year)
    else:
        _set_report_input_box(
            dr, "Period", month_year.strftime("%b %Y"), sleep=WAIT_TIME_PERIOD
        )


def _run_report(dr, click_filter_first=True):
    # Click in the Filter Name box before clicking OK
    if click_filter_first:
        filter_name_input = WebDriverWait(dr, 10).until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, 'input[data-automation-id="textInputBox"]')
            )
        )
        dr.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});", filter_name_input
        )
        filter_name_input.click()
        print_progress("Clicked in the Filter Name input box.")

    # Now wait for the OK button to be clickable and click it
    try:
        ok_button = WebDriverWait(dr, WAIT_TIME_BASE).until(
            EC.element_to_be_clickable(
                (
                    By.CSS_SELECTOR,
                    'button[data-automation-id="wd-CommandButton_uic_okButton"][title="OK"]',
                )
            )
        )
        dr.execute_script("arguments[0].scrollIntoView({block: 'center'});", ok_button)
        ok_button.click()
        print_progress("OK button to run the report.")
    except Exception as e:
        print("Could not find or click the OK button:", e)


def _set_date_by_label(dr, label_text, month, day, year):
    _set_report_input_box(
        dr,
        label_text,
        str(month).zfill(2),
        "[@data-automation-id='dateSectionMonth-input']",
    )
    _set_report_input_box(
        dr,
        label_text,
        str(day).zfill(2),
        "[@data-automation-id='dateSectionDay-input']",
    )
    _set_report_input_box(
        dr,
        label_text,
        str(year).zfill(2),
        "[@data-automation-id='dateSectionYear-input']",
    )
    return


def _goto_finance_reports(dr):
    # Click the global navigation button to open the menu
    global_nav_button = WebDriverWait(dr, WAIT_TIME_BASE).until(
        EC.element_to_be_clickable(
            (By.CSS_SELECTOR, 'button[data-automation-id="globalNavButton"]')
        )
    )
    time.sleep(WAIT_TIME_MENU_BUTTON)
    global_nav_button.click()
    print_progress("Menu button clicked.")

    # Click the Menu button
    menu_button = WebDriverWait(dr, WAIT_TIME_BASE).until(
        EC.element_to_be_clickable(
            (By.CSS_SELECTOR, 'button[data-automation-id="globalNavAppsTab"]')
        )
    )
    menu_button.click()
    print_progress("Menu button clicked.")

    # Wait for and click the BYU Finance Dashboard link
    finance_dashboard_link = WebDriverWait(dr, WAIT_TIME_BASE).until(
        EC.element_to_be_clickable(
            (
                By.CSS_SELECTOR,
                'a[data-automation-id="globalNavAppItemLink"][aria-label="BYU Finance Dashboard"]',
            )
        )
    )
    dr.execute_script(
        "arguments[0].scrollIntoView({block: 'center'});", finance_dashboard_link
    )
    WebDriverWait(dr, WAIT_TIME_BASE).until(EC.visibility_of(finance_dashboard_link))
    finance_dashboard_link.click()
    print_progress("BYU Finance Dashboard link clicked.")

    # Wait for and click the BYU Finance Reports tab
    tabs = WebDriverWait(dr, WAIT_TIME_BASE).until(
        EC.presence_of_all_elements_located(
            (
                By.CSS_SELECTOR,
                'li[data-automation-id="tab"] .gwt-Label[data-automation-id="tabLabel"]',
            )
        )
    )
    found = False
    for tab in tabs:
        if tab.text.strip() == "BYU Finance Reports":
            tab.click()
            print_progress("BYU Finance Reports tab clicked.")
            found = True
            break
    if not found:
        print("Could not find the BYU Finance Reports tab.")
    time.sleep(1)

    # Wait for and click the 'More' button before clicking the report
    try:
        # Wait for the 'More' button to be present in the DOM
        more_button = WebDriverWait(dr, WAIT_TIME_BASE).until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, 'div[data-automation-id="wd-MoreLink"]')
            )
        )
        # Wait until the button is visible (not zero size)
        WebDriverWait(dr, WAIT_TIME_BASE).until(
            lambda d: more_button.is_displayed()
            and more_button.size["height"] > 0
            and more_button.size["width"] > 0
        )
        dr.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});", more_button
        )
        # Try to click with JS if normal click fails
        try:
            more_button.click()
        except Exception:
            dr.execute_script("arguments[0].click();", more_button)
        print_progress("'More' button clicked.")
    except Exception as e:
        print("Could not find or click the 'More' button:", e)
    time.sleep(1)


def _click_finance_report(dr, report_name):
    """On the 'BYU Finance Reports' page, click the specified report by its name."""
    report_div = WebDriverWait(dr, WAIT_TIME_BASE).until(
        EC.element_to_be_clickable(
            (By.CSS_SELECTOR, f"div.WAYC[title='{report_name}']")
        )
    )
    dr.execute_script("arguments[0].scrollIntoView({block: 'center'});", report_div)
    report_div.click()
    print_progress(f"'{report_name}' report clicked.")


def _set_report_input_box(dr, label_name, value, filter="", sleep=0):
    search_path = f"//label[normalize-space(.)='{label_name}']/ancestor::li//input"
    if filter:
        search_path += filter
    input_box = WebDriverWait(dr, WAIT_TIME_BASE).until(
        EC.element_to_be_clickable(
            (
                By.XPATH,
                search_path,
            )
        )
    )
    dr.execute_script("arguments[0].scrollIntoView({block: 'center'});", input_box)
    dr.execute_script("arguments[0].focus();", input_box)
    input_box.clear()
    print_progress(f"Setting {label_name} to {value}")
    input_box.send_keys(value)
    time.sleep(0.5)
    input_box.send_keys(Keys.ENTER)
    time.sleep(sleep)
