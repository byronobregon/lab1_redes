import socket
import os
import json
import sys

HOST = os.getenv("SERVER_HOST", "localhost")
PORT = int(os.getenv("SERVER_PORT", "3000"))


def menu():
    print("----- Bienvenido a Adivina el Número -----")
    print("Seleccione una opción:")
    print("1 - Jugar")
    print("2 - Salir")
    return input()


def send_message(message):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.sendall(json.dumps(message).encode())
        return json.loads(s.recv(1024).decode())


def prompt_replay():
    while True:
        choice = input("¿Desea jugar de nuevo? (s/n)\n").lower()
        if choice in ("s", "n"):
            return choice


def play(attempts):
    number = input(f"Quedan {attempts} intentos: Ingrese un número:\n")

    request = {"action": "guess", "number": str(number)}
    response = send_message(request)
    print("Respuesta: ", response["message"])

    status = response.get("status")
    if status in ["won", "no_attempts"]:
        if prompt_replay() == "s":
            response = send_message({"action": "start"})
            play(response["attempts"])
        else:
            send_message({"action": "stop"})
    elif status == "closing":
        sys.exit()
    else:
        play(response["attempts"])


def start_game():
    response = send_message({"action": "start"})
    if response.get("status") == "busy":
        print("Server is busy right now.")
    else:
        print("Conectado al servidor: ", response["action"])
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