import json
import sys

import requests
from flask import Flask

from consts import REGISTER_NODE_PATH, ADD_NEW_BLOCK_PATH
from blockchain import Blockchain, BlockchainBlock
from transaction import Transaction


class Node:

    nodes_path: list[str] = []
    external_nodes_ports: list[str] = []
    port: str = ''

    def __init__(self, ext_node_ports = []):
        self.block_chain = Blockchain([], [])

    def register_me(self):
        for external_node_port in self.external_nodes_ports:
            result = requests.post(f'0.0.0.0:{external_node_port}{REGISTER_NODE_PATH}/{self.port}').json()
            for new_port in result["external_nodes_ports"]:
                if new_port not in self.external_nodes_ports:
                    self.external_nodes_ports.append(new_port)

    def broadcast_new_block(self, new_block: BlockchainBlock):
        for external_node_port in self.external_nodes_ports:
            requests.post(f'0.0.0.0:{external_node_port}{ADD_NEW_BLOCK_PATH}', json=json.dumps(new_block.to_dict()))

    def register_node(self, node_port):
        if node_port in self.external_nodes_ports:
            return self.external_nodes_ports
        old_node_ports = [i for i in self.external_nodes_ports]
        self.external_nodes_ports.append(node_port)
        return old_node_ports

    def add_new_block_to_blockchain(self, new_block: BlockchainBlock):
        self.block_chain.validate_block(new_block)
        self.block_chain.add_new_block(new_block)
        self.broadcast_new_block(new_block)

    def add_new_transaction(self, new_transaction: Transaction):
        self.block_chain.validate_transaction(new_transaction)
        self.block_chain.add_transaction_to_pool(new_transaction)

    def get_transactions_from_pool(self) -> list[Transaction]:
        return self.block_chain.transaction_pool


app = Flask(__name__)

port = sys.argv[1]
node = Node([port])


@app.route('/register_me')
def register_me():
    node.register_me()


@app.route('/reg_ext_node/<node_port>')
def reg_ext_node(node_port):
    return json.dumps(node.register_node(node_port))


@app.route('/add_transaction')
def add_transaction():
    pass


@app.route('/add_block')
def add_block():
    pass


@app.route('/fetch_transactions')
def fetch_transactions():
    pass


@app.route('/fetch_blockchain')
def fetch_blockchain():
    pass