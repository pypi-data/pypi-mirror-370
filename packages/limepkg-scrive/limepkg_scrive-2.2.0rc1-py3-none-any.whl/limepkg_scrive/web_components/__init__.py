import logging
from os.path import dirname, exists, join, realpath

import pkg_resources

logger = logging.getLogger(__name__)


def _get_static_path():
    root_path = realpath(dirname(__file__))
    static = join(root_path, "static")
    dist = join(root_path, "..", "..", "frontend", "dist")
    return static if exists(static) else dist


def _get_static_package_path():
    _root_path = realpath(dirname(__file__))
    _static = join(_root_path, "static_package")
    _frontend = join(_root_path, "..", "..", "frontend")
    return _static if exists(_static) else _frontend


def register_web_components():
    """
    No longer in use
    Still needs to exist, do not remove
    """
    return []


def register_static_content():
    """
    Returns a list with a tuple consisting of the route-name for web-components
    served by this plugin and the path to the dist folder for all
    web-components:

        (lwc-components, path_to_static_content_for_components).
    """

    def _get_plugin_version():
        package_name = __name__.split(".")[0]
        req = pkg_resources.Requirement.parse(package_name)
        working_set = pkg_resources.WorkingSet()
        dist = working_set.find(req)
        return dist.version if dist else None

    version = _get_plugin_version()
    static_path = _get_static_path()
    static_package_path = _get_static_package_path()

    route_name = (
        "lwc-components" if version is None else "lwc-components-{}".format(version)
    )

    package_name = f"lwc-package-{version}" if version else "lwc-package"

    return [(route_name, static_path), (package_name, static_package_path)]
