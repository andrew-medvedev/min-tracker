__author__ = 'a.medvedev'

import socket

cluster = None
server_sock = None
sock = None


def start_cluster(cluster_representation):
    cluster = cluster_representation
    serve_port = None
    this = None
    for link in cluster_representation.links:
        if link.b.is_this:
            serve_port = link.on_port
            break
    for node in cluster_representation.nodes:
        if node.is_this:
            this = node
            break
    if serve_port is not None:
        server_sock = socket.socket()
        server_sock.bind((this.address, serve_port))
        server_sock.listen(1)


HOST = 'localhost'
PORT = 1488
BUF_SIZE = 16

sockets = []


def loop():
    while True:
        sock_loop()
        data_loop()


def sock_loop():
    try:
        conn_socket, address = sock.accept()
    except socket.error:
        return
    sockets.append((conn_socket, address))


def data_loop():
    for i, sock_and_address in enumerate(sockets):
        sock, address = sock_and_address
        try:
            bdata = sock.recv(BUF_SIZE)
        except socket.error:
            continue
        if len(bdata) == 0:
            print('closed connection from {}'.format(address))
            sockets.pop(i)
            sock.close()
        else:
            print('{}(len = {}) from {}'.format(bdata.decode('utf-8'), len(bdata), address))


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

sock.bind((HOST, PORT))
sock.listen(5)
sock.settimeout(1.0)

loop()