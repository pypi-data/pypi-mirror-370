from __future__ import annotations
from abc import ABC
from os import mkdir, system
from os.path import isdir, isfile


class SpaceProject(ABC):
    def __init__(self, name: str, appDir: str):
        self.name = name
        self.appDir = appDir

    # ------------------------------------------------------------------------+
    #                                    LOGS                                 |
    # ------------------------------------------------------------------------+

    def success(self, message: str):
        """
        show success log on console

        Args:
            message (str): message in log
        """
        print(message)

    def warning(self, message: str):
        """
        show warning log on console

        Args:
            message (str): message in log
        """
        print(message)

    def error(self, message: str):
        """
        show error log on console

        Args:
            message (str): message in log
        """
        print(message)

    def info(self, message: str):
        """
        show info log on console

        Args:
            message (str): message in log
        """
        print(message)

    # ------------------------------------------------------------------------+
    #                               CHANGES FILES                             |
    # ------------------------------------------------------------------------+

    # set shell for project
    def shell(self, command: str, message: None | str = None):
        """run command on bash in project folder"""
        system(f"cd {self.appDir} && {command}")

        if message:
            self.success(f"{message} done.", False)

    def forceExsistDir(self, dir: str):
        """
        force exsist dir in folders
        check `dir` address and create folder if not exists
        """

        dir = dir.strip("/")
        _dir = ""
        # check for folder exsist if not create it
        for folder in (self.appDir + "/" + dir).split("/"):
            _dir += folder + "/"
            if not isdir(_dir):
                self.warning(f"{_dir} not found in project. create folder")
                mkdir(_dir)

    def write_file(self, dir: str, data, add: bool = False):
        """
        write a string data on dir
        this dir is forceExists
        """

        self.forceExsistDir("/".join(dir.split("/")[:-1]))
        with open(self.appDir + dir, "a" if add else "w") as f:
            f.write(str(data))

        self.success(
            f"added to file {dir}" if add else f"file {dir} is set done.",
            False,
        )

    def change_file(self, dir: str, old: str, new: str):
        """
        replace old to new in file
        """

        with open(self.appDir + dir, "r") as f:
            data = f.read()

        with open(self.appDir + dir, "w") as f:
            f.write(data.replace(old, new))

        self.success(f"file {dir} changed", False)

    def isDir(self, patch: str) -> bool:
        """check file is exists on project"""

        return isdir(self.appDir + patch)

    def isFile(self, patch: str) -> bool:
        """check file exists in dir"""

        return isfile(self.appDir + patch)

    def mkdir(self, patch: str):
        """create folder in project"""
        self.forceExsistDir(patch)
        self.success(f"folder on {self.appDir}/{patch} created.", False)
