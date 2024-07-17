import hashlib
import datetime
from typing import List

from src.Transaction import Transaction


class Block:
    # Keeps data like hash, nonce, prev hash, merkleRoot, timestamp

    def __init__(self, index: int, prevHash: str) -> None:
        self.index = 0 # todo pamiętać o tym - na razie nie mam pomysłu w jakim miejscu to inicjalozować
        self.hash = 0  # calc during mining
        self.prevHash = prevHash
        self.data = []  # list of transactions id
        self.nonce = 0
        self.timestamp = datetime.datetime.now()

    def calcHashWithNonce(self, nonce) -> str:
        sha = hashlib.sha256()
        sha.update(str(self.prevHash).encode('utf-8') +
                   str(self.data).encode('utf-8') +
                   str(self.timestamp).encode('utf-8') +
                   str(nonce).encode('utf-8'))

        return sha.hexdigest()

    def mineBlock(self):
        self.nonce, self.hash = self.compute_hash_with_proof_of_work()

    def compute_hash_with_proof_of_work(self, difficulty="00"):
        nonce = 0
        while True:  ## loop forever
            hash = self.calcHashWithNonce(nonce)
            if hash.startswith(difficulty):
                return [nonce, hash]  ## proof of work if hash starts with leading zeros (00)
            else:
                nonce += 1

    def confirmPow(self):
        pass

    def addTransaction(self, transaction: Transaction):
        self.data.append(transaction.transactionID)

    def to_dict(self):
        return {
            'index': self.index,
            'hash': self.hash,
            'prevHash': self.prevHash,
            'data': self.data,
            'timestamp': self.timestamp.isoformat(),
            'nonce': self.nonce
        }

    # def calculateMerkleRoot(self):

