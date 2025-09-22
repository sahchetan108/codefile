import socket

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('127.0.0.1', 12345))

msg = input("Enter message: ")
client.send(msg.encode())
echo = client.recv(1024).decode()
print("Echo from server:", echo)
client.close()

