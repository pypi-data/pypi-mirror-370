# SPDX-FileCopyrightText: UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

from .. import tokens as to
from ..models import Badge
from ._base import register_badges

register_badges(
    {
        to.SAFERATDAY0_LIBRARY: Badge(
            name=f"saferatday0-library",
            description=f"This component is part of the saferatday0 library.",
            example=f"https://img.shields.io/badge/saferatday0-library-009670?labelColor=303030",
            title=f"saferatday0 library",
            link="https://saferatday0.dev",
            image=f"https://img.shields.io/badge/saferatday0-library-009670?labelColor=303030",
            weight=-100,
        ),
    }
)
