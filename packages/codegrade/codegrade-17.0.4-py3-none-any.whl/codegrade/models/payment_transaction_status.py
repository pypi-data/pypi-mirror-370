"""The module that defines the ``PaymentTransactionStatus`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

from __future__ import annotations

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from .. import parsers
from ..utils import to_dict
from .transaction import Transaction


@dataclass
class PaymentTransactionStatus:
    """The status when payment for a course has been successfully completed."""

    #: A literal string to identify this payment status type.
    tag: t.Literal["transaction"]
    #: The specific method of payment used.
    transaction: Transaction

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: rqa.FixedMapping(
            rqa.RequiredArgument(
                "tag",
                rqa.StringEnum("transaction"),
                doc="A literal string to identify this payment status type.",
            ),
            rqa.RequiredArgument(
                "transaction",
                parsers.ParserFor.make(Transaction),
                doc="The specific method of payment used.",
            ),
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "tag": to_dict(self.tag),
            "transaction": to_dict(self.transaction),
        }
        return res

    @classmethod
    def from_dict(
        cls: t.Type[PaymentTransactionStatus], d: t.Dict[str, t.Any]
    ) -> PaymentTransactionStatus:
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            tag=parsed.tag,
            transaction=parsed.transaction,
        )
        res.raw_data = d
        return res
