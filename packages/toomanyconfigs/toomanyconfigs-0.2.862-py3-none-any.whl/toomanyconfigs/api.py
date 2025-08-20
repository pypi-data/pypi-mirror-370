import json
from dataclasses import dataclass, field
from functools import cached_property
from pathlib import Path
from typing import Any, Dict, Optional

import httpx
from loguru import logger as log

from . import TOMLSubConfig, DEBUG
from .core import TOMLConfig


class HeadersConfig(TOMLSubConfig):
    """Configuration for HTTP headers"""
    authorization: str = "Bearer ${API_KEY}"
    accept: str = "application/json"

    def to_headers(self):
        return self.as_dict()


class Shortcuts(TOMLSubConfig):
    pass


class RoutesConfig(TOMLSubConfig):
    """Configuration for URLs and shortcuts"""
    base: str = None
    shortcuts: Shortcuts

    def get(self, item):
        return str(self.base + self.shortcuts[item])


class VarsConfig(TOMLSubConfig):
    """Configuration for variable substitution"""


class APIConfig(TOMLConfig):
    """Main API configuration with sub-configs"""
    headers: HeadersConfig
    routes: RoutesConfig
    vars: VarsConfig

    def apply_variable_substitution(self):
        """Apply variable substitution recursively to all dict values"""
        vars_dict = self.vars
        if DEBUG:
            log.debug(f"[{self.__class__.__name__}]: Starting variable substitution with vars: {vars_dict}")

        self._substitute_dict_values(self, vars_dict)
        if DEBUG:
            log.debug(f"[{self.__class__.__name__}]: Variable substitution complete")

    def _substitute_dict_values(self, obj, vars_dict: dict):
        """Recursively substitute variables in all string values within dict-like objects"""
        if DEBUG:
            log.debug(f"[{self.__class__.__name__}]: Processing dict-like object: {type(obj).__name__}")

        # Handle both regular dicts and dict-like config objects
        if hasattr(obj, 'items'):
            items = obj.items()
        elif hasattr(obj, '__dict__'):
            items = obj.__dict__.items()
        else:
            if DEBUG:
                log.debug(f"[{self.__class__.__name__}]: Object {type(obj).__name__} is not dict-like, skipping")
            return

        for key, value in items:
            if key.startswith('_'):
                continue  # Skip private attributes

            if DEBUG:
                log.debug(
                    f"[{self.__class__.__name__}]: Processing key '{key}' with value: {value} (type: {type(value).__name__})")

            if isinstance(value, str):
                # Apply variable substitution to string
                original_value = value
                new_value = value

                for var_key, var_val in vars_dict.items():
                    if var_val:
                        old_value = new_value
                        new_value = new_value.replace(f"${{{var_key.upper()}}}", str(var_val))
                        new_value = new_value.replace(f"${var_key.upper()}", str(var_val))
                        if old_value != new_value and DEBUG:
                            log.debug(
                                f"[{self.__class__.__name__}]: Replaced '{var_key}' in '{key}': {old_value} → {new_value}")

                if original_value != new_value:
                    log.success(
                        f"[{self.__class__.__name__}]: Final substitution for '{key}': {original_value} → {new_value}")
                    try:
                        if hasattr(obj, 'items'):
                            obj[key] = new_value  # Regular dict
                        else:
                            setattr(obj, key, new_value)  # Config object
                    except (AttributeError, TypeError) as e:
                        if DEBUG:
                            log.debug(f"[{self.__class__.__name__}]: Cannot set '{key}': {e}")
                elif DEBUG:
                    log.debug(f"[{self.__class__.__name__}]: No changes for '{key}'")

            elif isinstance(value, (dict, object)) and not isinstance(value, (int, float, bool, list, tuple, str)):
                # Recurse into dict-like objects
                if DEBUG:
                    log.debug(f"[{self.__class__.__name__}]: Recursing into '{key}'")
                self._substitute_dict_values(value, vars_dict)

            elif DEBUG:
                log.debug(f"[{self.__class__.__name__}]: Skipping '{key}' (type: {type(value).__name__})")


