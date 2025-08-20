from matplotlib import pyplot as plt
import numpy as np
import random


class LedgerGrafics:

    def __init__(self):
        pass

    def create_balance_chart(self, balances, period):
        """
        Crea una gráfica de barras para los saldos por cuenta y moneda.

        :param balances: Diccionario con los balances por cuenta y moneda.
        :param period: Periodo para incluir en el título del gráfico.
        :return: La figura y los ejes del gráfico generado.
        """
        accounts = []
        totals = []
        colors = []

        # Generar una lista de colores únicos
        unique_colors = [
            "#%06x" % random.randint(0, 0xFFFFFF) for _ in range(len(balances))
        ]
        color_map = {}

        # Preparar datos para el gráfico, separando por moneda
        for account, currencies in balances.items():
            for currency, amount in currencies.items():
                account_label = f"{account} ({currency if currency else 'N/A'})"
                accounts.append(account_label)
                totals.append(amount)

                # Asignar un color único a cada cuenta
                if account not in color_map:
                    color_map[account] = unique_colors.pop()
                colors.append(color_map[account])

        # Crear el gráfico de barras
        fig, ax = plt.subplots(figsize=(7, 6))
        bars = ax.bar(accounts, totals, color=colors)

        # Formatear valores como moneda y agregar etiquetas de datos
        for bar, total in zip(bars, totals):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height(),
                f"${total:,.2f}",
                ha="center",
                va="bottom",
                fontsize=6,
                color="black",
            )

        # Configurar el gráfico
        ax.set_title(f"Balance General del {period}", fontsize=13)
        ax.set_xlabel("Cuentas", fontsize=9)
        ax.set_ylabel("Saldo Total", fontsize=9)
        ax.tick_params(axis="x", rotation=90, labelsize=7)
        ax.grid(axis="y", linestyle="--", alpha=0.7)

        plt.tight_layout()

        return fig, ax

    def create_balance_pie_chart(self, balances, period):
        """
        Crea una gráfica de pastel para los saldos por cuenta y moneda.

        :param balances: Diccionario con los balances por cuenta y moneda.
        :param period: Periodo para incluir en el título del gráfico.
        :return: La figura y los ejes del gráfico generado.
        """
        labels = []
        totals = []
        colors = []

        # Generar una lista de colores únicos
        unique_colors = [
            "#%06x" % random.randint(0, 0xFFFFFF) for _ in range(len(balances))
        ]
        color_map = {}

        # Preparar datos para el gráfico, separando por moneda
        for account, currencies in balances.items():
            for currency, amount in currencies.items():
                account_label = f"{account} ({currency if currency else 'N/A'})"
                labels.append(account_label)
                totals.append(amount)

                # Asignar un color único a cada cuenta
                if account not in color_map:
                    color_map[account] = unique_colors.pop()
                colors.append(color_map[account])

        totals = [abs(t) for t in totals]

        # Crear el gráfico de pastel
        fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(aspect="equal"))
        wedges, texts, autotexts = ax.pie(
            totals,
            # labels=labels,
            autopct="%1.1f%%",
            startangle=90,
            colors=colors,
            # textprops=dict(color="black"),
            # labeldistance=1.1,  # Ajustar la distancia de las etiquetas
            pctdistance=0.85,  # Ajustar la distancia de los porcentajes
        )

        ax.legend(
            wedges,
            labels,
            title="Ingredients",
            loc="center left",
            bbox_to_anchor=(1, 0, 0.5, 1),
        )

        plt.setp(autotexts, size=8, weight="bold")
        # Configurar el gráfico
        ax.set_title(f"Distribución de Balances del {period}", fontsize=16)

        # Ajustar el tamaño de los textos para evitar solapamientos
        # plt.setp(autotexts, size=8, weight="bold")
        # plt.setp(
        #     texts, fontsize=9, rotation=45
        # )  # Rotar etiquetas para mejor legibilidad

        # Asegurarse de que todo encaje en la figura
        plt.tight_layout()

        return fig, ax

    # def create_multiple_line_chart(self):
    #     # Datos financieros proporcionados
    #     data = {
    #         "Assets": {"MXN": 1186.6400000000006},
    #         "Liabilities": {"MXN": -6210.38},
    #         "Equity": {"MXN": 5849.74},
    #         "Income": {"MXN": -1750.0},
    #         "Expenses": {"MXN": 924.0},
    #     }

    #     # Extraer los valores de las categorías (solo en 'MXN' en este caso)
    #     categories = list(data.keys())
    #     values = [data[category]["MXN"] for category in categories]

    #     # Crear la figura y los ejes
    #     fig, ax = plt.subplots(figsize=(10, 6))

    #     # Crear el gráfico de líneas
    #     ax.plot(categories, values, marker="o", linestyle="-", color="b", label="Valor")

    #     # Títulos y etiquetas
    #     ax.set_title("Gráfico de Líneas de Datos Financieros")
    #     ax.set_xlabel("Categorías")
    #     ax.set_ylabel("Valor (MXN)")

    #     # Mostrar la leyenda
    #     ax.legend()

    #     # Mostrar el gráfico
    #     ax.grid(True)

    #     # Retornar fig y ax
    #     return fig, ax

    def save_chart(self, fig, filepath, filename):
        """
        Guarda la figura del gráfico en la ruta y nombre especificados.

        :param fig: Figura del gráfico.
        :param filepath: Ruta donde se guardará la imagen.
        :param filename: Nombre del archivo de la imagen.
        """
        full_path = f"{filepath}/{filename}"
        fig.savefig(full_path, format="png")
        print(f"Gráfico guardado en: {full_path}")

    def show_chart(self):
        plt.show()


if __name__ == "__main__":
    balances = {
        "Assets:Cash": {"USD": -320.0, "MXN": -2720.0},
        "Assets:Bank:Nubank": {"MXN": 9150.0, "$": 6800.0, None: 3400.0},
        "Liabilities:CreditCard:Nubank": {"MXN": -1500.0},
        "Equity:OpeningBalance": {"USD": 1000.0},
        "Liabilities:CreditCard:Visa": {"USD": -465.0},
        "Liabilities:Debts:Personal": {"MXN": -500.0},
        "Assets:Bank:Chase": {"USD": 1700.0, "$": -200.0, None: -400.0},
        "Expenses:Education:Books": {"USD": 45.0},
        "Assets:Bank:Savings": {"MXN": 3000.0, "USD": 400.0},
        "Income:Freelance": {"USD": -800.0},
        "Expenses:Dining": {"USD": 60.0},
        "Expenses:Transportation": {"MXN": 120.0},
        "Income:Other": {"USD": -150.0},
        "Expenses:Utilities": {"MXN": 750.0},
        "Expenses:Groceries": {"USD": 120.0},
        "Income:Bonus": {"USD": -1000.0},
        "Expenses:Entertainment": {"MXN": 600.0},
        "Expenses:Tipping": {"USD": 10.0},
        "Income:Rent": {"MXN": -4000.0},
    }

    ledger_graphics = LedgerGrafics()
    fig, ax = ledger_graphics.create_balance_chart(balances, "Enero 2025")

    # Mostrar el gráfico
    ledger_graphics.show_chart()

    # Guardar el gráfico
    # ledger_graphics.save_chart(fig, "./", "balance_general.png")
