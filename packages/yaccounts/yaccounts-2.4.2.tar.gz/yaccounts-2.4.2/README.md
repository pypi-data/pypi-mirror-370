# yaccounts Package
#### Scripts for generating BYU accounting reports with the new Workday system

## Installation
It is recommended that you first create a Python virtual environment to avoid conflicts with other packages. 

    python3 -m venv venv

Activate the virtual environment in your terminal (this needs to be done each time you open a new terminal session):
- On Windows:
    ```
    venv\Scripts\activate
    ```
- On macOS/Linux:
    ```
    source venv/bin/activate
    ```

Then install the package using pip:

    pip install yaccounts


## Command-Line Usage

1. **First run Chrome.**  This will run chrome with a remote debugging port open, and uses a new user profile so that it does not interfere with your normal Chrome profile.  When this window opens, you will need to log in to Workday with your BYU credentials, then return to the terminal and hit enter to continue.
    
        yaccounts run-chrome

2. **Actuals Report**. Then you can run the following to collect month-by-month actuals for a given account.  This can be done for any account, although non-GR accounts use different reports that will take a bit longer to run.

        yaccounts report-actuals GR01410

*Note:* The produced Excel file will have hidden rows with the journal entries. Click the '+' buttons on the left side of the sheet to expand these rows and see the journal entries.

### XLSX Merging

If you want to merge the Excel files for multiple accounts into a single file, you can use the `xlsx-merge` subcommand.  The first argument is the output file, and the rest are the input files to merge.  For example:

    yaccounts xlsx-merge merged.xlsx GR01410_2025.xlsx GR01172_2025.xlsx

## Python Usage

You can also use the package in Python code.  First, install the package as described above, then you can use it like this:

```python

from yaccounts import Account, run_chrome, get_chrome_webdriver


def main():
    run_chrome()

    dr = get_chrome_webdriver()

    payroll = PayrollData(2025)
    payroll.get_workday_data(dr)

    account = Account("GR00227", 2025)
    account.get_workday_data(dr)
    account.to_excel()
```

## FAQ

#### **Q: Can I run multiple reports at once?**

**A:** No, different accounts use different report types, so for simplicity, you can only run one account at a time.


#### **Q: Can I export the transaction data to Excel?**

**A:** Yes, you can export the transaction data to Excel by adding the `--transactions-xlsx-out <file>` argument to the `report-actuals` command.  For non-GR accounts, the transaction data comes from a combination of the journal report and the payroll report, which can be exported using `"--journals-xlsx-out` and `--payroll-xlsx-out`.

#### **Q: The sub-rows in the Excel report don't add up to the parent row. Why?**
**A:** The parent rows come from the budget and actual report, which provides month-by-month balances.  The sub-rows come from separate transaction reports, which may not always align perfectly with the parent row totals. I'm not sure why. This appears to mainly happen with the wages category; if you see this happening with other categories, please let me know.

#### **Q: Why are amounts for the current month negative?**
**A:** I'm not sure why it is done this way in Workday, but it seems to always occur.  Perhaps due to a partial pay period?

## Makefile

Here is a Makefile I use to run all my accounts:

```makefile
IN_ENV := . .venv/bin/activate;

YEAR := 2025

ACCOUNTS := \
    sandia:GR01410 \
    onr:GR01172 \
    consolidated:AC07190 \
    gift:GF02905

ACCOUNT_NAMES := $(foreach pair, $(ACCOUNTS), $(firstword $(subst :, ,$(pair))))

all_accounts: $(foreach name, $(ACCOUNT_NAMES), $(name)_${YEAR}.xlsx)

env: .venv/bin/activate

.venv/bin/activate: requirements.txt
	python3 -m venv .venv
	$(IN_ENV) pip install yaccounts

chrome:
	$(IN_ENV) yaccounts run-chrome

clean:
	rm -f $(foreach name, $(ACCOUNT_NAMES), $(name)_${YEAR}.xlsx) payroll_${YEAR}.pkl

# Pattern rule for each account
%_${YEAR}.xlsx:
	$(IN_ENV) yaccounts report-actuals $(call get_code,$*) --xlsx-out $@ --year ${YEAR} 

# Function to extract the code given a name
get_code = $(word 2, $(subst :, ,$(filter $1:%,$(ACCOUNTS))))
```