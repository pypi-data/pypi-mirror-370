"""The module that defines the ``Transaction`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

from __future__ import annotations

import datetime
import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from .. import parsers
from ..utils import to_dict
from .course_price import CoursePrice
from .transaction_state import TransactionState


@dataclass
class Transaction:
    """A transaction by a user."""

    #: The id of the transaction.
    id: str
    #: The state of the transaction.
    state: TransactionState
    #: The `CoursePrice` that this transaction pays for.
    course_price: CoursePrice
    #: The moment the payment was successful, this will always be not `None`
    #: when `state` is `success`.
    success_at: t.Optional[datetime.datetime]
    #: The moment this transaction was last updated.
    updated_at: datetime.datetime
    #: The short id of the transaction.
    short_id: str

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: rqa.FixedMapping(
            rqa.RequiredArgument(
                "id",
                rqa.SimpleValue.str,
                doc="The id of the transaction.",
            ),
            rqa.RequiredArgument(
                "state",
                rqa.EnumValue(TransactionState),
                doc="The state of the transaction.",
            ),
            rqa.RequiredArgument(
                "course_price",
                parsers.ParserFor.make(CoursePrice),
                doc="The `CoursePrice` that this transaction pays for.",
            ),
            rqa.RequiredArgument(
                "success_at",
                rqa.Nullable(rqa.RichValue.DateTime),
                doc="The moment the payment was successful, this will always be not `None` when `state` is `success`.",
            ),
            rqa.RequiredArgument(
                "updated_at",
                rqa.RichValue.DateTime,
                doc="The moment this transaction was last updated.",
            ),
            rqa.RequiredArgument(
                "short_id",
                rqa.SimpleValue.str,
                doc="The short id of the transaction.",
            ),
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "id": to_dict(self.id),
            "state": to_dict(self.state),
            "course_price": to_dict(self.course_price),
            "success_at": to_dict(self.success_at),
            "updated_at": to_dict(self.updated_at),
            "short_id": to_dict(self.short_id),
        }
        return res

    @classmethod
    def from_dict(
        cls: t.Type[Transaction], d: t.Dict[str, t.Any]
    ) -> Transaction:
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            id=parsed.id,
            state=parsed.state,
            course_price=parsed.course_price,
            success_at=parsed.success_at,
            updated_at=parsed.updated_at,
            short_id=parsed.short_id,
        )
        res.raw_data = d
        return res
