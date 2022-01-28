"""
Classes used for TCP communication. They handle checking the state and processing the data. The client and server act in the following way:

Client:
1) Connect to server
2) Generate request
3) Send to server
4) Wait for response
5) Process response
6) Go to 2

Server:
1) Create connection and listen
2) Accept connection
3) Wait for request
4) Process request
5) Perform action with data
6) Generate response
7) Send response
8) Go to 3

The code for this library was adapted from the Real Python tutorial on sockets.
"Socket Programming in Python (Guide)" by Nathan Jennings
URL: https://realpython.com/python-sockets/
"""

# TODO:
# Add a way to define the request and response messages in a separate class to be accessed in the "create_message" function. Then the user does not need to alter this library but rather create a new module following a set of rules to define the messages to be used for the server and client. Set defaults in this code, but check for redefinitions of the json header variables in the user-defined class. Let them set the content and be sure to have them include a description of the message content structure. Try to import the "tcp_impl" library for "TCPImpl" class. If it cannot import, use the defaults. Set a variable "implemenation_exists" to check throughout the code if successful.
# Make the "process_loop" function pass the "self.content" variable to a "perform_action" function that is defined by the user. If the user has not defined it, then skip to the next message function.
# Update the encoding parameter to check ithe individual message content_encoding variable to see if it is "None", if so use the default self.encoding variable.
# Write the documentation for the library at the top of the file. Follow the Numpy standard you used for the Pepper VR coding library.
"""
Make a "Rate" class with methods:
_remaining(curr_time) : calculates the time to sleep in order to maintain Hz
sleep() : sleep the remaining time to keep the loop running at Hz

"""

import socket
import json
import struct
import atexit
import random

#==============================================================================#
# Read Implementation
#==============================================================================#
try:
    from tcp_impl import TCPImpl
except ImportError as e:
    implementation_imported = False
    print(e)
    print("[INFO]: No TCP message implementation file. Using default values for messages. Must define the messages and functions found in 'tcp_impl.py'")
else:
    implementation_imported = True


class TCP:
    def __init__(self, sock=None, receive_size=4096):
        self.socket = sock
        self.local_address = self.socket.getsockname()
        self.local_host = self.local_address[0]
        self.local_port = self.local_address[1]
        self.remote_address = self.socket.getpeername()
        self.remote_host = self.remote_address[0]
        self.remote_port = self.remote_address[1]
        self.receive_size = receive_size
        self._recv_buffer = b''
        self._send_buffer = b''
        self._json_header_len = None
        self.json_header = None
        self.content = None

        #======================================================================#
        # Create Messages
        #======================================================================#
        self.tcp_implementation = TCPImpl()

        # Closes the socket if the python script closes
        atexit.register(self.close)

    def read(self):
        """ Reads raw data bytes from the socket. """
        try:
            data = self.socket.recv(self.receive_size)
        except BlockingIOError:
            pass
        else:
            if data:
                self._recv_buffer += data
            else:
                raise ConnectionClosedError('Peer closed at {0}:{1}'.format(self.remote_host, self.remote_port))

    def write(self):
        """ Sends data in buffer.

        Returns
        -------
        True : if message is fully sent
        False : if data is still in the buffer
        """
        if self._send_buffer:
            try:
                sent = self.socket.send(self._send_buffer)
            except BlockingIOError:
                return False
            else:
                self._send_buffer = self._send_buffer[sent:]
                if sent and not self._send_buffer:
                    # Message fully sent
                    return True
                else:
                    # Message not fully sent yet
                    return False

    def _json_encode(self, obj, encoding):
        """ Encode dictionary into JSON byte array.

        Parameters
        ----------
        obj : dict
            The object to be converted into a JSON byte array.
        encoding : str
            The encoding type for the JSON text. Most common is 'utf-8'.

        Returns
        -------
        Array of bytes containing the JSON string encoded as specified.
        """
        return json.dumps(obj, ensure_ascii=False).encode(encoding)

    def _json_decode(self, json_bytes, encoding):
        """ Decode a dictionary from a JSON byte array.

        Parameters
        ----------
        json_bytes : byte array
            The data bytes to be converted into a Python variables.
        encoding : str
            The encoding type for the JSON text. Most common is 'utf-8'.
        """
        return json.loads(json_bytes.decode(encoding))

    def _int_to_bytes(self, size):
        """ Convert Int into two raw bytes.

        Parameters
        ----------
        size : int
            The size of the JSON header array.
        """
        return struct.pack('>H', size)

    def _bytes_to_int(self, bytes):
        """ Convert two bytes into an unsigned Int.

        Parameters
        ----------
        bytes : byte array
            The pair of bytes to be converted into an Int (JSON header size).
        """
        return struct.unpack('>H', bytes)[0]

    def process_protocol_header(self):
        """ Creates the protocol header bytes. """
        header_length = 2
        if len(self._recv_buffer) >= header_length:
            self._json_header_len = self._bytes_to_int(self._recv_buffer[:header_length])
            self._recv_buffer = self._recv_buffer[header_length:]

    def process_json_header(self):
        """ Creates the JSON header bytes. """
        header_length = self._json_header_len
        if (len(self._recv_buffer)) >= header_length:
            self.json_header = self._json_decode(self._recv_buffer[:header_length], 'utf-8')
            self._recv_buffer = self._recv_buffer[header_length:]
            for required_header in ['is_big_endian', 'content-type', 'content-encoding', 'content-length']:
                if required_header not in self.json_header:
                    raise ValueError('Missing required header "{0}".'.format(required_header))

    def process_message(self):
        """ Converts the receive buffer bytes into data. """
        if self._json_header_len is None:
            self.process_protocol_header()

        if self._json_header_len is not None:
            if self.json_header is None:
                self.process_json_header()

        if self.json_header:
            self.process_content()

    def read_message(self):
        while self.content is None:
            self.read()
            self.process_message()

    def write_message(self):
        self.create_message()
        successfully_sent = False
        while not successfully_sent:
            successfully_sent = self.write()

    def close(self):
        print('Closing connection:\n\t {0}:{1} --> {2}:{3}'.format(self.local_host, self.local_port, self.remote_host, self.remote_port))
        self.socket.close()

    #==========================================================================#
    # Abstract Methods
    #==========================================================================#
    def process_content(self):
        raise NotImplementedError()

    def create_message(self):
        raise NotImplementedError()

