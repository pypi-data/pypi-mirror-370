import re
import json
from typing import List, Dict, Union
from datetime import datetime
from typing import List, Dict, Union, Any, TextIO
from datetime import datetime
import yaml
import copy


keywords = {
    "Assets": [
        # Español
        "activo",
        "activos",
        "act",
        "activ",
        "caja",
        "banco",
        "banc",
        "cuentas por cobrar",
        "inventario",
        "inv",
        "efectivo",
        # Inglés
        "asset",
        "assets",
        "ass",
        "cash",
        "bank",
        "inventory",
        "inv",
        "a/r",
        "ar",
        "accounts receivable",
        # Francés
        "actif",
        "actifs",
        "act",
        "banque",
        "encaisse",
        "inventaire",
        "créances",
        # Portugués
        "ativo",
        "ativos",
        "ati",
        "caixa",
        "banco",
        "contas a receber",
        "inventário",
        # Alemán
        "vermögen",
        "verm",
        "anlagen",
        "kasse",
        "bank",
        "forderungen",
        # Otros
        "recursos",
        "propiedades",
        "prop",
        "recur",
    ],
    "Liabilities": [
        # Español
        "pasivo",
        "pasivos",
        "pas",
        "pasiv",
        "deuda",
        "deudas",
        "prestamo",
        "prestamos",
        "obligaciones",
        "cuentas por pagar",
        # Inglés
        "liability",
        "liabilities",
        "liab",
        "liabs",
        "loan",
        "loans",
        "debts",
        "a/p",
        "ap",
        "accounts payable",
        "obligations",
        # Francés
        "passif",
        "dettes",
        "obligations",
        "emprunts",
        "pass",
        # Portugués
        "passivo",
        "passivos",
        "pass",
        "obrigações",
        "contas a pagar",
        "empréstimos",
        # Alemán
        "schuld",
        "schulden",
        "verbindlichkeiten",
        "verpflichtungen",
        "verb",
        "sch",
        # Otros
        "oblig",
        "creditos",
        "cred",
        "deuda",
    ],
    "Equity": [
        # Español
        "capital",
        "cap",
        "capital social",
        "patrimonio",
        "pat",
        "fondos propios",
        "utilidades retenidas",
        "aporte",
        "inv",
        "inversiones",
        # Inglés
        "equity",
        "eq",
        "owner's equity",
        "shareholder equity",
        "capital",
        "net worth",
        "retained earnings",
        "re",
        # Francés
        "capitaux propres",
        "fonds propres",
        "capital social",
        "cap soc",
        "capitaux",
        # Portugués
        "patrimônio líquido",
        "capital próprio",
        "lucros acumulados",
        "pl",
        "cp",
        # Alemán
        "eigenkapital",
        "reinvermögen",
        "kapital",
        "ek",
        # Otros
        "aport",
        "equ",
        "fondos",
        "fp",
    ],
    "Income": [
        # Español
        "ingreso",
        "ingresos",
        "ing",
        "venta",
        "ventas",
        "ven",
        "ganancia",
        "utilidad",
        "entrada",
        "entradas",
        "ing op",
        # Inglés
        "income",
        "inc",
        "revenue",
        "rev",
        "sales",
        "sale",
        "earnings",
        "ear",
        "profits",
        "profit",
        "turnover",
        # Francés
        "revenu",
        "rev",
        "ventes",
        "vente",
        "bénéfices",
        "benef",
        "chiffre d'affaires",
        # Portugués
        "receita",
        "rec",
        "rendimento",
        "rend",
        "vendas",
        "ganhos",
        # Alemán
        "einnahmen",
        "ein",
        "umsatz",
        "um",
        "erträge",
        "gewinne",
        "gew",
        # Otros
        "entr",
        "ingres",
        "ventas netas",
        "net sales",
    ],
    "Expenses": [
        # Español
        "gasto",
        "gastos",
        "gast",
        "egreso",
        "egresos",
        "costos",
        "cost",
        "compra",
        "compras",
        "salida",
        "salidas",
        # Inglés
        "expense",
        "expenses",
        "exp",
        "cost",
        "costs",
        "purchase",
        "purchases",
        "spending",
        "spend",
        "expenditure",
        "outflows",
        "out",
        # Francés
        "dépense",
        "dépenses",
        "dep",
        "coût",
        "coûts",
        "achats",
        "sorties",
        # Portugués
        "despesa",
        "despesas",
        "desp",
        "custos",
        "compras",
        "saida",
        "saídas",
        # Alemán
        "ausgaben",
        "aus",
        "kosten",
        "aufwand",
        "aufw",
        # Otros
        "eg",
        "consumo",
        "pagos",
        "sal",
    ],
}