class Headers:
    """Container for HTTP headers used in outgoing API requests."""
    index: Dict[str, str]
    accept: Optional[str] = None

    def __post_init__(self):
        self.accept = self.accept or "application/json"
        self.index["Accept"] = self.accept
        for k, v in self.index.items():
            setattr(self, k.lower().replace("-", "_"), v)
        if not self._validate():
            log.error("[Headers] Validation failed")

    def _validate(self) -> bool:
        try:
            if not isinstance(self.index, dict):
                raise TypeError
            for k, v in self.index.items():
                if not isinstance(k, str) or not isinstance(v, str):
                    raise ValueError
        except Exception as e:
            log.error(f"[Headers] Invalid headers: {e}")
            return False
        return True

    @cached_property
    def as_dict(self):
        return self.index


class _API:
    def __init__(self, config: APIConfig | Path = None):
        if isinstance(config, APIConfig):
            self.config = config
        elif isinstance(config, Path) or config is None:
            self.config = APIConfig.create(config)
        else:
            raise TypeError("Config must be 'APIConfig', Path, or None")


@dataclass
class Request:
    method: str
    path: str
    headers: dict
    force_refresh: bool = False
    kwargs: dict = field(default_factory=dict)

    @property
    def as_dict(self) -> dict:
        return self.__dict__.copy()


@dataclass
class Response:
    status: int
    method: str
    headers: dict
    body: Any

    @property
    def as_dict(self) -> dict:
        return self.__dict__.copy()

    @property
    def as_serialized_dict(self) -> dict:
        index = self.as_dict
        for key, value in index.items():
            index[key] = str(value)
        return index


class ResponseFields:
    path: str
    status: str
    method: str
    headers: str
    body: str


