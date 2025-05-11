from pathlib import Path
import importlib
import logging
import os
import yaml
import time
from box import ConfigBox
from functools import wraps
from typing import Any

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

def timeit(func):
    """
    A decorator that measures the execution time of a function.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        logger.info(f"'{func.__name__}' took {end - start:.4f} seconds.")
        return result
    return wrapper

def snake_to_camel_case(snake_str: str) -> str:
    """
    Converts a snake_case string to camelCase.

    Parameters:
        snake_str (str): The snake_case string to convert.

    Returns:
        str: The converted camelCase string.
    """
    components = snake_str.split('_')
    return components[0].title() + ''.join(x.title() for x in components[1:])

def get_class(file_name: str)->Any:
    """
    Dynamically imports a class from a module.

    Parameters:
        module_path (str): The path to the module.
        class_name (str): The name of the class to import.

    Returns:
        type: The imported class.
    """
    try:
        class_name = snake_to_camel_case(file_name.split('.')[0])
        module_path = find_module_path(file_name)
        module = importlib.import_module(module_path)
        class_ = getattr(module, class_name)
        return class_
    except (ModuleNotFoundError, AttributeError) as e:
        logger.error(f"Error importing {class_name} from {module_path}: {e}")
        raise e
    
def find_module_path(file_name:str, src_dir:str=str(get_root_directory()))-> Any:
    """
    Finds the Python module path of a given file inside the src directory.

    Args:
        file_name (str): The Python file name to search for (e.g., "my_module.py").
        src_dir (str): The root directory to search in (default: "src").

    Returns:
        str or None: The module import path (e.g., "package.subpackage.my_module") or None if not found.
    """
    file_name = file_name if file_name.endswith('.py') else file_name + '.py'
    for root, _, files in os.walk(src_dir):
        if file_name in files:
            full_path = os.path.join(root, file_name)
            rel_path = os.path.relpath(full_path, src_dir)
            module_path = rel_path.replace(os.path.sep, '.')
            return os.path.splitext(module_path)[0]
    return None