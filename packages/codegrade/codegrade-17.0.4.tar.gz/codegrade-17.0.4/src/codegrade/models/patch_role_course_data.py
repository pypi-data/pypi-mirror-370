"""The module that defines the ``PatchRoleCourseData`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

from __future__ import annotations

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from .. import parsers
from ..utils import to_dict
from .course_permission import CoursePermission


@dataclass
class PatchRoleCourseData:
    """Input data required for the `Course::PatchRole` operation."""

    #: The name of the permission to change.
    permission: CoursePermission
    #: The value to set the permission to (`True` means the specified role has
    #: the specified permission).
    value: bool

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: rqa.FixedMapping(
            rqa.RequiredArgument(
                "permission",
                rqa.EnumValue(CoursePermission),
                doc="The name of the permission to change.",
            ),
            rqa.RequiredArgument(
                "value",
                rqa.SimpleValue.bool,
                doc="The value to set the permission to (`True` means the specified role has the specified permission).",
            ),
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "permission": to_dict(self.permission),
            "value": to_dict(self.value),
        }
        return res

    @classmethod
    def from_dict(
        cls: t.Type[PatchRoleCourseData], d: t.Dict[str, t.Any]
    ) -> PatchRoleCourseData:
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            permission=parsed.permission,
            value=parsed.value,
        )
        res.raw_data = d
        return res
