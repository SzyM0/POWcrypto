import hashlib
import datetime


class Block:
    # Keeps data like hash, nonce, prev hash, merkleRoot, timestamp

    def __init__(self, prevHash, data) -> None:
        self.hash = 0  # calc during mining
        self.prevHash = prevHash
        self.data = data  # ??
        self.timestamp = datetime.datetime.now()
        self.nonce = 0

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

    def to_dict(self):


    # def calculateMerkleRoot(self):

