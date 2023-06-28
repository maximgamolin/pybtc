import Crypto
import Crypto.Random
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
import json

import binascii
import argparse


class Wallet:

    def __init__(self, wallet_name):
        self.wallet_file = f"{wallet_name}.wallet"
        self.private_key = None
        self.public_key = None

    def new_wallet(self):
        random_gen = Crypto.Random.new().read
        private_key = RSA.generate(1024, random_gen)
        public_key = private_key.publickey()
        str_wallet = json.dumps({
            'private_key': binascii.hexlify(private_key.exportKey(format='DER')).decode('ascii'),
            'public_key': binascii.hexlify(public_key.exportKey(format='DER')).decode('ascii')
        })
        with open(self.wallet_file, "w") as f:
            f.write(str_wallet)

    def load_wallet(self):
        with open(self.wallet_file, "r") as f:
            wallet_info = json.loads(f.read())
        self.public_key = wallet_info["public_key"]
        self.private_key = wallet_info["private_key"]

    def fetch_balance(self):
        pass

    def send_money(self, destination, recipient):
        pass


# wallet = Wallet('1.wallet')
# wallet.new_wallet()

parser = argparse.ArgumentParser()
parser.add_argument(dest='wallet_name')
parser.add_argument('--action', required=True, dest='action')
parser.add_argument("--sum", required=False, dest='sum')
parser.add_argument("--rec", required=False, dest='rec')
args = parser.parse_args()


wallet = Wallet(args.wallet_name)

if args.action == "new":
    wallet.new_wallet()
elif args.action == "send":
    wallet.load_wallet()
    wallet.send_money(int(args.sum), args.rec)
elif args.action == "balance":
    print(wallet.fetch_balance())
