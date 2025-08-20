from tabulate import tabulate
from typing import List, Dict, Union


class LedgerVisual:

    @staticmethod
    def display_journal_table(
        transactions_json: List[
            Dict[str, Union[str, List[Dict[str, Union[str, float]]]]]
        ],
        title_table="Ledger",
        period: str = "2025",
        label: str = "SUMAS IGUALES",
        style: str = "simple",
        headers: List[str] = ["N°", "Fecha", "Concepto", "Debe", "Haber"],
    ):
        """
        Display the transactions in a journal-like table format with columns:
        - N° (Transaction Index)
        - Date (Transaction Date and Time)
        - Concept (Account Name)
        - Debit (Positive Amounts)
        - Credit (Negative Amounts)

        At the end of the table, show "SUMAS IGUALES" with the total debit and credit.
        """
        table_data = []
        total_debit = 0.0
        total_credit = 0.0

        for idx, transaction in enumerate(transactions_json, start=1):
            for account in transaction["accounts"]:
                date_time = transaction["date"]
                if transaction.get("time"):
                    date_time += f" {transaction['time']}"

                account_name = account["account"]
                amount = account["amount"]
                debit = amount if amount > 0 else 0
                credit = -amount if amount < 0 else 0

                table_data.append([idx, date_time, account_name, debit, credit])

                total_debit += debit
                total_credit += credit

        # Add SUMAS IGUALES row
        table_data.append(["", "", label, total_debit, total_credit])

        table = tabulate(
            table_data,
            headers=headers,
            floatfmt=".2f",
            tablefmt=style,
            numalign="right",
        )
        # output = f"{title_table}\n{period}\n{'=' * len(title_table)}\n{table}"
        print(table)

    @staticmethod
    def display_general_balance(
        account_balances: Dict[str, Dict[str, float]],
        label="BALANCE GENERAL",
        style="simple",
        headers=["N°", "Concepto", "Unidad", "Saldo"],
    ):
        table = []
        total_balance = 0.0

        for index, (account, balances) in enumerate(account_balances.items(), start=1):
            for unit, balance in balances.items():
                table.append([index, account, unit, f"{balance:.2f}"])
                total_balance += balance

        table.append(["", label, "", f"{total_balance:.2f}"])
        print(tabulate(table, headers=headers, tablefmt=style, numalign="right"))

    @staticmethod
    def display_accounts_list(
        accounts: List[str],
        style="simple",
        headers=["N°", "Concepto"],
    ):
        table = []

        for index, account in enumerate(accounts, start=1):
            table.append([index, account])

        print(tabulate(table, headers=headers, tablefmt=style, numalign="right"))

    @staticmethod
    def display_details_balances(
        balances_details: Dict[str, Dict[str, Dict[str, float]]],
        style="simple",
        headers=["N°", "Concepto", "Unidad", "Saldo"],
    ):
        balance_total = 0

        def traverse_accounts(accounts, parent_name="", n=1, balance_total=0):
            rows = []
            for account, details in accounts.items():

                for unit, balance in details["balances"].items():
                    concept = f"{parent_name} -> {account}" if parent_name else account
                    balance = details["balances"][unit]
                    balance_total += balance
                    rows.append([n, concept, unit, balance])
                    n += 1

                # Recursively process sub-accounts
                sub_rows, n = traverse_accounts(
                    details.get("sub_accounts", {}),
                    concept,
                    n,
                    balance_total=balance_total,
                )
                rows.extend(sub_rows)
            return rows, n

        # Traverse all top-level accounts
        rows, _ = traverse_accounts(balances_details, balance_total=balance_total)
        rows.append(["", "BALANCE FINAL", "", balance_total])
        # Print the table
        print(tabulate(rows, headers=headers, tablefmt=style, floatfmt=".2f"))

    @staticmethod
    def display_parents_balances(
        balances_by_parents,
        headers=["N°", "Concepto", "Unidad", "Saldo"],
        style="simple",
    ):
        rows = []

        for index, account in enumerate(balances_by_parents, start=1):

            for unit in balances_by_parents[account]:
                rows.append([index, account, unit, balances_by_parents[account][unit]])

        print(tabulate(rows, headers=headers, tablefmt=style, floatfmt=".2f"))

    @staticmethod
    def print_balances(data):
        rows = []

        def process_account(name, account, level=0):
            indent = "  " * level
            for unit, balance in account.get("balances", {}).items():
                rows.append([len(rows) + 1, f"{indent}{name}", unit, balance])

            for sub_name, sub_account in account.get("sub_accounts", {}).items():
                process_account(sub_name, sub_account, level + 1)

        for main_account, account_data in data.items():
            process_account(main_account, account_data)

        headers = ["N", "Concepto", "Unidad", "Saldo"]
        print(tabulate(rows, headers=headers, tablefmt="grid"))


# Ejemplo de uso
if __name__ == "__main__":
    # Ejemplo de datos de transacciones
    example_transactions = [
        {
            "date": "2025/01/02",
            "time": "12:00:00",
            "verified": True,
            "description": "Compra de insumos",
            "accounts": [
                {"account": "Expenses:Office", "unit": "USD", "amount": 100.0},
                {"account": "Assets:Cash", "unit": "USD", "amount": -100.0},
            ],
        },
        {
            "date": "2025/01/03",
            "verified": True,
            "description": "Pago de servicios",
            "accounts": [
                {"account": "Expenses:Utilities", "unit": "USD", "amount": 50.0},
                {"account": "Assets:Bank", "unit": "USD", "amount": -50.0},
            ],
        },
    ]

    balances = {
        "Assets:Cash": {"MXN": 35.0},
        "Liabilities:Debts:Belem": {"MXN": -800.0},
        "Assets:Bank:Azteca:Guardadito": {"MXN": 0.0},
        "Assets:Bank:MercadoPago": {"MXN": 0.0},
        "Liabilities:CreditCard:MercadoPago": {"MXN": 78.36},
        "Assets:Bank:Nubank": {"MXN": -2.2737367544323206e-13},
        "Expenses:Pareja:Regalos": {"MXN": 270.0},
        "Income:Otros": {"MXN": -1250.0},
        "Income:Educacion": {"MXN": -500.0},
        "Expenses:Transporte": {"MXN": 65.0},
        "Expenses:Educacion:Universidad": {"MXN": 30.0},
        "Expenses:Pareja:Salidas": {"MXN": 373.0},
        "Expenses:Propinas": {"MXN": 36.0},
        "Assets:Bank:UALA": {"MXN": 1151.64},
        "Expenses:Otros": {"MXN": 81.0},
    }

    visual = LedgerVisual()
    visual.display_journal_table(example_transactions)
    visual.display_general_balance(balances)
