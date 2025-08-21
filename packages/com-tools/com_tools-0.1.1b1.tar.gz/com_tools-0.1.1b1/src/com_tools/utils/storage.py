
import json
from pathlib import Path
from typing import Dict, List

from pydantic import BaseModel

from com_tools.loggers import logger

DEFAULT_STORAGE_FOLDER = Path("~/com-tools/.profiles/").expanduser().resolve()
DEFAULT_STORAGE_FOLDER.mkdir(parents=True, exist_ok=True)


def scan_storage_directory(path: Path | str=DEFAULT_STORAGE_FOLDER) -> Dict[str, Path]:
    """
    Scans a given directory for .json and .yml files.

    Args:
        storage_path (Path): The pathlib.Path object representing the directory to scan.

    Returns:
        list[tuple[str, str]]: A list of tuples, where each tuple contains the
                                filename (without extension) and its extension.
                                Returns an empty list if the directory does not exist.
    """
    if isinstance(path, str):
        path = Path(path).expanduser().resolve()

    if not path.exists():
        raise FileNotFoundError(f"Directory does not exist: {path}")
    
    if not path.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {path}")
    
    found_files = {}
    # Iterate over all items (files and directories) in the storage_path
    for item in path.iterdir():
        # Check if the item is a file
        if item.is_file():
            # Get the file's extension (suffix includes the dot)
            extension = item.suffix.lower()
            # Check if the extension is .json or .yml
            if extension == '.json' or extension == '.yml':
                # Get the filename without the extension (stem)
                file_stem = item.stem
                
                # Append the (stem, extension without dot) to the list
                found_files[file_stem] = item
    return found_files


def save_file(model: BaseModel, directory_path: Path, filename: str) -> None:
    file_path = directory_path.joinpath(filename)
    with open(file_path, "w") as f:
        json.dump(model.model_dump(), f)


def remove_file(directory_path: Path, filename: str) -> None:
    for file in directory_path.iterdir():
        logger.info(f"{file=} | {filename=}")
        if file.is_file() and filename == file.stem:
            file.unlink()
