#!/usr/bin/python
# -*- coding: utf-8 -*-
import hashlib
import ecdsa
import unittest
from src.Wallet import *
from src.Transaction import TransactionOutput

class WalletTest(unittest.TestCase):


    def test_key_pair(self):
        wallet = Wallet()

        message = b"Dokad noca tupta jez"

        signature = wallet.prvKey.sign(message)
        self.assertEqual(wallet.pubKey.verify(signature, message), True)

    def test_send_funds(self):
        wallet = Wallet()

        uxto1 = TransactionOutput(wallet.pubKey, 1)
        uxto2 = TransactionOutput(wallet.pubKey, 2)
        uxto3 = TransactionOutput(wallet.pubKey, 3)

        in1 = TransactionInput(uxto1)
        in2 = TransactionInput(uxto2)
        in3 = TransactionInput(uxto3)

        wallet.getBalance([uxto1, uxto2, uxto3])
        sk, pk = generateKeyPair()

        # self.assertEqual(wallet.sendFunds(pk, 5), None)
        tx_obs = wallet.sendFunds(pk, 3)
        tx_exp = Transaction(wallet.pubKey, pk, 3, [in1, in2], 0)

        self.assertEqual(tx_obs, tx_exp)



if __name__ == '__main__':
    unittest.main()