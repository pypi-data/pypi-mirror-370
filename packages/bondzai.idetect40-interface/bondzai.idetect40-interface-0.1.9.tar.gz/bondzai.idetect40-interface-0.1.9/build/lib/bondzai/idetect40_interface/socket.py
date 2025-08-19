# coding: utf-8

import pickle
import socket
from threading import Thread
from typing import Any

import selectors
import traceback

import numpy as np


DEFAULT_HEADER_LEN = 4
DEFAULT_MAX_MSG_LEN = 4096


class RecvStatus:
    def __init__(self):
        self.expected = 0
        self.binary_data = []
        self.out_data = []

 # TODO : catch socket error

def encode_audio(data):
    audio_data, overflowed = data
    byte_array = bytearray(int(overflowed).to_bytes(1, "little"))
    byte_array.extend(audio_data.flatten().astype(np.float32).tobytes())
    return byte_array

class SocketServer():
    def __init__(self, host: str, port: int) -> None:
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self._selector = selectors.DefaultSelector()

        self._host = host
        self._port = port
        self.replace_header = None
        self._pck_max_len = DEFAULT_MAX_MSG_LEN

        self._on_msg = None

        self._run = False
        self.run_thread = None
        self.exception_function = None
        self._decode_func = pickle.loads
        self._encode_func = pickle.dumps
        self.out_data = []
    
    def on_exception(self, function: callable):
        """Define a callback if exception is raised within the service commands

        Args:
            function (callable): function with Exception as argument
        """
        self.exception_function = function

    def set_decoding_function(self, function: callable):
        """Set decoding function

        Args:
            func (callable): decoding function taking binary message as argument, returning data
        """
        self._decode_func = function
    
    def set_encoding_function(self, function: callable):
        """Set encoding function

        Args:
            func (callable): encoding function taking binary message as argument, returning data
        """
        self._encode_func = function
    
    def set_header_remplacement(self, size: int):
        """Set replacement to header by giving expected input size

        Args:
            size (int): expected input message size (in bytes)
        """
        self.replace_header = size

    def on_exit(self):
        self._run = False

    def on_read(self, callback):
        self._on_msg = callback

    def open(self) -> None:
        self._socket.bind((self._host, self._port))
        self._socket.listen()
        self._socket.setblocking(False)

        self._selector.register(self._socket, selectors.EVENT_READ, data=None)

    def close(self) -> None:
        self._run = False
        if self.run_thread.is_alive():
            self.run_thread.join()
        self._selector.close()
        self._socket.close()

    def new_client(self, socket: socket.socket) -> None:
        conn, addr = socket.accept()  # Should be ready to read

        conn.setblocking(False)
        events = selectors.EVENT_READ | selectors.EVENT_WRITE
        self._selector.register(conn, events, data=RecvStatus())

        # JDE: the connected event is sent only whe, the device is ready 

    def read_client(self, socket: socket.socket, status: RecvStatus):
        
        if status.expected == 0:
            if self.replace_header is None:
                length_data = []
                while len(length_data) < DEFAULT_HEADER_LEN:
                    try:
                        length_data += socket.recv(DEFAULT_HEADER_LEN - len(length_data))
                    except BlockingIOError as err:
                        if self.exception_function is not None:
                            self.exception_function(err)
                        return None
                    except ConnectionResetError as err:
                        if self.exception_function is not None:
                            self.exception_function(err)
                        raise err
                    
                    if len(length_data) == 0:
                        raise RuntimeError("Socket was closed")
                status.expected = int.from_bytes(length_data, "little")
            else:
                status.expected = self.replace_header
            status.binary_data = []

        while len(status.binary_data) < status.expected:
            try:
                status.binary_data += socket.recv(status.expected - len(status.binary_data))
            except BlockingIOError as err:
                if self.exception_function is not None:
                    self.exception_function(err)
                return None
            except ConnectionResetError as err:
                if self.exception_function is not None:
                    self.exception_function(err)
                raise err
           
            if len(status.binary_data) == 0:
                raise RuntimeError("Socket was closed")
        
        status.expected = 0

        return bytearray(status.binary_data.copy())
    
    def send_to_client(self, data: bytearray):
        byte_data = self._encode_func(data)
        self.out_data += [byte_data]

    def handle_connection(self, key, mask) -> None:
        sock = key.fileobj
        status: RecvStatus = key.data

        try:
            if mask & selectors.EVENT_READ:
                try:
                    msg = self.read_client(sock, status)
                    if msg:
                        if type(msg) == bytearray and self._on_msg:
                            self._on_msg(self._decode_func(msg) if self._decode_func else msg)
                except RuntimeError as e:
                    self._selector.unregister(sock)
                    if self.exception_function is not None:
                        self.exception_function(e)
                    sock.close()
                except ConnectionResetError as e:
                    if self.exception_function is not None:
                        self.exception_function(e)

            if mask & selectors.EVENT_WRITE:
                if len(self.out_data) > 0:
                    data = self.out_data[0]
                    l = len(data)
                    # log(f"Socket sending {l} bytes to device.")
                    if self.replace_header is None:
                        remaining = 4
                        while (remaining):
                            remaining -= sock.send(l.to_bytes(4, "little"))
                    remaining = l
                    while (remaining):
                        remaining -= sock.send(data)
                    self.out_data = self.out_data[1:]

        except ConnectionResetError as e:
            self._selector.unregister(sock)
            sock.close()
            if self.exception_function is not None:
                self.exception_function(e)

    def run(self) -> None:
        try:
            self._run = True
            while self._run:
                ev = self._selector.select(timeout=1)
                for key, mask in ev:
                    if key.data is None:
                        self.new_client(key.fileobj)
                    else:
                        self.handle_connection(key, mask)
        except KeyboardInterrupt:
            self._run = False
        except Exception:
            traceback.print_exc()

    def start(self):
        thread_name = f"{self.__class__.__name__}_connect"
        self.run_thread = Thread(name=thread_name, target=self.run, daemon=True)
        self.run_thread.start()


