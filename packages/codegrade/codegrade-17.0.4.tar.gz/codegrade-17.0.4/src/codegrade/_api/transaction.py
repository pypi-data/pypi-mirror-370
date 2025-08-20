"""The endpoints for transaction objects.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

from __future__ import annotations

import os
import typing as t

import cg_request_args as rqa
from cg_maybe import Maybe, Nothing

from .. import parsers, utils

if t.TYPE_CHECKING or os.getenv("CG_EAGERIMPORT", False):
    from .. import client
    from ..models.transaction import Transaction


_ClientT = t.TypeVar("_ClientT", bound="client._BaseClient")


class TransactionService(t.Generic[_ClientT]):
    __slots__ = ("__client",)

    def __init__(self, client: _ClientT) -> None:
        self.__client = client

    def get(
        self: TransactionService[client.AuthenticatedClient],
        *,
        transaction_id: str,
    ) -> Transaction:
        """Get a transaction by id.

        :param transaction_id: The id of the transaction you want to get.

        :returns: The found transaction.
        """

        url = "/api/v1/transactions/{transactionId}".format(
            transactionId=transaction_id
        )
        params = None

        with self.__client as client:
            resp = client.http.get(url=url, params=params)
        utils.log_warnings(resp)

        if utils.response_code_matches(resp.status_code, 200):
            from ..models.transaction import Transaction

            return parsers.JsonResponseParser(
                parsers.ParserFor.make(Transaction)
            ).try_parse(resp)

        from ..models.any_error import AnyError

        raise utils.get_error(
            resp,
            (
                (
                    (400, 409, 401, 403, 404, 429, 500),
                    utils.unpack_union(AnyError),
                ),
            ),
        )

    def refund(
        self: TransactionService[client.AuthenticatedClient],
        *,
        transaction_id: str,
    ) -> Transaction:
        """Refund a transaction.

        :param transaction_id: The id of the transaction you want to get.

        :returns: The found transaction.
        """

        url = "/api/v1/transactions/{transactionId}/refund".format(
            transactionId=transaction_id
        )
        params = None

        with self.__client as client:
            resp = client.http.post(url=url, params=params)
        utils.log_warnings(resp)

        if utils.response_code_matches(resp.status_code, 200):
            from ..models.transaction import Transaction

            return parsers.JsonResponseParser(
                parsers.ParserFor.make(Transaction)
            ).try_parse(resp)

        from ..models.any_error import AnyError

        raise utils.get_error(
            resp,
            (
                (
                    (400, 409, 401, 403, 404, 429, 500),
                    utils.unpack_union(AnyError),
                ),
            ),
        )
