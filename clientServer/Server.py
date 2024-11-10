

import socket
import threading
import os
import time
from PIL import Image  # Ensure the pillow package is installed for image handling

# Server configuration
DEFAULT_PORT = 1200
KEEP_ALIVE_TIMEOUT = 5  # Timeout in seconds for keep-alive connections

# Handle a single client connection with keep-alive support
def handle_client(connection_socket, address):
    print(f"Connected to {address}")
    connection_socket.settimeout(KEEP_ALIVE_TIMEOUT)  # Set initial timeout for keep-alive

    while True:
        try:
            # Receive request from client
            message = connection_socket.recv(1024).decode()
            if not message:
                break

            # Parse command and generate response
            response = parse_command(message)
            connection_socket.sendall(response.encode())

            # Check if the client requested to close the connection
            if "Connection: close" in message:
                print("Client requested to close the connection.")
                break
            
            # Set the timeout for next keep-alive based on server load (or leave it constant)
            connection_socket.settimeout(KEEP_ALIVE_TIMEOUT)

        except socket.timeout:
            print("Connection timed out.")
            break  # Close if client is idle

    connection_socket.close()
    print(f"Closed connection to {address}")

# Start the server
def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('', DEFAULT_PORT))
    server_socket.listen(5)
    print(f"Server ready to receive on port {DEFAULT_PORT}.")

    while True:
        # Accept incoming client connections
        connection_socket, address = server_socket.accept()
        
        # Handle the client connection in a new thread to allow for concurrent connections
        client_thread = threading.Thread(target=handle_client, args=(connection_socket, address))
        client_thread.start()

# File handling and response functions
def getfile(pathfile , type):
    if type == 'text' or type == 'html':
        try :
            with open(pathfile, 'r') as file:
                content = file.read()
                content = "HTTP/1.1 200 OK\\r\\n " + "\n{\n" + content +"\n}\n\\r\\n\n"
                
        except :
            content = 'HTTP/1.1 404 Not Found\\r\\n\n '
    
    elif type == 'image' :
        try :
            image = Image.open(pathfile)
            image = image.convert('RGB')
            pixels = list(image.getdata())
            pixels.append(image.size)
            content = ' , '.join(map(str, pixels))
            content = "HTTP/1.1 200 OK\\r\\n " + "\n{\nImage size : " + "".join(map(str , image.size)) + "\nPixels [\n" + content + "\n]\n\\r\\n\n"
        except :
            content = 'HTTP/1.1 404 Not Found\\r\\n\n  '

    return content 

# post content of file given its path and type
def postfile(file , type):
    print('posting')

def parse_command (command) :
    request = command.split(" ")
    if(request[0] == 'client_get')  :
        # check file type
        filename = request[1]
        if filename.endswith('.html'):
            type =  "html"
        elif filename.endswith('.txt'):
            type = "text"
        elif filename.endswith('.jpg') or filename.endswith('.png') or filename.endswith('.jpeg'):
            type = 'image'
        else :
            return  'HTTP/1.1 404 Not Found\\r\\n\n  '

        return getfile(request[1] , type)
    
    elif(request[0] == 'client_post' ) :
        postfile(file , type)
    

if __name__ == "__main__":
    start_server()