class SocketClient():
    """Socket client
    """
    def __init__(self) -> None:
        self.connection = None
        self._encode_func = pickle.dumps
        self._decode_func = pickle.loads
        self.replace_header = None
    
    def set_decoding_function(self, function: callable):
        """Set decoding function

        Args:
            func (callable): decoding function taking binary message as argument, returning data
        """
        self._decode_func = function
    
    def set_encoding_function(self, function: callable):
        """Set encoding function

        Args:
            func (callable): encoding function taking binary message as argument, returning data
        """
        self._encode_func = function
    
    def set_header_remplacement(self, size: int):
        """Set replacement to header by giving expected input size

        Args:
            size (int): expected input message size (in bytes)
        """
        self.replace_header = size
    
    def connect(self, host: str, port: int):
        """Connect to a certain server

        Args:
            host (str): server host name
            port (int): server port
        """
        # Bind the socket to a specific address and port
        server_address = (host, port)
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection.settimeout(1)
        self.connection.connect(server_address)


    def send_data(self, data: Any, encoding: callable = None):
        """Send data through socket, takes care of encoding

        Args:
            data (Any): Any type of data
            encoding (callable, optional): If given, encode data to bytarray using this function. Defaults to pickle.dumps.
        """
        if self.connection is not None:
            if encoding is None:
                encoding = self._encode_func
            encoded_data = encoding(data)
            if self.replace_header is None:
                encoded_data = len(encoded_data).to_bytes(4, "little") + encoded_data
            self.connection.sendall(encoded_data)
        
    def read_data(self) -> Any:
        """Read data from socket server

        Returns:
            Any: decoded data
        """
        if self.replace_header is None:
            length_data = []
            while len(length_data) < DEFAULT_HEADER_LEN:
                try:
                    length_data += self.connection.recv(DEFAULT_HEADER_LEN - len(length_data))
                except BlockingIOError as err:
                    if self.exception_function is not None:
                        self.exception_function(err)
                    return None
                except ConnectionResetError as err:
                    if self.exception_function is not None:
                        self.exception_function(err)
                    raise err
                
                if len(length_data) == 0:
                    raise RuntimeError("Socket was closed")

                expected_size = int.from_bytes(length_data, "little")
        else:
            expected_size = self.replace_header
        binary_data = []
        while len(binary_data) < expected_size:
            try:
                binary_data += self.connection.recv(expected_size - len(binary_data))
            except BlockingIOError as err:
                if self.exception_function is not None:
                    self.exception_function(err)
                return None
            except ConnectionResetError as err:
                if self.exception_function is not None:
                    self.exception_function(err)
                raise err
           
            if len(binary_data) == 0:
                raise RuntimeError("Socket was closed")
        byte_data = bytearray(binary_data.copy())
        data = self._decode_func(byte_data)

        return data
    
    def stop(self):
        """Stop socket instance
        """
        # Clean up the connection
        if self.connection is not None:
            self.connection.close()
            self.connection = None
