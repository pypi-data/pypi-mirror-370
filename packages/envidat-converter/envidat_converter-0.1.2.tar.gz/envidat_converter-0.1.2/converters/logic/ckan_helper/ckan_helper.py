"""
Helpers to access ckan data.
"""

from ckanapi import NotFound, RemoteCKAN, CKANAPIError

from converters.logic.exceptions import DOINotFoundException, MethodNotAllowedException
from converters.logic.read_config import Config


def get_remote_ckan(environment):
    """Functionality to get ckan"""
    config = Config(environment)
    ckan_url = config.get("CKAN_URL")
    return RemoteCKAN(address=str(ckan_url))


def ckan_package_show(package_id: str, environment="prod"):
    """Return CKAN package.

    Args:
        package_id (str): CKAN package id or name
        environment (str): environment name for the CKAN url from the config.ini
    """
    ckan = get_remote_ckan(environment)
    return ckan_call_action_handle_errors(ckan, "package_show", {"id": package_id})


def ckan_package_search_doi(doi: str, environment="prod"):
    """Functionality to search a package by doi"""
    ckan = get_remote_ckan(environment)
    result = ckan_call_action_handle_errors(ckan, "package_search", {"q": f"doi:{doi}"})
    if result.get("count") == 1:
        return result.get("results")[0]
    raise DOINotFoundException(doi)


def ckan_call_action_handle_errors(
    ckan: RemoteCKAN, action: str, data: dict | None = None
):
    """Wrapper for CKAN actions, handling errors.
    Copied from other ckan functions, unchanged for maintainability reasons.

    An authorised RemoteCKAN instance is required.
    NOTE: some CKAN API actions do not require authorization and will still return a
    response even if authorization invalid!

    Args:
        ckan (RemoteCKAN): RemoteCKAN session.
        action (str): the CKAN action name, for example 'package_create'
        data (dict): the dict to pass to the action, default is None
    """
    try:
        if data:
            response = ckan.call_action(action, data)
        else:
            response = ckan.call_action(action)
    except NotFound as e:
        raise e
    except CKANAPIError as e:
        if "MethodNotAllowed" in str(e):
            raise MethodNotAllowedException()
        else:
            raise e

    except Exception as e:
        raise e

    return response
