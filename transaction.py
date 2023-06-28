import binascii
from typing import NewType, Optional, TYPE_CHECKING
from uuid import uuid4

from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5

if TYPE_CHECKING:
    from blockchain import Blockchain


TransactionID = NewType('TransactionID', str)


class TXIN:

    def __init__(self, utxo_id):
        self.utxo_id = utxo_id

    def to_dict(self):
        return {'utxo_id': self.utxo_id}

    @classmethod
    def from_dict(cls, data):
        return cls(utxo_id=data['utxo_id'])

    def __eq__(self, other: 'TXIN'):
        return self.utxo_id == other.utxo_id

    def __hash__(self):
        return hash(self.utxo_id)


class UTXO:

    def __init__(self, amount, utxo_id, recipient_address):
        self.utxo_id = utxo_id
        self.amount = amount
        self.recipient_address = recipient_address

    def to_dict(self):
        return {
            'utxo_id': self.utxo_id,
            'amount': self.amount,
            'recipient_address': self.recipient_address
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            utxo_id=data['utxo_id'],
            amount=data['amount'],
            recipient_address=data['recipient_address']
        )

    def __eq__(self, other: 'UTXO'):
        return self.utxo_id == other.utxo_id and \
                    self.amount == other.utxo_id and \
                    self.recipient_address == other.recipient_address

    def __hash__(self):
        return hash((self.utxo_id, self.amount, self.recipient_address))


class Transaction:

    def __init__(self, intx_lst: list[TXIN], utxo_lst: list[UTXO], sender_address, is_block_founder=False):
        self.id = str(uuid4())
        self.sender_address = sender_address
        self.intx_lst = intx_lst
        self.utxo_lst = utxo_lst
        self.sign = None
        self.is_block_founder = is_block_founder

    def sign_transaction(self, sender_private_key):
        private_key = RSA.importKey(binascii.unhexlify(sender_private_key))
        signer = PKCS1_v1_5.new(private_key)
        h = SHA.new(str(self.dict_for_sign()).encode('utf8'))
        self.sign = binascii.hexlify(signer.sign(h)).decode('ascii')

    def verifacate_transaction(self):
        if not self.sign:
            return False
        public_key = RSA.importKey(binascii.unhexlify(self.sender_address))
        verifier = PKCS1_v1_5.new(public_key)
        h = SHA.new(str(self.dict_for_sign()).encode('utf8'))
        return verifier.verify(h, binascii.unhexlify(self.sign))

    def dict_for_sign(self):
        return {
            'id': self.id,
            'utxo_lst': [i.to_dict() for i in self.utxo_lst],
            'intx_lst': [i.to_dict() for i in self.intx_lst],
            'is_block_founder': self.is_block_founder
        }

    def to_dict(self):
        return {
            'id': self.id,
            'sign': self.sign,
            'utxo_lst': [i.to_dict() for i in self.utxo_lst],
            'intx_lst': [i.to_dict() for i in self.intx_lst],
            'sender_address': self.sender_address,
            'is_block_founder': self.is_block_founder,
        }

    @classmethod
    def from_dict(cls, data):
        utxo_lst = [UTXO.from_dict(i) for i in data['utxo_lst']]
        intx_lst = [TXIN.from_dict(i) for i in data['intx_lst']]
        tson = cls(
            intx_lst=intx_lst,
            utxo_lst=utxo_lst,
            sender_address=data['sender_address'],
            is_block_founder=data['is_block_founder']
        )
        tson.id = data['id']
        tson.sign = data['sign']
        return tson




    def __eq__(self, other: 'Transaction'):
        return self.id == other.id and \
                self.sender_address == other.sender_address and \
                self.intx_lst == other.intx_lst and \
                self.utxo_lst == other.utxo_lst and \
                self.sign == other.sign and \
                self.is_block_founder == other.is_block_founder

    def __hash__(self):
        return hash((
            self.id,
            self.sender_address,
            self.intx_lst,
            self.utxo_lst,
            self.sign,
            self.is_block_founder
        ))


