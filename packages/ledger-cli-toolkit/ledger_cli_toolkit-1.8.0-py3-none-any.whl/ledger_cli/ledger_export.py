from .exports.excel.excel_exports import LedgerExcel
from .exports.base.ledger_clasic import LedgerLedger
from .exports.sqL.ledger_sql import LedgerSQL


class LedgerExport:
    def __init__(self, transactions: list[dict], accounts: list[dict] = None):
        self.transactions = transactions or []
        self.accounts = accounts or []

    def export_classic(self, path: str):
        """Export the transactions and accounts to a .ledger file.

        Args:
            path (str): path to save the file

        Raises:
            ValueError: if the file format is not supported

        Returns:
            _type_: content and function to save the file
        """
        ledger = LedgerLedger(self.transactions, self.accounts)
        content = ledger.build_ledger_text()
        return content, lambda: ledger.save_file(file_path=path, multi_file=False)

    def export_excel(self, type: str, path: str):
        """Export the transactions and accounts to Excel.

        Args:
            type (str): extension file
            path (str): path to save the file

        Raises:
            ValueError: if the file format is not supported

        Returns:
            _type_: content and function to save the file
        """
        ledger = LedgerExcel(self.transactions, self.accounts)
        if type == "xlsx":
            file = ledger.export_transactions(file_format="xlsx")
            return file, lambda: ledger.save_file(file_path=path, file_format=type)
        elif type == "csv":
            file = ledger.export_transactions(file_format="csv")
            return file, lambda: ledger.save_file(file_path=path, file_format=type)
        else:
            raise ValueError("Formato no soportado ", type)

    def export_sql(self, engine: str = "standard", path: str = None):
        """Export the transactions and accounts to SQL.

        Args:
            engine (str, optional): SQL engine. Defaults to "standard".
            path (str, optional): path to save the file. Defaults to None.

        Raises:
            ValueError: if the file format is not supported

        Returns:
            _type_: content and function to save the file
        """
        ledger = LedgerSQL(self.transactions, self.accounts)
        content = ledger.export_sql(engine=engine)
        return content, lambda: ledger.save_file(file_path=path, engine=engine)
