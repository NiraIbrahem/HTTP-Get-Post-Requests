import socket
import os
import sys
import struct
import io
from Helper import change_file_to_string_image

BUFFERSIZE = 1024

def calculate_size(data_size, path_size):
    request_size = data_size + 44 + path_size
    request_size_no_of_digits = len(str(request_size))
    request_size_after_adding_no_of_digits = len(str(request_size + request_size_no_of_digits))
    if request_size_after_adding_no_of_digits != request_size_no_of_digits:
        request_size += (request_size_no_of_digits + 1)
    else:
        request_size += request_size_no_of_digits
    return request_size

# def extract_filename(request):
#     # This is a placeholder function for filename extraction logic.
#     # You need to implement how the filename is extracted from the request
#     return "output_file.txt"
def extract_filename(file_path):
    return os.path.basename(file_path)

# def extract_content_size(buffer):
#     # Placeholder function to extract content size from the header of the HTTP response
#     return 1024  # Example, replace with actual content size extraction logic

def extract_content_size(http_response):
    content_size = 0
    pos = http_response.find("content-length: ")
    if pos != -1:
        pos = http_response.find("\r\n", pos)
        if pos != -1:
            pos = http_response.find("0123456789", pos)
            if pos != -1:
                content_size = int(http_response[pos:])
    return content_size

def save_binary_data(file_data, filename):
    with open(filename, 'wb') as f:
        f.write(file_data)

def change_file_to_string_image(path):
    try:
        with open(path, 'rb') as f:
            return f.read().decode('latin1')  # Or appropriate encoding if needed
    except Exception as e:
        print("File not found:", e)
        return ""

def handle_get(path, sock):
    request = f"GET {path} HTTP/1.1"
    response = ''
    try:
        sock.send(request.encode())

        total_bytes_rcvd = 0
        total_size = -1
        first_time = True
        data_begun_sending = False
        file = bytearray()

        while True:
            buffer = sock.recv(BUFFERSIZE)
            if len(buffer) < 1:
                break  # Connection closed by server

            total_bytes_rcvd += len(buffer)

            if first_time:
                header_end_pos = buffer.find(b"\r\n\r\n")
                if header_end_pos != -1:
                    data_begun_sending = True
                    response += buffer[:header_end_pos + 4].decode()
                    file.extend(buffer[header_end_pos + 4:])
                else:
                    response += buffer.decode()

                total_size = extract_content_size(buffer)
                if total_size == -1:
                    print("Error: file size not received")
                    return

                first_time = False
                if b"HTTP/1.1 404 NOT FOUND" in response.encode():
                    break
            elif data_begun_sending:
                file.extend(buffer)

            if total_size <= total_bytes_rcvd:
                break

        print(response)
        if b"HTTP/1.1 404 NOT FOUND" not in response.encode():
            save_binary_data(file, extract_filename(request))
        if total_bytes_rcvd == 0:
            print("Receiving file: connection closed prematurely")
    except Exception as e:
        print(f"Error during GET request: {e}")

def handle_post(path, sock):
    data = change_file_to_string_image(path)
    if not data:
        print("File Not found in client")
        return

    request = f"POST {path} HTTP/1.1\r\nContent-Length: {calculate_size(len(data), len(path))}\r\n\r\n"
    sock.send(request.encode())

    buffer = sock.recv(BUFFERSIZE)
    print(buffer.decode())

    while data:
        bytes_to_send = min(BUFFERSIZE, len(data))
        buf = data[:bytes_to_send]
        sock.send(buf.encode())
        data = data[bytes_to_send:]

def handle_response(path, sock, get):
    if get:
        handle_get(path, sock)
    else:
        handle_post(path, sock)

def main():
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("Usage: <ServerDir Address> [<ServerDir Port>]")
        sys.exit(1)

    host_name = sys.argv[1]
    serv_port = int(sys.argv[2]) if len(sys.argv) == 3 else 7

    # Create socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((host_name, serv_port))
    except socket.error as e:
        print(f"Connection failed: {e}")
        sys.exit(1)

    # Read the command file
    cwd = os.getcwd()
    filepath = os.path.join(cwd, "requests.txt")

    try:
        with open(filepath, 'r') as input_file:
            for line in input_file:
                tokens = line.split()
                if len(tokens) < 2:
                    continue

                type_of_request, path = tokens[0], tokens[1]

                if type_of_request == "client_get":
                    handle_response(path, sock, True)
                elif type_of_request == "client_post":
                    handle_response(path, sock, False)
    except FileNotFoundError:
        print("Error opening file.")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)

    sock.close()

if __name__ == "__main__":
    main()
