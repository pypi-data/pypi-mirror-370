import inspect
import traceback
from functools import wraps
from slush.core.routing import Router
from slush.core.request import Request
from slush.core.response import Response
from slush.core.exception import HTTPBaseException
from slush.exception import NotFound, InternalServerError
from slush.settings import Config


class Slush:
    def __init__(self, config: Config = None):
        self.router = Router()
        self.config = config or Config()

    def route(self, path, methods=['GET']):
        """
        Decorator to register a route with the application.
        :param path: The URL path for the route.
        :param methods: List of HTTP methods this route responds to.
        :return: Decorator function.
        """
        if isinstance(methods, str):
            methods = [methods.upper()]
        if not all(method in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'] for method in methods):
            raise ValueError("Invalid HTTP method specified. Allowed methods are: GET, POST, PUT, DELETE, PATCH, OPTIONS.")
        if not path.startswith('/'):
            raise ValueError("Path must start with a '/' character.")
        if not path:
            raise ValueError("Path cannot be empty.")

        def decorator(func):
            @wraps(func)
            def wrapped_func(*args, **kwargs):
                return func(*args, **kwargs)

            for method in methods:
                self.router.add_route(path, method, wrapped_func)

            return wrapped_func

        return decorator

    def __call__(self, environ, start_response):
        """
        WSGI application entry point.
        :param environ: WSGI environment dictionary.
        :param start_response: WSGI start response callable.
        :return: WSGI response iterable.
        """

        request = Request(environ)
        handler, path_params = self.router.resolve(request.path, request.method)

        try:
            if not handler:
                raise NotFound()

            # Inject request and path params
            sig = inspect.signature(handler)
            kwargs = {}

            if "request" in sig.parameters:
                kwargs["request"] = request
            for name in path_params:
                if name in sig.parameters:
                    kwargs[name] = path_params[name]

            result = handler(**kwargs)
            if isinstance(result, Response):
                response = result
            else:
                response = Response(body=result)

            status, headers, body = response.finalize()
            start_response(status, headers)
            return body

        except HTTPBaseException as http_exc:
            response = http_exc.as_response()
            start_response(response.status, response.headers)
            return [response.body]

        except Exception as e:
        # Always print full traceback in terminal
            traceback.print_exc()

            if self.config.debug:
                # In debug mode, return full traceback to API
                tb_str = traceback.format_exc()
                response = Response({"error": str(e), "trace": tb_str}, status=500)
            else:
                # In prod, send generic message
                response = Response({"error": "Internal Server Error"}, status=500)

            status, headers, body = response.finalize()
            start_response(status, headers)
            return body
