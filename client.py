import socket
import threading

PORT = 53210
SERVER = "127.0.0.1"
addr = (SERVER, PORT)
DISCONNECT_MSG = "!DISCONNECT"
FORMAT = 'iso-8859-1'
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(addr)
connected = True


def start():
    while connected:
        msg = client.recv(100000000).decode(FORMAT)
        print(f"[{addr[0]}] {msg}")


def send(msg):
    message = msg.encode(FORMAT)
    print(message)
    client.send(message)


def inputting_msg():
    global connected
    while connected:
        msg = input()
        if msg == DISCONNECT_MSG:
            print("[DISCONNECTING] disconnecting from the server...")
            connected = False
        else:
            send(msg)

send("GET /index HTTP/1.1\nHost: 127.0.0.1\nAccept: text/html\nUser-Agent: Mozilla/5.0")
thread = threading.Thread(target=start, args=())
thread.start()
inputting_msg()
send(DISCONNECT_MSG)