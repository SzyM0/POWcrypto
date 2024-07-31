import ecdsa
import hashlib
from Transaction import TransactionInput, Transaction, TransactionOutput, pubKeyToStr
from typing import Tuple, List
from ecdsa import VerifyingKey, SigningKey
import requests


class Wallet:
    # private key, public key, UXTO
    def __init__(self) -> None:
        self.prvKey, self.pubKey = generateKeyPair()
        self.UXTO = []

    # todo możeby przenieść zapytania tutaj i dodać serwis get zwracający UXTO? 
    def getBalance(self, UXTO: List[TransactionOutput] | TransactionOutput) -> int:
        # Updates UXTO field by looking for unspent transactions in DB?

        self.UXTO.clear()
        balance = 0
        for uxto in UXTO:
            if uxto.recipient == self.pubKey:
                self.UXTO.append(uxto)
                balance += uxto.value

        return balance

    # def sendTransaction(self):

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
        # todo tutaj przypadek jak jest kilka recipientów
        txIN = []
        balance = 0

        if not self.UXTO:
            print("No UXTO to spend")
            return None

        for uxto in self.UXTO.copy():

            balance += uxto.value
            txIN.append(TransactionInput(uxto))
            self.UXTO.remove(uxto)

            if balance >= value:
                chng = balance - value
                tx = Transaction(sender=self.pubKey, recipient=recipient, value=value, inputs=txIN, change=chng)
                tx.createSignature(self.prvKey)
                return tx

        if balance < value:
            print("Not enough funds")
            return None

 # todo zrobić tą funkcję wewętrzną klasy wallet
def generateKeyPair() -> Tuple[SigningKey, VerifyingKey]:

    secretKey = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1, hashfunc=hashlib.sha256)
    publicKey = secretKey.get_verifying_key()

    return secretKey, publicKey

