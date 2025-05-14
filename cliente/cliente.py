import socket
import os
import json

HOST = os.getenv("SERVER_HOST", "localhost")
PORT = int(os.getenv("SERVER_PORT", "3000"))

def menu():
    print("----- Bienvenido a Adivina el Número -----")
    print("Seleccione una opción:")
    print("1 - Jugar")
    print("2 - Salir")
    return input()

def start_game():
    request_game_message = "1000" # TODO: 1000 indicates the request of a new game
                                  # evaluate a better option (¿JSON?)
    response = send_message(request_game_message)
    # TODO: This message should be "OK" or "Error" #############################
    print("Conectado al servidor: ", response["message"])
    ############################################################################
    play(response["attempts"])

def send_message(message):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.sendall(message.encode())
        return json.loads(s.recv(1024).decode())

def play(attempts):
    # TODO: it's missing a message to stop recursion
    # (servers should not end connection before client ask's for it)
    number = input(f"Quedan {attempts} intentos: Ingrese un número:\n")
    response = send_message(number)
    print("Respuesta: ", response["message"])
    play(response["attempts"])

def main():
    selection = menu()

    while True:
        if selection == "1":
            start_game()
            break
        elif selection == "2":
            break
        else:
            print("Opción inválida, por favor seleccione 1 o 2.")
            selection = menu()

if __name__ == "__main__":
    main()
