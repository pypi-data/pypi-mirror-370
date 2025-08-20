REPR = "[TooManyConfigs]"
ACTIVE_CFGS = {}
DEBUG = False
from .core import TOMLConfig, TOMLSubConfig
from .api import API, APIConfig, HeadersConfig, RoutesConfig, VarsConfig, Shortcuts, Response
from .cwd import CWD