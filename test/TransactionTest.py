#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
import unittest

from src.Chain import verify_transaction, UXTOs
from src.Transaction import *


sk = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1, hashfunc=hashlib.sha256)  # The default is sha1
wallet = sk.get_verifying_key()

sk2 = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1, hashfunc=hashlib.sha256, )  # The default is sha1
wallet2 = sk2.get_verifying_key()

sk3 = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1, hashfunc=hashlib.sha256, )  # The default is sha1
wallet3 = sk3.get_verifying_key()

class TransactionTest(unittest.TestCase):


    def test_transaction_constructor_1input(self):
        UXTO = TransactionOutput(wallet, 0.5, "0")
        inpt = TransactionInput(UXTO)

        tx = Transaction(wallet, wallet2, 0.1, inpt, 0)

        self.assertEqual(tx.outputs, [TransactionOutput(wallet2, 0.1, tx.transactionID)])

    def test_transaction_constructor_3input(self):
        UXTO = TransactionOutput(wallet, 0.5, "0")
        inpt = TransactionInput(UXTO)

        tx = Transaction(wallet, [wallet2, wallet3], [0.1, 0.2], inpt, 0)

        self.assertEqual(tx.outputs, [TransactionOutput(wallet2, 0.1, tx.transactionID),
                                      TransactionOutput(wallet3, 0.2, tx.transactionID)])

    def test_signature_verification(self):
        UXTO = TransactionOutput(wallet, 0.5, "0")
        inpt = TransactionInput(UXTO)

        tx = Transaction(wallet2, wallet3, 0.1, inpt, 0)

        tx.createSignature(sk)
        self.assertEqual(tx.comfirmSignature(wallet), True)
        self.assertEqual(tx.comfirmSignature(wallet2), False)

    def test_transaction_pubKeyFromString(self):
        uxto = TransactionOutput(wallet2, 0.5, "0")
        inpt = TransactionInput(uxto)

        tx = Transaction(wallet2, wallet3, 0.1, inpt, 0)

        tx.createSignature(sk)

        self.assertEqual(tx.comfirmSignature(wallet), True)
        self.assertEqual(tx.comfirmSignature(wallet2), False)

    def test_transaction_sigToStr(self):
        uxto = TransactionOutput(wallet2, 0.5, "0")
        inpt = TransactionInput(uxto)
        tx = Transaction(wallet2, wallet3, 0.1, inpt, 0)
        tx.createSignature(sk2)

        sig_to_str = sigToStr(tx.signature)
        sig_recovered = sigFromStr(sig_to_str)

        tx.signature = sig_recovered

        self.assertEqual(tx.comfirmSignature(wallet2), True)
        self.assertEqual(tx.comfirmSignature(wallet), False)

    def test_transaction_json(self):
        uxto = TransactionOutput(wallet, 0.5, "0")
        inpt = TransactionInput(uxto)
        tx = Transaction(wallet, wallet2, 0.3, inpt, 0)

        tx.createSignature(sk)

        data = tx.to_dict()

        jsonstr2 = json.dumps(tx.to_dict())
        tx_dict_from_json = json.loads(jsonstr2)
        txJSON = transactionFromJSON(tx_dict_from_json)

        # f = open("myfile.txt", "w")
        # f.write(jsonstr2)

        print(tx.comfirmSignature(wallet))
        print(txJSON.comfirmSignature(wallet))
        self.assertEqual(tx.comfirmSignature(wallet), txJSON.comfirmSignature(wallet))


        self.assertEqual(tx, txJSON)

        self.assertEqual(tx.blockIndex, txJSON.blockIndex, "Block indices are not equal")
        self.assertEqual(tx.sender, txJSON.sender, "Sender addresses are not equal")
        self.assertEqual(tx.recipient, txJSON.recipient, "Recipient addresses are not equal")
        self.assertEqual(tx.value, txJSON.value, "Transaction values are not equal")
        self.assertEqual(tx.change, txJSON.change, "Change values are not equal")
        self.assertEqual(tx.signature, txJSON.signature, "Signatures are not equal")
        self.assertEqual(tx.inputs, txJSON.inputs, "Input lists are not equal")
        self.assertEqual(tx.transactionID, txJSON.transactionID, "Transaction IDs are not equal")
        self.assertEqual(tx.outputs, txJSON.outputs, "Outputs are not equal")

    def test_verify_transaction(self):
        uxto = TransactionOutput(wallet, 0.5, "0")
        UXTOs.append(uxto)
        inpt = TransactionInput(uxto)
        tx = Transaction(wallet, wallet2, 0.3, inpt, 0.2)

        tx.createSignature(sk)
        print(verify_transaction(tx))
        self.assertEqual(verify_transaction(tx), (True, 'Tx valid'))

        tx = Transaction(wallet, wallet2, 0.3, inpt, 0)
        tx.createSignature(sk)
        self.assertEqual(verify_transaction(tx), (False, 'Mismatch between total inputs and total outputs.'))

    def test_sighature_to_str(self):

        data = str("Darek").encode('utf-8') + str("Krzysiek").encode('utf-8') + str(3).encode('utf-8')
        signature = sk.sign(data)

        sig_to_str = sigToStr(signature)
        sig_recovered = sigFromStr(sig_to_str)
        self.assertEqual(sig_recovered, signature)

        self.assertEqual(wallet.verify(signature, data), True)
        self.assertEqual(wallet.verify(sig_recovered, data), True)



if __name__ == '__main__':
    unittest.main()