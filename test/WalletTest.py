#!/usr/bin/python
# -*- coding: utf-8 -*-
import hashlib
import ecdsa
import unittest
from src.Wallet import *
from src.Transaction import TransactionOutput
# import unittest
from unittest.mock import patch, MagicMock
from src.Wallet import Wallet, Transaction, TransactionInput, VerifyingKey
class WalletTest(unittest.TestCase):

    def test_key_pair(self):
        wallet = Wallet()
        message = b"Dokad noca tupta jez"
        signature = wallet.prvKey.sign(message)
        self.assertEqual(wallet.pubKey.verify(signature, message), True)

    @patch('src.Wallet.requests.post')  # Mockowanie post
    @patch('src.Wallet.requests.get')  # Mockowanie get
    @patch('src.Wallet.Transaction')  # Mockowanie konstruktora Transaction
    def test_send_funds(self, mock_transaction_constructor, mock_requests_get, mock_requests_post):
        # Mockowanie odpowiedzi dla requests.get
        mock_get_response = MagicMock()
        mock_get_response.json.return_value = {'balance': 100}  # Załóżmy, że getBalance oczekuje takiego JSONa
        mock_requests_get.return_value = mock_get_response

        # Mockowanie odpowiedzi dla requests.post
        mock_post_response = MagicMock()
        mock_post_response.status_code = 200
        mock_requests_post.return_value = mock_post_response

        # Ustawienie zwrotu dla mocka konstruktora Transaction
        mock_transaction = MagicMock()
        mock_transaction_constructor.return_value = mock_transaction

        wallet = Wallet()
        sk, pk = generateKeyPair()

        uxto1 = TransactionOutput(wallet.pubKey, 1, "la vida")
        uxto2 = TransactionOutput(wallet.pubKey, 2, "una")
        uxto3 = TransactionOutput(wallet.pubKey, 3, "mierda")

        wallet.UXTO = [uxto1, uxto2, uxto3]

        # Wywołanie metody sendFunds
        result = wallet.sendFunds(pk, 3)

        # Sprawdzenie, czy zmockowana metoda zwraca oczekiwany obiekt
        self.assertEqual(result, mock_transaction)
        mock_transaction_constructor.assert_called_once()




if __name__ == '__main__':
    unittest.main()