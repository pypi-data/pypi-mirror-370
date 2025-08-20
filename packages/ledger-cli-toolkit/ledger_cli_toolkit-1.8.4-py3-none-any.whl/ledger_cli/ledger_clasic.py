from pathlib import Path


class LedgerLedger:
    def __init__(self, transactions: list[dict], accounts: list[dict] = None):
        self.transactions = transactions or []
        self.accounts = accounts or []

    @staticmethod
    def _format_account_line(account: dict, col_width: int = 40) -> str:
        acc_name = account["account"]
        unit = account.get("unit", "$")
        amount = account.get("amount", 0.0)
        if unit == "$":
            amount_str = f"{unit}{amount:,.2f}"
        elif unit == "N/A":
            amount_str = f"${amount:,.2f}"
        else:
            amount_str = f"{unit} {amount:,.2f}"
        return f"    {acc_name.ljust(col_width)} {amount_str}"

    @staticmethod
    def _format_properties_comment(properties) -> list[str]:
        lines = []
        if isinstance(properties, dict):
            for k, v in properties.items():
                lines.append(f"; {k}: {v}")
        elif isinstance(properties, list):
            for item in properties:
                lines.append(f"; {item}")
        else:
            lines.append(f"; {properties}")
        return lines

    def _build_accounts_text(self) -> str:
        """
        Construye la sección de cuentas contables.
        Maneja accounts como lista de dicts o lista de strings.
        """
        lines = []

        for acc in self.accounts:
            if isinstance(acc, dict):
                # Comentarios de propiedades adicionales
                for prop_line in self._format_properties_comment(
                    {
                        k: v
                        for k, v in acc.items()
                        if k
                        not in ["account", "amount", "unit", "subAccounts", "taxes"]
                    }
                ):
                    lines.append(prop_line)
                # Nombre de cuenta
                lines.append(f"account {acc['account']}")
            elif isinstance(acc, str):
                # Solo nombre de cuenta
                lines.append(f"account {acc}")
            else:
                # Otro tipo, convertir a string
                lines.append(f"; {acc}")

        return "\n".join(lines)

    def build_ledger_text(self) -> str:
        lines = []
        for tx in self.transactions:
            for prop_line in self._format_properties_comment(tx.get("properties", {})):
                lines.append(prop_line)
            date = tx.get("date", "")
            time = tx.get("time")
            verified_mark = "*" if tx.get("verified", False) else ""
            desc = tx.get("description", "")
            if time:
                lines.append(f"{date} {time} {verified_mark} {desc}")
            else:
                lines.append(f"{date} {verified_mark} {desc}")
            for acc in tx.get("accounts", []):
                for prop_line in self._format_properties_comment(
                    {
                        k: v
                        for k, v in acc.items()
                        if k
                        not in ["account", "amount", "unit", "subAccounts", "taxes"]
                    }
                ):
                    lines.append(prop_line)
                lines.append(self._format_account_line(acc))
            lines.append("")
        return "\n".join(lines)

    def save_file(self, file_path: str, multi_file: bool = False):
        path = Path(file_path)
        if multi_file:
            # Guardar transacciones
            text_tx = self.build_ledger_text()
            with open(path, "w", encoding="utf-8") as f:
                f.write(text_tx)
            print(f"Archivo de transacciones guardado en: {path.resolve()}")

            # Guardar cuentas en archivo separado
            accounts_path = path.with_name(f"{path.stem}_accounts{path.suffix}")
            text_acc = self._build_accounts_text()
            with open(accounts_path, "w", encoding="utf-8") as f:
                f.write(text_acc)
            print(
                f"Archivo de cuentas contables guardado en: {accounts_path.resolve()}"
            )

        else:
            # Guardar todo en un solo archivo
            text = "; Accounts\n"
            text += self._build_accounts_text() + "\n\n"
            text += "; Transactions\n"
            text += self.build_ledger_text()
            with open(path, "w", encoding="utf-8") as f:
                f.write(text)
            print(f"Archivo combinado guardado en: {path.resolve()}")
