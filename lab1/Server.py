import socket
import threading
import os
import time
import datetime
from Helper import change_file_to_string_image  # Import helpers


BUFFERSIZE = 1024
MAXPENDING = 10
clients = 0
count_lock = threading.Lock()

# Helper function to handle file retrieval (mock function)
def change_file_to_string_image(file_path):
    try:
        with open(file_path, 'rb') as f:
            return f.read()
    except FileNotFoundError:
        return b""

# Function to calculate the response size
def calculate_size(data_size):
    base_header = "HTTP/1.1 200 OK\r\nContent-Length: \r\n\r\n"
    request_size = data_size + len(base_header)
    request_size_str_len = len(str(request_size))
    final_size = request_size + request_size_str_len + 1
    return final_size

# Parsing HTTP GET request to extract file path
def parse_http_get(http_request):
    parts = http_request.split(" ")
    if len(parts) >= 2:
        return parts[1]
    return ""

# Client handler function
def handle_client(client_sock):
    global clients
    buffer = bytearray(BUFFERSIZE)
    
    # Lock the client count and adjust timeout based on number of clients
    with count_lock:
        clients += 1
        time_per_client = max(1.0 / clients, 0.1)  # minimum 0.1 second timeout per client
        curr_time = time.time() + time_per_client

    try:
        while True:
            current_time = time.time()
            if current_time > curr_time:
                print(f"Time out for client {client_sock}")
                break

            num_bytes_rcvd = client_sock.recv_into(buffer, BUFFERSIZE)
            if num_bytes_rcvd <= 0:
                break  # Client disconnected or error occurred

            http_request = buffer[:num_bytes_rcvd].decode('utf-8')
            if http_request.startswith("GET"):
                file_path = parse_http_get(http_request)
                file_contents = change_file_to_string_image(file_path)

                if file_contents:
                    response = f"HTTP/1.1 200 OK\r\nContent-Length: {calculate_size(len(file_contents))}\r\n\r\n"
                else:
                    response = "HTTP/1.1 404 NOT FOUND\r\nContent-Length: 44\r\n\r\n"

                client_sock.send(response.encode())

                if file_contents:
                    client_sock.send(file_contents)
            
            else:
                print("Unsupported HTTP method")
                break
    
    except Exception as e:
        print(f"Error with client {client_sock}: {e}")
    
    finally:
        with count_lock:
            clients -= 1
        client_sock.close()

# Main server function
def start_server(host, port):
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_sock.bind((host, port))
    server_sock.listen(MAXPENDING)
    
    print(f"Server started on {host}:{port}")

    while True:
        try:
            client_sock, client_addr = server_sock.accept()
            print(f"Connection from {client_addr}")
            client_thread = threading.Thread(target=handle_client, args=(client_sock,))
            client_thread.daemon = True
            client_thread.start()
        except Exception as e:
            print(f"Error accepting connection: {e}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python server.py <Port>")
        sys.exit(1)

    port = int(sys.argv[1])
    start_server("0.0.0.0", port)
