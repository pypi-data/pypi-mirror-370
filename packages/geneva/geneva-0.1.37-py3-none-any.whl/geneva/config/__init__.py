# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: Copyright The Geneva Authors

# module for configuration
import abc
import functools
import inspect
import itertools
import logging
import os
from pathlib import Path
from types import UnionType

from typing_extensions import Self

from geneva.config.loader import (
    ConfigLoader,
    ConfigResolver,
    chain,
    from_env,
    from_file,
    from_kv,
    from_pyproject,
    loader,
)

_LOG = logging.getLogger(__name__)


class ConfigBase(abc.ABC):
    @classmethod
    @abc.abstractmethod
    def name(cls) -> str:
        """Return the name of the configuration dict to extract"""

    @classmethod
    def from_loader(cls, data: ConfigLoader) -> Self:
        """Populate the configuration from a loader"""
        subloader = data.get(cls.name(), {})

        args = {}
        for arg, arg_type in inspect.get_annotations(cls).items():
            # handle Optional
            is_optional = False
            if isinstance(arg_type, UnionType):
                if len(arg_type.__args__) == 2 and arg_type.__args__[1] is type(None):
                    arg_type = arg_type.__args__[0]
                    is_optional = True
                else:
                    raise ValueError(f"Union type {arg_type} not supported")
            if issubclass(arg_type, ConfigBase):
                try:
                    args[arg] = arg_type.from_loader(subloader) if subloader else None
                except KeyError:
                    if not is_optional:
                        raise
                    _LOG.debug(
                        f"Optional key {arg} not found in {cls.name()},"
                        " treating as None"
                    )
            else:
                # if the key is not present, the default value is used, don't pass None
                if (value := subloader.get(arg, None)) is not None:
                    args[arg] = value

        return cls(**args)

    @classmethod
    @functools.lru_cache(None)
    def get(cls) -> Self:
        """
        Get the configuration from the global loader

        This method caches all configurations objects, so repeated calls
        to this method will return the same object instance

        This also means that if you change the configuration, no effect
        will be seen until the process is restarted -- you shouldn't be
        changing the configuration after initialization anyway
        """
        return cls.from_loader(_CONFIG_LOADER)


_CONFIG_DIR = Path(os.environ.get("GENEVA_CONFIG_DIR", "./.config")).absolute()

_CONFIG_CHAIN = chain(
    from_env(),
    from_pyproject(),
    *[
        from_file(Path(f))
        for f in sorted(
            itertools.chain(
                _CONFIG_DIR.glob("*.json"),
                _CONFIG_DIR.glob("*.yaml"),
                _CONFIG_DIR.glob("*.yml"),
                _CONFIG_DIR.glob("*.toml"),
            )
        )
    ],
)

_CONFIG_LOADER = loader(_CONFIG_CHAIN)


def override_config(config: ConfigResolver) -> None:
    """Add a configuration override, which will be applied first"""
    global _CONFIG_CHAIN
    _CONFIG_CHAIN.push_front(config)


def override_config_kv(config: dict[str, str]) -> None:
    """Add a configuration override from a dictionary of key-value pairs"""
    override_config(from_kv(config))


def default_config(config: ConfigResolver) -> None:
    """Add a configuration defaults, which will be applied last"""
    global _CONFIG_CHAIN
    _CONFIG_CHAIN.push_back(config)


__all__ = ["ConfigBase", "override_config", "default_config", "override_config_kv"]
