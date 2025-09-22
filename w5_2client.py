import socket

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('127.0.0.1', 12345))

password = input("Enter password: ")
client.send(password.encode())
response = client.recv(1024).decode()
print(response)
client.close()

