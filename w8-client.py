import socket
import threading

def receive_tcp(sock):
    while True:
        try:
            data = sock.recv(1024)
            if not data:
                break
            print(f"\n[Broadcast]: {data.decode()}\n> ", end="")
        except:
            break

def receive_udp(sock):
    while True:
        try:
            data, _ = sock.recvfrom(1024)
            print(f"\n[Broadcast]: {data.decode()}\n> ", end="")
        except:
            break

def main():
    protocol = input("Select protocol (TCP/UDP): ").strip().upper()
    server_ip = input("Enter server IP (e.g. 127.0.0.1): ").strip()
    if protocol == 'TCP':
        server_port = int(input("Enter server TCP port: "))
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((server_ip, server_port))

        threading.Thread(target=receive_tcp, args=(sock,), daemon=True).start()

        while True:
            msg = input("> ")
            if msg.lower() == "exit":
                break
            sock.sendall(msg.encode())

        sock.close()

    elif protocol == 'UDP':
        server_port = int(input("Enter server UDP port: "))
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        threading.Thread(target=receive_udp, args=(sock,), daemon=True).start()

        while True:
            msg = input("> ")
            if msg.lower() == "exit":
                break
            sock.sendto(msg.encode(), (server_ip, server_port))

        sock.close()

    else:
        print("Invalid protocol")

if __name__ == "__main__":
    main()
