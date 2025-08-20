<h1 align="center" >ledger-cli-toolkit</h1>

<p align="center">Ledger file manipulation library</p>

<p align="center">
 <img alt="banner_01" src="https://img.shields.io/github/last-commit/EddyBel/Ledgerpy?color=%23AED6F1&style=for-the-badge" />
 <img alt="banner_02" src="https://img.shields.io/github/license/EddyBel/Ledgerpy?color=%23EAECEE&style=for-the-badge" />
 <img alt="banner_03" src="https://img.shields.io/github/languages/top/EddyBel/Ledgerpy?color=%23F9E79F&style=for-the-badge" />
 <img alt="banner_04" src="https://img.shields.io/github/languages/count/EddyBel/Ledgerpy?color=%23ABEBC6&style=for-the-badge" />
 <img alt="banner_05" src="https://img.shields.io/github/languages/code-size/EddyBel/Ledgerpy?color=%23F1948A&style=for-the-badge" />
</p>


`ledgerpy` is a Python library designed to read, manipulate, and generate accounting files in `.ledger` format. It offers a simple way to work with these files within the Python ecosystem, transforming them into JSON-like structures that are easy to process and analyze.

![Preview](./doc/preview/768_1x_shots_so.png)
![Preview](./doc/preview/413_1x_shots_so.png)

## Why `ledgerpy`?

The project was born from the need to have a tool to manipulate and read `.ledger` files directly from Python. While there are powerful tools such as `ledger-cli` to interact with these types of files from the command line, `ledgerpy` seeks to offer the same capability, but within the language, allowing developers to integrate this data into their applications in a simple way.

## Features

### Current Features

- JSON Conversion: Converts .ledger files into JSON structures for easy analysis and manipulation.
- Transaction Filtering: Filters records between specific dates.
- Balance Calculation: Calculates account balances from processed transactions.
- Add transactions: Add new transactions to .ledger files.

### In development
Plugin: LedgerVisual: An additional module that allows the visualization of accounting data in tables in a simple way.

- Display of transactions in journal format: Presents transactions in a table style accounting journal, with columns for:
  - Transaction number.
  - Date and time.
  - Concept.
  - Debit.
  - Credit.
  - Includes a final row with "EQUAL SUM" to total debits and credits.

- Display of general balances: Shows the balances by account in a table organized with:
  - Account number.
  - Account name.
  - Unit (example: USD, MXN).
  - Balance.

## Long-term goals
- Export to popular formats:
- Export transactions and balances to CSV files.
- Generate reports in PDF format with tables and graphs.
- Connection with SQL databases:
- Integration with databases such as MySQL, PostgreSQL and SQLite for storage and advanced querying of accounting data.

## Installation

You can easily install `ledgerpy` from PyPI with the following command:

```bash
pip install ledger-cli-toolkit
```

## Usage Examples

### Read and Convert a `.ledger` File to JSON

```python
from ledger_cli import LedgerParser

# Create a Parser Instance
parser = LedgerParser("my_file.ledger")

# Convert the file to JSON
json_transactions = parser.to_json()
print(json_transactions)
```

### Filter Transactions by Dates

```python
# Get Transactions Between Two Dates
filtered_transactions = parser.get_registers_between_dates("2023/01/01", "2023/12/31")
print (filtered_transactions)
```

### Calculate balances by account

```python
# Parse transactions
transactions = parser. parse()

# Calculate balances
balances = parser. calculate_balances(transactions)
print(balances)
```

### Add a new transaction

```python
# Add a transaction to the .ledger file
parser. add_transaction(
    date="2024/01/01",
    description="Payment of services",
    accounts=[
        {"account": "Expenses:Services", "unit": "USD", "amount": 50.00},
        {"account": "Assets:Bank", "unit": "USD", "amount": -50.00},
    ])
```

## Contribute

Contributions are welcome! If you have ideas, find bugs, or want to improve the functionality of `ledgerpy`, feel free to open an [issue](https://github.com/your-user/ledgerpy/issues) or send a pull request.

## License

This project is licensed under the MIT License. This means that you can use, modify, and distribute the code freely, as long as you include the original license notice.

---

<p align="center">
  <a href="https://github.com/EddyBel" target="_blank">
    <img alt="Github" src="https://img.shields.io/badge/GitHub-%2312100E.svg?&style=for-the-badge&logo=Github&logoColor=white" />
  </a>
  <a href="https://www.linkedin.com/in/eduardo-rangel-eddybel/" target="_blank">
    <img alt="LinkedIn" src="https://img.shields.io/badge/linkedin-%230077B5.svg?&style=for-the-badge&logo=linkedin&logoColor=white" />
  </a>
</p>
