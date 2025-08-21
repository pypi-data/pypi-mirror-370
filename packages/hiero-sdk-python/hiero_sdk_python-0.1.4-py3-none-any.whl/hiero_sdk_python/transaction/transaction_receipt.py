import warnings 
from hiero_sdk_python.contract.contract_id import ContractId
from hiero_sdk_python.file.file_id import FileId
from hiero_sdk_python.tokens.token_id import TokenId
from hiero_sdk_python.consensus.topic_id import TopicId
from hiero_sdk_python.account.account_id import AccountId
from hiero_sdk_python._deprecated import _DeprecatedAliasesMixin

class TransactionReceipt(_DeprecatedAliasesMixin):
    """
    Represents the receipt of a transaction.
    Imports deprecated aliases for tokenId, topicId and accountId.

    The receipt contains information about the status and result of a transaction,
    such as the TokenId or AccountId involved.

    Attributes:
        status (ResponseCode): The status code of the transaction.
        _receipt_proto (TransactionReceiptProto): The underlying protobuf receipt.
    """

    def __init__(self, receipt_proto, transaction_id=None):
        """
        Initializes the TransactionReceipt with the provided protobuf receipt.

        Args:
            receipt_proto (TransactionReceiptProto): The protobuf transaction receipt.
        """
        self._transaction_id = transaction_id
        self.status = receipt_proto.status
        self._receipt_proto = receipt_proto

    @property
    def token_id(self):
        """
        Retrieves the TokenId associated with the transaction receipt, if available.

        Returns:
            TokenId or None: The TokenId if present; otherwise, None.
        """
        if self._receipt_proto.HasField('tokenID') and self._receipt_proto.tokenID.tokenNum != 0:
            return TokenId._from_proto(self._receipt_proto.tokenID)
        else:
            return None

    @property
    def topic_id(self):
        """
        Retrieves the TopicId associated with the transaction receipt, if available.

        Returns:
            TopicId or None: The TopicId if present; otherwise, None.
        """
        if self._receipt_proto.HasField('topicID') and self._receipt_proto.topicID.topicNum != 0:
            return TopicId._from_proto(self._receipt_proto.topicID)
        else:
            return None

    @property
    def account_id(self):
        """
        Retrieves the AccountId associated with the transaction receipt, if available.

        Returns:
            AccountId or None: The AccountId if present; otherwise, None.
        """
        if self._receipt_proto.HasField('accountID') and self._receipt_proto.accountID.accountNum != 0:
            return AccountId._from_proto(self._receipt_proto.accountID)
        else:
            return None

    @property
    def serial_numbers(self):
        """
        Retrieves the serial numbers associated with the transaction receipt, if available.
        
        Returns:
            list of int: The serial numbers if present; otherwise, an empty list.
        """
        return self._receipt_proto.serialNumbers

    @property
    def file_id(self):
        """
        Returns the file ID associated with this receipt.
        """
        if self._receipt_proto.HasField('fileID') and self._receipt_proto.fileID.fileNum != 0:
            return FileId._from_proto(self._receipt_proto.fileID)
        else:
            return None
          
    @property
    def transaction_id(self):
        """
        Returns the transaction ID associated with this receipt.

        Returns:
            TransactionId: The transaction ID.
        """
        return self._transaction_id

    @property
    def contract_id(self):
        """
        Returns the contract ID associated with this receipt.

        Returns:
            ContractId or None: The ContractId if present; otherwise, None.
        """
        if self._receipt_proto.HasField('contractID') and self._receipt_proto.contractID.contractNum != 0:
            return ContractId._from_proto(self._receipt_proto.contractID)
        else:
            return None

    def _to_proto(self):
        """
        Returns the underlying protobuf transaction receipt.

        Returns:
            TransactionReceiptProto: The protobuf transaction receipt.
        """
        return self._receipt_proto

    @classmethod
    def _from_proto(cls, proto, transaction_id=None):
        return cls(receipt_proto=proto, transaction_id=transaction_id)
