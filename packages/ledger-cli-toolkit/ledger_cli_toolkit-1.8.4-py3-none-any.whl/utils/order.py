from datetime import datetime
from typing import List, Dict, Union, Any, List
import json


def sort_transactions(transactions: List[Dict[str, Union[str, bool, list]]]) -> List[Dict]:
    """
    Ordena las transacciones por fecha y hora.
    Soporta fechas con '-' o '/' y si no hay hora, se asume 00:00:00.
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
