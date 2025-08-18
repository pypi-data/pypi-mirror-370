"""
Multifunctional helpers
"""


def join_tags(tags: list, sep: str = ".") -> str:
    """Join tags by a provided separator."""
    return sep.join([tag for tag in tags if tag])
