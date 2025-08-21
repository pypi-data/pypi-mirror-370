from collections import defaultdict
import re
import time

import pandas as pd
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from .config import WAIT_TIME_BASE, WAIT_TIME_TABLE
from .budget_categories import BudgetType, budget_desc_to_ledger_account
from .yutils import print_progress, workday_str_amount_to_float


class TableExtractionError(Exception):
    """Custom exception for errors during table extraction."""


def extract_payroll_data_from_table(dr):
    return _extract_df_from_simple_table(dr)


def extract_journal_data_from_table(dr):
    return _extract_df_from_simple_table(dr)


def extract_transaction_data_from_table(dr):
    return _extract_df_from_simple_table(dr)


def extract_actuals_from_grant_table(dr, expected_month):
    """Extracts actuals from the data table.
    expected_month: (datetime) is used to verify that the correct report is loaded.
    """
    # Wait for the data table to be present and visible
    table_div = WebDriverWait(dr, WAIT_TIME_TABLE).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "div.wd-DataGrid"))
    )

    # Expand grant row
    _expand_all_rows(dr, table_div, min_rows=0, max_rows=1)

    table_html = table_div.get_attribute("outerHTML")
    soup = BeautifulSoup(table_html, "html.parser")

    # Find the first <table> inside the data grid (header table)
    headers = _extract_headers_from_grant_table(soup)

    # Ensure data for correct month was returned
    if not headers[2].startswith(f"{expected_month.strftime('%Y - %b')}"):
        raise TableExtractionError

    # Find the first <table> with class containing 'grid-body-row' (data rows)
    body_table = soup.find("table", class_=lambda x: x and "grid-body-row" in x)
    extracted_data = defaultdict(dict)

    for row in body_table.find_all("tr", attrs={"data-automation-id": "gridrow"})[2:]:
        # Skip the first two rows ("Object Class" and Award Name)
        cells = row.find_all("td", attrs={"data-automation-id": "gridCell"})
        cells = [cell.text.strip() for cell in cells]

        if cells[0] == "Total":
            continue

        category = budget_desc_to_ledger_account(cells[0])

        extracted_data[category][BudgetType.ACTUALS] = workday_str_amount_to_float(
            cells[3]
        )
        extracted_data[category][BudgetType.BUDGET] = workday_str_amount_to_float(
            cells[2]
        )
        extracted_data[category][BudgetType.ACTUALS_YTD] = workday_str_amount_to_float(
            cells[4]
        )
        extracted_data[category][BudgetType.COMMITTED] = workday_str_amount_to_float(
            cells[5]
        )
        extracted_data[category][BudgetType.ACTUALS_PREV] = (
            extracted_data[category][BudgetType.ACTUALS_YTD]
            - extracted_data[category][BudgetType.ACTUALS]
        )

    return extracted_data


def extract_actuals_from_activity_table(dr, expected_month):
    """Extracts actuals from the data table.
    expected_month: (datetime) is used to verify that the correct report is loaded.
    """
    # Wait for the data table to be present and visible
    table_div = WebDriverWait(dr, WAIT_TIME_TABLE).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "div.wd-DataGrid"))
    )

    # Expand grant row
    _expand_all_rows(dr, table_div, min_rows=1, max_rows=1)

    # Expand revenue/income/transfer rows
    _expand_all_rows(dr, table_div, min_rows=1, max_rows=3)

    table_html = table_div.get_attribute("outerHTML")
    soup = BeautifulSoup(table_html, "html.parser")

    headers = _extract_headers_from_grant_table(soup)

    # Ensure data for correct month was returned
    if not headers[1].startswith(f"{expected_month.strftime('%b %Y')}"):
        raise TableExtractionError

    # Find the first <table> with class containing 'grid-body-row' (data rows)
    body_table = soup.find("table", class_=lambda x: x and "grid-body-row" in x)

    extracted_data = defaultdict(dict)

    for row in body_table.find_all("tr", attrs={"data-automation-id": "gridrow"}):
        cells = row.find_all("td", attrs={"data-automation-id": "gridCell"})
        cells = [cell.text.strip() for cell in cells]

        # Skip the header rows
        if (
            cells[0] == "Gift"
            or cells[0].startswith("AC")
            or cells[0].startswith("GF")
            or re.match(r"\d - ", cells[0])
        ):
            continue

        assert re.match(r"\d\d\d\d:", cells[0]), f"Unexpected row format: {cells[0]}"

        extracted_data[cells[0]][BudgetType.ACTUALS] = workday_str_amount_to_float(
            cells[2]
        )
        extracted_data[cells[0]][BudgetType.BUDGET] = workday_str_amount_to_float(
            cells[1]
        )
        extracted_data[cells[0]][BudgetType.ACTUALS_YTD] = workday_str_amount_to_float(
            cells[3]
        )
        extracted_data[cells[0]][BudgetType.COMMITTED] = workday_str_amount_to_float(
            cells[4]
        )
        extracted_data[cells[0]][BudgetType.ACTUALS_PREV] = (
            extracted_data[cells[0]][BudgetType.ACTUALS_YTD]
            - extracted_data[cells[0]][BudgetType.ACTUALS]
        )

    return extracted_data


