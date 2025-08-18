from ..exceptions.package_exceptions import MissingDependencyError

try:
    from flask import make_response, send_file, Response
except ImportError:
    raise MissingDependencyError("flask")

from .request_codes import RequestCode


def send_binary_image(data: bytes, content_type="image/webp", cache_control=3600) -> Response:
    """
    Send binary image data as a response.
    :param data: Binary image data
    :param content_type: Mimetype of the image
    :param cache_control: Cache control time in seconds
    :return: Response object
    """
    if data is None:
        return make_response(
            send_file("static/img/noimage.png"),
            # RequestCode.ClientError.NotFound
            RequestCode.Success.OK
        )

    resp = make_response(data, RequestCode.Success.OK)
    resp.headers.set("Content-Type", content_type)
    resp.cache_control.max_age = cache_control
    return resp
