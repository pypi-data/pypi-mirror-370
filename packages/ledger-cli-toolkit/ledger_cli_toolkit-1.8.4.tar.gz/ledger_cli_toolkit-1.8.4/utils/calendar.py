import calendar

def mostrar_calendario():
    while True:
        try:
            # Solicitar el año y el mes al usuario
            anio = int(input("Introduce el año (por ejemplo, 2025): "))
            mes = int(input("Introduce el mes (1-12): "))
            
            # Mostrar el calendario del mes
            print("\n", calendar.month(anio, mes))
            
            # Solicitar un día al usuario
            dia = int(input(f"Selecciona un día (1-{calendar.monthrange(anio, mes)[1]}): "))
            
            # Validar que el día esté en el rango correcto
            if 1 <= dia <= calendar.monthrange(anio, mes)[1]:
                print(f"\nFecha seleccionada: {anio}-{mes:02d}-{dia:02d}")
                return f"{anio}-{mes:02d}-{dia:02d}"
            else:
                print("Día fuera de rango. Intenta nuevamente.")
        except ValueError:
            print("Entrada no válida. Intenta nuevamente.")
        except Exception as e:
            print(f"Error: {e}. Intenta nuevamente.")

# Llamar a la función
if __name__ == "__main__":
    fecha = mostrar_calendario()
