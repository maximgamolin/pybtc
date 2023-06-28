from uuid import uuid4
from transaction import Transaction, UTXO, TXIN
from itertools import count
from datetime import datetime


class BlockchainBlock:

    def __init__(
            self,
            block_number,
            timestamp,
            transactions,
            nonce,
            previous_hash,
            founder
    ):
        self.block_number = block_number
        self.timestamp: datetime = timestamp
        self.transactions = transactions
        self.nonce = nonce
        self.previous_hash = previous_hash
        self.founder = founder

    def to_dict(self):
        return {
            'block_number': self.block_number,
            'timestamp': self.timestamp,
            'transactions': [i.to_dict() for i in self.transactions],
            'nonce': self.nonce,
            'previous_hash': self.previous_hash,
            'founder': self.founder
        }

    @classmethod
    def from_dict(cls, data):
        transactions = [Transaction.from_dict(i) for i in data['transactions']]
        return cls(
            block_number=data['block_number'],
            timestamp=datetime.fromisoformat(data['timestamp']),
            transactions=transactions,
            nonce=data['nonce'],

        )


    def __eq__(self, other: 'BlockchainBlock'):
        return self.block_number == other.block_number and \
                self.timestamp == other.timestamp and \
                self.transactions == other.transactions and \
                self.nonce == other.nonce and \
                self.previous_hash == other.previous_hash and\
                self.founder == other.founder

    def __hash__(self):
        return hash(
            (
                self.block_number,
                self.timestamp,
                self.transactions,
                self.nonce,
                self.previous_hash,
                self.founder
            )
        )


