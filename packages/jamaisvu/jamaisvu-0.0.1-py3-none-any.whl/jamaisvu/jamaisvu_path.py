"""
Developer: vujadeyoon
Email: vujadeyoon@gmail.com
Github: https://github.com/vujadeyoon/jamaisvu-python

Title: jamaisvu_path.py
Description: A module for path
"""


import os
import glob
import sys
import pathlib
import shutil
from typing import Union, List, Tuple, Optional
from jamaisvu.jamaisvu_debug import printd, pprintd


class Path(object):
    def __init__(self, _spath: str, _is_absolute: bool = False):
        super(Path, self).__init__()
        if _is_absolute is True:
            self.__spath = os.path.abspath(_spath)
        else:
            self.__spath = _spath
        self.name = self.path.stem
        self.ext = self.path.suffix
        self.filename = self.name + self.ext

    def __str__(self) -> str:
        return self.str

    def __repr__(self) -> str:
        return self.str

    @property
    def str(self) -> str:
        return self.__spath

    @property
    def path(self) -> pathlib.Path:
        return pathlib.Path(self.str)

    @property
    def parent(self):
        return Path(_spath=str(self.path.parent))

    def replace(self, _old: str, _new: str):
        return Path(_spath=self.str.replace(_old, _new))

    def replace_ext(self, _new: str):
        return self.replace(_old=self.ext, _new=_new)

    def move(self, _spath_dst: str) -> None:
        path_dst = Path(_spath_dst)

        if path_dst.path.is_dir() is True:
            path_dst = Path(os.path.join(path_dst.str, self.filename))
            path_dst.unlink(_missing_ok=True)

        try:
            shutil.move(src=self.str, dst=path_dst.str)
        except Exception as e:
            raise OSError('The file move is failed.: {}'.format(e))

    def copy(self, _spath_dst: str) -> None:
        path_dst = Path(_spath_dst)
        path_dst.parent.path.mkdir(mode=0o755, parents=True, exist_ok=True)
        try:
            shutil.copy2(src=self.str, dst=path_dst.str)
        except Exception as e:
            raise OSError('The file copy is failed.: {}'.format(e))

    def unlink(self, _missing_ok: bool = True) -> None:
        self.path.unlink(missing_ok=_missing_ok)

    def mkdir(self, _mode: int = 0o775, _parents: bool = True, _exist_ok: bool = True):
        self.path.mkdir(mode=_mode, parents=_parents, exist_ok=_exist_ok)

    def rmdir(self) -> None:
        self.path.rmdir()

    def rmtree(self, _ignore_errors: bool = False, _onerror: Optional[set] = None) -> None:
        if self.path.is_dir() is True:
            try:
                shutil.rmtree(path=self.str, ignore_errors=_ignore_errors, onerror=_onerror)
            except Exception as e:
                print('The rmtree is failed with exception: {}'.format(e))

    def cd(self) -> None:
        os.chdir(self.str)

    def count_number_files(self, _pattern: str = '*') -> int:
        if self.path.is_file() is True:
            raise ValueError('The given path should be a directory path.')

        return len(list(self.path.rglob('*')))

    def glob(self, _patterns: tuple = ('*', )) -> list:
        res = list()
        for _idx, _pattern in enumerate(_patterns):
            res.extend(list(self.path.glob(pattern=_pattern)))

        return list(map(str, res))

    def rglob(self, _patterns: tuple = ('*', )) -> list:
        res = list()
        for _idx, _pattern in enumerate(_patterns):
            res.extend(list(self.path.rglob(pattern=_pattern)))

        return list(map(str, res))
