#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Database controller?
'''
from src.Block import Block
from src.Transaction import Transaction
from src.Wallet import Wallet

UXTOs = []  # to troche na pałe na razie


class Chain:

    def __init__(self, txRepo, blockRepo, uxtoRepo, walletRepo):
        self.txRepo = txRepo
        self.blockRepo = blockRepo
        self.uxtoRepo = uxtoRepo
        self.walletRepo = walletRepo

        self.genenerateGenesisBlock()


    def genenerateGenesisBlock(self):

        coinbase = Wallet()

        genesisTransaction = Transaction(None, coinbase.pubKey, 50, None, 0, "0")
        UXTOs.append(genesisTransaction.outputs)

        # genesisBlock = Block(0, "0")
        # genesisBlock.addTransaction(genesisTransaction)
        # genesisBlock.mineBlock()
