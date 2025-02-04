from pathlib import Path
import logging

def get_root_directory() -> str:
    """
    Returns the root directory of the project by searching for the .git directory.

    Returns:
        str: The root directory of the project.
    """

    current_path = Path(__file__).resolve()

    while current_path != current_path.parent:
        if (current_path / '.git').exists():
            break
        current_path = current_path.parent

    return current_path


def split_dates_by_year(date_tuples:tuple=None) -> list:
    """
    Splits a list of date tuples into a list of lists, each containing dates from the same year.

    Args:
        date_tuples (list): A list of tuples containing dates (year, month, day).

    Returns:
        list: A list of lists, each containing date tuples from the same year.
    """

    year_dict = {}

    logging.info("Splitting dates by year...")

    try:
        for date_tuple in date_tuples:
            year = date_tuple[0]
            if year not in year_dict:
                year_dict[year] = []
            year_dict[year].append(date_tuple)
    except TypeError as e:
        logging.error("Date tuples not found")
        raise e

    return list(year_dict.values())