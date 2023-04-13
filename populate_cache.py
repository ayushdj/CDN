import csv
import os
from utils import *
import urllib.request
import argparse

DISK_SIZE_LIMIT = 20000000


def main(origin_server):
    # create the cache directory if it doesn't exist, because this is where we
    # store all the cached data.
    if not os.path.exists(CACHE_DIRECTORY):
        os.makedirs(CACHE_DIRECTORY)
        with open('pageviews.csv', newline='') as csvfile:
            CSV_READER = list(csv.DictReader(csvfile))
            for current_row in CSV_READER:
                current_row['article'] = current_row['article'].replace(' ', '_')
                with urllib.request.urlopen(f"http://{origin_server}/{current_row['article']}") as response:
                    data = response.read()
                    if int(size_of_cache_directory()) + len(data) <= DISK_SIZE_LIMIT:
                        with open(f"{CACHE_DIRECTORY}/{current_row['article']}", 'wb') as file:
                            # Write the content of the file to the file we're creating and close the file out.
                            file.write(data)
                            file.close()
                    else:
                        break


if __name__ == "__main__":
    default_origin_server = 'cs5700cdnorigin.ccs.neu.edu:8080'

    # Define the command line arguments
    parser = argparse.ArgumentParser(
        description='Determine HTTP Server arguments')
    parser.add_argument('-o', dest='origin', action='store', type=str,
                        help='The Origin Server (default: %(default)s)', default=default_origin_server)

    # Parse the arguments
    args = parser.parse_args()

    # Call the main method with the specified port and origin
    main(args.origin)
