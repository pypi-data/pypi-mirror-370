from time import time

from ..exceptions.package_exceptions import MissingDependencyError

try:
    from flask import request, redirect, make_response, session, Flask
except ImportError:
    raise MissingDependencyError("flask")

from ..other.decorators import deprecated
from ..tools.config import Config
from ..web.auth_manager import check_auth


def register_auth_routes(app: Flask, config: Config, app_name: str):
    """
    Registers the login and logout routes for the application.
    Registered routes:
    - /login
    - /logout
    Also updates the session with the user's IP and User-Agent before each request using the before_request decorator.
    If the user is not logged in, the login route will redirect the user to the UMS login page.
    If the user is logged in, the logout route will redirect the user to the UMS logout page.
    If no config value is provided for UMS_ROUTE, the default value will be used.
    Default value: https://ums.software-city.org
    :param app: Flask app
    :param config: Config object
    :param app_name: Name of the application displayed on the UMS login page
    :return:
    """
    ums_route = config.get("UMS_ROUTE", "https://ums.software-city.org")

    @app.route("/login", methods=["GET", "POST"])
    def login():
        url = request.root_url
        if "http://" in url or "https://" in url:
            url = url.split("//")[1]

        resp = make_response(
            redirect(f"{ums_route}/login?title={app_name}&redirect={url}{request.args.get('redirect') or '/'}")
        )

        if session.get("uuid") is None:
            session.clear()
            resp.delete_cookie("session")

        return resp

    @app.before_request
    def update_session():
        if session.get("uuid") is None:
            return
        session["updated"] = time()
        session["user_agent"] = request.headers.get("User-Agent")
        session["ip"] = request.headers.get("X-Real-IP") or request.remote_addr

    @app.route("/logout")
    def logout():
        url = request.root_url
        if "http://" in url or "https://" in url:
            url = url.split("//")[1]

        return redirect(f"{ums_route}/logout?redirect={url}")


@deprecated
def register_session_refresh(app: Flask, session_duration: int = 3600):
    """
    THIS FUNCTION IS DEPRECATED. USE register_auth_routes INSTEAD.
    Registers a function to refresh the session after a certain amount of time.
    :param app: Flask app
    :param session_duration: Amount of time in seconds before the session is refreshed
    :return:
    """
    @app.after_request
    def refresh_session(response):
        if not check_auth():
            return response

        # Check if the session has been updated in the last hour and redirect to the login if not
        if request.method == "GET" and request.path == "/":  # Make sure the session is only checked on the main page
            updated = session.get("updated")
            if updated is None or (time() - updated) > session_duration:
                return redirect(f"/login?redirect={request.path}")

        return response
