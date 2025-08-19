# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from dataclasses import dataclass

from ._attribute_abc import _Attribute


@dataclass
class _VectorAttribute(_Attribute):
    ATTRIBUTE_TYPE_IDENTIFIER = "vector"
    PYTHON_TYPE = list
