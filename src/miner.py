#!/usr/bin/python
# -*- coding: utf-8 -*-
from tinydb import TinyDB, Query
from flask import Flask, jsonify

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

app = Flask(__name__)

@app.route('/receiveTransaction', methods=['POST'])
def receiveTransaction():
    pass

'''
1. check if correct and send back a response  
2. add to local mempool
'''



if __name__ == '__main__':
    app.run(debug=True)


    """
    1. take tx from local mempool 
    
    2. create new block
    
    3. add tx to block
    
    4. mine block? 
    
    5. update uxto, tx, chain in local memory
    
    6. update them in database 
    """








