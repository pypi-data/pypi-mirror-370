# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: Copyright The Geneva Authors

import functools
from enum import Enum

import attrs

from geneva.config import ConfigBase


class TqdmMode(Enum):
    AUTO = "auto"
    SLACK = "slack"

    @staticmethod
    def from_str(s: str) -> "TqdmMode":
        return TqdmMode(s)


@attrs.define
class TqdmSlackConfig(ConfigBase):
    token: str | None = attrs.field(default=None)
    channel: str | None = attrs.field(default=None)
    mininterval: float | None = attrs.field(
        default=None, converter=attrs.converters.optional(float)
    )

    @classmethod
    def name(cls) -> str:
        return "slack"


@attrs.define
class TqdmConfig(ConfigBase):
    slack_config: TqdmSlackConfig | None = attrs.field(default=None)

    mode: TqdmMode = attrs.field(default=TqdmMode.AUTO, converter=TqdmMode.from_str)

    @classmethod
    def name(cls) -> str:
        return "tqdm"


_tqdm_config = TqdmConfig.get()
if _tqdm_config.mode == TqdmMode.AUTO:
    from tqdm.auto import tqdm
elif _tqdm_config.mode == TqdmMode.SLACK:
    from tqdm.contrib.slack import tqdm

    if (config := _tqdm_config.slack_config) is not None:
        args = {
            **({"token": config.token} if config.token is not None else {}),
            **({"channel": config.channel} if config.channel is not None else {}),
            **(
                {"mininterval": config.mininterval}
                if config.mininterval is not None
                else {}
            ),
        }
        tqdm = functools.partial(tqdm, **args)
else:
    raise ValueError(f"Unknown tqdm mode: {_tqdm_config.mode}")

__all__ = ["tqdm"]
