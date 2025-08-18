"""
Helper methods for size conversion.
"""

import json


def _get_sizes(self, resources):
    dc_sizes = []

    for resource in resources:
        dc_size = _get_size(self, resource)
        dc_size = {self.text_tag: dc_size}
        dc_sizes += [dc_size]
    return dc_sizes


def _get_size(self, resource):
    dc_size = "NaN"
    size = resource.get("size")
    if not size:
        resource_size = resource.get("resource_size")
        if resource_size:
            resource_size = json.loads(resource_size)
            size_value = resource_size.get("size_value")
            size_units = resource_size.get("size_units")
            if size_units and size_value:
                units = {
                    "kb": 1024,
                    "mb": 1024**2,
                    "gb": 1024**3,
                    "tb": 1024**4,
                }
                dc_size = f"{round(float(size_value) * units[size_units])} bytes"
    else:
        dc_size = f"{size} bytes"
    return dc_size
