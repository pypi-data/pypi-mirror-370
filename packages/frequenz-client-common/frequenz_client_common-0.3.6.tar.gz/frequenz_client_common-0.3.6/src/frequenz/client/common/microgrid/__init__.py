# License: MIT
# Copyright © 2023 Frequenz Energy-as-a-Service GmbH

"""Frequenz microgrid definition."""

from typing import final

from frequenz.core.id import BaseId


@final
class EnterpriseId(BaseId, str_prefix="EID"):
    """A unique identifier for an enterprise account."""


@final
class MicrogridId(BaseId, str_prefix="MID"):
    """A unique identifier for a microgrid."""
