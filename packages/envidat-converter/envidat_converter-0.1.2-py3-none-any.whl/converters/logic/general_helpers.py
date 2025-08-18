"""General helper functions."""

import os

import click

from converters.logic.constants import InputTypes


def get_inputtype(query: str) -> InputTypes:
    """
    Used to know if a query is a DOI or an ID.
    Since none of the IDs contain /, we treat all the queries that contain / as a DOI
    :param query: query
    :return: InputTypes
    """

    if "/" in query:
        return InputTypes.DOI
    return InputTypes.ID


class OptionalPath(click.ParamType):
    """Class used to determine where a file should be saved."""

    name = "path"

    def convert(self, value, param, ctx):
        if value is None:  # means: saved in default folder
            return True
        return os.path.abspath(value)
