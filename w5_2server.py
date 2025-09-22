import socket

def validate_password(pwd):
    if len(pwd) < 8 or len(pwd) > 20:
        return "Invalid: Length should be 8-20"
    if not all(c.isalpha() or c.isdigit() or c in "_@$" for c in pwd):
        return "Invalid: Only alphabets, digits, _, @, $ allowed"
    if not any(c.islower() for c in pwd):
        return "Invalid: At least one lowercase letter required"
    if not any(c.isupper() for c in pwd):
        return "Invalid: At least one uppercase letter required"
    if not any(c.isdigit() for c in pwd):
        return "Invalid: At least one digit required"
    if not any(c in "_@$" for c in pwd):
        return "Invalid: At least one special char (_@ $) required"
    return "Password is valid"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('0.0.0.0', 12345))
server.listen(5)
print("Server active and listening on port 12345")

while True:
    conn, addr = server.accept()
    pwd = conn.recv(1024).decode()
    res = validate_password(pwd)
    conn.send(res.encode())
    conn.close()

