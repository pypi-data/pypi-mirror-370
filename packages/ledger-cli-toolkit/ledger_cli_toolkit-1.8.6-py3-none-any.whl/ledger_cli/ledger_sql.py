from pathlib import Path


class LedgerSQL:
    """
    Clase para exportar transacciones y cuentas contables a SQL.
    Genera sentencias para:
      - SQL estándar
      - MySQL
      - PostgreSQL
    """

    def __init__(self, transactions: list[dict], accounts: list[dict] = None):
        self.transactions = transactions or []
        self.accounts = accounts or []

    def _escape_str(self, value: str, engine: str = "standard") -> str:
        """Escapa cadenas según el motor SQL"""
        if value is None:
            return "NULL"
        value = str(value).replace("'", "''")  # escape genérico
        return f"'{value}'"

    def _insert_accounts(self, engine: str = "standard") -> list[str]:
        lines = []

        # Cabecera de tabla
        if engine == "mysql":
            lines.append(
                "CREATE TABLE IF NOT EXISTS accounts (id INT AUTO_INCREMENT PRIMARY KEY, account VARCHAR(255), description TEXT, alias VARCHAR(100), type VARCHAR(50));"
            )
        else:
            lines.append(
                "CREATE TABLE IF NOT EXISTS accounts (id SERIAL PRIMARY KEY, account TEXT, description TEXT, alias TEXT, type TEXT);"
            )

        # Inserts
        for idx, acc in enumerate(self.accounts, start=1):
            if isinstance(acc, dict):
                account = self._escape_str(acc.get("account", ""), engine)
                description = self._escape_str(acc.get("description", ""), engine)
                alias = self._escape_str(acc.get("alias", ""), engine)
                type_ = self._escape_str(acc.get("type", ""), engine)
                lines.append(
                    f"INSERT INTO accounts (account, description, alias, type) VALUES ({account}, {description}, {alias}, {type_});"
                )
            elif isinstance(acc, str):
                account = self._escape_str(acc, engine)
                lines.append(f"INSERT INTO accounts (account) VALUES ({account});")
        return lines

    def _insert_transactions(self, engine: str = "standard") -> list[str]:
        lines = []

        # Cabecera de tabla transacciones y detalles
        if engine == "mysql":
            lines.append(
                "CREATE TABLE IF NOT EXISTS transactions (id INT AUTO_INCREMENT PRIMARY KEY, date DATE, verified BOOLEAN, description TEXT);"
            )
            lines.append(
                "CREATE TABLE IF NOT EXISTS transaction_lines (id INT AUTO_INCREMENT PRIMARY KEY, transaction_id INT, account VARCHAR(255), unit VARCHAR(10), amount DECIMAL(20,2), FOREIGN KEY(transaction_id) REFERENCES transactions(id));"
            )
        else:  # PostgreSQL o estándar
            lines.append(
                "CREATE TABLE IF NOT EXISTS transactions (id SERIAL PRIMARY KEY, date DATE, verified BOOLEAN, description TEXT);"
            )
            lines.append(
                "CREATE TABLE IF NOT EXISTS transaction_lines (id SERIAL PRIMARY KEY, transaction_id INT REFERENCES transactions(id), account TEXT, unit TEXT, amount NUMERIC(20,2));"
            )

        # Inserts
        for idx, tx in enumerate(self.transactions, start=1):
            date = self._escape_str(tx.get("date", ""), engine)
            verified = "TRUE" if tx.get("verified", False) else "FALSE"
            desc = self._escape_str(tx.get("description", ""), engine)
            lines.append(
                f"INSERT INTO transactions (id, date, verified, description) VALUES ({idx}, {date}, {verified}, {desc});"
            )

            for acc in tx.get("accounts", []):
                account = self._escape_str(acc.get("account", ""), engine)
                unit = self._escape_str(acc.get("unit", "$"), engine)
                amount = acc.get("amount", 0.0)
                lines.append(
                    f"INSERT INTO transaction_lines (transaction_id, account, unit, amount) VALUES ({idx}, {account}, {unit}, {amount});"
                )

        return lines

    def export_sql(self, engine: str = "standard") -> str:
        """
        Genera el SQL completo como texto.
        engine: 'standard', 'mysql', 'postgresql'
        """
        sql_lines = []
        sql_lines += self._insert_accounts(engine)
        sql_lines += [""]  # línea en blanco
        sql_lines += self._insert_transactions(engine)
        return "\n".join(sql_lines)

    def save_file(self, file_path: str, engine: str = "standard"):
        """Guarda el SQL en disco"""
        sql_text = self.export_sql(engine)
        path = Path(file_path)
        with open(path, "w", encoding="utf-8") as f:
            f.write(sql_text)
        print(f"Archivo SQL guardado en: {path.resolve()}")
