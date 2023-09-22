import os
import importlib

from fastapi import APIRouter

METHODS = ["get", "post", "put", "delete"]


class DirectoryRouter(APIRouter):
    """DirectoryRouter class inherit from fastapi.APIRouter.

    This class begins automatic route scanning upon initialization.

    Args:
        base_directory (str, optional): Defines the folder to be subjected to automatic route scanning.
        route_file_name (str, optional): Specifies the file name within the folder where route scanning will be conducted

    Examples:
        >>> from fastapi import FastAPI
        >>> from fastapi_directory_routing import DirectoryRouter
        >>> app = FastAPI()
        >>> easy_router = DirectoryRouter()
        >>> app.include_router(prefix="/easy-routes", router=easy_router)

    Todo:
        * For each route configuration, the __config__ variable will be searched within the files.
        * Error and exception handling scenarios will be enhanced/developed.
    """

    def __init__(
        self,
        base_directory: str = "api",
        route_file_name: str = "route",
        *args,
        **kwargs,
    ):
        self._base_directory = base_directory
        self._route_file_name = route_file_name
        super().__init__(*args, **kwargs)
        self.build_router()

    def build_router(self):
        for root, dirs, files in os.walk(
            os.path.join(os.getcwd(), self.base_directory)
        ):
            if self.route_file_name + ".py" in files:
                # Import route file
                route_file = importlib.import_module(
                    os.path.relpath(root).replace("/", ".") + "." + self.route_file_name
                )

                # Find routes
                find_routes = [r for r in dir(route_file) if r in METHODS]
                if find_routes:
                    if os.path.basename(root) == self.base_directory:
                        tags = ["default"]
                    else:
                        tags = os.path.relpath(root, self.base_directory).split("/")

                    _router = APIRouter(
                        prefix="/" + os.path.relpath(root, self.base_directory),
                        tags=tags,
                    )

                    for r in find_routes:
                        _router.add_api_route("/", getattr(route_file, r), methods=[r])

                    self.include_router(_router)

    @property
    def base_directory(self):
        return self._base_directory

    @base_directory.setter
    def base_directory(self, value):
        self._base_directory = value

    @property
    def route_file_name(self):
        return self._route_file_name
