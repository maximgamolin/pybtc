import json
from uuid import uuid4
from datetime import datetime

from blockchain import Blockchain, BlockchainBlock
from transaction import Transaction, UTXO, TXIN
from pprint import pprint


wallets = {1: {}, 2: {}}
for i in wallets.keys():
    with open(f"{i}.wallet", "r") as f:
        wallets[i] = json.loads(f.read())

blockchain = Blockchain([], [])
# t1 u1
txin1_1 = TXIN(
    None
)

utxo1_1 = UTXO(
    utxo_id=str(uuid4()),
    amount=100,
    recipient_address=wallets[1]["public_key"]
)

transaction1 = Transaction(
    intx_lst=[],
    utxo_lst=[utxo1_1],
    sender_address=wallets[1]["public_key"],
    is_block_founder=True
)
transaction1.sign_transaction(wallets[1]["private_key"])
block1 = BlockchainBlock(
    block_number=1,
    timestamp=datetime.now(),
    transactions=[transaction1],
    nonce=10,
    previous_hash=None,
    founder=wallets[1]["public_key"]
)
blockchain.validate_block(block1)
blockchain.add_new_block(block1)
# t2 u1
txin2_1 = TXIN(
    None
)
utxo2_1 = UTXO(
    utxo_id=str(uuid4()),
    amount=100,
    recipient_address=wallets[1]["public_key"]
)
transaction2 = Transaction(
    intx_lst=[],
    utxo_lst=[utxo2_1],
    sender_address=wallets[1]["public_key"],
    is_block_founder=True
)
transaction2.sign_transaction(wallets[1]["private_key"])
block2 = BlockchainBlock(
    block_number=2,
    timestamp=datetime.now(),
    transactions=[transaction2],
    nonce=10,
    previous_hash=None,
    founder=wallets[1]["public_key"]
)
blockchain.validate_block(block2)
blockchain.add_new_block(block2)
# t3 u2
txin3_1 = TXIN(
    None
)
utxo3_1 = UTXO(
    utxo_id=str(uuid4()),
    amount=100,
    recipient_address=wallets[2]["public_key"]
)
transaction3 = Transaction(
    intx_lst=[],
    utxo_lst=[utxo3_1],
    sender_address=wallets[2]["public_key"],
    is_block_founder=True
)
transaction3.sign_transaction(wallets[2]["private_key"])

block3 = BlockchainBlock(
    block_number=3,
    timestamp=datetime.now(),
    transactions=[transaction3],
    nonce=10,
    previous_hash=None,
    founder=wallets[2]["public_key"]
)
blockchain.validate_block(block3)
blockchain.add_new_block(block3)

# t4 u2 -> u1 50
t = blockchain.send_funds(wallets[2]["public_key"], wallets[1]["public_key"], 50)
t.sign_transaction(wallets[2]["private_key"])

block4 = BlockchainBlock(
    block_number=4,
    timestamp=datetime.now(),
    transactions=[t],
    nonce=10,
    previous_hash=None,
    founder=wallets[1]["public_key"]
)

blockchain.validate_block(block4)

# if __name__ == '__main__':
#     blockchain.transaction_pool.append(t)
#     print(blockchain.transaction_pool)
#     blockchain.add_new_block(block4)
#     print(blockchain.transaction_pool)
#
#     print(blockchain.user_balance(wallets[1]["public_key"]))
#     txin4 = TXIN(
#         None
#     )
#
#     utxo4 = UTXO(
#         utxo_id=str(uuid4()),
#         amount=100,
#         recipient_address=wallets[1]["public_key"]
#     )
#
#     transaction4 = Transaction(
#         intx_lst=[],
#         utxo_lst=[utxo1_1],
#         sender_address=wallets[1]["public_key"],
#         is_block_founder=True
#     )
#     print(transaction4.verifacate_transaction())
#     transaction4.sign_transaction(wallets[2]["private_key"])
#     print(transaction4.verifacate_transaction())
#     transaction4.sign_transaction(wallets[1]["private_key"])
#     print(transaction4.verifacate_transaction())
#
#     new_blockchain = Blockchain([], [])
#     new_blockchain.change_blockchain(blockchain.blockchain)
#     json_blockchain = json.dumps(new_blockchain.to_dict(), default=str)
#     pprint(json_blockchain)
#     restored_blockchain = json.loads(json_blockchain)
#     new_blockchain.change_blockchain(blockchain.blockchain[:-1])

if __name__ == '__main__':
    pass