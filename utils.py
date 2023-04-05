import os
import time
from typing import Callable

CACHE_DIRECTORY = 'bitbusters_cache'


# def does_file_exist(path_to_file: str) -> int:
#     """
#     Helper function to determine if a file exists in the system
#
#     Args:
#         path_to_file: the name of the file we want to see exist
#     """
#     if os.path.isfile(path_to_file):
#         return True
#     return False


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


# def check_file_in_directory(path_to_file: str, filename: str) -> Optional[str]:
#     """
#     Helper function to see if a file exists in a directory. Includes any subdirectories. If the file exists, then
#     we return both the path to the file, and true. otherwise, we return False.
#
#     Args:
#         path_to_file: the directory the file we're looking for lives in
#         filename: the name of the file we're looking for
#
#     Returns:
#         A string representing the path of the file if the file we're looking for exists, None otherwise
#     """
#     for dirpath, dirnames, filenames in os.walk(path_to_file):
#         for file in filenames:
#             if file == filename:
#                 return os.path.join(dirpath, filename)
#     return None

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