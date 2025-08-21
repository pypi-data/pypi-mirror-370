import os
import sys
import tomllib
from typing import Iterator
from pathlib import Path


def _walk_to_root(path: str) -> Iterator[str]:
    """
    Yield directories starting from the given directory up to the root
    """
    if not os.path.exists(path):
        raise IOError("Starting path not found")

    if os.path.isfile(path):
        path = os.path.dirname(path)

    last_dir = None
    current_dir = os.path.abspath(path)
    while last_dir != current_dir:
        yield current_dir
        parent_dir = os.path.abspath(os.path.join(current_dir, os.path.pardir))
        last_dir, current_dir = current_dir, parent_dir

def _find_file(
    filename: str,
    raise_error_if_not_found: bool = False,
    usecwd: bool = False,
) -> str:
    """
    Search in increasingly higher folders for the given file

    Returns path to the file if found, or an empty string otherwise
    """

    def _is_interactive():
        """Decide whether this is running in a REPL or IPython notebook"""
        try:
            main = __import__("__main__", None, None, fromlist=["__file__"])
        except ModuleNotFoundError:
            return False
        return not hasattr(main, "__file__")

    def _is_debugger():
        return sys.gettrace() is not None

    if usecwd or _is_interactive() or _is_debugger() or getattr(sys, "frozen", False):
        # Should work without __file__, e.g. in REPL or IPython notebook.
        path = os.getcwd()
    else:
        # will work for .py files
        frame = sys._getframe()
        current_file = __file__
        # print(f'current_file:{current_file}')
        # print(f'frame.f_code.co_filename:{frame.f_code.co_filename}')

        while frame.f_code.co_filename == current_file or not os.path.exists(
            frame.f_code.co_filename
        ):
            assert frame.f_back is not None
            frame = frame.f_back
        frame_filename = frame.f_code.co_filename
        path = os.path.dirname(os.path.abspath(frame_filename))
    # print(f'path:{path}')
    for dirname in _walk_to_root(path):
        check_path = os.path.join(dirname, filename)
        if os.path.isfile(check_path):
            return check_path

    if raise_error_if_not_found:
        raise IOError("File not found")

    return ""


def find_toml(
    filename: str,
    raise_error_if_not_found: bool = False,
    usecwd: bool = False)->Path:
    """
    Search in increasingly higher folders for the given file

    Returns path to the file if found, or an empty Path otherwise
    """
    
    
    try:
        path_str = _find_file(filename,
                               raise_error_if_not_found,
                               usecwd)
        # print(f'path_str:{[path_str]}')
        return Path(path_str)
    except:
        raise
        
def load_toml(toml_name_or_path: str|Path|None = None,
              raise_error_if_not_found: bool = True,
              usecwd: bool = False)->dict:
    """
    Load toml file from increasingly higher folders for the given file

    Returns toml value dict if found, or an empty dict otherwise
    """
    if toml_name_or_path is None:
        toml_path = find_toml('config.toml')
    elif isinstance(toml_name_or_path, str):
        toml_path = find_toml(toml_name_or_path)
    elif isinstance(toml_name_or_path, Path):
        toml_path = toml_name_or_path
    else:
        raise TypeError("toml_name_or_path must be a string, Path, or None")
    
    
    
    if raise_error_if_not_found and toml_path == Path():
        raise IOError("File not found")

    if raise_error_if_not_found and not toml_path.is_file():
        raise IOError("File is not a regular file")
    
    if raise_error_if_not_found and not toml_path.suffix == '.toml':
        raise IOError("File suffix is not .toml")
    
    try:
        # 未找到toml文件且不需要报错的情况 返回一个空字典
        if toml_path == Path():
            return {}
        with open(toml_path, "rb") as f:
            return tomllib.load(f)
    except tomllib.TOMLDecodeError as e:
        raise IOError(f"Error decoding TOML file: {e}") from e
