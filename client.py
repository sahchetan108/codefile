import socket
import threading
import sys

class ChatClient:
    def __init__(self, name):
        self.name = name
        self.socket = None
        self.running = True
    
    def connect(self, host, port):
        """Connect to a server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((host, port))
            print(f"Connected to server {host}:{port}")
            
            # Send join message
            join_message = f"{self.name} joined the chatroom"
            self.socket.send(join_message.encode('utf-8'))
            
            # Start a thread to listen for messages
            listen_thread = threading.Thread(target=self.listen_for_messages)
            listen_thread.daemon = True
            listen_thread.start()
            
            return True
        except Exception as e:
            print(f"Failed to connect to server: {e}")
            return False
    
    def listen_for_messages(self):
        """Listen for messages from the server"""
        while self.running:
            try:
                message = self.socket.recv(1024).decode('utf-8')
                if not message:
                    break
                print(f"\n{message}\nEnter your message: ", end="")
            except Exception as e:
                if self.running:
                    print(f"Error receiving message: {e}")
                break
    
    def send_message(self, message):
        """Send a message to the server"""
        if self.socket:
            try:
                full_message = f"{self.name}: {message}"
                self.socket.send(full_message.encode('utf-8'))
            except Exception as e:
                print(f"Error sending message: {e}")
    
    def disconnect(self):
        """Disconnect from the server"""
        self.running = False
        if self.socket:
            self.socket.close()

def main():
    if len(sys.argv) != 2:
        print("Usage: python client.py <client_name>")
        sys.exit(1)
    
    name = sys.argv[1]
    client = ChatClient(name)
    
    # Server selection
    print("Available servers:")
    print("1. localhost:8000")
    print("2. localhost:8001")
    
    choice = input("Select server (1 or 2): ").strip()
    
    if choice == "1":
        host, port = "localhost", 8000
    elif choice == "2":
        host, port = "localhost", 8001
    else:
        print("Invalid choice. Using server 1 by default.")
        host, port = "localhost", 8000
    
    # Connect to the selected server
    if not client.connect(host, port):
        sys.exit(1)
    
    # Main loop to send messages
    try:
        while client.running:
            message = input("Enter your message: ")
            if message.lower() == '/quit':
                break
            client.send_message(message)
    except KeyboardInterrupt:
        print("\nDisconnecting...")
    finally:
        client.disconnect()

if __name__ == "__main__":
    main()