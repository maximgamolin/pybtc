import hashlib
import json
from datetime import datetime
from pprint import pprint
from uuid import uuid4

import requests

from consts import BLOCK_CHAIN_NETWORK_ADDRESS, ALL_BLOCKCHAIN_PATH, INIT_BLOCK, MINING_DIFFICULTY, CURRENT_FEE


class Miner:

    def __init__(self, node_port=0):
        # self.node_path = f"0.0.0.0:{node_port}"
        self.blockchain = [INIT_BLOCK]

    def broadcast_new_block(self, new_block):
        # requests.post(f'{self.node_path}{ADD_NEW_BLOCK_PATH}', json=json.dumps(new_block))
        print("BLOCK FOUND")
        pprint(self.blockchain)
        self.blockchain.append(new_block)

    def fetch_block_chain(self):
        return self.blockchain
        # return requests.get(f'{self.node_path}{ALL_BLOCKCHAIN_PATH}').json()

    def hash(self, block):
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def proof_of_work(self, transactions, nonce, last_hash) -> bool:
        guess = (str(transactions) + str(last_hash) + str(nonce)).encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:MINING_DIFFICULTY] == '0' * MINING_DIFFICULTY

    def miner_fee_transaction(self):
        return [{
            'id': str(uuid4()),
            'txin': [],
            'utxo': [],
            'value': CURRENT_FEE
        }]

    def build_block(self, nonce, transactions, last_hash):
        return {
            'block_number': self.blockchain[-1]["block_number"] + 1,
            'timestamp': datetime.now().isoformat(),
            'transactions': transactions,
            'nonce': nonce,
            'previous_hash': last_hash,
            'founder': None
        }

    def fetch_transactions(self) -> list:
        return []

    def mine(self):
        nonce = 1
        while True:
            transactions = [self.miner_fee_transaction()] + self.fetch_transactions()
            last_hash = self.hash(self.blockchain[-1])
            if self.proof_of_work(nonce, transactions, last_hash):
                block = self.build_block(nonce, transactions, last_hash)
                self.broadcast_new_block(block)
            self.blockchain = self.fetch_block_chain()
            nonce += 1
