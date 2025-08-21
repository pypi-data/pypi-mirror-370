import enum


def budget_desc_to_ledger_account(budget_desc: str) -> str:
    """Convert a workday category to an AccountCategory enum."""
    lookup = {
        "BYU Grants: Benefits": "5900:Benefits",
        "BYU Grants: Indirect Costs": "6400:Indirect Costs",
        "BYU Grants: Materials and Supplies": "6100:Materials and Supplies",
        "BYU Grants: Salaries and Wages": "5000:Salaries and Wages",
        "BYU Grants: Student Aid": "6300:Student Aid",
        "BYU Grants: Travel": "7000:Travel",
        "BYU Grants: Unallocated": "9999:Unallocated",
        "BYU Grants: Capital Equipment": "6900:Capital Equipment",
        "BYU Grants: Contract Services": "6450:Contract Services",
    }
    if budget_desc in lookup:
        return lookup[budget_desc]
    else:
        raise ValueError(f"Unknown category: {budget_desc}. Please update the lookup.")


class BudgetType(enum.Enum):
    """Enum for budget types."""

    ACTUALS = 0
    BUDGET = 1
    ACTUALS_YTD = 2
    ACTUALS_PREV = 3
    COMMITTED = 4


class AccountType(enum.Enum):
    """Enum for account types."""

    GR = "GR"
    AC = "AC"
    GF = "GF"
