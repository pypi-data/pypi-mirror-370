# TooManyConfigs

A simple Python library for TOML-based configuration with interactive setup and clipboard integration.

## Installation

```bash
pip install toomanyconfigs
```

## Basic Usage

```python
from toomanyconfigs import TOMLConfig

class Test(TOMLConfig):
    foo: str = None  # Each field that should prompt user input should be 'None'

if __name__ == "__main__":
    Test.create()  # Without specifying a path, TOMLConfig will automatically make a .toml in your cwd with the name of your inheriting class.
```

Output:
```
WARNING  | toomanyconfigs.core:create:164 - [TooManyConfigs]: Config file not found, creating new one
INFO     | toomanyconfigs.core:create:182 - [Test]: Missing fields detected: ['foo']
[Test]: Enter value for 'foo' (or press Enter to paste from clipboard): bar
SUCCESS  | toomanyconfigs.core:_prompt_field:226 - [Test]: Set foo
```

## Advanced Usage

```python
from toomanyconfigs import TOMLConfig
from loguru import logger as log

class Test2(TOMLConfig):
    foo: str = None
    bar: int = 33  # We'll set bar at 33 to demonstrate the translation ease between dynamic python objects and .toml

if __name__ == "__main__":
    t = Test2.create()  # initialize a dataclass from a .toml
    log.debug(t.bar)  # view t.bar
    t.bar = 34  # override python memory
    log.debug(t.bar)  # view updated t.bar
    t.write()  # write to the specified .toml file
    data = t.read()  # ensure overwriting
    log.debug(data)
```

Output:
```
#Example STDOUT
# WARNING  | toomanyconfigs.core:create:191 - [TooManyConfigs]: Config file not found at C:\Users\foobar\PycharmProjects\TooManyConfigs\src\test2.toml, creating new one
# INFO     | toomanyconfigs.core:create:209 - Test2: Missing fields detected: ['foo']
# [Test2]: Enter value for 'foo' (or press Enter to paste from clipboard): bar
# SUCCESS  | toomanyconfigs.core:_prompt_field:258 - [Test2]: Set foo
# DEBUG    | __main__:<module>:31 - 33
# DEBUG    | __main__:<module>:33 - 34
# DEBUG    | toomanyconfigs.core:write:273 - [TooManyConfigs]: Writing config to C:\Users\foobar\PycharmProjects\TooManyConfigs\src\test2.toml
# DEBUG    | toomanyconfigs.core:read:280 - [TooManyConfigs]: Reading config from C:\Users\foobar\PycharmProjects\TooManyConfigs\src\test2.toml
# DEBUG    | toomanyconfigs.core:read:295 - [Test2]: Overrode 'foo' from file!
# DEBUG    | toomanyconfigs.core:read:295 - [Test2]: Overrode 'bar' from file!
# DEBUG    | __main__:<module>:36 - {'foo': 'bar', 'bar': 34}
# WARNING  | toomanyconfigs.core:create:191 - [TooManyConfigs]: Config file not found at C:\Users\foobar\PycharmProjects\TooManyConfigs\src\test2.toml, creating new one
# DEBUG    | __main__:<module>:47 - 99
# DEBUG    | toomanyconfigs.core:read:280 - [TooManyConfigs]: Reading config from C:\Users\foobar\PycharmProjects\TooManyConfigs\src\test2.toml
# DEBUG    | toomanyconfigs.core:read:295 - [Test2]: Overrode 'foo' from file!
# DEBUG    | toomanyconfigs.core:read:295 - [Test2]: Overrode 'bar' from file!
# DEBUG    | __main__:<module>:49 - {'foo': 'resurrected_bar', 'bar': 99}
```

## Subconfigs

```python
from toomanyconfigs import TOMLConfig, TOMLSubConfig
from loguru import logger as log

class Test4(TOMLSubConfig):
    foo: str = None

class Test3(TOMLConfig):
    key: str = "val"
    sub_config: Test4

if __name__ == "__main__":
    t = Test3.create()
    log.debug(t.__dict__)
```

