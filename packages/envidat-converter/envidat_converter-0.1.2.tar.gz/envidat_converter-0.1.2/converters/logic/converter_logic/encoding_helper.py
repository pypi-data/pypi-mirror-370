"""
Helper method for extracting encoding and finding the mimetype.
"""

import mimetypes
import os
from urllib.parse import urlparse


def encoding_format_helper(resource):
    resource_format = resource.get("mimetype")

    if not resource_format:
        url = resource.get("url")
        # note: if this is tested on windows, mimetypes might differ. did not find a better solution so far
        if url.startswith("https://www.envidat.ch/dataset/"):
            resource_format = mimetypes.guess_type(url)[0]
        if not resource_format:
            path = urlparse(url).path
            _, resource_format = os.path.splitext(path)
        if not resource_format:
            resource_format = "No Info"

    return resource_format
