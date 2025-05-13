import socket
import os

HOST = os.getenv("SERVER_HOST", "localhost")
PORT = int(os.getenv("SERVER_PORT", "3000"))

def main():
    numero = input("Ingresa un número: ")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.sendall(numero.encode())
        respuesta = s.recv(1024).decode()
        print("Respuesta del servidor:", respuesta)

if __name__ == "__main__":
    main()
