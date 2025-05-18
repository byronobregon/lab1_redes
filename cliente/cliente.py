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


def start_game():
    request = {
        "action": "start"
    }

    response = send_message(request)
    print(response)
    # TODO: This message should be "OK" or "Error" #############################
    print("Conectado al servidor: ", response["action"])
    ############################################################################
    if response.get("status") == "busy":
        print("Servidor Ocupado.")
        return
    play(response["attempts"])


def send_message(message):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.sendall(json.dumps(message).encode())
        return json.loads(s.recv(1024).decode())


def play(attempts):
    number = input(f"Quedan {attempts} intentos: Ingrese un número:\n")

    request = {
        "action": "guess",
        "number": str(number)
    }
    response = send_message(request)
    print("Respuesta: ", response["message"])

    if response.get("status") == "won" or response.get("status") == "lost":
        # play_response = input(f"¿Desea jugar de nuevo? (s/n)\n").lower()
        # if play_response == "s":
        #     request = {
        #         "action": "start"
        #     }
        #     response = send_message(request)
        #     play(response["attempts"])
        # elif play_response == "n":
        #     request_stop = {"action": "stop"}
        #     send_message(request_stop)
        request_stop = {"action": "stop"}
        send_message(request_stop)
        print("CLOSING")
        sys.exit()
    elif response.get("status") == "closing":
        print("CLOSING")
        sys.exit()
    else:
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