class LedgerParser:
    def __init__(
        self,
        file: Union[str, TextIO],
        file_accounts: str = None,
        parents_accounts=None,
    ):
        self.file_path = file
        self.file_accounts_path = file_accounts
        self.keywords = keywords  # Asegúrate que esta variable esté definida o pasada
        self.parents_accounts = (
            {
                "Assets": "Assets",
                "Liabilities": "Liabilities",
                "Equity": "Equity",
                "Income": "Income",
                "Expenses": "Expenses",
            }
            if parents_accounts is None
            else parents_accounts
        )

    def __str__(self):
        return f"LedgerParser(file_path='{self.file_path}')"

    def parse(self) -> List[Dict[str, Union[str, List[Dict[str, Union[str, float]]]]]]:
        """
        Parses the ledger file to extract a list of transactions.
        """
        transactions = []
        last_amount = None
        last_unit = None

        with open(self.file_path, "r", encoding="utf-8") as file:
            lines = file.readlines()

        current_transaction = None

    # ----------------------------------------------------------------------------------------------
    #                              Funciones procesamiento general
    # ----------------------------------------------------------------------------------------------

    def parser(self):
        """
        Ejemplo de uso:
        parser = LedgerParser("test.ledger")
        transactions_json = parser.parse_transactions()
        print(parser.get_registers_between_dates("2025/01/02", "2025/01/04"))
        print(parser.get_registers_by_month(2025, 1))
        balances = parser.calculate_balances(transactions_json)
        print(json.dumps(balances, indent=4, ensure_ascii=False))
        specific_balance = parser.calculate_balance_for_account(transactions_json, "Assets")
        print(json.dumps(specific_balance, indent=4, ensure_ascii=False))
        """

        transactions = self.parse_transactions()
        accounts = self.parse_accounts()
        accounts_details = self.parse_accounts_with_details()
        parent_accounts = self.detected_parents_accounts()
        metada = self.parse_metadata_yaml()
        map_doc = self.parse_doc()
        resolved_transactions = self.resolve(
            transactions,
            {
                "IVA": {"percentage": 0.16, "account": "Taxes:IVA"},
                "RET_ISR": {"percentage": 0.10, "account": "Taxes:RET_ISR"},
            },
        )
        ordered_transactions = self.sort_transactions(transactions)

        return {
            "transactions": transactions,
            "ordered_transactions": ordered_transactions,
            "parent_accounts": parent_accounts,
            "accounts": accounts,
            "accounts_details": accounts_details,
            "metada": metada,
            "map_doc": map_doc,
            "resolved_transactions": resolved_transactions,
        }

    # ----------------------------------------------------------------------------------------------
    #                                      Funciones auxiliares
    # ----------------------------------------------------------------------------------------------

    def __str__(self):
        return f"LedgerParser(file_path='{self.file_path}')"

    def _get_content(self, file: Union[str, TextIO] = None) -> str:
        """Retorna el contenido del archivo Ledger desde múltiples formas posibles."""

        # Adapta en caso de recibir un archivo como parametro
        current_file = None
        if file is None:
            current_file = self.file_path
        else:
            current_file = file

        # Si es un archivo abierto
        if hasattr(current_file, "read"):
            return current_file.read()

        # Si es un string pero contiene saltos de línea, asumimos que es el contenido
        if isinstance(current_file, str) and "\n" in current_file:
            return current_file

        # Si es una ruta a archivo
        try:
            with open(current_file, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            raise ValueError(f"No se pudo obtener el contenido del archivo: {e}")

    # ----------------------------------------------------------------------------------------------
    #                              Funciones de extraccion de datos
    # ----------------------------------------------------------------------------------------------

    def _is_comment_or_empty(self, line: str) -> bool:
        """Verifica si la linea es un comentario o vacía."""
        return not line or line.startswith(";")

    def _is_transaction_header(self, line: str) -> bool:
        """Verifica si la linea es un encabezado de transacción."""
        return bool(re.match(r"^\d{4}[-/]\d{2}[-/]\d{2}", line))

    def _parse_transaction_header(
        self, line: str
    ) -> Dict[str, Union[str, bool, None, list]]:
        date_match = re.match(
            r"^(\d{4}[-/]\d{2}[-/]\d{2})(?: (\d{2}:\d{2}:\d{2}))?( \*?)?(.*)$", line
        )
        date, time, verified, description = date_match.groups()
        return {
            "date": date,
            "time": time if time else None,
            "verified": bool(verified and verified.strip() == "*"),
            "description": description.strip(),
            "accounts": [],
            "properties": [],
        }

    def _extract_property_line(self, line: str) -> Union[Dict[str, str], None]:
        """
        Detecta líneas con propiedades de la transacción y las extrae.
        Formato: -key: value
        """
        if not line.startswith("-"):
            return None

        match = re.match(r"^-([a-zA-Z0-9_-]+):\s*(.+)$", line)
        if not match:
            return None

        key = match.group(1).strip()
        value = match.group(2).strip()
        return {"key": key, "value": value}

    def _extract_taxes(self, line: str) -> (str, List[Dict[str, str]]):
        """
        Extrae la expresión de impuestos del final de la línea y retorna la línea limpia y los impuestos.
        """
        taxes = []
        tax_match = re.search(r"([+\-=])\{([A-Za-z0-9_, ]+)\}$", line)
        if tax_match:
            modifier = tax_match.group(1)
            names = [name.strip() for name in tax_match.group(2).split(",")]
            taxes = [{"name": name, "mode": modifier} for name in names]
            line = line[: tax_match.start()].rstrip()  # Elimina la parte del impuesto
        return line, taxes

    def _parse_account_line(
        self, line: str, last_amount: float, last_unit: str
    ) -> (Union[dict, None], float, str):
        # Extraer impuestos si existen
        line, taxes = self._extract_taxes(line)

        # Primero verifica si es solo una cuenta (sin monto)
        if not re.search(r"[\d\$\-\+,]", line):  # Si no hay números, $, -, +, o comas
            account_name = line.strip()
            if ":" in account_name or any(
                keyword in account_name.lower()
                for keyword in ["assets", "liabilities", "equity", "income", "expenses"]
            ):
                return (
                    {
                        "account": account_name,
                        "subAccounts": [s.strip() for s in account_name.split(":")],
                        "unit": last_unit if last_unit else "N/A",
                        "amount": -last_amount if last_amount else 0.0,
                        "taxes": taxes,
                    },
                    last_amount,
                    last_unit,
                )

        # Patrones regex MEJORADOS para manejar múltiples espacios
        patterns = [
            # Patrón 1: Cuenta + unidad separada + cantidad (ej: "Account USD 100.00")
            r"^(?P<account>[A-Za-z0-9:_\s]+?)\s{2,}(?P<unit>[A-Z]{2,3}|\$)\s+(?P<amount>-?\$?[\d,]+(?:\.\d+)?)$",
            # Patrón 2: Cuenta + cantidad + unidad separada (ej: "Account 100.00 USD")
            r"^(?P<account>[A-Za-z0-9:_\s]+?)\s{2,}(?P<amount>-?\$?[\d,]+(?:\.\d+)?)\s+(?P<unit>[A-Z]{2,3}|\$)$",
            # Patrón 3: Cuenta + cantidad con símbolo $ pegado (ej: "Account $-100.00")
            r"^(?P<account>[A-Za-z0-9:_\s]+?)\s{2,}(?P<amount_unit>-?\$[\d,]+(?:\.\d+)?)$",
            # Patrón 4: Cuenta + cantidad con símbolo $ pegado (ej: "Account -$100.00")
            r"^(?P<account>[A-Za-z0-9:_\s]+?)\s{2,}(?P<amount_unit>\$-?[\d,]+(?:\.\d+)?)$",
            # Patrón 5: Cuenta + cantidad sin unidad (ej: "Account 100.00")
            r"^(?P<account>[A-Za-z0-9:_\s]+?)\s{2,}(?P<amount>-?[\d,]+(?:\.\d+)?)$",
            # Patrón 6: Cuenta + unidad + cantidad (menos espacios)
            r"^(?P<account>[A-Za-z0-9:_\s]+)\s+(?P<unit>[A-Z]{2,3}|\$)\s+(?P<amount>-?\$?[\d,]+(?:\.\d+)?)$",
            # Patrón 7: Cuenta + cantidad con $ (menos espacios)
            r"^(?P<account>[A-Za-z0-9:_\s]+)\s+(?P<amount_unit>-?\$[\d,]+(?:\.\d+)?)$",
            # Patrón 8: Solo cuenta (usa último monto)
            r"^(?P<account>[A-Za-z0-9:_\s]+)$",
        ]

        for pattern in patterns:
            match = re.match(pattern, line, re.IGNORECASE)
            if match:
                account_name = match.group("account").strip()
                amount = None
                unit = last_unit or "N/A"

                # Procesar según el patrón que coincidió
                if "amount_unit" in match.groupdict() and match.group("amount_unit"):
                    # Patrón 3 o 4: cantidad con $ pegado
                    amount_str = match.group("amount_unit")
                    unit = "$"
                    # Extraer solo la parte numérica
                    amount_str = re.sub(r"[^\d\-\.]", "", amount_str)

                elif "amount" in match.groupdict() and match.group("amount"):
                    # Patrones 1, 2, 5: cantidad separada
                    amount_str = match.group("amount")
                    if "unit" in match.groupdict() and match.group("unit"):
                        unit = match.group("unit")

                else:
                    # Patrón 8: solo cuenta
                    amount_str = None

                # Procesar el monto
                if amount_str:
                    # Limpiar el string del monto
                    amount_str = amount_str.replace("$", "").replace(",", "")
                    try:
                        amount = float(amount_str)
                    except ValueError:
                        amount = -last_amount if last_amount else 0.0
                else:
                    amount = -last_amount if last_amount else 0.0

                # Si la unidad es "$", asegurarse de que esté en formato consistente
                if unit == "$":
                    unit = "$"  # Mantener como símbolo de dólar

                return (
                    {
                        "account": account_name,
                        "subAccounts": [s.strip() for s in account_name.split(":")],
                        "unit": unit,
                        "amount": amount,
                        "taxes": taxes,
                    },
                    amount,
                    unit,
                )

        # Si ningún patrón coincide, tratar como cuenta sin monto
        return (
            {
                "account": line.strip(),
                "subAccounts": [line.strip()],
                "unit": last_unit or "N/A",
                "amount": -last_amount if last_amount else 0.0,
                "taxes": taxes,
            },
            last_amount,
            last_unit,
        )

    def parse_transactions(
        self,
    ) -> List[Dict[str, Union[str, List[Dict[str, Union[str, float]]]]]]:
        """Función para parsear el contenido del archivo Ledger y extraer las transacciones."""

        transactions = []
        content = self._get_content()
        lines = content.splitlines()

        current_transaction = None
        last_amount = None
        last_unit = None

        for line in lines:
            line = line.strip()

            if self._is_comment_or_empty(line):
                # Save the current transaction and reset on comments/empty lines
                if current_transaction:
                    transactions.append(current_transaction)
                    current_transaction = None
                continue

            if self._is_transaction_header(line):
                # Save previous transaction if exists
                if current_transaction:
                    transactions.append(current_transaction)
                current_transaction = self._parse_transaction_header(line)
                current_transaction["properties"] = []
                continue

            if current_transaction:
                prop = self._extract_property_line(line)
                if prop:
                    current_transaction["properties"].append(prop)
                    continue

                # Usa tu método auxiliar existente _parse_account_line
                account_entry, last_amount, last_unit = self._parse_account_line(
                    line, last_amount, last_unit
                )
                if account_entry:
                    current_transaction["accounts"].append(account_entry)

        # Add the last transaction if any
        if current_transaction:
            transactions.append(current_transaction)

        return transactions

    def parse_doc(self) -> List[Dict[str, Union[int, List[int], str, List[str]]]]:
        """
        Retorna un mapa del documento agrupando:
          - Transacciones completas
          - Comentarios multilinea
          - Bloques de metadatos
          - Títulos estilo markdown (# y ##)
          - Líneas individuales restantes
        """
        content = self._get_content()
        lines = content.splitlines()
        result = []

        inside_transaction = False
        inside_comment_block = False
        inside_metadata_block = False

        current_block = None

        def close_block():
            nonlocal current_block
            if current_block:
                result.append(current_block)
                current_block = None

        for idx, raw_line in enumerate(lines):
            line = raw_line.strip()

            # --- Detectar metadatos ---
            if line == "---":
                if not inside_metadata_block:
                    # Abrimos bloque de metadatos
                    close_block()
                    inside_metadata_block = True
                    current_block = {
                        "type": "metadata",
                        "index": [idx],
                        "lines": [raw_line],
                    }
                else:
                    # Cerramos bloque de metadatos
                    current_block["index"].append(idx)
                    current_block["lines"].append(raw_line)
                    inside_metadata_block = False
                    close_block()
                continue

            if inside_metadata_block:
                current_block["index"].append(idx)
                current_block["lines"].append(raw_line)
                continue

            # --- Detectar transacciones ---
            if self._is_transaction_header(line):
                close_block()
                inside_transaction = True
                current_block = {
                    "type": "transaction",
                    "index": [idx],
                    "lines": [raw_line],
                }
                continue

            if inside_transaction:
                if not line:  # línea vacía → fin de transacción
                    inside_transaction = False
                    close_block()
                else:
                    current_block["index"].append(idx)
                    current_block["lines"].append(raw_line)
                continue

            # --- Detectar comentarios multilinea ---
            if line.startswith(";"):
                if not inside_comment_block:
                    close_block()
                    inside_comment_block = True
                    current_block = {
                        "type": "comment",
                        "index": [idx],
                        "lines": [raw_line],
                    }
                else:
                    current_block["index"].append(idx)
                    current_block["lines"].append(raw_line)
                continue
            else:
                if inside_comment_block:
                    inside_comment_block = False
                    close_block()

            # --- Detectar títulos estilo markdown ---
            if line.startswith("####"):
                close_block()
                result.append({"type": "title4", "index": idx, "line": raw_line})
                continue
            elif line.startswith("###"):
                close_block()
                result.append({"type": "title3", "index": idx, "line": raw_line})
                continue
            elif line.startswith("##"):
                close_block()
                result.append({"type": "title2", "index": idx, "line": raw_line})
                continue
            elif line.startswith("#"):
                close_block()
                result.append({"type": "title1", "index": idx, "line": raw_line})
                continue

            # --- Si no es ninguno de los anteriores, es una línea normal ---
            close_block()
            result.append({"type": "line", "index": idx, "line": raw_line})

        # Cerrar bloque abierto al final
        close_block()

        return result

    def parse_accounts(self) -> List[str]:
        """
        Parses the file to extract a list of accounting accounts.
        """
        accounts = []
        content = self._get_content(self.file_accounts_path)
        lines = content.splitlines()

        for line in lines:
            line = line.strip()
            account_match = re.match(r"^account\s+([A-Za-z0-9:]+)$", line)
            if account_match:
                account_name = account_match.group(1)
                account_name = account_name.replace(" ", "")
                accounts.append(account_name)

        return accounts

    def parse_accounts_advance(self) -> List[Dict[str, str]]:
        """
        Parses the file to extract a list of accounting accounts with additional metadata.
        Example input:
        account Activos:Banco
          description "Cuenta bancaria principal para operaciones diarias"
          category "Activo Corriente"
          type "Activo"
          currency "MXN"
          created "2023-01-15"
          notes "Cuenta para depósitos y pagos automáticos"

        Returns a list of dicts like:
        [
            {
                "account": "Activos:Banco",
                "description": "Cuenta bancaria principal para operaciones diarias",
                "category": "Activo Corriente",
                "type": "Activo",
                "currency": "MXN",
                "created": "2023-01-15",
                "notes": "Cuenta para depósitos y pagos automáticos"
            },
            ...
        ]
        Soporta:
          - key "valor con comillas"
          - key valor
          - key: valor
        """
        accounts = []
        current_account = None
        current_data = {}
        content = self._get_content(self.file_accounts_path)
        lines = content.splitlines()

        for line in lines:
            line = line.strip()
            # Detecta inicio de nueva cuenta
            account_match = re.match(r"^account\s+([A-Za-z0-9:]+)$", line)
            if account_match:
                # Si ya había una cuenta anterior, la guarda
                if current_account is not None:
                    accounts.append(current_data)

                # Nueva cuenta
                current_account = account_match.group(1).replace(" ", "")
                current_data = {"account": current_account}
                continue

            # Si está dentro de una cuenta, parsea pares clave-valor
            if current_account is not None and line:
                key_value_match = None

                # Caso: key "valor"
                key_value_match = re.match(r'^([a-zA-Z0-9_]+)\s+"(.+)"$', line)
                if key_value_match:
                    key = key_value_match.group(1).lower()
                    value = key_value_match.group(2)
                    current_data[key] = value
                    continue

                # Caso: key valor
                key_value_match = re.match(r"^([a-zA-Z0-9_]+)\s+(.+)$", line)
                if key_value_match:
                    key = key_value_match.group(1).lower()
                    value = key_value_match.group(2)
                    current_data[key] = value
                    continue

                # Caso: key: valor
                key_value_match = re.match(r"^([a-zA-Z0-9_]+):\s+(.+)$", line)
                if key_value_match:
                    key = key_value_match.group(1).lower()
                    value = key_value_match.group(2)
                    current_data[key] = value
                    continue

        # Añade la última cuenta si existe
        if current_account is not None:
            accounts.append(current_data)

        return accounts

    def parse_metadata_yaml(self):
        """
        Extrae y parsea metadatos YAML desde el inicio del archivo Ledger, delimitados por '---'.

        Args:
            filepath (str): Ruta al archivo Ledger.

        Returns:
            dict: Diccionario con los metadatos YAML extraídos, o un diccionario vacío si no se encuentra o hay error.
        """
        try:
            content = self._get_content()

            # Buscar el bloque YAML al principio del archivo
            match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
            if match:
                yaml_content = match.group(1)
                metadata = yaml.safe_load(yaml_content)
                return metadata if isinstance(metadata, dict) else {}
            else:
                return {}

        except Exception as e:
            print(f"Error al parsear metadatos YAML: {e}")
            return {}

    def detected_parents_accounts(self):
        accounts = self.parse_accounts()

        # Valores por defecto si no hay cuentas
        if not accounts:
            default_parents = {
                "Assets": "Assets",
                "Liabilities": "Liabilities",
                "Equity": "Equity",
                "Income": "Income",
                "Expenses": "Expenses",
            }
            self.parents_accounts = default_parents
            return default_parents

        # Extraer cuentas padres únicas
        parents_set = set()
        for account in accounts:
            parent = account.split(":")[0]
            parents_set.add(parent)

        parents_list = list(parents_set)

        # Diccionario de categorías con sus posibles keywords en múltiples idiomas
        keywords = self.keywords

        def normalize(text):
            return text.strip().lower()

        detected = {}
        used = set()

        for category, words in keywords.items():
            detected[category] = None
            for parent in parents_list:
                p_norm = normalize(parent)
                if any(word == p_norm for word in words):
                    detected[category] = parent
                    used.add(parent)
                    break

        # Rellenar categorías faltantes con padres no usados
        remaining = [p for p in parents_list if p not in used]
        for category in detected:
            if detected[category] is None:
                detected[category] = (
                    remaining.pop(0) if remaining else f"Unknown-{category}"
                )

        self.parents_accounts = detected
        return detected

    def details_account(self, account: str):
        sub_accounts = account.split(":")
        return {"parent": sub_accounts[0], "sub_accounts": sub_accounts[1:]}

    def parse_accounts_with_details(self):
        accounts = self.parse_accounts()
        return [
            {"account": account, "details": self.details_account(account)}
            for account in accounts
        ]

    def transactions_to_json(self) -> str:
        transactions = self.parse()
        return json.dumps(transactions, indent=4, ensure_ascii=False)

    def to_json(
        self, data: List[Dict[str, Union[str, List[Dict[str, Union[str, float]]]]]]
    ) -> str:
        return json.dumps(data, indent=4, ensure_ascii=False)

    def accounts_to_json(self) -> str:
        transactions = self.parse_accounts_with_details()
        return json.dumps(transactions, indent=4, ensure_ascii=False)

    # ----------------------------------------------------------------------------------------------
    #                              Funciones de resolucion
    # ----------------------------------------------------------------------------------------------

    def resolve(
        self,
        transactions: list,
        tax_definitions: dict,
        fallback_counterpart: str = None,
    ) -> list:
        """
        Resuelve operaciones dentro de las transacciones, como el cálculo de impuestos.

        :param transactions: Lista de transacciones a resolver.
        :param tax_definitions: Diccionario de impuestos con forma:
            {
                "IVA": {
                    "percentage": 0.16,
                    "account": "Taxes:IVA"
                },
                ...
            }
        :param fallback_counterpart: Cuenta a usar como contrapartida si no se detecta automáticamente.
        :return: Lista de transacciones con impuestos resueltos.
        """
        transactions = copy.deepcopy(transactions)
        resolved = []

        for transaction in transactions:
            resolved_transaction = self._resolve_transaction(
                transaction, tax_definitions, fallback_counterpart
            )
            resolved.append(resolved_transaction)

        return resolved

    def _resolve_transaction(
        self, transaction: dict, tax_definitions: dict, fallback_counterpart: str = None
    ) -> dict:
        """
        Aplica la resolución de impuestos a una transacción completa.
        """
        transaction["accounts"] = self._resolve_accounts_taxes(
            transaction["accounts"], tax_definitions, fallback_counterpart
        )
        return transaction

    def _build_tax_account_name(self, tax_definitions: dict, name: str) -> str:
        """
        Construye el nombre de la cuenta de impuesto a partir de la definición de impuestos.
        """
        tax_info = tax_definitions.get(name, {})
        account = tax_info.get(
            "account", self.parents_accounts["Assets"] + ":Taxes:" + name
        )
        if not account:
            raise ValueError(f"No se ha definido la cuenta de impuesto para {name}")
        return account

    def _resolve_accounts_taxes(
        self, accounts: list, tax_definitions: dict, fallback_counterpart: str = None
    ) -> list:
        """
        Recorre todas las cuentas, aplica impuestos y ajusta la cuenta contrapartida.
        """
        result_accounts = copy.deepcopy(accounts)

        for i, account in enumerate(accounts):
            taxes = account.get("taxes", [])
            if not taxes:
                continue

            base_amount = account["amount"]
            unit = account["unit"]

            for tax in taxes:
                name = tax.get("name")
                mode = tax.get("mode")

                tax_info = tax_definitions.get(name, {})
                percentage = tax_info.get("percentage", 0.0)
                tax_account_name = self._build_tax_account_name(tax_definitions, name)

                # Calcula el monto del impuesto
                tax_amount = round(abs(base_amount) * percentage, 2)

                if tax_amount == 0:
                    continue

                if mode == "=":
                    # El impuesto ya está incluido en el monto original
                    net_amount = round(base_amount / (1 + percentage), 2)
                    tax_amount = round(base_amount - net_amount, 2)

                    result_accounts[i]["amount"] = net_amount

                    # Agrega cuenta para el impuesto
                    result_accounts.append(
                        {
                            "account": tax_account_name,
                            "subAccounts": tax_account_name.split(":"),
                            "unit": unit,
                            "amount": tax_amount,
                            "taxes": [],
                        }
                    )

                elif mode in ("+", "-"):
                    # Buscamos contrapartida
                    counterpart_index = self._find_counterpart_index(
                        result_accounts, i, fallback_counterpart
                    )
                    if counterpart_index is None:
                        continue  # No contrapartida válida encontrada

                    counterpart = result_accounts[counterpart_index]
                    counterpart_sign = 1 if counterpart["amount"] >= 0 else -1
                    counterpart["amount"] += counterpart_sign * tax_amount

                    # Agrega cuenta de impuesto
                    result_accounts.append(
                        {
                            "account": tax_account_name,
                            "subAccounts": tax_account_name.split(":"),
                            "unit": unit,
                            "amount": tax_amount,
                            "taxes": [],
                        }
                    )

        return result_accounts

    def _find_counterpart_index(
        self, accounts: list, current_index: int, fallback_account: str = None
    ) -> int:
        """
        Encuentra el índice de la cuenta contraria en signo a la actual.
        Si no se encuentra, usa la cuenta indicada por fallback_account si existe.
        """
        current_amount = accounts[current_index]["amount"]
        for idx, acct in enumerate(accounts):
            if idx == current_index:
                continue
            if acct["amount"] * current_amount < 0:
                return idx

        # Buscar por nombre de cuenta si fue pasada por parámetro
        if fallback_account:
            for idx, acct in enumerate(accounts):
                if acct["account"] == fallback_account:
                    return idx

        return None

    # ----------------------------------------------------------------------------------------------
    #                              Funciones de filtros
    # ----------------------------------------------------------------------------------------------

    def get_registers_between_dates(self, start_date: str, end_date: str) -> str:
        transactions = self.parse()
        start = datetime.strptime(start_date, "%Y/%m/%d")
        end = datetime.strptime(end_date, "%Y/%m/%d")

        filtered_transactions = [
            transaction
            for transaction in transactions
            if start <= datetime.strptime(transaction["date"], "%Y/%m/%d") <= end
        ]

        return json.dumps(filtered_transactions, indent=4, ensure_ascii=False)

    def get_registers_by_month(self, year: int, month: int) -> str:
        transactions = self.parse()
        filtered_transactions = [
            transaction
            for transaction in transactions
            if datetime.strptime(transaction["date"], "%Y/%m/%d").year == year
            and datetime.strptime(transaction["date"], "%Y/%m/%d").month == month
        ]

        return json.dumps(filtered_transactions, indent=4, ensure_ascii=False)

    def get_date_range(
        self,
        transactions_json: List[
            Dict[str, Union[str, List[Dict[str, Union[str, float]]]]]
        ],
    ):
        # Extraer todas las fechas únicas de las transacciones
        dates = {
            transaction["date"]
            for transaction in transactions_json
            if "date" in transaction
        }

        # Función para convertir las fechas a objetos datetime
        def parse_date(date_str: str):
            # Detectar el formato de fecha y convertirlo a datetime
            if "/" in date_str:
                return datetime.strptime(date_str, "%Y/%m/%d")
            elif "-" in date_str:
                return datetime.strptime(date_str, "%Y-%m-%d")
            else:
                raise ValueError(f"Fecha con formato no soportado: {date_str}")

        # Convertir las fechas a objetos datetime para calcular los límites
        date_objects = [parse_date(date) for date in dates]

        # Determinar la fecha mínima y máxima
        min_date = min(date_objects)
        max_date = max(date_objects)

        # Retornar las fechas en formato string
        return min_date.strftime("%Y/%m/%d"), max_date.strftime("%Y/%m/%d")

    # ----------------------------------------------------------------------------------------------
    #                              Funciones de cálculos
    # ----------------------------------------------------------------------------------------------

    def calculate_balances(
        self,
        transactions_json: List[
            Dict[str, Union[str, List[Dict[str, Union[str, float]]]]]
        ],
        reference: List[str] = None,
    ) -> Dict[str, Dict[str, float]]:
        balances = {}

        for transaction in transactions_json:
            for account in transaction["accounts"]:
                account_name = account["account"]
                unit = account["unit"]
                amount = account["amount"]

                if account_name not in balances:
                    balances[account_name] = {}

                if unit not in balances[account_name]:
                    balances[account_name][unit] = 0.0

                balances[account_name][unit] += amount

        # Si se proporciona la lista de referencia, ordenamos los balances
        if reference:
            # Ordenamos las cuentas basándonos en la lista de referencia
            sorted_balances = {}
            for ref_account in reference:
                if ref_account in balances:
                    sorted_balances[ref_account] = balances.pop(ref_account)

            # Agregamos las cuentas que no están en la lista de referencia al final
            for account_name, balance in balances.items():
                sorted_balances[account_name] = balance

            return sorted_balances

        return balances

    def calculate_balance_for_account(
        self,
        transactions_json: List[
            Dict[str, Union[str, List[Dict[str, Union[str, float]]]]]
        ],
        target_account: str,
    ) -> Dict[str, float]:
        account_balance = {}

        for transaction in transactions_json:
            for account in transaction["accounts"]:
                account_name = account["account"]
                unit = account["unit"]
                amount = account["amount"]

                if account_name.startswith(target_account):
                    if unit not in account_balance:
                        account_balance[unit] = 0.0

                    account_balance[unit] += amount

        return account_balance

    def calculate_balances_by_parents_accounts(
        self,
        transactions_json: List[
            Dict[str, Union[str, List[Dict[str, Union[str, float]]]]]
        ],
    ) -> Dict[str, Dict[str, Dict[str, float]]]:
        assets = {}
        liabilities = {}
        equity = {}
        income = {}
        expenses = {}

        for transaction in transactions_json:
            for account in transaction["accounts"]:
                account_name = account["account"]
                unit = account["unit"]
                amount = account["amount"]

                if account_name.startswith(self.parents_accounts["Assets"]):
                    if unit not in assets:
                        assets[unit] = 0.0
                    assets[unit] += amount
                elif account_name.startswith(self.parents_accounts["Liabilities"]):
                    if unit not in liabilities:
                        liabilities[unit] = 0.0
                    liabilities[unit] += amount
                elif account_name.startswith(self.parents_accounts["Equity"]):
                    if unit not in equity:
                        equity[unit] = 0.0
                    equity[unit] += amount
                elif account_name.startswith(self.parents_accounts["Income"]):
                    if unit not in income:
                        income[unit] = 0.0
                    income[unit] += amount
                elif account_name.startswith(self.parents_accounts["Expenses"]):
                    if unit not in expenses:
                        expenses[unit] = 0.0
                    expenses[unit] += amount

        # Asignamos "N/A" solo si el objeto está vacío
        if not assets:
            assets["N/A"] = 0.0
        if not liabilities:
            liabilities["N/A"] = 0.0
        if not equity:
            equity["N/A"] = 0.0
        if not income:
            income["N/A"] = 0.0
        if not expenses:
            expenses["N/A"] = 0.0

        return {
            "Assets": assets,
            "Liabilities": liabilities,
            "Equity": equity,
            "Income": income,
            "Expenses": expenses,
        }

    def calculate_balances_by_details_accounts(
        self,
        transactions_json: List[
            Dict[str, Union[str, List[Dict[str, Union[str, float]]]]]
        ],
    ) -> Dict[str, Dict[str, Union[Dict[str, float], List[str]]]]:
        # Diccionario para almacenar los saldos
        balances = {}

        for transaction in transactions_json:
            for account in transaction["accounts"]:
                account_name = account["account"]
                amount = account["amount"]
                unit = account["unit"]
                details = self.details_account(account_name)
                parent_account = details["parent"]

                # Inicializar el nivel raíz si no existe
                if parent_account not in balances:
                    balances[parent_account] = {
                        "balances": {},
                        "sub_accounts": {},
                    }

                # Mantén un puntero al nivel actual en la jerarquía
                current_level = balances[parent_account]

                # Recorre cada subcuenta para agregar niveles de profundidad
                for sub_account in details["sub_accounts"]:
                    # Si el subnivel no existe, inicialízalo
                    if sub_account not in current_level["sub_accounts"]:
                        current_level["sub_accounts"][sub_account] = {
                            "balances": {},
                            "sub_accounts": {},
                        }

                    # Mueve el puntero al siguiente nivel
                    current_level = current_level["sub_accounts"][sub_account]

                    # Inicializa el saldo de la unidad si no existe
                    if unit not in current_level["balances"]:
                        current_level["balances"][unit] = 0.0

                    # Agrega el monto a la unidad en este nivel
                    current_level["balances"][unit] += amount

                # También actualiza los saldos del nivel padre
                if unit not in balances[parent_account]["balances"]:
                    balances[parent_account]["balances"][unit] = 0.0

                balances[parent_account]["balances"][unit] += amount

        return balances

    def calculate_status_results(self, balances: Dict[str, Dict[str, float]]):
        # Diccionarios para almacenar los totales por cada moneda
        total_income_by_currency = {}
        total_expenses_by_currency = {}
        utility_by_currency = {}

        income_details = []
        expenses_details = []

        for account, currencies in balances.items():
            for currency, amount in currencies.items():
                if account.startswith(self.parents_accounts["Income"]):
                    amount = abs(amount)
                    # Sumar ingresos por cada moneda
                    if currency not in total_income_by_currency:
                        total_income_by_currency[currency] = 0
                    total_income_by_currency[currency] += amount
                    income_details.append(
                        {account: {"currency": currency, "amount": amount}}
                    )
                elif account.startswith(self.parents_accounts["Expenses"]):
                    amount = -amount
                    # Sumar gastos por cada moneda
                    if currency not in total_expenses_by_currency:
                        total_expenses_by_currency[currency] = 0
                    total_expenses_by_currency[currency] += amount
                    expenses_details.append(
                        {account: {"currency": currency, "amount": amount}}
                    )

        # Calcular utilidad por cada moneda
        for currency in total_income_by_currency:
            income = total_income_by_currency.get(currency, 0)
            expenses = total_expenses_by_currency.get(currency, 0)
            utility_by_currency[currency] = income + expenses
            # Ledger: Income viene como negativo → lo convertimos a positivo
            income_amount = abs(amount)
            # Sumar ingresos por cada moneda
            if currency not in total_income_by_currency:
                total_income_by_currency[currency] = 0
                total_income_by_currency[currency] += income_amount
                income_details.append(
                    {account: {"currency": currency, "amount": income_amount}}
                )
            elif account.startswith(self.parents_accounts["Expenses"]):
                # Ledger: Expenses viene como positivo → lo convertimos a negativo
                expense_amount = -abs(amount)
                # Sumar gastos por cada moneda
                if currency not in total_expenses_by_currency:
                    total_expenses_by_currency[currency] = 0
                total_expenses_by_currency[currency] += expense_amount
                expenses_details.append(
                    {account: {"currency": currency, "amount": expense_amount}}
                )

        # Calcular utilidad por cada moneda presente en ingresos o gastos
        all_currencies = set(total_income_by_currency.keys()).union(
            set(total_expenses_by_currency.keys())
        )

        for currency in all_currencies:
            income = total_income_by_currency.get(currency, 0)
            expenses = total_expenses_by_currency.get(currency, 0)
            utility_by_currency[currency] = income + expenses  # income(+), expenses(-)

        return {
            "total_income_by_currency": total_income_by_currency,
            "total_expenses_by_currency": total_expenses_by_currency,
            "utility_by_currency": utility_by_currency,
            "income_details": income_details,
            "expenses_details": expenses_details,
        }

    from typing import Dict, List, Union

    def calculate_general_balance(
        self,
        balances: Dict[str, Dict[str, float]],
        utility_by_currency: Dict[str, float],
    ) -> Dict[str, Dict[str, Union[Dict[str, float], List[Dict]]]]:
        """
        Calcula el balance general agrupado por tipo de cuenta y moneda.

        Args:
            balances: Diccionario con saldos de cuentas {cuenta: {moneda: cantidad}}
            utility_by_currency: Utilidad por moneda {moneda: cantidad}

        Returns:
            {
                "totals_by_currency": {
                    "Assets": {"USD": X, "MXN": Y},
                    "Liabilities": {...},
                    "Equity": {...}
                },
                "details": [
                    {"account": "Assets:Bank", "currency": "USD", "amount": 1000},
                    ...
                ],
                "validation": {
                    "USD": {"Assets": X, "Liabilities+Equity": Y, "balanced": True/False},
                    ...
                }
            }
        """
        # 1. Inicializar estructuras para resultados
        totals_by_currency = {"Assets": {}, "Liabilities": {}, "Equity": {}}
        details = []

        # 2. Procesar cada cuenta y clasificarla
        for account, currencies in balances.items():
            # Determinar el tipo de cuenta (Assets, Liabilities o Equity)
            account_type = None
            for parent_account, prefix in self.parents_accounts.items():
                if parent_account in ["Income", "Expenses"]:
                    continue  # Saltamos estas cuentas
                if account.startswith(prefix):
                    account_type = parent_account
                    break

            if not account_type:
                continue  # Si no es un tipo que nos interese, saltamos

            # Procesar cada moneda de la cuenta
            for currency, amount in currencies.items():
                # Inicializar moneda si no existe
                if currency not in totals_by_currency[account_type]:
                    totals_by_currency[account_type][currency] = 0.0

                # Sumar al total correspondiente
                totals_by_currency[account_type][currency] += amount

                # Agregar detalle
                details.append(
                    {"account": account, "currency": currency, "amount": amount}
                )

        # 3. Agregar la utilidad al Equity
        for currency, utility in utility_by_currency.items():
            if currency not in totals_by_currency["Equity"]:
                totals_by_currency["Equity"][currency] = 0.0
            totals_by_currency["Equity"][currency] += utility

        # 4. Validar que Assets = Liabilities + Equity para cada moneda
        validation = {}
        all_currencies = set()

        # Recoger todas las monedas presentes
        for account_type in totals_by_currency.values():
            all_currencies.update(account_type.keys())

        for currency in all_currencies:
            assets = totals_by_currency["Assets"].get(currency, 0.0)
            liabilities = totals_by_currency["Liabilities"].get(currency, 0.0)
            equity = totals_by_currency["Equity"].get(currency, 0.0)

            validation[currency] = {
                "Assets": assets,
                "Liabilities": liabilities,
                "Equity": equity,
                "Liabilities+Equity": liabilities + equity,
                "balanced": abs(assets - (liabilities + equity))
                < 0.01,  # Considera floats
            }

        return {
            "totals_by_currency": totals_by_currency,
            "details": details,
            "validation": validation,
        }

    from typing import List, Dict

    def calculate_debit_credit(
        self, transactions: List[Dict]
    ) -> Dict[str, Dict[str, float]]:
        """
        Calcula los totales de Debe y Haber por moneda a partir de transacciones.

        Args:
            transactions: Lista de transacciones en formato Ledger.

        Returns:
            {
                "MXN": {"debit": 100.0, "credit": 116.0},
                "$": {"debit": 100.0, "credit": 116.0},
                ...
            }
        """
        debit_credit_totals = {}

        for transaction in transactions:
            for entry in transaction["accounts"]:
                currency = entry["unit"]
                amount = entry["amount"]

                # Inicializar la moneda si no existe
                if currency not in debit_credit_totals:
                    debit_credit_totals[currency] = {"debit": 0.0, "credit": 0.0}

                # Clasificar en débito o crédito
                if amount > 0:
                    debit_credit_totals[currency]["debit"] += amount
                else:
                    debit_credit_totals[currency]["credit"] += abs(amount)

        return debit_credit_totals

    def _create_transaction(
        self,
        date: str,
        description: str,
        accounts: List[Dict[str, Union[str, float]]],
        verify: bool = False,
    ) -> str:
        transaction = f"{date}{' * ' if verify else ' '}{description}\n"
        for account in accounts:
            account_line = (
                f"    {account['account']}    {account['unit']} {account['amount']:.2f}"
            )
            transaction += account_line + "\n"
        return transaction

    # ----------------------------------------------------------------------------------------------
    #                              Funciones auxiliares
    # ----------------------------------------------------------------------------------------------

    def sort_transactions(
        self, transactions: List[Dict[str, Union[str, bool, list]]]
    ) -> List[Dict]:
        """
        Ordena las transacciones por fecha y hora.
        Si no hay hora, se asume 00:00:00.
        """

        def parse_datetime(tx: Dict) -> datetime:
            date_str = tx.get("date")
            time_str = tx.get("time") or "00:00:00"
            dt_str = f"{date_str} {time_str}"

            # Probar varios formatos
            for fmt in ("%Y-%m-%d %H:%M:%S", "%Y/%m/%d %H:%M:%S"):
                try:
                    return datetime.strptime(dt_str, fmt)
                except ValueError:
                    continue

            raise ValueError(f"Formato de fecha/hora no soportado: {dt_str}")

        return sorted(transactions, key=parse_datetime)

    def remove_duplicates(arr: List[Any]) -> List[Any]:
        """
        Elimina duplicados de un array que puede contener strings, números u objetos.
        Retorna un nuevo array con los elementos únicos, manteniendo el orden original.
        """
        seen = set()
        unique = []

        for item in arr:
            # Para objetos usamos JSON ordenado como representación única
            if isinstance(item, (dict, list)):
                marker = json.dumps(item, sort_keys=True)
            else:
                marker = str(item)

            if marker not in seen:
                seen.add(marker)
                unique.append(item)

        return unique

    # ----------------------------------------------------------------------------------------------
    #                              Funciones de unidad
    # ----------------------------------------------------------------------------------------------

    def unify_currencies(
        self,
        balances: Dict[str, Dict[str, float]],
        exchange_rates: Dict[str, float],
        target_currency: str,
        default_currency: str = "USD",
        base_currency: str = "USD",
    ) -> Dict[str, Dict[str, float]]:
        """
        Unifica todas las monedas a la moneda objetivo especificada.

        Args:
            balances: Diccionario con los balances por cuenta y moneda
            exchange_rates: Tasas de cambio {moneda: tasa} con respecto a la moneda base
            target_currency: Moneda objetivo a la que convertir (ej: "MXN")
            default_currency: Moneda por defecto para cuentas sin currency especificada
            base_currency: Moneda base de referencia para las tasas de cambio

        Returns:
            Diccionario con todos los montos convertidos a la moneda objetivo
        """
        unified_balances = {}

        # Validaciones
        if target_currency not in exchange_rates:
            raise ValueError(f"Tasa de cambio para {target_currency} no proporcionada")

        if base_currency not in exchange_rates:
            raise ValueError(
                f"Tasa de cambio para la moneda base {base_currency} no proporcionada"
            )

        # Obtener la tasa de la moneda objetivo con respecto a la base
        target_rate = exchange_rates[target_currency]
        base_rate = exchange_rates[
            base_currency
        ]  # Siempre debería ser 1 si base_currency es la referencia

        for account, currency_amounts in balances.items():
            unified_balances[account] = {}
            total_in_target = 0.0

            for currency, amount in currency_amounts.items():
                # Manejar casos donde la currency no está especificada
                if currency in ["N/A", "None", None, "", "?"]:
                    currency = default_currency

                # Si ya está en la moneda objetivo, usar directamente
                if currency == target_currency:
                    converted_amount = amount
                else:
                    # Convertir usando la moneda base como intermediaria
                    if currency in exchange_rates:
                        # Paso 1: Convertir a moneda base
                        # amount / tasa_de_la_moneda (para obtener valor en base currency)
                        currency_rate = exchange_rates[currency]
                        amount_in_base = amount / currency_rate

                        # Paso 2: Convertir de base currency a moneda objetivo
                        # amount_in_base * tasa_objetivo
                        converted_amount = amount_in_base * target_rate
                    else:
                        # Si no tenemos tasa para esta moneda, usar valor directo con advertencia
                        converted_amount = amount
                        # print(f"Advertencia: No se encontró tasa para {currency}, usando valor directo")

                total_in_target += converted_amount

            # Almacenar solo el total en la moneda objetivo
            unified_balances[account][target_currency] = round(total_in_target, 2)

        return unified_balances

    def verify_currency_conversion(
        self,
        amount: float,
        from_currency: str,
        to_currency: str,
        exchange_rates: Dict[str, float],
        base_currency: str = "USD",
    ) -> float:
        """
        Verifica y realiza la conversión de moneda de forma individual.

        Args:
            amount: Monto a convertir
            from_currency: Moneda origen
            to_currency: Moneda destino
            exchange_rates: Tasas de cambio con respecto a la moneda base
            base_currency: Moneda base de referencia

        Returns:
            Monto convertido redondeado a 2 decimales
        """
        if from_currency == to_currency:
            return round(amount, 2)

        if from_currency not in exchange_rates:
            raise ValueError(f"Tasa de cambio para {from_currency} no disponible")

        if to_currency not in exchange_rates:
            raise ValueError(f"Tasa de cambio para {to_currency} no disponible")

        # Convertir a moneda base primero
        from_rate = exchange_rates[from_currency]
        amount_in_base = amount / from_rate

        # Convertir de moneda base a moneda destino
        to_rate = exchange_rates[to_currency]
        converted_amount = amount_in_base * to_rate

        return round(converted_amount, 2)

    # ----------------------------------------------------------------------------------------------
    #                              Funciones de archivo
    # ----------------------------------------------------------------------------------------------

    # FIX: Esta función no está funcionando correctamente falta adaptar al nuevo formato de contenido
    # - Agregar las nuevas reglas de sintaxis como option
    def add_transaction(
        self, date: str, description: str, accounts: List[Dict[str, Union[str, float]]]
    ):
        """
        # FIX (2023-08-05): Esta función no está funcionando correctamente falta adaptar al nuevo formato de contenido
        Adds a new transaction to the ledger file.

        :param date: Date of the transaction in 'YYYY/MM/DD' format.
        :param description: Description of the transaction.
        :param accounts: List of account dictionaries with 'account', 'unit', and 'amount'.
        """
        with open(self.file_path, "a", encoding="utf-8") as file:
            file.write("\n")
            transaction_string = self._create_transaction(date, description, accounts)
            file.write(transaction_string)
            file.write("\n")

    # FUNCIONES AUXILIARES

    def get_date_range(
        self,
        transactions_json: List[
            Dict[str, Union[str, List[Dict[str, Union[str, float]]]]]
        ],
    ):
        # Extraer todas las fechas únicas de las transacciones
        dates = {
            transaction["date"]
            for transaction in transactions_json
            if "date" in transaction
        }

        # Función para convertir las fechas a objetos datetime
        def parse_date(date_str: str):
            # Detectar el formato de fecha y convertirlo a datetime
            if "/" in date_str:
                return datetime.strptime(date_str, "%Y/%m/%d")
            elif "-" in date_str:
                return datetime.strptime(date_str, "%Y-%m-%d")
            else:
                raise ValueError(f"Fecha con formato no soportado: {date_str}")

        # Convertir las fechas a objetos datetime para calcular los límites
        date_objects = [parse_date(date) for date in dates]

        # Determinar la fecha mínima y máxima
        min_date = min(date_objects)
        max_date = max(date_objects)

        # Retornar las fechas en formato string
        return min_date.strftime("%Y/%m/%d"), max_date.strftime("%Y/%m/%d")
