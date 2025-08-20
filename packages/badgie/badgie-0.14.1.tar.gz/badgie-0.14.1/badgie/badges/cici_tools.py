# SPDX-FileCopyrightText: UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

from .. import tokens as to
from ..models import Badge
from ._base import register_badges

register_badges(
    {
        to.CICI_TOOLS: Badge(
            name="cici",
            description="This project uses [cici](https://gitlab.com/saferatday0/cici).",
            example="https://img.shields.io/badge/%E2%9A%A1_cici-enabled-c0ff33",
            title="cici enabled",
            link="https://gitlab.com/saferatday0/cici",
            image="https://img.shields.io/badge/%E2%9A%A1_cici-enabled-c0ff33",
            weight=20,
        ),
    }
)
