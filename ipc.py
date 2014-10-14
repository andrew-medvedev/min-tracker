__author__ = 'a.medvedev'

import socket
import utils
import constants
import json

# Глобальные переменные модуля
pass_phrase = None
pass_phrase_len = None
sockets_backlog = None
agents = None
agents_tree = None
server_sock = None
procedures = None
step = None


class BacklogSocketWrapper():
    def __init__(self, sock, address):
        self.socket = sock
        self.address = address
        self.buffer = ''
        self.add_ts = utils.timestamp()


class Connection():
    def __init__(self, host, outer, port=None):
        self.host = host
        self.outer = outer
        self.port = port
        self.socket = None
        self.in_buffer = bytearray()
        self.current_pack_len = None
        self.last_heartbeat_ts = utils.timestamp()


def start_cluster(cluster_representation, node_procedures):
    global pass_phrase, \
        pass_phrase_len, \
        agents, \
        agents_tree, \
        server_sock, \
        procedures, \
        step, \
        sockets_backlog

    # Присваиваем всякое говно
    pass_phrase = cluster_representation.pass_phrase
    pass_phrase_len = len(cluster_representation.pass_phrase)
    procedures = node_procedures
    sockets_backlog = []
    agents = []
    agents_tree = {}
    serve_port = None
    this = None

    # Если есть входящие соединения - запускаем сервак
    for link in cluster_representation.links:
        if link.b.is_this:
            # Находим свой порт для приема
            serve_port = link.on_port

    for node in cluster_representation.nodes:
        if node.is_this:
            this = node
            break
    if serve_port is not None:
        server_sock = socket.socket()
        server_sock.bind((this.address, serve_port))
        server_sock.listen(1)
        server_sock.setblocking(False)
        step = _loop_with_serve
    else:
        step = _loop_no_serve

    # Создаем всех агентов
    for link in cluster_representation.links:
        con = None
        if link.a == this:
            con = Connection(link.b.address, True, link.on_port)
            con.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        elif link.b == this:
            con = Connection(link.a.address, False)
        if con is not None:
            agents.append(con)
            agents_tree[con.host] = con


def _serve_loop():
    try:
        conn_socket, address = server_sock.accept()
        if address[0] in agents_tree:
            conn_socket.setblocking(False)
            sockets_backlog.append(BacklogSocketWrapper(conn_socket, address))
        else:
            conn_socket.close()
    except socket.error:
        pass


def _backlog_loop():
    for i, sock_wrapper in enumerate(sockets_backlog):
        if utils.timestamp() - sock_wrapper.add_ts > constants.IPC_TIME_TO_REPRESENT_MS:
            sock_wrapper.socket.close()
            sockets_backlog.pop(i)
            continue
        try:
            bdata = sock_wrapper.socket.recv(pass_phrase_len)
            if len(bdata) == 0:
                sock_wrapper.socket.close()
                sockets_backlog.pop(i)
                continue
            else:
                sock_wrapper.buffer += bdata.decode('utf-8')
                if len(sock_wrapper.buffer) >= pass_phrase_len:
                    if sock_wrapper.buffer[:pass_phrase_len] == pass_phrase:
                        _push_socket_to_connection(sock_wrapper.socket, sock_wrapper.address)
                    else:
                        sock_wrapper.socket.close()
                        sockets_backlog.pop(i)
        except socket.error:
            pass


def _push_socket_to_connection(sock, from_address):
    con = agents_tree[from_address]
    if not con.outer:
        con.socket = sock
        con.last_heartbeat_ts = utils.timestamp()


def _agents_loop():
    for agent in agents:
        if agent.socket is not None:
            # Сначала отыгрываем вариант, при котором агент имеет открытое соединение

            # Проверяем простой сокета
            if utils.timestamp() - agent.last_heartbeat_ts() >= constants.IPC_NODE_MAX_IDLE_MS:
                _clear_agent_sock(agent)
                continue
            # Считываем из буфера сокета
            try:
                bdata = agent.socket.recv(constants.IPC_BUFFER_SIZE)
                if len(bdata) == 0:
                    _clear_agent_sock(agent)
                else:
                    if agent.current_pack_len is None:
                        agent.current_pack_len = int.from_bytes(bdata[:3], byteorder='big')
                        agent.in_buffer.extend(bdata[2:])
                    else:
                        agent.in_buffer.extend(bdata)
                    if len(agent.in_buffer) >= agent.current_pack_len:
                        _read_message(agent)
                    agent.last_heartbeat_ts = utils.timestamp()
            except socket.error:
                continue
        else:
            # Если у агента нет соединения
            if agent.outer:
                # Бесконечно стучимся на другой конец провода
                pass


def _clear_agent_sock(agent):
    if agent.socket is not None:
        agent.socket.close()
        agent.socket = None
    agent.in_buffer.clear()
    agent.current_pack_len = None


def _read_message(from_agent):
    message = from_agent.in_buffer[:from_agent.current_pack_len + 1].decode('utf-8')
    from_agent.in_buffer = from_agent.in_buffer[from_agent.current_pack_len + 1:]
    from_agent.current_pack_len = None

    decoded_m = _decode_message(message)
    decoded_m['from'] = from_agent
    procedures[decoded_m['f']](**decoded_m)


def _decode_message(m):
    decoded = json.loads(m)
    return decoded


# Дальше там фигня идет


def _data_loop():
    for i, socket_wrapper in enumerate(sockets):
        try:
            bdata = socket_wrapper.socket.recv(constants.IPC_BUFFER_SIZE)
            socket_wrapper.last_heartbeat = utils.timestamp()
        except socket.error:
            continue
        if len(bdata) == 0:
            socket_wrapper.socket.close()
            sockets.pop(i)
        else:
            if socket_wrapper.current_pack_len is None:
                socket_wrapper.current_pack_len = int.from_bytes(bdata[:3], byteorder='big')
                socket_wrapper.in_buffer.extend(bdata[2:])
            else:
                socket_wrapper.in_buffer.extend(bdata)
            if len(socket_wrapper.in_buffer) >= socket_wrapper.current_pack_len:
                _read_message(socket_wrapper)
            socket_wrapper.last_heartbeat_ts = utils.timestamp()


def _loop_rep():
    pass





def _present_rpc(**kwargs):
    if kwargs['pass'] == pass_phrase:
        from_s = kwargs['from']
        from_s.presented = True
        for node in cluster.nodes:
            if node.name == kwargs['name']:

                return



def _loop_with_serve():
    _sock_loop()
    _data_loop()
    _loop_rep()


def _loop_no_serve():
    _data_loop()
    _loop_rep()