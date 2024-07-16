#!/usr/bin/python
# -*- coding: utf-8 -*-
import hashlib
import ecdsa

import json
import unittest
from src.Transaction import *


class TransactionTest(unittest.TestCase):


    def test_transaction_constructor_1input(self):
        UXTO = TransactionOutput("rcpnt", 0.5, "0")
        inpt = TransactionInput(UXTO)

        tx = Transaction("sndr", ["rcpnt2"], [0.1], inpt, 0)

        self.assertEqual(tx.outputs, [TransactionOutput("rcpnt2", 0.1, tx.transactionID)] )

    def test_transaction_constructor_3input(self):
        UXTO = TransactionOutput("rcpnt", 0.5, "0")
        inpt = TransactionInput(UXTO)

        tx = Transaction("sndr", ["rcpnt2", "rcpnt1", "rcpnt3"], [0.1, 0.2, 0.3], inpt, 0)

        self.assertEqual(tx.outputs, [TransactionOutput("rcpnt2", 0.1, tx.transactionID),
                                      TransactionOutput("rcpnt1", 0.2, tx.transactionID),
                                      TransactionOutput("rcpnt3", 0.3, tx.transactionID)])

    def test_signature_verification(self):
        UXTO = TransactionOutput("rcpnt", 0.5, "0")
        inpt = TransactionInput(UXTO)

        tx = Transaction("sndr", ["rcpnt2"], [0.1], inpt, 0)

        sk = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1, hashfunc=hashlib.sha256) # The default is sha1
        vk = sk.get_verifying_key()

        sk2 = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1, hashfunc=hashlib.sha256, )  # The default is sha1
        vk2 = sk2.get_verifying_key()

        tx.createSignature(sk)
        self.assertEqual(tx.comfirmSignature(vk), True)
        self.assertEqual(tx.comfirmSignature(vk2), False)


    def test_transaction_json(self):
        sk = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1, hashfunc=hashlib.sha256, )  # The default is sha1
        vk = sk.get_verifying_key()

        UXTO = TransactionOutput(vk, 0.5, "0")
        inpt = TransactionInput(UXTO)

        # tx = Transaction("sndr", ["rcpnt2"], [0.1], inpt, 0)
        exp = {
            'recipient': vk,
            'value': 0.5,
            'ID': "0"
        }

        jsonstr2 = json.dumps(UXTO.to_dict())
        data = json.loads(jsonstr2)
        print(pubKeyFromStr(data["recipient"]))

        self.assertEqual(vk, pubKeyFromStr(data["recipient"]))

if __name__ == '__main__':
    unittest.main()