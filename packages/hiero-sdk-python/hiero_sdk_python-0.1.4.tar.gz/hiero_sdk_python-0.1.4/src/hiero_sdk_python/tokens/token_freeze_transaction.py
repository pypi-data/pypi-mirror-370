"""
hiero_sdk_python.transaction.token_freeze_transaction
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Provides TokenFreezeTransaction, a subclass of Transaction for freezing a specified token
for an account on the Hedera network using the Hedera Token Service (HTS) API.
"""
from hiero_sdk_python.transaction.transaction import Transaction
from hiero_sdk_python.hapi.services import token_freeze_account_pb2
from hiero_sdk_python.channels import _Channel
from hiero_sdk_python.executable import _Method

class TokenFreezeTransaction(Transaction):
    """
    Represents a token freeze transaction on the Hedera network.

    This transaction freezes a specified token for a given account.

    Inherits from the base Transaction class and implements the required methods
    to build and execute a token freeze transaction.
    """

    def __init__(self, token_id=None, account_id=None):
        """
        Initializes a new TokenFreezeTransaction instance with optional token_id and account_id.

        Args:
            token_id (TokenId, optional): The ID of the token to be frozen.
            account_id (AccountId, optional): The ID of the account to have their token frozen.
        """
        super().__init__()
        self.token_id = token_id
        self.account_id = account_id
        self._default_transaction_fee = 3_000_000_000

    def set_token_id(self, token_id):
        """
        Sets the ID of the token to be frozen.

        Args:
            token_id (TokenId): The ID of the token to be frozen.

        Returns:
            TokenFreezeTransaction: Returns self for method chaining.
        """
        self._require_not_frozen()
        self.token_id = token_id
        return self

    def set_account_id(self, account_id):
        """
        Sets the ID of the account to be frozen.

        Args:
            account_id (AccountId): The ID of the account to have their token frozen.

        Returns:
            TokenFreezeTransaction: Returns self for method chaining.
        """
        self._require_not_frozen()
        self.account_id = account_id
        return self

    def build_transaction_body(self):
        """
        Builds and returns the protobuf transaction body for token freeze.

        Returns:
            TransactionBody: The protobuf transaction body containing the token freeze details.

        Raises:
            ValueError: If the token ID is missing.
            ValueError: If the account ID is missing.
        """

        if not self.token_id:
            raise ValueError("Missing required TokenID.")

        if not self.account_id:
            raise ValueError("Missing required AccountID.")

        token_freeze_body = token_freeze_account_pb2.TokenFreezeAccountTransactionBody(
            token=self.token_id._to_proto(),
            account=self.account_id._to_proto()
        )

        transaction_body = self.build_base_transaction_body()
        transaction_body.tokenFreeze.CopyFrom(token_freeze_body)

        return transaction_body


    def _get_method(self, channel: _Channel) -> _Method:
        return _Method(
            transaction_func=channel.token.freezeTokenAccount,
            query_func=None
        )
