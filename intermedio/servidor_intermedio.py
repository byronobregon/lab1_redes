import socket
import os
import json
import sys

TCP_HOST = '0.0.0.0'
TCP_PORT = int(os.getenv("TCP_PORT", 3000))

UDP_FINAL_HOST = os.getenv("FINAL_SERVER_HOST", "localhost")

def number_response(str):
    if str == "bigger":
        return "El número es mayor"
    elif str == "smaller":
        return "El número es menor"
    elif str == "Error al convertir texto a número.":
        return "Favor ingresar un número del 1 al 100"
    else:
        return "¡Has acertado!"

def send_request_to_server(attempts, message, status, conn):
    response = {
        "action": "OK",
        "attempts": attempts,
        "message": message,
        "status": status
    }
    conn.sendall(json.dumps(response).encode('utf-8'))


def main():
    # TODO Refactor this
    UDP_FINAL_PORT = 6000
    attempts_count = 8
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_sock:
        tcp_sock.bind((TCP_HOST, TCP_PORT))
        tcp_sock.listen()
        print("Servidor intermedio escuchando TCP...")

        while True:
            conn, addr = tcp_sock.accept()
            with conn:
                data = conn.recv(1024).decode()
                request = json.loads(data)
                number = request.get("number")
                with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_sock:
                    start_request = {
                        "action": "start"
                    }
                    if request.get("action") == "start":
                        udp_sock.sendto(json.dumps(start_request).encode('utf-8'),
                                        (UDP_FINAL_HOST, UDP_FINAL_PORT))
                    elif request.get("action") == "guess":
                        guess_request = {
                            "action": "guess",
                            "number": number
                        }
                        udp_sock.sendto(json.dumps(guess_request).encode('utf-8'),
                                        (UDP_FINAL_HOST, UDP_FINAL_PORT))
                    elif request.get("action") == "stop":
                        guess_request = {
                            "action": "stop",
                        }
                        udp_sock.sendto(json.dumps(guess_request).encode('utf-8'),
                                        (UDP_FINAL_HOST, UDP_FINAL_PORT))

                    udp_response, _ = udp_sock.recvfrom(1024)
                    json_response = json.loads(udp_response.decode('utf-8'))
                    UDP_FINAL_PORT = int(json_response.get("port"))
                    print(json_response)
                    message = number_response(json_response.get("message"))
                    status = json_response.get("status")
                    if json_response.get("status") == "playing":
                        attempts_count -= 1
                        if attempts_count == 0:
                            message = "¡Has perdido!"
                            status = "lost"
                    send_request_to_server(attempts_count, message, status, conn)
                    if status == "closing":
                        print("Middle server closing.")
                        sys.exit()


if __name__ == "__main__":
    main()
