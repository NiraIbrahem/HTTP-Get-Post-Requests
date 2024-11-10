from PIL import Image
import io
# get content of file given its path and type
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
    


from socket import*
# creation server socket
serverPort = 12000
serverSocket = socket(AF_INET , SOCK_STREAM)
serverSocket.bind(('' , serverPort))

while True :
    # Accept new connection from incoming client
    serverSocket.listen(1)
    # debug
    print('The server ready to recieve.')
    #delegate connection to worker thread/process  
    connectionSocket , addr = serverSocket.accept()

    # receieve HTTP/1.1 request , message = request command
    message = connectionSocket.recv(1024).decode()

    #print(message)
    response =  parse_command(message)
    connectionSocket.send(response.encode())
    connectionSocket.close()
