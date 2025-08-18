from functools import wraps
from .request_codes import RequestCode
from ..exceptions.package_exceptions import MissingDependencyError

try:
    from flask import session, request, abort, redirect
except ImportError:
    raise MissingDependencyError("flask")

from swc_utils.redis_db import get_app_redis_interface


def check_auth() -> bool:
    """
    Check if the user is authenticated
    :return: True if authenticated, False otherwise
    """
    return session.get("uuid") is not None


def event_manager():
    """
    Get the event manager from the redis interface
    :return: Event manager object
    """
    return get_app_redis_interface().event_manager


def get_user():
    """
    Get the user object from the event manager in dict format
    :return: User dict object. Returns empty dict if user is not authenticated.
    """
    return event_manager().query("get-user", session.get("uuid")) or {}


def search_user(search_by: str, search_value: str):
    """
    Search for a user by any possible attribute (username, email, etc.)
    :param search_by: Field to search by (username, email, etc.)
    :param search_value: Value to search for
    :return: User dict object. Returns empty dict if user is not found.
    """
    return event_manager().query("search-user", search_by, search_value) or {}


def check_admin() -> bool:
    """
    Check if the user is an admin (superadmin flag set)
    :return: True if admin, False otherwise
    """
    return event_manager().query("is-admin", session.get("uuid")) or False


def get_namespaced_permissions(namespace: str) -> list:
    """
    Get the permissions for the given namespace
    Usually application specific namespace. '*' is a wildcard for all namespaces
    :param namespace: Namespace to get permissions for
    :return: List of permissions
    """
    if not check_auth():
        return []

    return event_manager().query("get-permissions", session.get("uuid"), namespace) or []


def check_permission(namespace: str, permission: str) -> bool:
    """
    Check if the user has the given permission in the given namespace.
    Always returns True if user is admin. Always returns False if user is not authenticated.
    '*' is a wildcard for all permissions in the namespace.
    :param namespace: Permission namespace (usually application specific)
    :param permission: Permission to check
    :return: True if user has permission, False otherwise
    """
    if not check_auth():
        return False

    if check_admin():
        return True

    namespaced_permissions = get_namespaced_permissions(namespace)
    return "*" in namespaced_permissions or permission in namespaced_permissions


def auth_required(func: callable):
    """
    Decorator to check if the user is authenticated. Redirects to login page if not.
    :param func: Function to decorate
    :return: Decorator
    """
    @wraps(func)
    def check(*args, **kwargs):
        if check_auth():
            return func(*args, **kwargs)
        return redirect(f"/login?redirect={request.path}")

    return check


def admin_required(func: callable):
    """
    Decorator to check if the user is an admin. Returns 401 if not.
    :param func: Function to decorate
    :return: Decorator
    """
    @wraps(func)
    def check(*args, **kwargs):
        if check_admin():
            return func(*args, **kwargs)
        return abort(RequestCode.ClientError.Unauthorized)

    return check


def permission_required(namespace: str, permission: str):
    """
    Decorator to check if the user has the given permission in the given namespace.
    Returns 401 if not. Behavior is same as check_permission.
    :param namespace: For which namespace to check permission.
    :param permission: Permission to check
    :return: Decorator
    """
    def wrapper(func):
        @wraps(func)
        def check(*args, **kwargs):
            if check_permission(namespace, permission):
                return func(*args, **kwargs)
            return abort(RequestCode.ClientError.Unauthorized)

        return check

    return wrapper
