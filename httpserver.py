#!/usr/bin/env python3
import argparse
from http.server import BaseHTTPRequestHandler, HTTPServer
import socketserver
import urllib.request
from http_server_utils import *
from http_cache import HTTPCache
import os
import csv

MY_SERVER_NAME = 'cdn-http4.5700.network'
ORIGIN_SERVER = 'http://cs5700cdnorigin.ccs.neu.edu:8080'
# DISK_SIZE_LIMIT = 20000000
DISK_SIZE_LIMIT = 500000


class ReplicaHTTPServer(BaseHTTPRequestHandler):
    """
    This class inherits from the BaseHTTPRequestHandler in the 'http.server' library and outlines logic for
    a GET request on the replica HTTP server.
    """

    def __init__(self, request: bytes, client_address: tuple[str, int], server: socketserver.BaseServer):
        super().__init__(request, client_address, server)
        self.http_cache = HTTPCache()

    def _send_information_over(self, response_code, html_string):
        """
        Helper method to send information to the client. Put this into a function because
        the contents of this function are used multiple times.

        Args:
            response_code: the response code to send over
            html_string: the response message to send over.
        """
        self.send_response(response_code)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(bytes(html_string, "utf-8"))

    def do_GET(self):
        """
        This method is an override of the do_GET function specified in the BaseHTTPRequestHandler class.
        If the data we are looking for based on the path exists in our cache, then we send that data over. Otherwise,
        we send the data from the origin server.
        """

        current_directory = get_current_directory()

        # if the file we're looking for exists in the disk cache, then pull the data
        # from there, otherwise go to the Origin server and pull the data from there.
        if does_file_exist(f'{CACHE_DIRECTORY}/{self.path[1:]}'):
            # open the file from the cache
            with open(f'{current_directory}/{CACHE_DIRECTORY}/{self.path[1:]}', 'r') as file:
                file_lines = file.readlines()

            # join the string list and send the data back out.
            joined_result = "".join(file_lines)
            self._send_information_over(200, joined_result)
            return

        else:
            print("entered outer else block")
            try:
                # actual path to the resource on the Origin server
                actual_resource_path = f'http://{ORIGIN_SERVER}/{self.path[1:]}'

                # contact the Origin server for the requested resource
                with urllib.request.urlopen(actual_resource_path) as response:
                    # Set the response status code and headers
                    data = response.read()
                    headers = response.info()
                    self._send_information_over(response.status, data.decode())
                    print("entered response block right before if check for disk limit size")
                    print("THIS IS THE SIZE OF THE CACHE DIRECTORY: ", size_of_cache_directory())
                    print("This is the size of the incoming data from the origin server: ", headers['Content-Length'])

                    # ============================================================================================

                    if int(size_of_cache_directory()) + int(headers['Content-Length']) > DISK_SIZE_LIMIT:
                        with open('pageviews.csv', newline='') as csvfile:
                            CSV_READER = csv.DictReader(csvfile)
                            CSV_READER = list(CSV_READER)
                            for row in reversed(CSV_READER):

                                row['article'] = row['article'].replace(' ', '_')

                                directory = check_file_in_directory(CACHE_DIRECTORY, row['article'])

                                if directory is not None:
                                    os.remove(f'{current_directory}/{directory}')

                                if int(size_of_cache_directory()) + int(headers['Content-Length']) > DISK_SIZE_LIMIT:
                                    continue
                                else:
                                    break

                    # extract the directory path and the name of the file and make the directory.
                    dir_path, file_name = os.path.split(self.path[1:])
                    mk_dir(f'{CACHE_DIRECTORY}/{dir_path}')

                    with open(f'{CACHE_DIRECTORY}/{self.path[1:]}', "wb") as file:
                        # Write the content of the file to the file we're creating and close the file out.
                        file.write(data)
                        file.close()



            except Exception as e:
                print("Unble to retrieve data from the origin server. Please request for the resource again")
                self.send_response(400)
                self.send_header('Content-type', 'text/html')
                self.end_headers()


def main(server_port_number):
    """
    The entry point into the http server.
    Args:
        server_port_number: the port number this http server is listening/sending on

    """
    # create the cache directory if it doesn't exist, because this is where we
    # store all the cached data.
    mk_dir(CACHE_DIRECTORY)

    with socketserver.TCPServer(("127.0.0.1", server_port_number), ReplicaHTTPServer) as httpd:
        print("serving at port", server_port_number)
        httpd.serve_forever()


if __name__ == "__main__":
    # Define the command line arguments
    parser = argparse.ArgumentParser(description="Determine HTTP Server arguments")
    parser.add_argument('-p', dest="port", action='store', type=int, help="Port Number")
    parser.add_argument('-o', dest="origin", action='store', type=str, help="The origin server")

    # specify the port number and the origin server
    port_number = 0

    origin_server = ''
    # Parse the arguments
    args = parser.parse_args()

    # if the origin server and the port number are stated in the arguments, then we set them here,
    # otherwise we revert them to their defaults.
    if args.origin and args.port:
        port_number = args.port
        ORIGIN_SERVER = args.origin
    else:
        port_number = 20200  # port 20200 is bitbuster's specific port number
        ORIGIN_SERVER = 'cs5700cdnorigin.ccs.neu.edu:8080'

    # Call the main method with the specified port and origin
    main(port_number)
