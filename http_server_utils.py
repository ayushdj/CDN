import os

CACHE_DIRECTORY = 'bitbusters_cache'


def does_file_exist(path_to_file: str) -> int:
    """
    Helper function to determine if a file exists in the system

    Args:
        path_to_file: the name of the file we want to see exist
    """
    if os.path.isfile(path_to_file):
        return True
    return False


def size_of_cache_directory():
    """
    Helper function to determine the size of the cache directory. This is needed

    :return: an integer re
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
            a string representing the current working directory
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
