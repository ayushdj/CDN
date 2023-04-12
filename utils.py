import os
import ipaddress
import sys
import requests
import json
import math
import time
from typing import Callable, Optional

CACHE_DIRECTORY = 'bitbusters_cache'


def get_rtt(hostname: str) -> float:
    """This function calculates the Round Trip Time (RTT) to a given host using the ping command"""
    # Ping the host and capture the output
    ping_command = f"ping -c 1 -W 0.5 {hostname} | grep -E -i '^(rtt|round-trip)'"
    stats = os.popen(ping_command).read()
    # try:
    if stats:
        min, avg, max, std_dev  = stats.split(" = ")[1].replace("ms", "").strip().split("/")
        return float(avg)
    return -1
    # except:
    #     return -1

def size_of_cache_directory():
    """
    Helper function to determine the size of the cache directory. This is needed

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
    Helper function to determine the current working directory in the system

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
            file_list.append((file_path, file_size))

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

    Args:
        ip1: A string representing the first IP address.
        ip2: A string representing the second IP address.

    Returns:
        A float representing the distance in meters between the 
        two IP addresses, or -1 if an error occurs.
    """
    try:
        IP_API = 'http://ip-api.com/json/'

        # Construct the API request URL
        url = f'{IP_API}{ip1}'

        # Set up the HTTP headers
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

        # Make the first API request to get the location data for the first IP address
        response1 = requests.get(url, headers=headers)
        data1 = json.loads(response1.text)

        # Make the second API request to get the location data for the second IP address
        url = f'{IP_API}{ip2}'
        response2 = requests.get(url, headers=headers)
        data2 = json.loads(response2.text)

        # Extract the latitude and longitude data from the location data for each IP address
        lat1 = data1['lat']
        lon1 = data1['lon']
        lat2 = data2['lat']
        lon2 = data2['lon']

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
    except Exception:
        return -1
    
    
class MemCache:
    
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.tm = 0
        self.cache = {}
        self.lru = {}

    def get(self, key: str) -> Optional[str]:
        if key in self.cache:
            self.lru[key] = self.tm
            self.tm += 1
            return self.cache[key]
        return None
    
    def has(self, key: str) -> bool:
        return key in self.lru
    
    def keys(self) -> list:
        return list(self.lru.keys())

    def set(self, key: str, value: str) -> None:
        if len(self.cache) >= sys.getsizeof(self.lru):
            old_key = min(self.lru.keys(), key=lambda k:self.lru[k])
            self.cache.pop(old_key)
            self.lru.pop(old_key)
        self.cache[key] = value
        self.lru[key] = self.tm
        self.tm += 1