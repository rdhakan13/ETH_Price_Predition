from pathlib import Path
import logging
import os
import yaml
from box import ConfigBox

logger = logging.getLogger(__name__)


def get_root_directory() -> Path:
    """
    Returns the root directory of the project by searching for the .git directory.

    Returns:
        str: The root directory of the project.
    """

    current_path = Path(__file__).resolve()

    while current_path != current_path.parent:
        if (current_path / ".git").exists():
            break
        current_path = current_path.parent

    return current_path


def make_directory(directory: str) -> None:
    """
    Creates a directory if it does not exist.

    Parameters:
        directory (str): The directory to be created.

    Returns:
        None
    """
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)


def split_dates_by_year(
    date_tuples: list[tuple[int, int, int]],
) -> list[list[tuple[int, int, int]]]:
    """
    Splits a list of date tuples into a list of lists, each containing dates from the same year.

    Parameters:
        date_tuples (list): A list of tuples containing dates (year, month, day).

    Returns:
        list: A list of lists, each containing date tuples from the same year.
    """

    year_dict: dict[int, list[tuple[int, int, int]]] = {}

    logger.info("Splitting dates by year...")

    try:
        for date_tuple in date_tuples:
            if not isinstance(date_tuple, tuple) or len(date_tuple) != 3:
                raise TypeError(
                    "Date tuples must be tuples of the form (year, month, day)."
                )
            year = date_tuple[0]
            if year not in year_dict:
                year_dict[year] = []
            year_dict[year].append(date_tuple)
    except TypeError as e:
        logger.error("Date tuples not found")
        raise e

    return list(year_dict.values())


def read_yaml(path_to_yaml: str) -> ConfigBox:
    """
    Reads the content of a YAML file.

    Parameters:
        path_to_yaml (str): The path to the YAML file.

    Returns:
        dict: The content of the YAML file.
    """

    try:
        with open(path_to_yaml, "r") as file:
            content = yaml.safe_load(file)
            logging.info(f"File {path_to_yaml} read successfully")
            return ConfigBox(content)
    except FileNotFoundError as e:
        logging.error(f"File {path_to_yaml} not found")
        raise e