class Receptionist(_API):
    cache: dict[str | Response] = {}
    database: Any

    def __init__(self, config: APIConfig | Path | None = None, database: bool = False):
        from p2d2 import Database
        _API.__init__(self, config)

        class APIDB(Database):
            responses: ResponseFields

        if database:
            self.database: Database = APIDB(db_name=self.__class__.__name__)

    def __repr__(self):
        return f"[{self.__class__.__name__}]"

    @property
    def database_enabled(self):
        return bool(getattr(self, "database", None))

    @property
    def cache_enabled(self):
        return not self.database_enabled

    def _build_path(self, route: str = None, append: str = "", format: dict = None):
        """Build the full request path"""
        if not route:
            path = self.config.routes.base
        else:
            try:
                path = self.config.routes.get(route)
            except KeyError:
                path = self.config.routes.base + str(route)

        if format:
            path = path.format(**format)
        if append:
            path += append
        return path

    def _build_headers(self, append_headers: dict = None, override_headers: dict = None):
        """Build request headers"""
        if override_headers:
            return override_headers

        headers = self.config.headers.to_headers()
        if append_headers:
            headers.update(append_headers)
        return headers

    def _check_cache(self, path: str, method: str, force_refresh: bool):
        """Check cache for existing response"""
        if force_refresh:
            return None

        if self.database_enabled:
            from p2d2 import Database
            df = getattr(self.database, "responses")
            match = df[(df['path'] == path) & (df['method'] == method)]
            if not match.empty:
                first_match = match.iloc[0]
                log.debug(f"{self}: Database hit for {method.upper()} {path}")
                try:
                    return Response(
                        status=int(first_match['status']),
                        method=first_match['method'],
                        headers=first_match['headers'],
                        body=first_match['body']
                    )
                except (json.JSONDecodeError, ValueError) as e:
                    log.warning(f"{self}: Error deserializing cached response: {e}")
                    return None
            return None

        elif self.cache_enabled:
            if path not in self.cache:
                return None

            cached = self.cache[path]
            if cached.method == method:
                log.debug(f"{self}: Cache hit for {method.upper()} {path}")
                return cached
            else:
                log.warning(f"{self}: Cache method mismatch: {cached.method} != {method}")
                return None

        log.warning(f"{self}: Neither cache nor database enabled")
        return None

    def _make_response(self, request: Request, httpx_response, method: str, signature: str = None) -> Response:
        """Convert httpx response to our Response object"""
        try:
            content_type = httpx_response.headers.get("Content-Type", "")
            content = httpx_response.json() if "json" in content_type else httpx_response.text
        except Exception as e:
            content = httpx_response.text
            log.warning(f"{self}: Response decode error: {e}")

        resp = Response(
            status=httpx_response.status_code,
            method=method,
            headers=dict(httpx_response.headers),
            body=content,
        )

        if self.database_enabled:
            data = resp.as_serialized_dict
            data["path"] = request.path
            try:
                from p2d2 import Database
                self.database: Database
                self.database.create("responses", signature, **data)
            except Exception as e:
                log.warning(f"{self}: Could not persist request to database: {e}")

        return resp

    def _prep_request(self, method: str, **kwargs):
        """Prepare request parameters"""
        request = Request(
            method=method,
            path=self._build_path(kwargs.pop('route', None),
                                  kwargs.pop('append', ''),
                                  kwargs.pop('format', None)),
            headers=self._build_headers(kwargs.pop('append_headers', None),
                                        kwargs.pop('override_headers', None)),
            force_refresh=kwargs.pop('force_refresh', False),
            kwargs=kwargs
        )

        log.info(f"{self}: {request.method.upper()} request to {request.path}")

        # Check cache first
        if cached := self._check_cache(request.path, request.method, request.force_refresh):
            return cached

        return request

    def sync_api_request(self, method: str, signature: str = None, **kwargs) -> Response | None:
        result = self._prep_request(method, **kwargs)

        if isinstance(result, Response):
            return result
        elif isinstance(result, Request):
            request: Request = result
            with httpx.Client(headers=request.headers) as client:
                response = client.request(request.method.upper(), request.path, **request.kwargs)

            out = self._make_response(request, response, request.method, signature=signature)
            if self.cache_enabled:
                self.cache[request.path] = out
            return out

    async def api_request(self, method: str, signature: str = None, **kwargs) -> Response:
        result = self._prep_request(method, **kwargs)

        # If it's a Response, return it (cache hit)
        if isinstance(result, Response):
            return result

        # Otherwise it's a Request object, make the request
        request: Request = result
        async with httpx.AsyncClient(headers=request.headers) as client:
            response = await client.request(request.method.upper(), request.path, **request.kwargs)

        out = self._make_response(request, response, request.method, signature=signature)
        if self.cache_enabled:
            self.cache[request.path] = out
        return out

    # Async methods
    async def api_get(self, route=None, signature: str = None, **kwargs):
        return await self.api_request("get", route=route, signature=signature, **kwargs)

    async def api_post(self, route=None, signature: str = None, **kwargs):
        return await self.api_request("post", route=route, signature=signature, **kwargs)

    async def api_put(self, route=None, signature: str = None, **kwargs):
        return await self.api_request("put", route=route, signature=signature, **kwargs)

    async def api_delete(self, route=None, signature: str = None, **kwargs):
        return await self.api_request("delete", route=route, signature=signature, **kwargs)

    # Sync methods
    def sync_api_get(self, route=None, signature: str = None, **kwargs):
        return self.sync_api_request("get", route=route, signature=signature, **kwargs)

    def sync_api_post(self, route=None, signature: str = None, **kwargs):
        return self.sync_api_request("post", route=route, signature=signature, **kwargs)

    def sync_api_put(self, route=None, signature: str = None, **kwargs):
        return self.sync_api_request("put", route=route, signature=signature, **kwargs)

    def sync_api_delete(self, route=None, signature: str = None, **kwargs):
        return self.sync_api_request("delete", route=route, signature=signature, **kwargs)

API = Receptionist