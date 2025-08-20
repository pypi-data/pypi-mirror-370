"""The module that defines the ``BaseTenantCoupon`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

from __future__ import annotations

import datetime
import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from ..utils import to_dict


@dataclass
class BaseTenantCoupon:
    """The base representation of a tenant coupon."""

    #: The id of the coupon
    id: str
    #: The moment the coupon was created.
    created_at: datetime.datetime
    #: The maximum amount of times the coupon can be used. If it is `None` the
    #: coupon can be used for an unlimited amount.
    limit: t.Optional[int]
    #: The scope of validity of the coupon. Used to discriminate from Coupon.
    scope: t.Literal["tenant"]
    #: The id of the tenant for this coupon.
    tenant_id: str
    #: The amount of times it has been used.
    used_amount: int

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: rqa.FixedMapping(
            rqa.RequiredArgument(
                "id",
                rqa.SimpleValue.str,
                doc="The id of the coupon",
            ),
            rqa.RequiredArgument(
                "created_at",
                rqa.RichValue.DateTime,
                doc="The moment the coupon was created.",
            ),
            rqa.RequiredArgument(
                "limit",
                rqa.Nullable(rqa.SimpleValue.int),
                doc="The maximum amount of times the coupon can be used. If it is `None` the coupon can be used for an unlimited amount.",
            ),
            rqa.RequiredArgument(
                "scope",
                rqa.StringEnum("tenant"),
                doc="The scope of validity of the coupon. Used to discriminate from Coupon.",
            ),
            rqa.RequiredArgument(
                "tenant_id",
                rqa.SimpleValue.str,
                doc="The id of the tenant for this coupon.",
            ),
            rqa.RequiredArgument(
                "used_amount",
                rqa.SimpleValue.int,
                doc="The amount of times it has been used.",
            ),
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "id": to_dict(self.id),
            "created_at": to_dict(self.created_at),
            "limit": to_dict(self.limit),
            "scope": to_dict(self.scope),
            "tenant_id": to_dict(self.tenant_id),
            "used_amount": to_dict(self.used_amount),
        }
        return res

    @classmethod
    def from_dict(
        cls: t.Type[BaseTenantCoupon], d: t.Dict[str, t.Any]
    ) -> BaseTenantCoupon:
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            id=parsed.id,
            created_at=parsed.created_at,
            limit=parsed.limit,
            scope=parsed.scope,
            tenant_id=parsed.tenant_id,
            used_amount=parsed.used_amount,
        )
        res.raw_data = d
        return res
