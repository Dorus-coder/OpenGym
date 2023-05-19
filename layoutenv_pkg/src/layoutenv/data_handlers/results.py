import os
import csv
from typing import List


def append_to_csv(file_path: str, data: List[list]) -> None:
    """
    Append data to an existing CSV file.
    file_path: The path of the CSV file.
    data: A list of lists, where each inner list represents a row of data.
    """
    with open(file_path, 'a', newline="") as file:
        writer = csv.writer(file, delimiter=',')
        writer.writerows(data)

def write_results_to_csv(data: List[list], filename: str = "results_per_episode.csv") -> None:
    if not os.path.exists(filename):
        with open(filename, 'w', newline="") as file:
            
            writer = csv.writer(file, delimiter=',')
            writer.writerows([['volume', 'attained idx']])
    
    append_to_csv(file_path=filename, data=data)


if __name__ == "__main__":
    write_results_to_csv([["500", "0.5"]])
    write_results_to_csv([["500", "0.5"]])
    write_results_to_csv([["500", "0.5"]])
