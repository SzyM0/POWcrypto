import hashlib
import datetime


from Transaction import Transaction


class Block:
    # Keeps data like hash, nonce, prev hash, merkleRoot, timestamp

    def __init__(self, prevHash: str, index:  int = 0) -> None:
        self.blockIndex = index
        self.hash = 0  # calc during mining
        self.prevHash = prevHash
        self.data = []  # list of transactions id
        self.nonce = 0
        self.timestamp = datetime.datetime.now()

    def calcHashWithNonce(self, nonce) -> str:
        sha = hashlib.sha256()
        sha.update(str(self.prevHash).encode('utf-8') +
                   str(self.blockIndex).encode('utf-8') +
                   str(self.timestamp).encode('utf-8') +
                   str(nonce).encode('utf-8'))

        return sha.hexdigest()

    def mineBlock(self, difficulty: str) -> None:
        self.nonce, self.hash = self.computeHashWithProofOfWork(difficulty)
        print(f"\n ---------- "
              f"Block mined successfully at {self.timestamp}"
              f" ---------- \n"
              f"Block index:{self.blockIndex}\n"
              f"Hash: {self.hash}\n"
              f"PrevHash: {self.prevHash}"
              f"\n")

    def computeHashWithProofOfWork(self, difficulty="00"):
        nonce = 0
        while True:  ## loop forever
            hash = self.calcHashWithNonce(nonce)
            if hash.startswith(difficulty):
                return [nonce, hash]  ## proof of work if hash starts with leading zeros (00)
            else:
                nonce += 1

    def addTransaction(self, transaction: Transaction):
        self.data.append(transaction.transactionID)

    def to_dict(self):
        return {
            'index': self.blockIndex,
            'hash': self.hash,
            'prevHash': self.prevHash,
            'data': self.data,
            'timestamp': self.timestamp.isoformat(),
            'nonce': self.nonce
        }


