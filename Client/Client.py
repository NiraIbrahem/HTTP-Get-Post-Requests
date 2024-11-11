from socket import*
import os
from PIL import Image
import time
import sys

serverName = sys.argv[1]
serverPort = int(sys.argv[2])
commands_path = sys.argv[3]
clientSocket = socket(AF_INET , SOCK_STREAM)
clientSocket.connect((serverName , serverPort))


with open(commands_path, 'r') as file:      
    for line in file:
        # read request from file
        line = line.strip()
        request = line.split(" ")

        '''
        serverName = request[2] 
        # get server port
        if(len(request)== 3):
            serverPort = 80
        else:
            serverPort = request[3]
        '''

        # send request
        clientSocket.send((line+'\n').encode())
        # handle get request
       
        if(request[0] == 'client_get'):
            # get response
            received_message = b""
            while True :
                data = clientSocket.recv(1024)
                if data.endswith(b'END_OF_FILE') :
                    received_message += data[:-1*len(b'END_OF_FILE')]
                    break 
                received_message += data

            # error
            if(received_message == b"HTTP/1.1 404 Not Found\\r\\n\n"):
                print(received_message.decode())

            # save files on device
            else:
                # print response
                print("HTTP/1.1 200 OK\\r\\n\n{")
                file_name = os.path.basename(request[1])
                if file_name.endswith('.txt') or file_name.endswith('.html') :
                    print(received_message.decode())
                else :
                    #print(received_message)
                    print('photo received')
                print("}\n\\r\\n\n")

                # open files
                with open(file_name, 'wb') as file:
                    # save file on device               
                    file.write(received_message)
                


        # handle post request
        elif(request[0] == 'client_post') :
            filename = request[1]
            # send request 
            # get html & txt & image file contents
            if filename.endswith('.html') or filename.endswith('.txt') or filename.endswith('.jpg') or filename.endswith('.png') or filename.endswith('.jpeg') :
                try :
                    with open(filename, 'rb') as file:
                        while chunk := file.read(1024) :
                            clientSocket.sendall(chunk)
                        clientSocket.sendall(b'END_OF_FILE')                     
                except :
                    clientSocket.sendall(b'Not-foundEND_OF_FILE')
            else:
                clientSocket.sendall(b'Not-foundEND_OF_FILE')

            received_message = clientSocket.recv(1024)
            print(received_message.decode())  


    print('end of requests') 
    #clientSocket.close()
