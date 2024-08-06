import argparse

# Crear el parser
parser = argparse.ArgumentParser(description='Procesa un número entero y una cadena opcional.')

# Definir los argumentos que aceptará el programa
parser.add_argument('numero', type=int, help='Un número entero')
parser.add_argument('--cadena', type=str, help='Una cadena opcional', default='Hola')

# Analizar los argumentos de la línea de comandos
args = parser.parse_args()

# Usar los argumentos en el programa
print(f"El número proporcionado es: {args.numero}")
print(f"La cadena proporcionada es: {args.cadena}")


# Se ejecuta proporcionando un numero despues
# python3 ejemplo_argparse.py 123
# pyhon ejemplo_argparse.py 123 --cadena Manuel
