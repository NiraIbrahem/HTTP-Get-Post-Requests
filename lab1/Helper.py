import os

DEFAULT_TIME = 5 * 1000  # 5 seconds
MIN_TIME = 1000

def die_with_user_message(msg, detail):
    print(f"{msg}: {detail}", file=sys.stderr)
    exit(1)

def die_with_system_message(msg):
    print(f"System error: {msg}", file=sys.stderr)
    exit(1)

def change_file_to_string(file_path):
    try:
        with open(file_path, 'rb') as infile:
            content = infile.read().decode('utf-8')
            return content
    except Exception as e:
        die_with_system_message(f"Error opening file: {e}")

def change_file_to_string_image(image_file_path):
    try:
        with open(image_file_path, 'rb') as image_file:
            return image_file.read()
    except Exception as e:
        print(f"Error opening image file: {image_file_path}")
        return None


def save_binary_data(data, file_name):
    try:
        current_directory = os.getcwd()
        full_path = os.path.join(current_directory, file_name)
        with open(full_path, 'wb') as outfile:
            outfile.write(data)
    except Exception as e:
        die_with_system_message(f"Error opening file for writing: {e}")

def save_string(content, file_name):
    try:
        with open(file_name, 'w', encoding='utf-8') as outfile:
            outfile.write(content)
    except Exception as e:
        print(f"Error opening file for writing: {file_name}", file=sys.stderr)

def extract_filename(file_path):
    return os.path.basename(file_path)

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

def extract_file_name(http_request):
    method_pos = http_request.find(" ")
    if method_pos == -1:
        return ""
    
    method = http_request[:method_pos]
    start_pos = method_pos + 1
    end_pos = http_request.find(" ", start_pos)
    
    if start_pos != -1 and end_pos != -1:
        file_path = http_request[start_pos:end_pos]
        return os.path.basename(file_path)
    
    return ""
