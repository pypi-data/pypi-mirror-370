"""The module that defines the ``PaymentCouponUsageStatus`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

from __future__ import annotations

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from ..utils import to_dict


@dataclass
class PaymentCouponUsageStatus:
    """A payment method representing the use of a course or tenant coupon."""

    #: A literal string to identify this payment method type.
    tag: t.Literal["coupon-usage"]

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: rqa.FixedMapping(
            rqa.RequiredArgument(
                "tag",
                rqa.StringEnum("coupon-usage"),
                doc="A literal string to identify this payment method type.",
            ),
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "tag": to_dict(self.tag),
        }
        return res

    @classmethod
    def from_dict(
        cls: t.Type[PaymentCouponUsageStatus], d: t.Dict[str, t.Any]
    ) -> PaymentCouponUsageStatus:
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            tag=parsed.tag,
        )
        res.raw_data = d
        return res
