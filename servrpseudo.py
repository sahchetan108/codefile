START
Read server_id from command line (default 1)

SET CLIENT_PORT, INTER_SERVER_PORT, PEER_PORT based on server_id

GLOBAL clients = []
GLOBAL peer_socket = None

FUNCTION broadcast_to_clients(msg):
    FOR each client IN copy of clients:
        TRY send msg to client
        IF send fails: remove client

FUNCTION handle_client(client_sock):
    LOOP:
        msg = receive from client_sock
        IF no msg: break
        print received
        broadcast_to_clients("[SERVER id] " + msg)
        IF peer_socket is set:
            TRY send "[SERVER id] " + msg to peer_socket
    remove client_sock from clients and close it

FUNCTION handle_peer_messages():
    LOOP:
        msg = receive from peer_socket
        IF no msg: break
        print from peer
        broadcast_to_clients(msg)

FUNCTION connect_to_peer():
    REPEAT until connected:
        TRY create socket and connect to ('localhost', PEER_PORT)
            set peer_socket
            start thread handle_peer_messages()
            break
        EXCEPT: wait 2 seconds and retry

FUNCTION start_inter_server():
    create listening socket on INTER_SERVER_PORT
    LOOP:
        peer_conn = accept incoming connection
        set peer_socket = peer_conn
        start thread handle_peer_messages() using peer_conn

MAIN:
    start thread start_inter_server()
    IF server_id == 2: wait 1 second
    start thread connect_to_peer()
    create client listening socket on CLIENT_PORT
    LOOP:
        client_sock = accept client
        append client_sock to clients
        start thread handle_client(client_sock)

END