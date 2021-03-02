import socket
import os
import pathlib

DEFAULT_URL = # enter your default URL
IP = # should ne localhost
PORT = 80
REDIRECTION_DICTIONARY = {
    '\\forbidden.txt': '\\allowed.txt'
}
FORBIDDEN_LIST = []
SOCKET_TIMEOUT = 150


def get_file_data(filename):
    """ Get data from file """
    prepath = str(pathlib.Path().absolute()) + '\\'

    with open(prepath + filename, 'rb') as f:
        r = f.read()
        f.close()
    return r


def handle_client_request(resource, client_socket):
    """ Check the required resource, generate proper HTTP response and send to client"""
    # TO DO : add code that given a resource (URL and parameters) generates the proper response
    if resource == '' or resource == '\\' or resource == '/':
        url = DEFAULT_URL
    else:
        url = resource
    # TO DO: check if URL had been redirected, not available or other error code. For example:
    if url in REDIRECTION_DICTIONARY:
        # TO DO: send 302 redirection response
        response = "HTTP/1.0 302 - Moved Temporarily, please redirect to-" + REDIRECTION_DICTIONARY[url] + "\r\n"
        client_socket.send(response.encode())
        return
    if url in FORBIDDEN_LIST:
        client_socket.send("HTTP/1.0 403 - Forbidden\r\n".encode())
        return
    # TO DO: extract requested file tupe from URL (html, jpg etc)
    if 'html' in url:
        filetype = 'html'
    elif 'jpg' in url:
        filetype = 'jpg'
    elif 'js' in url:
        filetype = 'js'
    elif 'css' in url:
        filetype = 'css'
    else:
        filetype = 'else'
    if '\\pic' in url:
        data = get_file_data() # enter path to jpg file inside the brackets
        client_socket.send(data)
        return
    if '\\calculate-next' in url:
        urlist = url.split('?')
        if len(urlist) == 2:
            numl = urlist[1].split('=')
            if len(numl) == 2:
                if numl[1].isnumeric():
                    n = int(numl[1])
                    client_socket.send(str(n + 1).encode())
                    return
                elif numl[1] == 'hello':
                    client_socket.send("hola".encode())
                    return
                else:
                    client_socket.send("400 - Bad Request".encode())
                    return
    # TO DO: generate proper HTTP header
    if filetype == 'html':
        http_header = "HTTP/1.0 200 OK\r\n Content-Type: text/html; charset=utf-8\r\n"
    elif filetype == 'jpg':
        http_header = "HTTP/1.0 200 OK\r\n Content-Type: image/jpeg\r\n"  # TO DO: generate proper jpg header
    # TO DO: handle all other headers
    elif filetype == 'js':
        http_header = "HTTP/1.0 200 OK\r\n Content-Type: text/javascript; charset=UTF-8\r\n"
    elif filetype == 'css':
        http_header = "HTTP/1.0 200 OK\r\n Content-Type: text/css\r\n"
    else:  # unknown request
        client_socket.send("HTTP/1.0 500 - Internal Server Error\r\n".encode())
        return
    # TO DO: read the data from the file
    data = get_file_data(url)
    # http_response = http_header + data
    # print("line 71")
    # client_socket.send(http_header.encode())
    client_socket.send(data)


def validate_http_request(request):
    """ Check if request is a valid HTTP request and returns TRUE / FALSE and the requested URL """
    # TO DO: write function
    if "\r" not in request or "\n" not in request:
        print("Illegal request protocol, closing server")
        return False, ''
    words = request.split()
    if len(words) < 3:
        print("Sorry, wrong request, disconnecting")
        return False, ''
    req = words[0]
    if req != 'GET':
        print("Wrong request, closing server")
        return False, ''
    ver = words[2]
    if 'HTTP/' not in ver or '1.1' not in ver:
        print("Wrong app protocol or version, disconnecting")
        return False, ''
    path = words[1]
    chng = list(path)
    length = len(chng)
    i = 0
    while i < length:
        if chng[i] == '/':
            chng[i] = '\\'
        i += 1
    winpath = ''.join(chng)
    prepath = str(pathlib.Path().absolute())
    # if not os.listdir(winpath) and os.path.exists('C:\\' + winpath):
        # return False, '403'
    if '\\pic' in winpath:
        return True, winpath
    if '\\calculate-next' in winpath:
        return True, winpath
    if not os.path.isfile(prepath + winpath) and winpath != '\\' and winpath != '/':
        print("Path not found, disconnecting")
        return False, '404'

    return True, winpath


def handle_client(client_socket):
    """ Handles client requests: verifies client's requests are legal HTTP, calls function to handle the requests """
    print('Client connected')
    while True:
        # TO DO: insert code that receives client request
        client_request = client_socket.recv(1024)
        valid_http, resource = validate_http_request(client_request.decode())
        if valid_http:
            print('Got a valid HTTP request')
            handle_client_request(resource, client_socket)
            break
        else:
            print('Error: Not a valid HTTP request')
            if resource == '404':
                client_socket.send("404 (Not Found)\r\n".encode())
            elif resource == '403':
                client_socket.send("403 - forbidden\r\n".encode())
            break
    print('Closing connection')
    client_socket.close()


def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', PORT))
    server_socket.listen()
    print("Server listening on port {}".format(PORT))
    # (client_socket, client_address) = server_socket.accept()
    while True:
        (client_socket, client_address) = server_socket.accept()
        # data = client_socket.recv(1024).decode()
        print('New connection received')
        # client_socket.settimeout(SOCKET_TIMEOUT)
        handle_client(client_socket)
        """
        if data == b"":
            server_socket.close()
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.bind(('127.0.0.1', 80))
            server_socket.listen()
            print("Server listening")
            (client_socket, client_address) = server_socket.accept()
        
        if "\r" not in data or "\n" not in data:
            print("Illegal request protocol, closing server")
            break
        words = data.split()
        if len(words) != 3:
            print("Sorry, wrong request, disconnecting")
        req = words[0]
        if req != 'GET':
            print("Wrong request, closing server")
            break
        ver = words[2]
        if 'HTTP/' not in ver or '1.1' not in ver:
            print("Wrong app protocol or version, disconnecting")
            break
        path = words[1]
        chng = list[path]
        for char in chng:
            if char == '/':
                char = '\''
        winpath = ''.join(chng)
        client_socket.send(path.encode())
        
        if not os.path.isfile(winpath):
            client_socket.send("404 (not found)".encode())
            print("Path not found, disconnecting")
            break
        """


if __name__ == "__main__":
    # Call the main handler function
    main()






