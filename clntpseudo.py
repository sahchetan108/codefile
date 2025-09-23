START

IMPORT socket, threading, sys

SET client_id = command line argument if provided, otherwise 1
SET username = "User" + client_id

FUNCTION select_server():
    DISPLAY "Server Selection Menu"
    DISPLAY "1. Server 1 (port 8001)"
    DISPLAY "2. Server 2 (port 8002)"
    DISPLAY "3. Auto-select (round-robin)"
    
    LOOP until valid choice:
        INPUT choice
        IF choice == 1:
            RETURN port=8001, name="Server 1"
        ELSE IF choice == 2:
            RETURN port=8002, name="Server 2"
        ELSE IF choice == 3:
            IF client_id is odd:
                RETURN port=8001, name="Server 1 (auto)"
            ELSE:
                RETURN port=8002, name="Server 2 (auto)"
        ELSE:
            DISPLAY "Invalid choice"

END FUNCTION

CALL select_server() → SERVER_PORT, server_name

FUNCTION receive_messages(socket):
    LOOP forever:
        TRY:
            RECEIVE message from socket
            IF message is empty:
                EXIT LOOP
            DISPLAY message
            DISPLAY prompt (username>)
        CATCH error:
            DISPLAY "Disconnected from server"
            EXIT LOOP
END FUNCTION

FUNCTION main():
    DISPLAY "Starting client"
    DISPLAY "Connecting to server_name on SERVER_PORT"
    
    TRY:
        CREATE TCP socket
        CONNECT to localhost:SERVER_PORT
        DISPLAY "Connected!"
        
        SEND message: "username joined the chat"
        
        START new thread to run receive_messages(socket)
        
        DISPLAY "You can start chatting (type 'quit' to exit)"
        
        LOOP forever:
            INPUT user_message
            
            IF user_message == "quit":
                SEND "username left the chat"
                BREAK LOOP
            
            IF user_message not empty:
                SEND "username: user_message"
        
        CLOSE socket
        DISPLAY "Goodbye!"
    
    CATCH exception:
        DISPLAY "Error connecting to server"

END FUNCTION

IF this file is the main program:
    CALL main()

END