class TCPServer(TCP):
    def __init__(self, host='127.0.0.1', port=65432):
        #======================================================================#
        # Create Socket
        #======================================================================#
        # Server address
        self.server_host = host
        self.server_port = port
        self.server_address = (self.server_host, self.server_port)

        # Create listening socket
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        atexit.register(self.close_server)

        # Bind and listen
        print('Establishing TCP server on {0}:{1}'.format(self.server_host, self.server_port))
        self.server_socket.bind(self.server_address)
        self.server_socket.listen()

        print('Waiting for connection...')
        self.wait_for_connection()

    def wait_for_connection(self):
        self.connection, self.connection_address = self.server_socket.accept()
        print('Server connected to {0}:{1}'.format(self.connection_address[0], self.connection_address[1]))

        # Initialize TCP connection socket object
        super().__init__(sock=self.connection)

    #==========================================================================#
    # Define Response Message
    #==========================================================================#
    def create_message(self):
        """ Generate the Response message bytes. """
        # Declare these parameters here for external scope from the "if" block
        is_big_endian, content_type, encoding, content = None, None, None, None

        # Define JSON header parameters
        if implementation_imported:
            is_big_endian = self.tcp_implementation.response.is_big_endian
            content_type = self.tcp_implementation.response.content_type
            encoding = self.tcp_implementation.response.content_encoding
            content = self.tcp_implementation.response.get_content()
        else: # DEFAULTS
            is_big_endian = False
            content_type = 'text/json'
            encoding = self.encoding
            content = {'content': 'content'}

        # Encode response content
        content_bytes = self._json_encode(content, encoding)

        # Create JSON header
        json_header = {
            'is_big_endian': is_big_endian,
            'content-type': content_type,
            'content-encoding': encoding,
            'content-length': len(content_bytes)
        }

        json_header_bytes = self._json_encode(json_header, encoding)

        # Create protocol header
        protocol_header_bytes = self._int_to_bytes(len(json_header_bytes))

        self._send_buffer = protocol_header_bytes + json_header_bytes + content_bytes

    #==========================================================================#
    # Define Request Interpretation
    #==========================================================================#
    def process_content(self):
        """ Process the Request content.

        Processes the content bytes and performs the desired action with them.
        """
        content_length = self.json_header['content-length']
        if len(self._recv_buffer) >= content_length:
            self.content = self._json_decode(self._recv_buffer[:content_length], self.json_header['content-encoding'])
            self._recv_buffer = self._recv_buffer[content_length:]

    #==========================================================================#
    # Define State Flow
    #==========================================================================#
    def process_loop(self):
        while True:
            try:
                # Read request data until you have a full message
                self.read_message()

                # Service
                response_content = self.tcp_implementation.perform_service(self.content)
                self.tcp_implementation.response.set_content(response_content)

                # Send back response
                self.write_message()

                # Reset variables and start process over
                self._send_buffer = b''
                self._json_header_len = None
                self.json_header = None
                self.content = None
            except KeyboardInterrupt:
                break
            except ConnectionClosedError as err:
                print('[Connection closed]: {0}'.format(err))
                self.reset()
                print('Waiting for new connection...')
                self.wait_for_connection()

    def reset(self):
        """ Resets the variables and waits for re-connection. """
        self._recv_buffer = b''
        self._send_buffer = b''
        self._json_header_len = None
        self.json_header = None
        self.content = None

    def close_server(self):
        # Close the server socket
        print('Closing server at {0}:{1}'.format(self.server_host, self.server_port))
        self.server_socket.close()

