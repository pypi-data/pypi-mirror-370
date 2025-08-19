import re
from typing import Callable, Dict, Tuple, Any
from slush.exception import NotFound, MethodNotAllowed

class Route:
    def __init__(self, path: str, method: str, handler: Callable):
        """
        Initialize a Route object.
        :param path: The URL path for the route.
        :param method: The HTTP method (GET, POST, etc.) for the route.
        :param handler: The function that handles requests to this route.
        """
        self.path = path
        self.method = method.upper()
        self.handler = handler
        self.path_regex, self.param_names = self._compile_path(path)

    def _compile_path(self, path: str):
        # Convert /user/<int:id>/ to regex pattern
        """
        Compile the path into a regex pattern and extract parameter names.
        :param path: The URL path to compile.
        :return: A tuple containing the compiled regex pattern and a list of parameter names.
        """
        pattern = "^"
        param_names = []

        tokens = path.strip("/").split("/")
        for token in tokens:
            if token.startswith("<") and token.endswith(">"):
                type_and_name = token[1:-1].split(":")
                if len(type_and_name) != 2:
                    raise ValueError("Invalid dynamic path: " + token)
                type_, name = type_and_name
                param_names.append((name, type_))
                if type_ == "int":
                    pattern += r"/(?P<%s>\d+)" % name
                elif type_ == "str":
                    pattern += r"/(?P<%s>[^/]+)" % name
                else:
                    raise ValueError(f"Unsupported path type: {type_}")
            else:
                pattern += f"/{token}"

        pattern += "/?$"
        return re.compile(pattern), param_names

    def match(self, path: str):
        """
        Match the given path against the route's regex pattern.
        :param path: The URL path to match.
        :return: A dictionary of extracted parameters if the path matches, otherwise None.
        """
        match = self.path_regex.match(path)
        if not match:
            return None
        return match.groupdict()

class Router:
    """A singleton router that manages routes and resolves them based on the request path and method.
    """
    def __init__(self):
        self.routes: list[Route] = []

    def add_route(self, path: str, method: str, handler: Callable):
        self.routes.append(Route(path, method, handler))

    def resolve(self, path: str, method: str) -> Tuple[Callable, Dict[str, Any]]:
        allowed_methods = []

        for route in self.routes:
            params = route.match(path)
            if params is not None:
                allowed_methods.append(route.method)
                if route.method == method:
                    return route.handler, params

        if allowed_methods:
            raise MethodNotAllowed(
                detail=f"Allowed methods: {', '.join(allowed_methods)}",
                allowed_methods=allowed_methods
            )

        raise NotFound()
