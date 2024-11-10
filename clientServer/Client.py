import threading
from socket import *
import os

# Define a function to handle a single client_get request
def handle_get_request(request):
    request = request.strip()
    line = request.split(" ")
    serverName = 'localhost'
    serverPort = 1200

    # Create socket and connect to server
    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.connect((serverName, serverPort))

    if line[0] == 'client_get':
        clientSocket.send(request.encode())

        received_message = ""
        while True:
            data = clientSocket.recv(4096).decode()
            if not data:
                break
            received_message += data

        if received_message.startswith("HTTP/1.1 404 Not Found"):
            print(f"File not found: {line[1]}")
        else:
            file_name = os.path.basename(line[1])
            print(f"Saving file: {file_name}")
            if file_name.endswith('.html') or file_name.endswith('.txt'):
                with open(file_name, 'w') as file:
                    content = received_message.split('\n')[2:-3]
                    file.write('\n'.join(content))
            elif file_name.endswith(('.jpg', '.png', '.jpeg')):
                print("Image received, further processing would be required here.")
        
    clientSocket.close()

# Read commands from a file and execute each in a separate thread
def process_commands(file_path):
    with open(file_path, 'r') as file:
        threads = []
        for request in file:
            # Start a new thread for each client_get command
            thread = threading.Thread(target=handle_get_request, args=(request,))
            thread.start()
            threads.append(thread)
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()

# Run the client commands from commands.txt
if __name__ == "__main__":
    process_commands("commands.txt")