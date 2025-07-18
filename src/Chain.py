#!/usr/bin/python
# -*- coding: utf-8 -*-
import decimal
import json
import random
import threading
import time
from typing import Tuple, List
from tinydb import Query
from src.Block import Block
from src.Transaction import Transaction, TransactionInput, TransactionOutput
from src.Wallet import Wallet

lock = threading.Lock()

SUPPLY = 100
MIN_NOMINAL = 0.000001
DIFFICULTY = "000"

validatedTx = []
UXTOs = []

class Chain:

    def __init__(self, txRepo, blockRepo, txOutRepo):
        self.txRepo = txRepo
        self.blockRepo = blockRepo
        self.txOutRepo = txOutRepo

        self.walletA = Wallet()
        self.walletB = Wallet()
        self.walletC = Wallet()

    def genenerateGenesisBlock(self) -> str:
        coinbase = Wallet()

        genesisTransaction = Transaction(coinbase.pubKey, [self.walletA.pubKey, self.walletB.pubKey],
                                         [SUPPLY / 2, SUPPLY / 2], None, 0, ID="0"*64)
        genesisTransaction.setBlockIndex(0)
        genesisTransaction.createSignature(self.walletA.prvKey)

        genesisBlock = Block(prevHash="", index=0)
        genesisBlock.addTransaction(transaction=genesisTransaction)
        genesisBlock.setGenesisHash()
        # genesisBlock.mineBlock(difficulty=DIFFICULTY)
        self.addBlock(block=genesisBlock, transactions=[genesisTransaction])

        print(f"\n ---------- "
              f"Genesis Block created at {genesisBlock.timestamp}"
              f" ---------- \n"
              f"Block index:{genesisBlock.blockIndex}\n"
              f"Hash: {genesisBlock.hash}\n"
              f"PrevHash: {genesisBlock.prevHash}"
              f"\n")

        return genesisBlock.hash

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

            if inputs:  # special case - genesis block
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

    def sendTransactions(self) -> None:
        self.walletA.sendFunds(self.walletB.pubKey, round(random.uniform(1, 5), 4))
        self.walletB.sendFunds(self.walletA.pubKey, round(random.uniform(1, 5), 4))
        # self.walletC.sendFunds(self.walletA.pubKey, random.randint(1, 10))

    def clearRepo(self):
        self.txRepo.truncate()
        self.blockRepo.truncate()
        self.txOutRepo.truncate()

        self.txRepo.close()
        self.blockRepo.close()
        self.txOutRepo.close()

    def run(self):
        prevIndex = 0
        prevHash = self.genenerateGenesisBlock()

        for i in range(10):
            time.sleep(1)
            self.sendTransactions()

            with lock:
                txMempool = validatedTx.copy()

        # create new block and mine
            newBlock = Block(index=prevIndex + 1, prevHash=prevHash)
            for tx in txMempool:
                newBlock.addTransaction(tx)
            newBlock.mineBlock(difficulty=DIFFICULTY)
            self.addBlock(newBlock, txMempool)

            prevIndex += 1
            prevHash = newBlock.hash
            txMempool.clear()
            print(f"{self.walletA.getBalance()=}")
            print(f"{self.walletB.getBalance()=}")
        self.clearRepo()


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

    if transaction is None:
        print("Transaction is null - discarded")
        return False, "Transaction is null - discarded"

    # Verify recipient and value list match
    if isinstance(transaction.recipient, list) and isinstance(transaction.value, list):
        if len(transaction.recipient) != len(transaction.value):
            print("Mismatch in number of recipients and values.")
            return False, "Mismatch in number of recipients and values."

    # Ensure all inputs are unspent
    inputs = transaction.inputs if isinstance(transaction.inputs, list) else [transaction.inputs]
    if not all(txInput in UXTOs for txInput in inputs):
        print("Funds already spent.")
        return False, "Funds already spent."

    if not transaction.comfirmSignature():
        print("Invalid signature.")
        return False, "Invalid signature."

    # Check for balance equality between inputs and outputs
    balance_in = sum(txInput.UXTO.value for txInput in inputs if isinstance(txInput, TransactionInput))
    balance_out = sum(txOutput.value for txOutput in transaction.outputs if isinstance(txOutput, TransactionOutput))

    d = decimal.Decimal(str(balance_out))
    if d.as_tuple().exponent < -6:
        print("The transaction amount is invalid. Please enter an amount rounded to the nearest cent.")
        return False, "The transaction amount is invalid. Please enter an amount rounded to the nearest cent."

    if balance_in != balance_out:
        print("Mismatch between total inputs and total outputs.")
        return False, "Mismatch between total inputs and total outputs."

    return True, "Tx valid"
