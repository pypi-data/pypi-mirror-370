"""The module that defines the ``PaymentPendingStatus`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

from __future__ import annotations

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from .. import parsers
from ..utils import to_dict
from .course_price import CoursePrice


@dataclass
class PaymentPendingStatus:
    """The status when payment for a course is required but not yet made."""

    #: A literal string to identify this payment status type.
    tag: t.Literal["pending"]
    #: The price of this course.
    price: CoursePrice

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: rqa.FixedMapping(
            rqa.RequiredArgument(
                "tag",
                rqa.StringEnum("pending"),
                doc="A literal string to identify this payment status type.",
            ),
            rqa.RequiredArgument(
                "price",
                parsers.ParserFor.make(CoursePrice),
                doc="The price of this course.",
            ),
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "tag": to_dict(self.tag),
            "price": to_dict(self.price),
        }
        return res

    @classmethod
    def from_dict(
        cls: t.Type[PaymentPendingStatus], d: t.Dict[str, t.Any]
    ) -> PaymentPendingStatus:
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            tag=parsed.tag,
            price=parsed.price,
        )
        res.raw_data = d
        return res