class Blockchain:

    def __init__(self, blockchain: list[BlockchainBlock], transaction_pool: list[Transaction]):
        self.blockchain = blockchain
        self.transaction_pool = transaction_pool

    def add_new_block(self, block: BlockchainBlock):
        for block_transaction in block.transactions:
            for idx in count(len(self.transaction_pool)-1, -1):
                if idx < 0:
                    break
                if block_transaction.id == self.transaction_pool[idx].id:
                    del self.transaction_pool[idx]
                    break
        self.blockchain.append(block)

    def find_sender_utxos(self, sender_address, blockchain=None) -> list[UTXO]:
        blockchain = blockchain or self.blockchain
        sender_utxos = []
        for block in blockchain:
            for transaction in block.transactions:
                for utxo in transaction.utxo_lst:
                    if utxo.recipient_address == sender_address:
                        sender_utxos.append(utxo)
        for transaction in self.transaction_pool:
            for utxo in transaction.utxo_lst:
                if utxo.recipient_address == sender_address:
                    sender_utxos.append(utxo)
        return sender_utxos

    def find_unused_utxos(self, sender_utxos: list[UTXO]) -> list[UTXO]:
        used_utxo_ids = set()
        sender_utxos_ids = set(i.utxo_id for i in sender_utxos)
        for block in self.blockchain:
            for transaction in block.transactions:
                for intx in transaction.intx_lst:
                    if intx.utxo_id in sender_utxos_ids:
                        used_utxo_ids.add(intx.utxo_id)
        for transaction in self.transaction_pool:
            for intx in transaction.intx_lst:
                if intx.utxo_id in sender_utxos_ids:
                    used_utxo_ids.add(intx.utxo_id)
        result = []
        for i in sender_utxos:
            if i.utxo_id not in used_utxo_ids:
                result.append(i)
        return result

    @staticmethod
    def find_few_utxo_more_than_amount(utxos, needed_amount):
        result = []
        amount = 0
        for utxo in utxos:
            amount += utxo.amount
            result.append(utxo)
            if amount >= needed_amount:
                return result

    @staticmethod
    def sum_of_utxos_amount(utxos) -> int:
        return sum((i.amount for i in utxos))

    def convert_unused_utxo_to_new_transaction_utxo(self, recipient_address, sender_address, unused_utxos, amount):
        inseparable_utxos = unused_utxos[:-1]
        sum_without_last = self.sum_of_utxos_amount(inseparable_utxos)
        remainder = amount - sum_without_last
        if remainder > 0:
            return [
                UTXO(amount, str(uuid4()), recipient_address),
                UTXO(remainder, str(uuid4()), sender_address)
            ]
        else:
            return [
                UTXO(amount, str(uuid4()), recipient_address)
            ]

    @staticmethod
    def convert_utxo_to_txin(utxos):
        return [TXIN(i.utxo_id) for i in utxos]

    def build_transaction(self, recipient_address, sender_address, utxos, amount):
        new_utxos = self.convert_unused_utxo_to_new_transaction_utxo(recipient_address, sender_address, utxos, amount)
        new_txins = self.convert_utxo_to_txin(utxos)
        return Transaction(
            intx_lst=new_txins,
            utxo_lst=new_utxos,
            sender_address=sender_address
        )

    def send_funds(self, sender_address, recipient_address, amount):
        user_utxos = self.find_sender_utxos(sender_address)
        unused_utxos = self.find_unused_utxos(user_utxos)
        if self.sum_of_utxos_amount(unused_utxos) < amount:
            raise Exception('NOT ENOUGH MONEY')
        utxos_for_amount = self.find_few_utxo_more_than_amount(unused_utxos, amount)
        return self.build_transaction(recipient_address, sender_address, utxos_for_amount, amount)

    def validate_founder_transaction(self, transaction: Transaction, block: BlockchainBlock):
        if len(transaction.utxo_lst) != 1:
            raise Exception('INCORRECT UTXO IN TRANSACTION')
        if transaction.utxo_lst[0].recipient_address != block.founder:
            raise Exception('INCORRECT RECIPIENT ADDRESS IN TRANSACTION')
        if len([i for i in block.transactions if i.is_block_founder]) > 1:
            raise Exception('MORE THAN ONE FOUNDER TRANSACTION')

    def validate_transaction(self, transaction: Transaction):
        if not transaction.verifacate_transaction():
            raise Exception("INCORRECT TRANSACTION")
        # проверить что входы транзакции не использованны в других транзакциях
        # проверить что сумма на выходах других транзакций достаточна новым тразакциям
        user_utxos = self.find_sender_utxos(transaction.sender_address)
        unused_utxos = self.find_unused_utxos(user_utxos)
        utxo_for_transaction = []
        for transaction_intx in transaction.intx_lst:
            utxo = next((i for i in unused_utxos if i.utxo_id == transaction_intx.utxo_id), None)
            if not utxo:
                raise Exception("USED UTXO IN TRANSACTION")
            utxo_for_transaction.append(utxo)
        if sum(i.amount for i in transaction.utxo_lst) != sum(i.amount for i in utxo_for_transaction):
            raise Exception("INCORRECT TRANSACTION SUM")

    def user_balance(self, sender_address) -> int:
        user_utxos = self.find_sender_utxos(sender_address)
        unused_utxos = self.find_unused_utxos(user_utxos)
        return self.sum_of_utxos_amount(unused_utxos)

    def validate_block(self, new_block: BlockchainBlock):
        for transaction in new_block.transactions:
            if not transaction.intx_lst and transaction.sender_address != new_block.founder:
                raise Exception('INVALID_BLOCK')
            if transaction.is_block_founder:
                self.validate_founder_transaction(transaction, new_block)
            else:
                self.validate_transaction(transaction)

    def add_transaction_to_pool(self, transaction: Transaction):
        self.validate_transaction(transaction)
        self.transaction_pool.append(transaction)

    def change_blockchain(self, blockchain: list[BlockchainBlock]):
        if self.blockchain == blockchain:
            return
        if len(self.blockchain) > len(blockchain):
            return
        tmp_blockchain = Blockchain([], [])
        for num, block in enumerate(blockchain, start=0):
            try:
                tmp_blockchain.validate_block(block)
            except Exception:
                return
            tmp_blockchain.add_new_block(block)
        self.blockchain = blockchain

    def blockchain_to_dict(self) -> list[dict]:
        result = []
        for block in self.blockchain:
            result.append(block.to_dict())
        return result

    def to_dict(self):
        return [i.to_dict() for i in self.blockchain]

    @classmethod
    def from_dict(cls, data):
        blockchain = [BlockchainBlock.from_dict(i) for i in data]
        transactions = [i for i in data['transactions']]






# node = Node()
# app = Flask(__name__)
#
#
# @app.route(f"{ALL_BLOCKCHAIN_PATH}")
# def all_blockchain():
#     return json.dumps(node.block_chain)
#
#
# @app.route(f"{REGISTER_NODE_PATH}")
# def register_node():
#     print(request.json)
#
#
# @add.route(f"")
