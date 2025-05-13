import socket
import os
import json

TCP_HOST = '0.0.0.0'
TCP_PORT = int(os.getenv("TCP_PORT", 3000))

UDP_FINAL_HOST = os.getenv("FINAL_SERVER_HOST", "localhost")
UDP_FINAL_PORT = int(os.getenv("FINAL_SERVER_PORT", 6000))

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_sock:
        tcp_sock.bind((TCP_HOST, TCP_PORT))
        tcp_sock.listen()
        print("Servidor intermedio escuchando TCP...")

        while True:
            conn, addr = tcp_sock.accept()
            with conn:
                numero = conn.recv(1024).decode()
                with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_sock:
                    udp_sock.sendto(numero.encode(), (UDP_FINAL_HOST, UDP_FINAL_PORT))
                    respuesta, _ = udp_sock.recvfrom(1024)
                    conn.sendall(respuesta)
                    # parsed = json.load(respuesta)
                    # formated = json.dump(parsed, indent=4)
                    # print(formated)

if __name__ == "__main__":
    main()
