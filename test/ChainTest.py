#!/usr/bin/python
# -*- coding: utf-8 -*-
import json
import unittest

from tinydb import TinyDB

from src.Chain import Chain, verify_transaction, UXTOs
from src.Transaction import transactionFromJSON
from src.Block import Block

blockRepo = TinyDB('../database/test_database/blockRepo.json', create_dirs=True)
txRepo = TinyDB('../database/test_database/txRepo.json')
txOutRepo = TinyDB('../database/test_database/txOutRepo.json')
walletRepo = TinyDB('../database/test_database/walletRepo.json')

class ChainTest(unittest.TestCase):

    def setUp(self):
        self.chain = Chain(txRepo, blockRepo, txOutRepo)
    def test_verify_transaction(self):
        # txJSON = self.chain.sendTransactions()
        with open('myfile.txt') as f:
            txJSON = json.load(f)

        tx = transactionFromJSON(txJSON)
        verify_transaction(tx)
        self.assertEqual((False, 'Funds already spent.'), verify_transaction(tx))

    # def test_store_tx(self):
    #     with open('myfile.txt') as f:
    #         txJSON = json.load(f)
    #     self.chain.storeTransactions([txJSON])




