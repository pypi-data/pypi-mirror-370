"""The module that defines the ``TenantCouponUsage`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

from __future__ import annotations

import datetime
import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from .. import parsers
from ..utils import to_dict
from .course_of_tenant_coupon_usage import CourseOfTenantCouponUsage
from .tenant_coupon import TenantCoupon, TenantCouponParser


@dataclass
class TenantCouponUsage:
    """A link that represents the usage of a coupon by a user."""

    #: The scope of the coupon usage
    scope: t.Literal["tenant"]
    #: The id of the coupon usage
    id: str
    #: The moment the coupon was used.
    created_at: datetime.datetime
    coupon: TenantCoupon
    #: The user that used the coupon.
    user_id: int
    #: The course for which the coupon was used.
    course: CourseOfTenantCouponUsage

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: rqa.FixedMapping(
            rqa.RequiredArgument(
                "scope",
                rqa.StringEnum("tenant"),
                doc="The scope of the coupon usage",
            ),
            rqa.RequiredArgument(
                "id",
                rqa.SimpleValue.str,
                doc="The id of the coupon usage",
            ),
            rqa.RequiredArgument(
                "created_at",
                rqa.RichValue.DateTime,
                doc="The moment the coupon was used.",
            ),
            rqa.RequiredArgument(
                "coupon",
                TenantCouponParser,
                doc="",
            ),
            rqa.RequiredArgument(
                "user_id",
                rqa.SimpleValue.int,
                doc="The user that used the coupon.",
            ),
            rqa.RequiredArgument(
                "course",
                parsers.ParserFor.make(CourseOfTenantCouponUsage),
                doc="The course for which the coupon was used.",
            ),
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "scope": to_dict(self.scope),
            "id": to_dict(self.id),
            "created_at": to_dict(self.created_at),
            "coupon": to_dict(self.coupon),
            "user_id": to_dict(self.user_id),
            "course": to_dict(self.course),
        }
        return res

    @classmethod
    def from_dict(
        cls: t.Type[TenantCouponUsage], d: t.Dict[str, t.Any]
    ) -> TenantCouponUsage:
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            scope=parsed.scope,
            id=parsed.id,
            created_at=parsed.created_at,
            coupon=parsed.coupon,
            user_id=parsed.user_id,
            course=parsed.course,
        )
        res.raw_data = d
        return res
