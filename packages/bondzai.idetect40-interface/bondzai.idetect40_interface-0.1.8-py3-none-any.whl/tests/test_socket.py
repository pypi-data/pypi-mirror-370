

import random
import time
import uuid
import pytest

from idetect40_interface.socket import SocketClient, SocketServer

def generate_random_data(string: bool = False):
    if string:
        data = str(uuid.uuid4())
    else:
        data = (random.sample(range(100), 20), random.choice([True, False]))
    return data

def encode(string: str):
    return string.encode()

def decode(b: bytes):
    return b.decode()

class DataRecorder():
    def __init__(self) -> None:
        self.data_list = []
        self.overflowed_list = []
        self.exception_list = []

    def append_data_list(self, data, overflowed):
        self.data_list += list(data)
        self.overflowed_list.append(overflowed)
    
    def set_exception(self, e):
        self.exception_list.append(e)
    
    def flush(self):
        self.data_list = []
        self.overflowed_list = []
        self.exception_list = []

class Test_socket_handler():
    port = 1502
    host = "localhost"
    data_recorder = DataRecorder()
    socket_server = None
    received_data = False

    @pytest.fixture(scope="class", autouse=True)
    def class_tear_up_and_down(self):
        Test_socket_handler.socket_server = SocketServer(Test_socket_handler.host, Test_socket_handler.port)
        Test_socket_handler.socket_server.open()
        Test_socket_handler.socket_server.start()
        
        yield
        
        Test_socket_handler.socket_server.close()

    def on_exception(self, exception):
        raise exception

    def on_read(self, content):
        self.received_data = content
        data, overflowed = content
        self.data_recorder.append_data_list(data, overflowed)
    
    def got_data(self, data):
        self.received_data = data
    
    def wait_for_data(self):
        counter = 0
        polling = 0.05
        while self.received_data is None and counter < int(1 / polling):
            time.sleep(polling)

    def test_socket_server_client(self):

        self.socket_server.on_read(self.got_data)
        
        socket_client = SocketClient()
        socket_client.connect(self.host, self.port)

        data = generate_random_data()

        # Send/ receive data
        self.received_data = None
        socket_client.send_data(data)
        self.wait_for_data()
        assert self.received_data == data

        # Send/ receive data
        self.received_data = None
        data = generate_random_data()
        socket_client.send_data(data)
        self.wait_for_data()
        assert self.received_data == data

        # Reconnect
        socket_client.stop()
        socket_client.connect(self.host, self.port)

        # Send/ receive data
        self.received_data = None
        data = generate_random_data()
        socket_client.send_data(data)
        self.wait_for_data()
        assert self.received_data == data

        # Send data from server
        self.received_data = None
        data = generate_random_data()
        self.socket_server.send_to_client(data)
        received_data = socket_client.read_data()
        assert received_data == data
        socket_client.stop()

    @pytest.mark.parametrize("interruption", [False, True])
    def test_server_listening(self, interruption):
        self.data_recorder.flush()
        socket_client = SocketClient()
        self.socket_server.on_read(self.on_read)
        socket_client.connect(self.host, self.port)
        data_recorder = DataRecorder()
        for _ in range(10):
            content = generate_random_data()
            data_recorder.append_data_list(*content)
            self.received_data = None
            socket_client.send_data(content)
            self.wait_for_data()
            if interruption:
                socket_client.stop()
                socket_client.connect(self.host, self.port)
        assert self.data_recorder.data_list == data_recorder.data_list
        assert self.data_recorder.overflowed_list == data_recorder.overflowed_list
        socket_client.stop()

    def test_change_encoding(self):

        self.socket_server.on_read(self.got_data)
        self.socket_server.set_decoding_function(decode)

        socket_client = SocketClient()
        socket_client.set_encoding_function(encode)
        socket_client.connect(self.host, self.port)

        data = generate_random_data(True)

        # Send/ receive data
        self.received_data = None
        socket_client.send_data(data)
        self.wait_for_data()
        assert  self.received_data == data

        socket_client.set_decoding_function(decode)
        self.socket_server.set_encoding_function(encode)
        
        # Send data from server
        data = generate_random_data(True)
        self.socket_server.send_to_client(data)
        time.sleep(0.2)
        received_data = socket_client.read_data()
        assert received_data == data
        
        socket_client.stop()
    
    def test_no_header(self):
        
        expected_msg_len = len(encode(generate_random_data(True)))

        self.socket_server.on_read(self.got_data)
        self.socket_server.set_decoding_function(decode)
        self.socket_server.set_header_remplacement(expected_msg_len)

        socket_client = SocketClient()
        socket_client.set_encoding_function(encode)
        socket_client.connect(self.host, self.port)

        socket_client.set_header_remplacement(expected_msg_len)

        data = generate_random_data(True)

        # Send/ receive data
        self.received_data = None
        socket_client.send_data(data)
        self.wait_for_data()
        assert self.received_data == data

        socket_client.set_decoding_function(decode)
        self.socket_server.set_encoding_function(encode)
        
        # Send data from server
        data = generate_random_data(True)
        self.socket_server.send_to_client(data)
        time.sleep(0.2)
        received_data = socket_client.read_data()
        assert received_data == data
        
        socket_client.stop()
