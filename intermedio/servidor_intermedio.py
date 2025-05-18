import socket
import os
import json
import sys

TCP_HOST = '0.0.0.0'
TCP_PORT = int(os.getenv("TCP_PORT", 3000))
UDP_FINAL_HOST = os.getenv("FINAL_SERVER_HOST", "localhost")
MAX_ATTEMPTS = 3


def number_response(str):
    dict_responses = {
        "bigger": "El número es mayor",
        "smaller": "El número es menor",
        "same": "¡Has acertado!"
    }
    return dict_responses.get(str)


def send_udp_request(udp_sock, request_data, udp_port):
    udp_sock.sendto(json.dumps(request_data).encode('utf-8'), (UDP_FINAL_HOST, udp_port))
    response, _ = udp_sock.recvfrom(1024)
    return json.loads(response.decode('utf-8'))


def create_tcp_response(attempts, message, status):
    return {
        "action": "OK",
        "attempts": attempts,
        "message": message,
        "status": status
    }


def main():
    # TODO Refactor this
    UDP_FINAL_PORT = 6000
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_sock:
        tcp_sock.bind((TCP_HOST, TCP_PORT))
        tcp_sock.listen()
        print("Servidor intermedio escuchando TCP...")
        attempts_count = MAX_ATTEMPTS

        while True:
            conn, addr = tcp_sock.accept()
            with conn:
                data = conn.recv(1024).decode()
                request = json.loads(data)
                action = request.get("action")
                number = request.get("number")
                with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_sock:
                    if action == "start":
                        udp_request = {"action": "start"}
                        attempts_count = MAX_ATTEMPTS
                    elif action == "guess":
                        udp_request = {"action": "guess", "number": number}
                        attempts_count -= 1
                    elif action == "stop":
                        udp_request = {"action": "stop"}
                    json_response = send_udp_request(udp_sock, udp_request, UDP_FINAL_PORT)
                    json_status = json_response.get("status")
                    print(json_response)

                    if attempts_count <= 0:
                        message = "No attempts left"
                        response = create_tcp_response(attempts_count, message, "no_attempts")
                        udp_request = {"action": "reset"}
                        send_udp_request(udp_sock, udp_request, UDP_FINAL_PORT)
                    elif json_status in ["playing", "won"]:
                        message = number_response(json_response.get("message"))
                        response = create_tcp_response(attempts_count, message, json_status)
                    elif json_status == "closing":
                        response = {"action": "OK", "status": "closing"}
                        conn.sendall(json.dumps(response).encode('utf-8'))
                        sys.exit()
                    conn.sendall(json.dumps(response).encode('utf-8'))


if __name__ == "__main__":
    main()