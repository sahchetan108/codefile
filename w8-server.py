import socket
import threading
import sys

# Configurations (change IPs if needed)
SERVER1_IP = '127.0.0.1'
SERVER1_TCP_PORT = 5000
SERVER1_UDP_PORT = 5001

SERVER2_IP = '127.0.0.1'
SERVER2_TCP_PORT = 6000
SERVER2_UDP_PORT = 6001

# Choose which server this is (1 or 2) via command line
SERVER_ID = int(sys.argv[1]) if len(sys.argv) > 1 else 1

if SERVER_ID == 1:
    MY_TCP_PORT = SERVER1_TCP_PORT
    MY_UDP_PORT = SERVER1_UDP_PORT
    PEER_TCP_PORT = SERVER2_TCP_PORT
    PEER_UDP_PORT = SERVER2_UDP_PORT
    PEER_IP = SERVER2_IP
else:
    MY_TCP_PORT = SERVER2_TCP_PORT
    MY_UDP_PORT = SERVER2_UDP_PORT
    PEER_TCP_PORT = SERVER1_TCP_PORT
    PEER_UDP_PORT = SERVER1_UDP_PORT
    PEER_IP = SERVER1_IP

# Data structures to hold clients
tcp_clients = []
udp_clients = set()  # set of (address, port) tuples

# Locks for thread safety
tcp_clients_lock = threading.Lock()
udp_clients_lock = threading.Lock()

# UDP socket for clients
udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_sock.bind((SERVER1_IP if SERVER_ID == 1 else SERVER2_IP, MY_UDP_PORT))

# UDP socket for inter-server communication
inter_server_udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
inter_server_udp_sock.bind((SERVER1_IP if SERVER_ID == 1 else SERVER2_IP, MY_UDP_PORT + 100))  # use different port

# TCP socket for clients
tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_sock.bind((SERVER1_IP if SERVER_ID == 1 else SERVER2_IP, MY_TCP_PORT))
tcp_sock.listen(5)

# TCP socket for inter-server communication
inter_server_tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
inter_server_tcp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
inter_server_tcp_sock.bind((SERVER1_IP if SERVER_ID == 1 else SERVER2_IP, MY_TCP_PORT + 100))
inter_server_tcp_sock.listen(1)

def broadcast_tcp(message, sender_sock=None):
    with tcp_clients_lock:
        for client in tcp_clients:
            if client != sender_sock:
                try:
                    client.sendall(message)
                except:
                    tcp_clients.remove(client)

def broadcast_udp(message, sender_addr=None):
    with udp_clients_lock:
        for addr in udp_clients:
            if addr != sender_addr:
                try:
                    udp_sock.sendto(message, addr)
                except:
                    udp_clients.remove(addr)

def handle_tcp_client(client_sock, addr):
    print(f"[TCP Client connected] {addr}")
    with tcp_clients_lock:
        tcp_clients.append(client_sock)

    try:
        while True:
            data = client_sock.recv(1024)
            if not data:
                break
            print(f"[TCP from {addr}]: {data.decode()}")
            # Broadcast locally
            broadcast_tcp(data, sender_sock=client_sock)
            broadcast_udp(data)  # forward UDP clients too
            
            # Forward to peer server over inter-server TCP socket
            try:
                inter_server_sock.sendall(data)
            except Exception as e:
                print(f"[Error forwarding to peer server] {e}")

    finally:
        with tcp_clients_lock:
            tcp_clients.remove(client_sock)
        client_sock.close()
        print(f"[TCP Client disconnected] {addr}")

def tcp_accept_clients():
    while True:
        client_sock, addr = tcp_sock.accept()
        threading.Thread(target=handle_tcp_client, args=(client_sock, addr), daemon=True).start()

def handle_udp_clients():
    while True:
        data, addr = udp_sock.recvfrom(1024)
        with udp_clients_lock:
            udp_clients.add(addr)
        print(f"[UDP from {addr}]: {data.decode()}")
        # Broadcast to other UDP clients
        broadcast_udp(data, sender_addr=addr)
        # Forward to TCP clients
        broadcast_tcp(data)

        # Forward to peer server over inter-server UDP socket
        try:
            inter_server_udp_sock.sendto(data, (PEER_IP, PEER_UDP_PORT + 100))
        except Exception as e:
            print(f"[Error forwarding UDP to peer] {e}")

def handle_inter_server_tcp(conn):
    while True:
        try:
            data = conn.recv(1024)
            if not data:
                break
            # Broadcast to local clients (both TCP and UDP)
            print(f"[From peer server TCP]: {data.decode()}")
            broadcast_tcp(data)
            broadcast_udp(data)
        except:
            break

def inter_server_tcp_accept():
    while True:
        conn, addr = inter_server_tcp_sock.accept()
        print(f"[Inter-server TCP connected from {addr}]")
        threading.Thread(target=handle_inter_server_tcp, args=(conn,), daemon=True).start()

def inter_server_tcp_connect():
    global inter_server_sock
    inter_server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    while True:
        try:
            inter_server_sock.connect((PEER_IP, PEER_TCP_PORT + 100))
            print("[Connected to peer server TCP socket]")
            break
        except:
            print("[Retrying peer server TCP connection...]")
            threading.Event().wait(2)

def handle_inter_server_udp():
    while True:
        try:
            data, addr = inter_server_udp_sock.recvfrom(1024)
            print(f"[From peer server UDP]: {data.decode()}")
            # Broadcast to local clients
            broadcast_tcp(data)
            broadcast_udp(data)
        except:
            pass

if __name__ == '__main__':
    # Start TCP server for clients
    threading.Thread(target=tcp_accept_clients, daemon=True).start()

    # Start UDP server for clients
    threading.Thread(target=handle_udp_clients, daemon=True).start()

    # Start inter-server TCP listener
    threading.Thread(target=inter_server_tcp_accept, daemon=True).start()

    # Connect to peer inter-server TCP socket
    threading.Thread(target=inter_server_tcp_connect, daemon=True).start()

    # Start inter-server UDP listener
    threading.Thread(target=handle_inter_server_udp, daemon=True).start()

    print(f"Server {SERVER_ID} running... TCP port {MY_TCP_PORT}, UDP port {MY_UDP_PORT}")
    while True:
        try:
            threading.Event().wait(1)
        except KeyboardInterrupt:
            print("Shutting down server")
            break