Output:
```
WARNING  | toomanyconfigs.core:create:164 - [TooManyConfigs]: Config file not found, creating new one
INFO     | toomanyconfigs.core:create:182 - [Test3]: Missing fields detected: ['sub_config']
DEBUG    | toomanyconfigs.core:create:39 - [TooManyConfigs]: Building subconfig named 'test4'
INFO     | toomanyconfigs.core:create:57 - [Test4]: Missing fields detected: ['foo']
[Test4]: Enter value for 'foo' (or press Enter to paste from clipboard): bar
SUCCESS  | toomanyconfigs.core:_prompt_field:73 - [Test4]: Set foo
SUCCESS  | toomanyconfigs.core:create:190 - [Test3]: Created Test4 for sub_config
```

## API Configurations

### Basic API Usage

```python
import asyncio
from toomanyconfigs import API
from loguru import logger as log

if __name__ == "__main__":
    obj = API()
    response = asyncio.run(obj.api_request("get"))
    log.debug(response)
```

Output:
```
WARNING  | toomanyconfigs.core:create:179 - [TooManyConfigs]: Config file not found, creating new one
INFO     | toomanyconfigs.core:create:197 - APIConfig: Missing fields detected: ['headers', 'routes', 'vars']
DEBUG    | toomanyconfigs.core:create:41 - [TooManyConfigs]: Building subconfig named 'headersconfig'
SUCCESS  | toomanyconfigs.core:create:205 - APIConfig: Created HeadersConfig for headers
INFO     | toomanyconfigs.core:create:59 - RoutesConfig: Missing fields detected: ['base', 'shortcuts']
[RoutesConfig]: Enter value for 'base' (or press Enter to paste from clipboard): http://example.com
SUCCESS  | toomanyconfigs.core:_prompt_field:84 - [RoutesConfig]: Set base
SUCCESS  | toomanyconfigs.core:create:68 - RoutesConfig: Created Shortcuts for shortcuts
DEBUG    | toomanyconfigs.api:api_request:146 - Attempting request to API: method=get, path=http://example.com
```

Generated TOML:
```toml
[headers]
authorization = "Bearer ${API_KEY}"
accept = "application/json"

[routes]
base = "http://example.com"

[vars]

[routes.shortcuts]
```

### Advanced API Usage

```python
import asyncio
from dataclasses import field
from pathlib import Path
from toomanyconfigs import API, APIConfig, HeadersConfig, RoutesConfig, VarsConfig, Shortcuts
from loguru import logger as log

if __name__ == "__main__":
    src = (Path.cwd() / "json_api.toml")
    src.touch(exist_ok=True)

    base_url = 'https://jsonplaceholder.typicode.com/'
    quick_routes = {
        "c": "/comments?postId=1"
    }
    routes = RoutesConfig(
        base=base_url,
        shortcuts=Shortcuts.create(_source=src, **quick_routes)
    )


    class JSONVars(VarsConfig):
        api_key: str = None


    json_vars = JSONVars.create(
        source=src,
        name="vars"
    )

    cfg = APIConfig.create(_source=src, routes=routes, vars=json_vars)
    json_placeholder = API(cfg)
    log.debug(json_placeholder.config.__dict__)
    response = asyncio.run(json_placeholder.api_get("c"))
    log.debug(response)
```

Output:
```
DEBUG    | toomanyconfigs.core:create:41 - [TooManyConfigs]: Building subconfig named 'shortcuts'
DEBUG    | toomanyconfigs.core:create:41 - [TooManyConfigs]: Building subconfig named 'vars'
INFO     | toomanyconfigs.core:create:59 - JSONVars: Missing fields detected: ['api_key']
[JSONVars]: Enter value for 'api_key' (or press Enter to paste from clipboard): ****
SUCCESS  | toomanyconfigs.core:_prompt_field:84 - [JSONVars]: Set api_key
DEBUG    | toomanyconfigs.core:create:153 - [TooManyConfigs]: Building config from json_api.toml
INFO     | toomanyconfigs.core:create:197 - APIConfig: Missing fields detected: ['headers']
SUCCESS  | toomanyconfigs.core:create:205 - APIConfig: Created HeadersConfig for headers
DEBUG    | toomanyconfigs.api:api_request:146 - Attempting request to API: method=get, path=https://jsonplaceholder.typicode.com//comments?postId=1
DEBUG    | __main__:<module>:151 - Response(status=200, method='get', body=[...])
```

Generated TOML:
```toml
[routes]
base = "https://jsonplaceholder.typicode.com/"

[vars]
api_key = "****"

[headers]
authorization = "Bearer ${API_KEY}"
accept = "application/json"

[routes.shortcuts]
c = "/comments?postId=1"
```