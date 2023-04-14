import os
import ipaddress
import json
import math
import socket
import time
import urllib.request
import json
from typing import Callable

CACHE_DIRECTORY = 'bitbusters_cache'
GEO_DATA = {}

def size_of_cache_directory():
    """
    Helper function to determine the size of the cache directory.

    Returns:
         An integer representing the size of the directory
    """
    return sum(
        os.path.getsize(os.path.join(dirpath, filename))
        for dirpath, _, filenames in os.walk(CACHE_DIRECTORY)
        for filename in filenames
    )


def get_current_directory() -> str:
    """
    Helper function to determine the current working directory in the system.

    Return:
            A string representing the current working directory
    """
    return os.getcwd()


def delete_file(file_path: str) -> None:
    """
    Deletes a file from the cache.

    Args:
        file_path: The path to the file.
    """
    os.remove(file_path)


def mk_dir(directory: str) -> None:
    """
    If the directory exists, we don't create the directory. Otherwise, we create it.

    Args:
        directory: the directory in the system

    """

    if not os.path.exists(directory):
        os.makedirs(directory)


def find_recently_modified_files():
    """
    Gets all the files from a directory and sorts them in descending order (oldest file to youngest file),
    along with their size in bytes.

    Returns:
        List of tuples, where each tuple contains the file path and size (in bytes) sorted by the date they were modified
    """
    # Create a list of all files in the directory and its subdirectories, along with their size
    file_list = []
    for root, dirs, files in os.walk(CACHE_DIRECTORY):
        for file in files:
            file_path = os.path.join(root, file)
            file_size = os.path.getsize(file_path)
            with open(file_path, 'rb') as f:
                file_content = f.read()
            file_list.append((file_path, file_size, file_content))

    # Sort the list of files based on their modification time, with the most recently modified file last
    file_list.sort(key=lambda x: os.path.getmtime(x[0]), reverse=False)

    return file_list

def is_valid_ip(address: str) -> bool:
    """
    Checks if a given string is a valid IP address.

    Args:
        address: A string containing an IP address.

    Returns:
        A boolean value indicating whether the input string is a valid IP address.
        Returns True if the input string is a valid IP address, False otherwise.
    """
    try:
        ipaddress.ip_address(address)
        return True
    except ValueError:
        return False

def process_monitor(func: Callable) -> Callable:
    """A decorator that wraps a function and continuously monitors its execution.

    If the function throws an exception, it waits for 3 seconds and then tries again.
    This allows the function to recover from transient errors and continue running.

    Args:
        func: The function to monitor and automatically recover from errors.

    Returns:
        A wrapped version of the input function that continuously monitors and retries it.
    """
    def wrapped(*args):
        """The wrapped function that continuously monitors the input function."""
        while True:
            try:
                func(*args)
            except Exception as exp:
                # If an exception is raised, wait for 3 seconds before retrying.
                print(exp)
            time.sleep(3)
            print('Restarting process ...')
    return wrapped

def get_dist_between(ip1: str, ip2: str) -> float:
    """
    Calculates the distance in meters between two IP addresses using 
    the haversine formula and the IP-API geolocation API.
    Ref: https://towardsdatascience.com/calculating-distance-between-two-geolocations-in-python-26ad3afe287b
    
    Args:
        ip1: A string representing the first IP address.
        ip2: A string representing the second IP address.

    Returns:
        A float representing the distance in meters between the 
        two IP addresses
    """
    try:
        IP_API = 'http://ip-api.com/json/'
        def get_geo_ip(url):
            if url in GEO_DATA:
                lat, lon, ts = GEO_DATA[url]
                if ts > 3600 and url in GEO_DATA:
                    GEO_DATA.pop(ts)
                return (lat, lon, ts)
            with urllib.request.urlopen(url) as resp:
                data = json.loads(resp.read().decode())
                if data['status'] == 'success':
                    result = (data['lat'], data['lon'], time.time())
                    GEO_DATA[url] = result
                    return result
                return None
        
        # Make the first API request to get the location data for the first IP address
        url = f'{IP_API}{ip1}'
        data1 = get_geo_ip(url)
        if not data1:
            return float('inf')
        lat1, lon1, ts = data1

        # Make the second API request to get the location data for the second IP address
        url = f'{IP_API}{ip2}'
        data2 = get_geo_ip(url)
        if not data2:
            return float('inf')
        lat2, lon2, ts = data2

        # Calculate the distance between the two locations using the haversine formula
        R = 6371e3
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)

        a = math.sin(delta_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        distance = R * c
    
        return distance
    
    except Exception as exp:
        return float('inf')
    
def get_rtt(ip: str) -> float:
    """
    Get the round-trip time (RTT) using the Scamper tool.

    Args:
        ip (str): The destination IP address.

    Returns:
        float: The average RTT in milliseconds.
    """
    ping_command = f"scamper -c \"ping -c 1\" -i {ip} | grep -E -i '^(rtt|round-trip)'"
    try:
        stats = os.popen(ping_command).read()
        if stats:
            min, avg, max, std_dev  = stats.split(" = ")[1].replace("ms", "").strip().split("/")
            return float(avg)
        raise Exception("Invalid stats")
    except:
        return float('inf')

def get_rtt_from_http(http_host: str, src_ip: str) -> float:
    """
    Sends an HTTP request to the specified host to get the round-trip time (RTT)
    between the host and the source IP address.

    Args:
        http_host (str): The hostname or IP address of the host to send the request to.
        src_ip (str): The source IP address to include in the request.

    Returns:
        float: The RTT in milliseconds.
    """
    url = f'http://{http_host}/rtt/{src_ip}'
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req) as resp:
        if resp.status == 200:
            return float(resp.read().decode())
        else:
            return float('inf')
    
def get_server_ip_address(host: str) -> str:
    """
    Get the IP address of a server given its hostname.

    Args:
        host (str): The hostname or IP address of the server.

    Returns:
        str: The IP address of the server.
    """
    return host if is_valid_ip(host) else socket.gethostbyname(host)