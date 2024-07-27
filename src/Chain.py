#!/usr/bin/python
# -*- coding: utf-8 -*-
import json
import random
import threading
import time
from typing import Tuple, List
import requests
from tinydb import Query
from Block import Block
from Transaction import Transaction, TransactionInput, TransactionOutput
from Wallet import Wallet


lock = threading.Lock()

SUPPLY = 100
MIN_NOMINAL = 0.000001 # TODO MOŻNA DODAĆ SPRAWDZENIE TEGO

validatedTx = []
UXTOs = []


class Chain:

    def __init__(self, txRepo, blockRepo, txOutRepo, walletRepo):
        self.txRepo = txRepo
        self.blockRepo = blockRepo
        self.txOutRepo = txOutRepo
        self.walletRepo = walletRepo

        self.walletA = Wallet()
        self.walletB = Wallet()

        self.genenerateGenesisBlock()

    def genenerateGenesisBlock(self) -> None:
        coinbase = Wallet()

        genesisTransaction = Transaction(coinbase.pubKey, [self.walletA.pubKey, self.walletB.pubKey],
                                         [SUPPLY / 2, SUPPLY / 2], None, 0)
        genesisTransaction.setBlockIndex(0)
        genesisTransaction.createSignature(self.walletA.prvKey)
        UXTOs.extend(genesisTransaction.outputs)

        genesisBlock = Block(0, "0")
        genesisBlock.addTransaction(genesisTransaction, index=0)
        genesisBlock.mineBlock()

    def storeTransactions(self, data: List[Transaction] | Transaction) -> None:
        # Bierze transakcje i zapisuje je do bazy danych
        transactions = data if isinstance(data, list) else [data]
        for transaction in transactions:
            self.txRepo.insert(transaction.to_dict())

    def updateUXTOs(self, data: List[Transaction] | Transaction) -> None:
        # Dostaje transakcję, usuwa z listy uxto inputy transakcji, dodaje outputy
        # zapisuje to w bazie danych i do lokalnej zmiennej
        transactions = data if isinstance(data, list) else [data]  # jak pojedyncza

        for transaction in transactions:
            outputs = transaction.outputs
            inputs = transaction.inputs

            for input_tx in inputs:
                self.txOutRepo.remove(Query().ID == input_tx.ID)
                UXTOs.remove(input_tx)

            for output in outputs:
                self.txOutRepo.insert(output.to_dict())
                UXTOs.append(output)

    def addBlock(self, block: Block, transactions: List[Transaction]) -> None:

        self.storeTransactions(transactions)
        self.updateUXTOs(transactions)
        self.blockRepo.insert(block.to_dict())
        with lock:
            validatedTx.clear()

    def sendTransactions(self):
        self.walletA.getBalance(UXTOs)
        txA = self.walletA.sendFunds(self.walletB.pubKey, random.randint(2,6))
        url = 'http://127.0.0.1:5000/receiveTransaction'
        requests.post(url, json=txA.to_dict())
        return txA

    def sendTransactionsB(self):
        self.walletB.getBalance(UXTOs)
        txB = self.walletB.sendFunds(self.walletB.pubKey, random.randint(2,6))
        url = 'http://127.0.0.1:5000/receiveTransaction'
        requests.post(url, json=txB.to_dict())
        return txB

    def run(self):
        prevIndex = 0
        prevHash = ''
        txMempool = []
        tx = 0
        for i in range(10):
            print(f"Iteration {i=}")
            # print_uxto(UXTOs)

            txA = self.sendTransactions()
            txB = self.sendTransactionsB()

            # print(f"tx: {tx.inputs=}")
            # print(f"tx: {tx.outputs=}")
            time.sleep(1)

            # #  Wysłać kilka transakcji
            # validatedTx.append(txA)
            # validatedTx.append(txB)

            with lock:
                txMempool = validatedTx.copy()
        #
        # # create new block and mine
            newBlock = Block(index=prevIndex + 1, prevHash=prevHash)
            for tx in txMempool:
                newBlock.addTransaction(tx, prevIndex+1)
            newBlock.mineBlock()  # todo dodać difficulty
            self.addBlock(newBlock, txMempool)

            # todo dodać żeby blok kopał się mając z dwie transakcje przynajmniej
            # dodać zapisywanie danych do tego wszystkiego

            prevIndex += 1
            prevHash = newBlock.hash

            # self.storeTransactions(txMempool)
            # self.updateUXTOs(txMempool)


            txMempool.clear()
            # validatedTx.clear()

        print(f"{self.walletB.getBalance(UXTOs)=}")
        print(f"{self.walletA.getBalance(UXTOs)=}")



def print_uxto(data):
    for uxto in data:
        print(f"UXTO id: {uxto.ID=} Value: {uxto.value}")


def verify_transaction(transaction: Transaction) -> Tuple[bool, str]:
    """
    Verifies the transaction by checking:
    - If the number of recipients matches the number of values.
    - The format of transaction inputs.
    - All inputs are in UXTOs.
    - The signature is valid.
    - The total input value matches the total output value.

    :param transaction: The transaction to verify.
    :param UXTOs: Dictionary of unspent transaction outputs.
    :return: True if the transaction is valid, False otherwise and error message.
    """

    # Verify recipient and value list match
    if isinstance(transaction.recipient, list) and isinstance(transaction.value, list):
        if len(transaction.recipient) != len(transaction.value):
            print("Mismatch in number of recipients and values.")
            return False, "Mismatch in number of recipients and values."

    # Ensure all inputs are in a proper format and unspent
    inputs = transaction.inputs if isinstance(transaction.inputs, list) else [transaction.inputs]
    # Sprawdzenie, czy wszystkie elementy są odpowiedniego typu
    if not all(isinstance(txInput, TransactionInput) for txInput in inputs):
        print("Wrong input format.")
        return False, "Wrong input format."

    # Sprawdzenie, czy wszystkie elementy znajdują się w UXTOs
    if not all(txInput in UXTOs for txInput in inputs):
        print("Funds already spent.")
        return False, "Funds already spent."

    # Verify signature
    if isinstance(transaction.signature, int):
        print("No signature")
        return False, "No signature"

    if not transaction.comfirmSignature(transaction.sender):
        print("Invalid signature.")
        return False, "Invalid signature."

    # Check for balance equality between inputs and outputs
    balance_in = sum(txInput.UXTO.value for txInput in inputs if isinstance(txInput, TransactionInput))
    balance_out = sum(txOutput.value for txOutput in transaction.outputs if isinstance(txOutput, TransactionOutput))

    if balance_in != balance_out:
        print("Mismatch between total inputs and total outputs.")
        return False, "Mismatch between total inputs and total outputs."

    return True, "Tx valid"
