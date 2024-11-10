from socket import*
import subprocess
import io
import os


with open("commands.txt", 'r') as file:
    for request in file:
        request = request.strip()
        line = request.split(" ")
        serverName = line[2] 
        if(len(line)== 3):
            serverPort = 80

        else:
            serverPort = line[3]

        clientSocket = socket(AF_INET , SOCK_STREAM)
        clientSocket.connect((serverName , int(serverPort)))

        if(line[0] == 'client_get'):
            
            clientSocket.send(request.encode())

            received_message = ""
            while True:
                data = clientSocket.recv(4096).decode()
                received_message = received_message + data
                if not data:
                    break  # Exit loop if the connection is closed
                
                if(received_message == "HTTP/1.1 404 Not Found\\r\\n\n "):
                    print(received_message)

                else:
                    file_name = os.path.basename(line[1])
                    print(file_name)
                    #print(received_message)
                    
                    if file_name.endswith('.html'):
                        with open(file_name, 'w') as file:
                            html_content = received_message.split('\n')
                            print(html_content)
                            file.write('\n'.join(map(str,html_content[2:len(html_content)-3])))

                    elif file_name.endswith('.txt'):
                        with open(file_name, 'w') as file:
                            text_content = received_message.split('\n')
                            file.write('\n'.join(map(str,text_content[2:len(text_content)-3])))

                    elif file_name.endswith('.jpg') or file_name.endswith('.png') or file_name.endswith('.jpeg'):
                        type = 'image'
            clientSocket.close()
