import socket
import threading

def handle_client(conn):
    while True:
        data = conn.recv(1024).decode()
        if not data:
            break
        op1, operator, op2 = data.split()
        op1, op2 = float(op1), float(op2)
        if operator == '+':
            res = op1 + op2
        elif operator == '-':
            res = op1 - op2
        elif operator == '*':
            res = op1 * op2
        elif operator == '/':
            res = op1 / op2 if op2 != 0 else 'Error: Division by zero'
        else:
            res = 'Error: Invalid operator'
        conn.send(str(res).encode())
    conn.close()

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('0.0.0.0', 12345))
server.listen(2)

while True:
    conn, _ = server.accept()
    threading.Thread(target=handle_client, args=(conn,)).start()

