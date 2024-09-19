import ecdsa
import hashlib
from src.Transaction import TransactionInput, Transaction, TransactionOutput, pubKeyToStr, transactionOutputFromJSON
from typing import Tuple, List
from ecdsa import VerifyingKey, SigningKey
import requests


class Wallet:
    # private key, public key, UXTO
    def __init__(self) -> None:
        self.prvKey, self.pubKey = generateKeyPair()
        self.UXTO = []

    # todo możeby przenieść zapytania tutaj i dodać serwis get zwracający UXTO?
    def getBalance(self) -> int:
        # Updates UXTO field by looking for unspent transactions in DB?

        url = 'http://127.0.0.1:5000/getUXTO'
        params = {'pubKey': pubKeyToStr(self.pubKey)}
        response = requests.get(url, params=params)

        if response.status_code == 200:
            unspentTxGet = [transactionOutputFromJSON(item) for item in response.json()['data']]
            self.UXTO.clear()
            self.UXTO = unspentTxGet
            balance = sum([item.value for item in unspentTxGet])

            return balance

    def getBalanceOffline(self):
        return sum([item.value for item in self.UXTO])

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
        self.getBalance()

        # todo pomyśleć jak lepiej zrobić ten get balance czy nie lepiej go wywoływać jak jest za mało kasy czy jest sens za każdym
        #  razem bo inaczej może nie być sensu trzymać listy uxto lokalnie

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
                url = 'http://127.0.0.1:5000/postTransaction'
                requests.post(url, json=tx.to_dict())
                return tx

        if balance < value:
            print("Not enough funds")
            return None

 # todo zrobić tą funkcję wewętrzną klasy wallet
def generateKeyPair() -> Tuple[SigningKey, VerifyingKey]:

    secretKey = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1, hashfunc=hashlib.sha256)
    publicKey = secretKey.get_verifying_key()

    return secretKey, publicKey

