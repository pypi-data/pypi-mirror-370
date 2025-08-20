import time
from functools import cached_property
from pathlib import Path

import pyperclip
import toml
from loguru import logger as log

from . import REPR


class TOMLSubConfig(dict):
    def __init__(self, **kwargs):
        super().__init__()

        # Initialize with annotation defaults first
        annotations = getattr(self.__class__, '__annotations__', {})
        for field_name in annotations:
            if hasattr(self.__class__, field_name):
                default_value = getattr(self.__class__, field_name)
                self[field_name] = default_value
                setattr(self, field_name, default_value)

        # Then update with kwargs, converting sub-dicts to subconfigs
        for k, v in kwargs.items():
            if isinstance(v, dict) and not isinstance(v, TOMLSubConfig):
                # Convert dict to TOMLSubConfig
                v = TOMLSubConfig(**v)
            self[k] = v
            setattr(self, k, v)

    @cached_property
    def __log_repr__(self):
        return f"[{self.__class__.__name__}]"

    @classmethod
    def create(
            cls,
            _source: Path = None,
            _name: str = None,
            prompt_empty_fields=True,
            **kwargs
    ):
        hit = None
        if _source:
            if not _name: _name = cls.__name__.lower()
            log.debug(f"{REPR}: Building subconfig named '{_name}' from {_source}")
            with _source.open('r') as f:
                raw_data = toml.load(f)
                hit = raw_data.get(_name)

        if hit: kwargs = {**hit, **kwargs}

        inst = cls(**kwargs)

        # Check class annotations for required fields
        required_fields = getattr(cls, '__annotations__', {})
        missing_fields = []

        for field_name in required_fields:
            if field_name not in inst or inst[field_name] is None:
                missing_fields.append(field_name)

        if missing_fields:
            log.info(f"{cls.__name__}: Missing fields detected: {missing_fields}")
            for field_name in missing_fields:
                # Check if this field should be a subconfig
                field_type = required_fields.get(field_name)
                if field_type and hasattr(field_type, 'create') and issubclass(field_type, TOMLSubConfig):
                    # Create the subconfig, which will handle its own prompting
                    subconfig = field_type.create()
                    inst[field_name] = subconfig
                    setattr(inst, field_name, subconfig)
                    log.success(f"{cls.__name__}: Created {field_type.__name__} for {field_name}")
                else:
                    if prompt_empty_fields:
                        inst._prompt_field(field_name)
                    else:
                        log.warning(f"{inst}: Skipping empty field '{field_name}'")

        return inst

    def _prompt_field(self, field_name):
        time.sleep(1)
        prompt = f"{self.__log_repr__}: Enter value for '{field_name}' (or press Enter to paste from clipboard): "
        user_input = input(prompt).strip() or pyperclip.paste()
        if not user_input.strip():
            log.debug(f"{self.__log_repr__}: Using clipboard value for {field_name}")
        # Update both dict and attribute
        self[field_name] = user_input
        setattr(self, field_name, user_input)
        time.sleep(1)
        log.success(f"{self.__log_repr__}: Set {field_name}")

    def __setattr__(self, name, value):
        # Keep dict and attributes in sync
        if not name.startswith('_'):
            self[name] = value
        super().__setattr__(name, value)

    def __setitem__(self, name, value):
        # Keep dict and attributes in sync
        super().__setitem__(name, value)
        if not name.startswith('_'):
            super().__setattr__(name, value)

    def as_dict(self):
        return {k: v for k, v in self.items() if not k.startswith('_')}

    def as_list(self):
        return [k for k in self if not k.startswith('_')]


