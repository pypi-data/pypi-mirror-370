import pandas as pd
from io import BytesIO
from pathlib import Path

class LedgerExcel:
    def __init__(
        self,
        transactions: list[dict],
        accounts: list[dict] = None,
        transactions_columns: dict = None,
        accounts_columns: dict = None,
    ):
        self.transactions = transactions or []
        self.accounts = accounts or []

        # Columnas para libro diario
        self.transactions_columns = transactions_columns or {
            "ID": "ID",
            "Date": "Fecha",
            "Concept": "Concepto",
            "Debit": "Debe",
            "Credit": "Haber",
            "Description": "Descripción",
        }

        # Configuración de columnas de cuentas contables
        self.accounts_columns = {}
        self.configure_accounts_columns(accounts_columns)

        # Para multi-hojas
        self._multi_sheet_writer = None
        self._multi_sheet_buffer = None

    def configure_accounts_columns(self, manual_columns: dict = None):
        if manual_columns:
            self.accounts_columns = manual_columns
        else:
            all_keys = set()
            for acc in self.accounts:
                if isinstance(acc, dict):
                    all_keys.update(acc.keys())
            self.accounts_columns = {key: key.capitalize() for key in all_keys}
            if "account" in self.accounts_columns:
                self.accounts_columns = {"account": self.accounts_columns.pop("account"), **self.accounts_columns}

    def _to_ledger_table(self):
        rows = []
        id_counter = 1
        for tx in self.transactions:
            for account in tx["accounts"]:
                row = {}
                if "ID" in self.transactions_columns:
                    row[self.transactions_columns["ID"]] = id_counter
                if "Date" in self.transactions_columns:
                    row[self.transactions_columns["Date"]] = tx["date"]
                if "Concept" in self.transactions_columns:
                    row[self.transactions_columns["Concept"]] = account["account"]
                if "Debit" in self.transactions_columns:
                    row[self.transactions_columns["Debit"]] = (
                        account["amount"] if account["amount"] > 0 else ""
                    )
                if "Credit" in self.transactions_columns:
                    row[self.transactions_columns["Credit"]] = (
                        abs(account["amount"]) if account["amount"] < 0 else ""
                    )
                if "Description" in self.transactions_columns:
                    row[self.transactions_columns["Description"]] = tx["description"]
                rows.append(row)
            id_counter += 1
        return pd.DataFrame(rows)

    def _to_accounts_table(self, accounts: list = None):
        accounts = accounts or self.accounts
        rows = []

        if not accounts:
            return pd.DataFrame()

        if isinstance(accounts[0], str):
            for idx, acc in enumerate(accounts, start=1):
                row = {"ID": idx}
                if "account" in self.accounts_columns:
                    row[self.accounts_columns["account"]] = acc
                rows.append(row)
        elif isinstance(accounts[0], dict):
            for idx, acc in enumerate(accounts, start=1):
                row = {"ID": acc.get("id", idx)}
                for key, col_name in self.accounts_columns.items():
                    if key != "id":
                        row[col_name] = acc.get(key, "")
                rows.append(row)
        return pd.DataFrame(rows)

    # -------------------- Multi-sheet support --------------------
    def start_multi_sheet(self):
        """Inicia un libro de Excel en memoria para múltiples hojas."""
        self._multi_sheet_buffer = BytesIO()
        self._multi_sheet_writer = pd.ExcelWriter(self._multi_sheet_buffer, engine="openpyxl")

    def add_sheet(self, df: pd.DataFrame, sheet_name: str):
        """Agrega un DataFrame como hoja al libro multi-sheet en memoria."""
        if not self._multi_sheet_writer:
            raise ValueError("Debes llamar primero a start_multi_sheet()")
        df.to_excel(self._multi_sheet_writer, index=False, sheet_name=sheet_name)

    def save_multi_sheet(self, file_path: str):
        """Finaliza el libro multi-hoja y guarda en disco."""
        if not self._multi_sheet_writer:
            raise ValueError("No hay libro multi-hoja iniciado")
        self._multi_sheet_writer.save()
        self._multi_sheet_writer.close()
        path = Path(file_path)
        with open(path, "wb") as f:
            f.write(self._multi_sheet_buffer.getvalue())
        print(f"Archivo multi-hoja guardado en: {path.resolve()}")
        self._multi_sheet_writer = None
        self._multi_sheet_buffer = None
    # -------------------------------------------------------------

    # Export individual tables (normal behavior)
    def export_accounts(self, file_format: str = "xlsx") -> bytes:
        df = self._to_accounts_table()
        buffer = BytesIO()
        if file_format == "xlsx":
            with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
                df.to_excel(writer, index=False, sheet_name="Cuentas")
        elif file_format == "csv":
            df.to_csv(buffer, index=False, encoding="utf-8")
        else:
            raise ValueError("Formato no soportado")
        return buffer.getvalue()

    def export_transactions(self, file_format: str = "xlsx") -> bytes:
        df = self._to_ledger_table()
        buffer = BytesIO()
        if file_format == "xlsx":
            with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
                df.to_excel(writer, index=False, sheet_name="Libro Diario")
        elif file_format == "csv":
            df.to_csv(buffer, index=False, encoding="utf-8")
        else:
            raise ValueError("Formato no soportado")
        return buffer.getvalue()

    def save_file(self, file_path: str, file_format: str = "xlsx"):
        file_bytes = self.export_transactions(file_format)
        path = Path(file_path)
        with open(path, "wb") as f:
            f.write(file_bytes)
        print(f"Archivo guardado en: {path.resolve()}")
