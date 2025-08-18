"""
Exceptions.
"""


class TypeNotFoundException(Exception):
    def __init__(self, type_value):
        self.type_value = type_value
        self.message = f"No type '{type_value}' found."
        super().__init__(self.message)


class ConverterNotFoundException(Exception):
    def __init__(self, converter_value):
        self.converter_value = converter_value
        self.message = f"No converter type '{converter_value}' found."
        super().__init__(self.message)


class DOINotFoundException(Exception):
    def __init__(self, doi):
        self.doi = doi
        self.message = f"No DOI '{doi}' found."
        super().__init__(self.message)


class MethodNotAllowedException(Exception):
    def __init__(self):
        self.message = "CKAN threw a method is not allowed exception. Check if your config.ini is correct."
        super().__init__(self.message)
