from .ledger import LedgerParser
from ..utils import sort_transactions, remove_duplicates

class LedgerMultiParser:
    def __init__(self, files, parents_accounts=None):
        self.files = files
        self.parents_accounts = parents_accounts or []
        self.parsers = []

        for f in files:
            parser = LedgerParser(
                file=f,
                file_accounts=f,
                parents_accounts=self.parents_accounts,
            )
            self.parsers.append(parser)

    def parse_all(self):
        all_transactions = []
        all_accounts = []
        all_accounts_advance = []
        all_parents = []
        all_metadata_yaml = {}
        all_map_docs = []

        for parser in self.parsers:
            transactions = parser.parse_transactions()
            accounts = parser.parse_accounts()
            accounts_advance = parser.parse_accounts_advance()
            parents = parser.detected_parents_accounts()
            metadata_yaml = parser.parse_metadata_yaml()
            map_doc = parser.parse_doc()

            all_transactions.extend(transactions)
            all_accounts.extend(accounts)
            all_accounts_advance.extend(accounts_advance)
            all_parents.extend(parents)
            all_metadata_yaml.update(metadata_yaml)
            all_map_docs.append(map_doc)
        
        ordered_transactions = sort_transactions(all_transactions)
        all_accounts = remove_duplicates(all_accounts)
        all_accounts_advance = remove_duplicates(all_accounts_advance)
        all_parents = remove_duplicates(all_parents)

        return {
            "transactions": all_transactions,
            "ordered_transactions": ordered_transactions,
            "accounts": all_accounts,
            "accounts_advance": all_accounts_advance,
            "parents": all_parents,
            "metadata_yaml": all_metadata_yaml,
            "map_docs": all_map_docs,
        }

    def resolve_all(self, extra_rules=None):
        merged = self.parse_all()
        resolved = []
        for parser in self.parsers:
            resolved.extend(parser.resolve(merged["transactions"], extra_rules or {}))
        return resolved
