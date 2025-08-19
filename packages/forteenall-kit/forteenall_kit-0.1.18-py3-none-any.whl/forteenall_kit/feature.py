# Main imports
from __future__ import annotations

# Invokers import
from forteenall_kit._features import features


class FeatureManager:
    def __init__(self):
        self.features = features
        self.executed = set()

    # ------------------------------------------------------------------------+
    #                                    LOGS                                 |
    # ------------------------------------------------------------------------+

    def success(self, message: str):
        """
        show success log on console

        Args:
            message (str): message in log
        """

    def warning(self, message: str):
        """
        show warning log on console

        Args:
            message (str): message in log
        """

    def error(self, message: str):
        """
        show error log on console

        Args:
            message (str): message in log
        """

    def info(self, message: str):
        """
        show info log on console

        Args:
            message (str): message in log
        """

    # ------------------------------------------------------------------------+
    #                               CHANGES FILES                             |
    # ------------------------------------------------------------------------+

    # set shell for project
    def shell(self, command: str, message: None | str = None):
        """run command on bash in project folder"""

    def forceExsistDir(self, dir: str):
        """
        force exsist dir in folders
        check `dir` address and create folder if not exists
        """

    def write_file(self, dir: str, data, add: bool = False):
        """
        write a string data on dir
        this dir is forceExists
        """

    def change_file(self, dir: str, old: str, new: str):
        """
        replace old to new in file
        """

    def isDir(self, patch: str) -> bool:
        """check file is exists on project"""

    def isFile(self, patch: str) -> bool:
        """check file exists in dir"""

    def mkdir(self, patch: str):
        """create folder in project"""

    # ------------------------------------------------------------------------+
    #                                  RUNTIME                                |
    # ------------------------------------------------------------------------+

    def execute(self, feature_name: str, **params):
        """
        this function run invokers.
        Args:
            feature_name (str): name of feature
        """
