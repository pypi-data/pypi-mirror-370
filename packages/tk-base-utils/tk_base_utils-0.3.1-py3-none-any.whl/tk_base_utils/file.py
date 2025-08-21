import sys
import os


from pathlib import Path
from typing import Iterator
from datetime import datetime
# from warnings import warn
# from warnings import deprecated

def _is_interactive():
    """Decide whether this is running in a REPL or IPython notebook"""
    '''code copy from python-dotenv->load_dotenv->find_dotenv'''
    try:
        main = __import__("__main__", None, None, fromlist=["__file__"])
    except ModuleNotFoundError:
        return False
    return not hasattr(main, "__file__")

def _is_debugger():
    '''code copy from python-dotenv->load_dotenv->find_dotenv'''
    return sys.gettrace() is not None

def _walk_to_root(path: str) -> Iterator[str]:
    """
    Yield directories starting from the given directory up to the root
    """
    '''code copy from python-dotenv->load_dotenv->find_dotenv'''
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


def get_current_dir_path(usecwd=False) -> Path:
    """Returns the dir of the current file."""
    '''code copy from python-dotenv->load_dotenv->find_dotenv'''
    if usecwd or _is_interactive() or _is_debugger() or getattr(sys, "frozen", False):
        # Should work without __file__, e.g. in REPL or IPython notebook.
        path = os.getcwd()
    else:
        # will work for .py files
        frame = sys._getframe()
        current_file = __file__

        while frame.f_code.co_filename == current_file or not os.path.exists(
            frame.f_code.co_filename
        ):
            assert frame.f_back is not None
            frame = frame.f_back
        frame_filename = frame.f_code.co_filename
        path = os.path.dirname(os.path.abspath(frame_filename))
    return Path(path)

def get_target_file_path(filename: str,
                         raise_error_if_not_found: bool = True, 
                         usecwd=False) -> Path:
    """Returns the path of the target file."""
    '''code copy from python-dotenv->load_dotenv->find_dotenv'''
    current_file_path = get_current_dir_path(usecwd)
    currrent_file_path_str = str(current_file_path.resolve())
    for dir in _walk_to_root(currrent_file_path_str):
        target_file_path = Path(dir) /filename
        if target_file_path.exists():
            return target_file_path
    if raise_error_if_not_found:
        raise IOError(f"{filename} not found")
    return Path()


def get_root_dir_path(target_file_name: str =None):
    '''获取项目根目录
    param target_file_name: 目标文件名，默认为None，表示使用默认设置
    默认会按照.env->pyproject.toml->requirements.txt->readme.md顺序进行查找,在某个层级找到则返回
    如果未找到则返回当前文件夹
    返回Path对象
    '''
    current_dir = get_current_dir_path()
    if target_file_name is not None:
        target_file_list = [target_file_name]
    else:
        target_file_list = []
    target_file_list.extend(['.env','pyproject.toml','requirements.txt','readme.md'])
    # 遍历文件夹 寻找相关目标文件作为根目录
    for dirname in _walk_to_root(current_dir):
        for file in target_file_list:
            temp_path = Path(dirname)
            if (temp_path / file).exists():
                return temp_path

    return current_dir
# @deprecated('get_abs_file_path is deprecated, use get_abs_path instead',category=None,stacklevel=2)
# def get_abs_file_path(file_name:str) -> Path:
#     '''获取绝对路径'''
#     warn("get_abs_file_path is deprecated, use get_abs_path instead",DeprecationWarning,stacklevel=2)

#     if file_name[0] == '$':
#         keywords_file_dir = get_root_dir_path()
#     else:
#         keywords_file_dir = get_current_dir_path()
#     if file_name[0] in ['.','$']:
#         file_path = keywords_file_dir / file_name[1:].lstrip('/')
#     else:
#         file_path = keywords_file_dir / file_name.lstrip('/')
#     return file_path
def get_abs_path(file_name:str) -> Path:
    '''获取绝对路径'''
    if file_name[0] == '$':
        keywords_file_dir = get_root_dir_path()
    else:
        keywords_file_dir = get_current_dir_path()
    if file_name[0] in ['.','$']:
        file_path = keywords_file_dir / file_name[1:].lstrip('/')
    else:
        file_path = keywords_file_dir / file_name.lstrip('/')
    return file_path

def create_file_name_with_time(file_name:str|Path):
    if isinstance(file_name,str):
        file_name = Path(file_name)
    file_name = file_name.with_name(f"{file_name.stem}_{datetime.now().strftime('%Y%m%d-%H%M%S')}{file_name.suffix}")
    return file_name




        
