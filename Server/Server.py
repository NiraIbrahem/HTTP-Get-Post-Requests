from socket import*
import os
import sys
from threading import Thread
import time

# parse command
def parse_command (command , connectionSocket) :
    request = command[0].decode().split(" ")
    # handle get request
    if(request[0] == 'client_get')  :
        getfile(request[1] , connectionSocket)
    
    # handle post request
    elif(request[0] == 'client_post' ) :
        message = b'\n'.join(command[1:])
        postfile(request[1] , connectionSocket , message )


# get content of file given its path and type
def getfile(filename , connectionSocket):
    # get html & txt & image file contents
    if filename.endswith('.html') or filename.endswith('.txt') or filename.endswith('.jpg') or filename.endswith('.png') or filename.endswith('.jpeg') :
        try :
            with open(filename, 'rb') as file:
                content = file.read()                   
        except :
            content = 'HTTP/1.1 404 Not Found\\r\\n\n'.encode()
    else:
        content = 'HTTP/1.1 404 Not Found\\r\\n\n'.encode()
    content += b'END_OF_FILE'

    connectionSocket.sendall(content)


# post content of file given its path
def postfile(file , connectionSocket , file_content):
    # get file content
    if file_content.endswith(b'END_OF_FILE') :
        file_content = file_content[0:-1*len(b'END_OF_FILE')]
    else:
        while True :
            chunk = connectionSocket.recv(1024)
            if chunk.endswith(b'END_OF_FILE') :
                file_content += chunk[:-1*len(b'END_OF_FILE')]
                break 
            file_content += chunk

    if(file_content == b'Not-found'):
        connectionSocket.sendall('HTTP/1.1 404 Not Found\\r\\n\n'.encode())

    else :
        # send response then write file
        connectionSocket.sendall('HTTP/1.1 200 OK\\r\\n\n' .encode())
        file_name = os.path.basename(file)
        '''
        print("{")
        if file_name.endswith('.html') or file_name.endswith('.txt') :
            print(file_content.decode())
        else :
            print('photo received')
        print("}\n")
        '''
        # open file on device
        with open(file_name, 'wb') as file:
            file.write(file_content)


# Configurable parameters
DEFAULT_TIMEOUT_IDLE = 10  # seconds
DEFAULT_TIMEOUT_BUSY = 2  # seconds
MAX_ACTIVE_CONNECTIONS = 5  # Maximum number of active connections allowed
# Shared resource for active connections
active_connections = 0


def handle_client(connectionSocket, addr):
    global active_connections
    connectionSocket.settimeout(DEFAULT_TIMEOUT_IDLE)   # set timeout
    start_time = time.time() # starting time

    # When the timeout period is exceeded, a socket.timeout exception is raised.
    #The operation (e.g., connect(), recv(), send()) fails, and control is passed to the except block if one is defined.
    # connectivity issues, or the server is taking too long to respond.
    # When the timeout period is exceeded, a socket.timeout exception is raised.
    #The operation (e.g., connect(), recv(), send()) fails, and control is passed to the except block if one is defined.


    while True: # receive requests from same client
        try:
            message = connectionSocket.recv(1024).split(b'\n')
            # there is a new request
            if message != [b'']:
                # Your server should first printout the received command
                print(message[0].decode())
                parse_command(message, connectionSocket)

            # Check timeout based on the number of active connections
            if active_connections > MAX_ACTIVE_CONNECTIONS:
                connectionSocket.settimeout(DEFAULT_TIMEOUT_BUSY) # Server busy
            else:
                connectionSocket.settimeout(DEFAULT_TIMEOUT_IDLE) # server idle

            # If no data received for the timeout period, close the connection
            if time.time() - start_time > connectionSocket.gettimeout():
                print(f"Connection with {addr} timed out.")
                break
            
        except Exception as e:
            print(f"Error occurred: {e}")
            break

    # Close connection after all commands are handled or on timeout
    connectionSocket.close()
    active_connections -= 1
    print(f"Connection with {addr} closed.")




# creation server socket
serverPort = int(sys.argv[1])
serverSocket = socket(AF_INET , SOCK_STREAM)
serverSocket.bind(('' , serverPort))
# backlog : size of waiting queue , number of waiting connections before refusing new connections
serverSocket.listen(5)

# Accept new connection from incoming client
while True:
    connectionSocket, addr = serverSocket.accept()
    active_connections += 1
    print(f"New connection from {addr}. Active connections: {active_connections}")
    
    # Handle client connection in a separate thread
    thread = Thread(target = handle_client , args = (connectionSocket, addr))
    thread.start()
