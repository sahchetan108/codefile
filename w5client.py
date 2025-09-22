import socket

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('127.0.0.1', 12345))

op1 = input("Enter first operand: ")
operator = input("Enter operator (+, -, *, /): ")
op2 = input("Enter second operand: ")

client.send(f"{op1} {operator} {op2}".encode())
result = client.recv(1024).decode()

print("Result:", result)
client.close()