class TCPClient(TCP):
    def __init__(self, remote_host='127.0.0.1', remote_port=65432):
        #======================================================================#
        # Create Socket
        #======================================================================#
        # Create client socket and connect to server (TCP, IPv4)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print('Connecting to server at {0}:{1}'.format(remote_host, remote_port))
        self.socket.connect((remote_host, remote_port))

        # Initialize TCP connection socket object
        super().__init__(self.socket)
        print('Local socket at {0}:{1}'.format(self.local_host, self.local_port))

    #==========================================================================#
    # Define Request Message
    #==========================================================================#
    def create_message(self):
        """ Generate the Request message bytes. """
        # Declare these parameters here for external scope from the "if" block
        is_big_endian, content_type, encoding, content = None, None, None, None

        # Define JSON header parameters
        if implementation_imported:
            is_big_endian = self.tcp_implementation.request.is_big_endian
            content_type = self.tcp_implementation.request.content_type
            encoding = self.tcp_implementation.request.content_encoding
            content = self.tcp_implementation.request.get_content()
        else: # DEFAULTS
            is_big_endian = False
            content_type = 'text/json'
            encoding = self.encoding
            content = {'content': 'content'}

        # Encode response content
        content_bytes = self._json_encode(content, encoding)

        # Create JSON header
        json_header = {
            'is_big_endian': is_big_endian,
            'content-type': content_type,
            'content-encoding': encoding,
            'content-length': len(content_bytes)
        }

        json_header_bytes = self._json_encode(json_header, encoding)

        # Create protocol header
        protocol_header_bytes = self._int_to_bytes(len(json_header_bytes))

        self._send_buffer = protocol_header_bytes + json_header_bytes + content_bytes

    #==========================================================================#
    # Define Response Interpretation
    #==========================================================================#
    def process_content(self):
        """ Process the Response content.

        Processes the content bytes and performs the desired action with them.
        The expected message should be a dictionary with the following
        structure:
        """
        content_length = self.json_header['content-length']
        if len(self._recv_buffer) >= content_length:
            self.content = self._json_decode(self._recv_buffer[:content_length], self.json_header['content-encoding'])
            self._recv_buffer = self._recv_buffer[content_length:]

    #==========================================================================#
    # Define State Flow
    #==========================================================================#
    def service_request(self, request_content):
        self.tcp_implementation.request.set_content(request_content)
        self.write_message()
        self.read_message()
        return self.content

    def process_loop(self):
        self.tcp_implementation.client_loop(self.service_request)

#==============================================================================#
# Exception Classes
#==============================================================================#
class TCPError(Exception):
    """ Base class for TCP exceptions. """
    pass

class ConnectionClosedError(TCPError):
    """ Exception raised when a connection is lost.

    Attributes
    ----------
    message : str
        The error message to raise.
    """
    def __init__(self, message):
        self.message = message
