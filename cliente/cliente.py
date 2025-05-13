import socket
import os

HOST = os.getenv("SERVER_HOST", "localhost")
PORT = int(os.getenv("SERVER_PORT", "3000"))

def menu():
    print("----- Bienvenido a Adivina el Número -----")
    print("Seleccione una opción:")
    print("1 - Jugar")
    print("2 - Salir")
    return input()

def play():
    numero = input("Ingresa un número: ")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.sendall(numero.encode())
        respuesta = s.recv(1024).decode()
        print("Respuesta del servidor:", respuesta)

def main():
    while True:
        selection = menu()

        if selection == "1":
            play()
        elif selection == "2":
            break
        else:
            print("Opción inválida, por favor seleccione 1 o 2.")

if __name__ == "__main__":
    main()
