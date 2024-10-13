import socket
import threading
import sys
import gzip
import io

def handle_client(conn, addr):
    with conn:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            request_data = data.decode().split('\r\n')
            response = b"HTTP/1.1 200 OK\r\n\r\n"
            print(request_data)
            # Handling /echo/
            if request_data[0].split(' ')[1].startswith('/echo/'):
                value = request_data[0].split(' ')[1].split('/echo/')[1]
                if request_data[2].startswith('Accept-Encoding'):
                    schemes = ''.join(request_data[2].split(',')).split(' ')
                    if 'gzip' in schemes:
                        out = io.BytesIO()
                        with gzip.GzipFile(fileobj=out, mode="w") as f:
                            f.write(value.encode())
                        compressed_value = out.getvalue()
                        response = f'HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Encoding: gzip\r\nContent-Length: {len(compressed_value)}\r\n\r\n'.encode() + compressed_value
                    else:
                        response = f'HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(value)}\r\n\r\n{value}'.encode()
                else:
                    response = f'HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(value)}\r\n\r\n{value}'.encode()
            # Handling /user-agent
            elif request_data[0].split(' ')[1].startswith('/user-agent'):
                agent_header = request_data[2].split(' ')[1]
                response = f'HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(agent_header)}\r\n\r\n{agent_header}'.encode()

            # Handling /files/{filename}
            elif request_data[0].split(' ')[1].startswith('/files/'):
                filename = request_data[0].split(' ')[1].split('/files/')[1]
                directory = sys.argv[2]
                if request_data[0].split(' ')[0] == 'POST':
                    text = request_data[5]
                    try:
                        with open(f"/{directory}/{filename}", "w") as f:
                            f.write(text)
                        response = b"HTTP/1.1 201 Created\r\n\r\n"
                    except FileNotFoundError:
                        response = b"HTTP/1.1 404 Not Found\r\n\r\n"
                else:
                    try:
                        with open(f"/{directory}/{filename}", "r") as f:
                            body = f.read()
                        response = f"HTTP/1.1 200 OK\r\nContent-Type: application/octet-stream\r\nContent-Length: {len(body)}\r\n\r\n{body}".encode()
                    except FileNotFoundError:
                        response = b"HTTP/1.1 404 Not Found\r\n\r\n"

            # Handle invalid routes
            elif request_data[0].split(' ')[1] != '/':
                response = b'HTTP/1.1 404 Not Found\r\n\r\n'

            conn.sendall(response)

def main():
    server_socket = socket.create_server(('localhost', 4221), reuse_port=True)
    # Accept clients in a loop and handle them in separate threads
    while True:
        conn, addr = server_socket.accept()
        # Start a new thread for each client connection
        client_thread = threading.Thread(target=handle_client, args=(conn, addr))
        client_thread.start()

if __name__ == "__main__":
    main()
