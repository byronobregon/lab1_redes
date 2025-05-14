import socket
import os
import json

TCP_HOST = '0.0.0.0'
TCP_PORT = int(os.getenv("TCP_PORT", 3000))

UDP_FINAL_HOST = os.getenv("FINAL_SERVER_HOST", "localhost")


# UDP_FINAL_PORT = int(os.getenv("FINAL_SERVER_PORT", 6000))

def number_response(str):
    if str == "bigger":
        return "El número es mayor"
    elif str == "smaller":
        return "El número es menor"
    else:
        return "¡Has acertado!"


def main():
    # TODO Refactor this
    UDP_FINAL_PORT = 6000
    attempts_count = 7
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_sock:
        tcp_sock.bind((TCP_HOST, TCP_PORT))
        tcp_sock.listen()
        print("Servidor intermedio escuchando TCP...")

        while True:
            conn, addr = tcp_sock.accept()
            with conn:
                number = conn.recv(1024).decode()
                with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_sock:
                    udp_sock.sendto(number.encode(), (UDP_FINAL_HOST, UDP_FINAL_PORT))
                    response, _ = udp_sock.recvfrom(1024)
                    json_response = json.loads(response.decode('utf-8'))
                    # TODO refactor this
                    UDP_FINAL_PORT = int(json_response.get("port"))
                    print(json_response)
                    if attempts_count <= 0:
                        conn.sendall(b"No trys left")
                        # TODO it should await from client message to close
                        # after that it should tell the server to close the process
                        # then it should receive an ok from the server, and
                        # send a message to the client
                        # after that it should close the process
                        break
                    elif number_response(json_response.get("message")) == "¡Has acertado!":
                        conn.sendall(b"You won!")
                        # TODO it should await from client message to close
                        # after that it should tell the server to close the process
                        # then it should receive an ok from the server, and
                        # send a message to the client
                        # after that it should close the process
                        break
                    client_message = {
                        "message": number_response(json_response.get("message")),
                        "attempts": attempts_count
                    }
                    print(number)
                    conn.sendall(json.dumps(client_message).encode('utf-8'))
                    if number != "1000": # TODO check with client request game condition
                        attempts_count -= 1


if __name__ == "__main__":
    main()
