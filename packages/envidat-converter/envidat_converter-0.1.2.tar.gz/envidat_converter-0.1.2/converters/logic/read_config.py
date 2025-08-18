"""
Class to read the config.ini file
"""

import configparser


class Config:
    def __init__(self, environment="prod"):
        self.config = configparser.ConfigParser()
        self.config.read("config.ini")
        self.environment = environment
        if self.environment not in self.config.sections():
            raise ValueError(f"{environment} is not defined")

    def get(self, key):
        try:
            return self.config.get(self.environment, key)
        except KeyError:
            raise KeyError(f"Key '{key}' not found in environment '{self.environment}'")
