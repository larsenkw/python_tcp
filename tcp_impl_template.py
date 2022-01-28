""" Defines the Request and Response structures for the 'libtcp' module.

Module for defining the Request and Response messages used by the 'libtcp'
module. Also defines the process functions used by either the Server or the
Client.

Typically only one implementation of this class will be used, for either the
Server or the Client. In that case, both the Request and the Response need to be
defined, however, only the relevant function needs to be defined. If using a
Server, the user will define 'perform_service', if a Client, 'client_loop'. If
the user is using both a Python Server and Client from this code, both functions
can be defined.
"""

#==============================================================================#
#------------------- Instructions for Editing this Template -------------------#
#==============================================================================#
# This file is a module template for defining the message structures and actions
# performed by the Server or the Client. The developer should define the
# structures and fill in the actions performed by the functions.
#
# The developer should edit the sections between the lines denoted by:
#    vvvvv USER EDIT vvvvv
#    ^^^^^ USER EDIT ^^^^^
#
# Once edits are complete there are two options for applying them to the
# 'libtcp.py' file:
#    1) Remove '_template' from this file's name.
#    OR
#    2) Replace 'tcp_impl' with the name of the file (without '.py', this is the
#       module name) in the line 'from tcp_impl import TCPImpl' found in
#       'libtcp.py': 'from [module_name] import TCPImpl'
#==============================================================================#
#------------------- Instructions for Editing this Template -------------------#
#==============================================================================#


#==============================================================================#
# Define Message Structures
#==============================================================================#
"""
The content for the request and response should be a dictionary contatining any
variable type. TCP messages are sent as JSON text and interpreted as
dictionaries in Python. When writing the definitions, put the variable name and
the variable type separated by a colon, following the dictionary format.

Use the following variable type names:
--------------------------------------
int: integer
float: floating point
double: double precision floating point
str: string
char: character
vector[type]: vector containing variables of 'type'
list of [type]: python list
dict: python dictionary
[class]: independently defined class object
"""
#======================================================================#
#vvvvv USER EDIT vvvvv
#======================================================================#
request_definition = '''
content = {
    'variable1': type1,
    'variable2': type2
}
'''
response_definition = '''
content = {
    'variable1': type1,
    'variable2': type2
}
'''
#======================================================================#
#^^^^^ USER EDIT ^^^^^
#======================================================================#

class TCPMessage:
    def __init__(self, is_big_endian = False, content_type = 'text/json', content_encoding = 'utf-8', content = None, content_definition = 'no definition'):
        self.is_big_endian = is_big_endian
        self.content_type = content_type
        self.content_encoding = content_encoding
        self.content = content
        self.content_definition = content_definition

    def set_content(self, content):
        self.content = content

    def get_content(self):
        return self.content

    def print_definition(self):
        print(self.content_definition)

class TCPImpl:
    def __init__(self):
        #======================================================================#
        #vvvvv USER EDIT vvvvv
        #======================================================================#
        #----- Request Parameters -----#
        # Set request content
        request_content = {'content': 'request'}
        self.request = TCPMessage(content = request_content, content_definition = request_definition)

        #----- Response Parameters -----#
        # Set response content
        response_content = {'content': 'response'}
        self.response = TCPMessage(content = response_content, content_definition = response_definition)
        #======================================================================#
        #^^^^^ USER EDIT ^^^^^
        #======================================================================#

    def perform_service(self, content):
        """ Performs the service actions.

        This is the function that gets called by the client as a request. It
        performs the service, determines the response message content, then
        returns that content. The structure of the request and response content
        must be known by the developer and should be defined above in this
        module.

        Parameters
        ----------
        content : request.content (TCPMessage.content, dict)
            The content of the request message. It should be a dictionary with
            the structure defined above in this module.

        Returns
        -------
        dict
            The content for the response message.
        """
        #======================================================================#
        #vvvvv USER EDIT vvvvv
        #======================================================================#
        # Use the content here (the developer needs to know the structure)
        # 1) Read content
        # 2) Perform service action
        # 3) Determine response message
        # 4) Return response_content
        response_content = {}
        #======================================================================#
        #^^^^^ USER EDIT ^^^^^
        #======================================================================#

        return response_content

    def client_loop(self, service_request):
        """ Client action loop.

        This is the function called by the TCPClient object intended to continue
        running as a loop until the program is closed. It should perform
        actions, determine the content needed for a request, send the request,
        wait for response content, perform actions with the response content.

        Parameters
        ----------
        service_request : python function
            This is the function that handles sending the request message to the
            server and returns the content of the response from the server. It
            is functionally equivalent to the 'perform_service' function above.

        Returns
        -------
        None
        """
        #======================================================================#
        #vvvvv USER EDIT vvvvv
        #======================================================================#
        # This function should be implemented as a 'while' loop. Perform actions
        # create request message content, send it to the 'service_request'
        # function, then save the response.
        # e.g.
        # while True:
        #     request_content = dictionary containing request variables
        #     response_content = service_request(request_content)
        #     perform action with response
        pass
        #======================================================================#
        #^^^^^ USER EDIT ^^^^^
        #======================================================================#
