import socket
import threading
import json

class ChatServer:
    def __init__(self, host, port, partner_host, partner_port):
        self.host = host
        self.port = port
        self.partner_host = partner_host
        self.partner_port = partner_port
        self.clients = []
        self.lock = threading.Lock()
        self.running = True
        
    def start(self):
        # Main server socket
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        print(f"Server started on {self.host}:{self.port}")
        
        # Connect to partner server
        self.connect_to_partner()
        
        # Accept client connections
        while self.running:
            try:
                client_socket, address = self.server_socket.accept()
                print(f"New connection from {address}")
                
                with self.lock:
                    self.clients.append(client_socket)
                
                # Start a thread to handle the client
                client_thread = threading.Thread(
                    target=self.handle_client, 
                    args=(client_socket,)
                )
                client_thread.daemon = True
                client_thread.start()
            except Exception as e:
                if self.running:
                    print(f"Error accepting connection: {e}")
    
    def connect_to_partner(self):
        """Connect to the other server for inter-server communication"""
        try:
            self.partner_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.partner_socket.connect((self.partner_host, self.partner_port))
            print(f"Connected to partner server at {self.partner_host}:{self.partner_port}")
            
            # Start a thread to listen for messages from partner server
            partner_thread = threading.Thread(target=self.listen_to_partner)
            partner_thread.daemon = True
            partner_thread.start()
        except Exception as e:
            print(f"Failed to connect to partner server: {e}")
            self.partner_socket = None
    
    def listen_to_partner(self):
        """Listen for messages from the partner server"""
        while self.running:
            try:
                data = self.partner_socket.recv(1024).decode('utf-8')
                if not data:
                    break
                
                # Broadcast the message to all connected clients
                self.broadcast(data, source="partner")
            except Exception as e:
                if self.running:
                    print(f"Error receiving from partner: {e}")
                break
    
    def handle_client(self, client_socket):
        """Handle messages from a client"""
        while self.running:
            try:
                message = client_socket.recv(1024).decode('utf-8')
                if not message:
                    break
                
                print(f"Received message: {message}")
                
                # Broadcast to all clients on this server
                self.broadcast(message, source="local")
                
                # Forward to partner server
                self.forward_to_partner(message)
            except Exception as e:
                if self.running:
                    print(f"Error handling client: {e}")
                break
        
        # Remove client when disconnected
        with self.lock:
            if client_socket in self.clients:
                self.clients.remove(client_socket)
        client_socket.close()
    
    def broadcast(self, message, source="local"):
        """Send a message to all connected clients"""
        with self.lock:
            disconnected_clients = []
            for client in self.clients:
                try:
                    client.send(message.encode('utf-8'))
                except Exception as e:
                    print(f"Error broadcasting to client: {e}")
                    disconnected_clients.append(client)
            
            # Remove disconnected clients
            for client in disconnected_clients:
                self.clients.remove(client)
    
    def forward_to_partner(self, message):
        """Forward a message to the partner server"""
        if self.partner_socket:
            try:
                self.partner_socket.send(message.encode('utf-8'))
            except Exception as e:
                print(f"Error forwarding to partner: {e}")
    
    def stop(self):
        self.running = False
        self.server_socket.close()
        if hasattr(self, 'partner_socket') and self.partner_socket:
            self.partner_socket.close()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 5:
        print("Usage: python server.py <host> <port> <partner_host> <partner_port>")
        sys.exit(1)
    
    host = sys.argv[1]
    port = int(sys.argv[2])
    partner_host = sys.argv[3]
    partner_port = int(sys.argv[4])
    
    server = ChatServer(host, port, partner_host, partner_port)
    
    try:
        server.start()
    except KeyboardInterrupt:
        print("Shutting down server...")
        server.stop()