class TOMLConfig(dict):
    _path: Path

    def __init__(self, **kwargs):
        super().__init__()
        # Separate private attributes from config data
        self._private = {}

        # Initialize with annotation defaults first
        annotations = getattr(self.__class__, '__annotations__', {})
        for field_name in annotations:
            if hasattr(self.__class__, field_name):
                default_value = getattr(self.__class__, field_name)
                if field_name.startswith('_'):
                    self._private[field_name] = default_value
                else:
                    self[field_name] = default_value
                    setattr(self, field_name, default_value)

        # Then update with kwargs, converting sub-dicts to subconfigs
        for k, v in kwargs.items():
            if k.startswith('_'):
                self._private[k] = v
                setattr(self, k, v)
            else:
                if isinstance(v, dict) and not isinstance(v, (TOMLSubConfig, TOMLConfig)):
                    # Check if we have a type annotation for this field
                    field_type = annotations.get(k)
                    if field_type and hasattr(field_type, 'create'):
                        v = field_type(**v)
                    else:
                        v = TOMLSubConfig(**v)
                self[k] = v
                setattr(self, k, v)

    @cached_property
    def __log_repr__(self):
        return f"[{self.__class__.__name__}]"

    @classmethod
    def create(
            cls,
            _source: Path = None,
            prompt_empty_fields: bool = True,
            **kwargs
    ):
        # Set up paths first
        if _source:
            path = Path(_source)
            cwd = path.parent
        else:
            cwd = Path.cwd()
            name = cls.__name__.lower()
            path = Path.cwd() / (name + ".toml")

        if path.exists():
            log.info(f"{REPR}: Building config from {path}")
            with path.open('r') as f:
                raw_data = toml.load(f)

            # Process subconfigs in the raw data
            file_data = {}
            for name, value in raw_data.items():
                if isinstance(value, dict):
                    # Check if we already have an instance passed in kwargs
                    if name in kwargs and hasattr(kwargs[name], 'get'):
                        # Use the type of the passed instance
                        field_type = type(kwargs[name])
                        file_data[name] = field_type.create(_source=path, _name=name, **value)
                    else:
                        # Try to get field type from class annotations or defaults
                        field_type = getattr(cls, '__annotations__', {}).get(name)
                        if field_type and hasattr(field_type, 'create'):
                            file_data[name] = field_type.create(_source=path, _name=name, **value)
                        else:
                            file_data[name] = value
                else:
                    file_data[name] = value

            # Merge file data with kwargs
            kwargs = {**file_data, **kwargs}
        else:
            log.warning(f"{REPR}: Config file not found at {path}, creating new one")
            path.touch(exist_ok=True)

        # Add private attributes
        kwargs['_cwd'] = cwd
        kwargs['_path'] = path

        inst = cls(**kwargs)

        # Check class annotations for required fields
        required_fields = getattr(cls, '__annotations__', {})
        missing_fields = []

        for field_name in required_fields:
            if field_name not in inst or inst[field_name] is None:
                missing_fields.append(field_name)

        if missing_fields:
            log.info(f"{cls.__name__}: Missing fields detected: {missing_fields}")
            for field_name in missing_fields:
                # Check if this field should be a subconfig
                field_type = required_fields.get(field_name)
                if field_type and hasattr(field_type, 'create') and issubclass(field_type, TOMLSubConfig):
                    subconfig = field_type.create(path)
                    inst[field_name] = subconfig
                    setattr(inst, field_name, subconfig)
                    log.success(f"{cls.__name__}: Created {field_type.__name__} for {field_name}")
                else:
                    if prompt_empty_fields:
                        inst._prompt_field(field_name)
                    else:
                        log.warning(f"{inst}: Skipping empty field '{field_name}'")

        inst.write(verbose=False)
        return inst

    def __setattr__(self, name, value):
        # Keep dict and attributes in sync, handle private attributes
        if name.startswith('_'):
            if hasattr(self, '_private'):
                self._private[name] = value
            super().__setattr__(name, value)
        else:
            self[name] = value
            super().__setattr__(name, value)

    def __setitem__(self, name, value):
        # Keep dict and attributes in sync
        super().__setitem__(name, value)
        if not name.startswith('_'):
            super().__setattr__(name, value)

    def as_dict(self):
        return {k: v for k, v in self.items() if not k.startswith('_')}

    def as_list(self):
        return [k for k in self if not k.startswith('_')]

    def _prompt_field(self, field_name):
        time.sleep(1)
        prompt = f"{self.__log_repr__}: Enter value for '{field_name}' (or press Enter to paste from clipboard): "
        user_input = input(prompt).strip() or pyperclip.paste()
        if not user_input.strip():
            log.debug(f"{self.__log_repr__}: Using clipboard value for {field_name}")
        # Update both dict and attribute
        self[field_name] = user_input
        setattr(self, field_name, user_input)
        time.sleep(1)
        log.success(f"{self.__log_repr__}: Set {field_name}")

    def write(self, verbose: bool = True):
        if not hasattr(self, '_path') or not self._path:
            raise ValueError("No path set for configuration file")

        config_data = {}
        for name, value in self.items():
            if value is not None and not name.startswith('_'):
                # Check if value is a dict-like config object
                if isinstance(value, dict):
                    config_data[name] = dict(value)
                else:
                    config_data[name] = value

        if verbose: log.debug(f"{REPR}: Writing config to {self._path}")
        with self._path.open('w') as f:
            toml.dump(config_data, f) #type: ignore

    def read(self):
        if not hasattr(self, '_path') or not self._path or not self._path.exists():
            return {}
        log.debug(f"{REPR}: Reading config from {self._path}")
        with self._path.open('r') as f:
            data = toml.load(f)

        # Update self with data from file
        for name, value in data.items():
            if isinstance(value, dict) and name in self:
                # If it's a nested config, update it
                current_obj = self[name]
                if isinstance(current_obj, dict):
                    current_obj.update(value)
                    log.debug(f"{self.__log_repr__}: Updated '{name}' from file!")
            else:
                self[name] = value
                setattr(self, name, value)
                log.debug(f"{self.__log_repr__}: Overrode '{name}' from file!")

        return data
