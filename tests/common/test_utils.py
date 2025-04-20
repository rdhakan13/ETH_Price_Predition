import pytest
import os
from pathlib import Path
from unittest.mock import patch, MagicMock
from src.common.utils import get_root_directory, make_directory, split_dates_by_year, read_yaml
from box import ConfigBox


def test_get_root_directory(tmp_path, monkeypatch):
    root_dir = tmp_path / "project_root"
    sub_dir = root_dir / "src" / "common"
    sub_dir.mkdir(parents=True)
    (root_dir / ".git").mkdir()
    fake_file_path = sub_dir / "utils.py"
    fake_file_path.write_text("# dummy script")
    monkeypatch.setattr("src.common.utils.__file__", str(fake_file_path))
    result = get_root_directory()
    assert result == root_dir


def test_make_directory_creates_new_directory():
    with patch("os.makedirs") as mock_makedirs:
        with patch("os.path.exists") as mock_exists:
            mock_exists.return_value = False
            make_directory("/new_directory")
            mock_makedirs.assert_called_once_with("/new_directory", exist_ok=True)


def test_make_directory_already_exists():
    with patch("os.makedirs") as mock_makedirs:
        with patch("os.path.exists") as mock_exists:
            mock_exists.return_value = True
            make_directory("/existing_directory")
            mock_makedirs.assert_not_called()


def test_split_dates_by_year_basic():
    date_tuples = [(2020, 1, 1), (2021, 2, 2), (2020, 3, 3), (2021, 4, 4), (2022, 5, 5)]
    expected_result = [
        [(2020, 1, 1), (2020, 3, 3)],
        [(2021, 2, 2), (2021, 4, 4)],
        [(2022, 5, 5)],
    ]
    result = split_dates_by_year(date_tuples)
    assert result == expected_result

def test_split_dates_by_year_empty():
    date_tuples = []
    result = split_dates_by_year(date_tuples)
    assert result == []

def test_split_dates_by_year_single_year():
    date_tuples = [(2020, 1, 1), (2020, 5, 5), (2020, 7, 7)]
    expected_result = [
        [(2020, 1, 1), (2020, 5, 5), (2020, 7, 7)],
    ]
    result = split_dates_by_year(date_tuples)
    assert result == expected_result

def test_split_dates_by_year_invalid_data(monkeypatch):
    date_tuples = [
        (2020, 1, 1), 
        "invalid",
        (2021, 3, 3)
    ]

    def mock_error(message):
        assert message == "Date tuples not found"
    
    monkeypatch.setattr("src.common.utils.logger.error", mock_error)
    with pytest.raises(TypeError):
        split_dates_by_year(date_tuples)

def test_split_dates_by_year_mixed_years():
    date_tuples = [(2021, 1, 1), (2020, 2, 2), (2020, 3, 3), (2021, 4, 4)]
    expected_result = [
        [(2021, 1, 1), (2021, 4, 4)],
        [(2020, 2, 2), (2020, 3, 3)],
    ]
    result = split_dates_by_year(date_tuples)
    assert result == expected_result


def test_read_yaml_valid_file():
    yaml_content = {"key": "value"}
    with patch("builtins.open", MagicMock()) as mock_open:
        with patch("yaml.safe_load", return_value=yaml_content):
            result = read_yaml("path/to/yaml")
            assert isinstance(result, ConfigBox)
            assert result.key == "value"

def test_read_yaml_file_not_found():
    with patch("builtins.open", MagicMock(side_effect=FileNotFoundError)):
        with pytest.raises(FileNotFoundError):
            read_yaml("path/to/nonexistent/yaml")