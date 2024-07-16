import ecdsa
import hashlib
from src.Transaction import TransactionInput, Transaction, TransactionOutput
from typing import Tuple, List
from ecdsa import VerifyingKey, SigningKey


class Wallet:
    # private key, public key, UXTO
    def __init__(self) -> None:
        self.prvKey, self.pubKey = generateKeyPair()
        self.UXTO = []

    def getBalance(self, UXTO: TransactionOutput):
        # Updates UXTO field by looking for unspent transactions in DB?

        self.UXTO = UXTO

    def sendFunds(self, recipient: List[VerifyingKey] | VerifyingKey, value: List[float] | float) -> Transaction | None:
        # Creates transaction and sends it to DB

        """
        :Input: recipent_address, value,

        sender address - known

        1. shoudld choose UXTO in the way the sum is greater than value (UXTO > value)
        2. should calculate the change - to zorbi transakcja w sumie, nie?
        3. should create Transaction object and put it to database?

        :return: Transaction
        """
        txIN = []
        balance = 0

        if not self.UXTO:
            print("No UXTO to spend")
            return None

        for uxto in self.UXTO:
            balance += uxto.value
            txIN.append(TransactionInput(uxto))

            if balance >= value:
                chng = balance - value
                # Todo: zrobić coś z tym - to się wysyła do bazy?
                return Transaction(self.pubKey, recipient, value, txIN, chng)

        if balance < value:
            print("Not enough funds")
            return None


def generateKeyPair() -> Tuple[SigningKey, VerifyingKey]:

    secretKey = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1, hashfunc=hashlib.sha256)
    publicKey = secretKey.get_verifying_key()

    return secretKey, publicKey

