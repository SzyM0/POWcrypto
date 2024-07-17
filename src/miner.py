#!/usr/bin/python
# -*- coding: utf-8 -*-
from tinydb import TinyDB, Query

transactionRepo = TinyDB('../database/Transactions.json')
uxtoRepo = TinyDB('../database/UXTO.json')
blockRepo = TinyDB('../database/Blocks.json')
walletRepo = TinyDB('../database/Wallets.json')
mempool = TinyDB('../database/mempool.json')

'''
1. get transactions
2. if enough make a block
3. make pow
4. add to chain
5. update UXTO set

create DATA:
block repo
transaction repo
uxto repo
'''



if __name__ == '__main__':
    pass






