# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: Copyright The Geneva Authors

import attrs


@attrs.define
class RayOptions:
    docker_image: str | None = attrs.field(
        default=None,
    )
