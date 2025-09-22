import socket
import threading

def handle_client(conn, addr):
    while True:
        data = conn.recv(1024)
        if not data:
            break
        conn.send(data)
    conn.close()

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('0.0.0.0', 12345))
server.listen(5)
print("Server started and listening on port 12345")

while True:
    conn, addr = server.accept()
    threading.Thread(target=handle_client, args=(conn, addr)).start()