################################################################################
############################# Internal Helpers #################################
################################################################################
def _extract_headers_from_grant_table(soup):
    # Find the first <table> inside the data grid (header table)
    header_table = soup.find("table", class_="grid")
    headers = []
    if header_table:
        header_row = header_table.find("tr", class_="grid-head-row")
        if header_row:
            for th in header_row.find_all("td", attrs={"role": "columnheader"}):
                label = th.find("span", attrs={"data-automation-id": "columnLabel-0"})
                headers.append(label.text.strip() if label else th.text.strip())
    return headers


def _extract_df_from_simple_table(dr):
    """Extracts a simple table from the current page and returns it as a DataFrame."""

    # Find the table and get the headers
    table_div = dr.find_element(By.CSS_SELECTOR, 'div[data-testid="tableWrapper"]')
    table_html = table_div.get_attribute("outerHTML")
    soup = BeautifulSoup(table_html, "html.parser")

    headers = []
    header_row = soup.find("tr", attrs={"data-automation-id": "tableHeaderRow"})
    for th in header_row.find_all("th", attrs={"role": "columnheader"}):
        headers.append(th.find("span").get_text(strip=True))

    # Create empty dataframe with headers
    df = pd.DataFrame(columns=headers)

    row_count_elem = WebDriverWait(dr, WAIT_TIME_BASE).until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, '[data-automation-id="rowCountLabel"]')
        )
    )
    num_rows = row_count_elem.text.strip()
    m = re.match(r"(\d+) item", num_rows)
    assert m, f"Unexpected row count format: {num_rows}"
    num_rows = int(m.group(1))
    multiple_pages = num_rows > 30

    # Change the max rows to 30 to avoid hidden scrollable rows
    if multiple_pages:
        _set_max_rows_to_30(dr)

    while True:
        # Get the current active page number
        if multiple_pages:
            current_page_button = WebDriverWait(dr, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'button[aria-current="page"]')
                )
            )
            current_page = int(current_page_button.text.strip())
            print_progress(f"Currently on page {current_page}.")

        # Reload the table HTML to ensure we have the latest data
        table_div = dr.find_element(By.CSS_SELECTOR, 'div[data-testid="tableWrapper"]')
        table_html = table_div.get_attribute("outerHTML")
        soup = BeautifulSoup(table_html, "html.parser")

        # Find all data rows, and add them to the DataFrame
        data_rows = soup.find_all("tr", attrs={"data-automation-id": "row"})
        for row in data_rows:
            row_data = []
            cells = row.find_all("td", attrs={"data-automation-id": "cell"})
            for cell in cells:
                text = cell.get_text(strip=True)
                row_data.append(text)

            if row_data:
                df.loc[len(df)] = row_data

        if not multiple_pages:
            print_progress("Single page table extracted.")
            break

        # Find the 'Next' button
        next_button = dr.find_element(
            By.CSS_SELECTOR, 'button[data-automation-id="navigateNextPage"]'
        )

        # Check if it's disabled
        if next_button.get_attribute("aria-disabled") == "true":
            print_progress("Reached last page.")
            break
        next_button.click()

        print_progress(f"Clicked to go to page {current_page + 1}.")

        # Wait for page number to update
        WebDriverWait(dr, WAIT_TIME_BASE).until(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR, 'button[aria-current="page"]'),
                str(current_page + 1),
            )
        )
        # Sleep to allow the new page to load
        time.sleep(3)

    return df


def _expand_all_rows(dr, table_div, min_rows=None, max_rows=None):
    expand_buttons = table_div.find_elements(
        By.CSS_SELECTOR, 'div[data-automation-id="expand"][aria-expanded="false"]'
    )

    if min_rows is not None:
        assert (
            len(expand_buttons) >= min_rows
        ), f"Expected at least {min_rows} expandable rows, found {len(expand_buttons)}"
    if max_rows is not None:
        assert (
            len(expand_buttons) <= max_rows
        ), f"Expected at most {max_rows} expandable rows, found {len(expand_buttons)}"

    for expand_button in expand_buttons:
        dr.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});", expand_button
        )
        expand_button.click()
        time.sleep(3)  # Give time for expansion


def _extract_text(cell):
    # Try to get button value if present (for numbers)
    btn = cell.find("button", attrs={"data-automation-id": "drillDownNumberLabel"})
    if btn:
        return btn["aria-label"].strip()
    else:
        # Try to get text from gwt-Label or fallback to cell text
        label = cell.find("div", class_="gwt-Label")
        if label:
            return label.text.strip()
        else:
            return cell.text.strip()


def _set_max_rows_to_30(driver):
    # 1. Find the dropdown input
    dropdown_input = WebDriverWait(driver, WAIT_TIME_BASE).until(
        EC.element_to_be_clickable(
            (By.CSS_SELECTOR, 'input[data-testid="showAllRowsDropdownInput"]')
        )
    )

    # 2. Click to open the dropdown
    dropdown_input.click()

    # 3. Clear existing text (optional)
    dropdown_input.clear()

    # 4. Type "30"
    dropdown_input.send_keys("30")

    # 5. Press Enter to select
    dropdown_input.send_keys(Keys.ENTER)

    print_progress("Set max rows per page to 30.")
