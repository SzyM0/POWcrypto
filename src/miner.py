#!/usr/bin/python
# -*- coding: utf-8 -*-
from tinydb import TinyDB, Query
from flask import Flask, jsonify, request
import json
from Transaction import transactionFromJSON
from src.Transaction import verify_transaction
import threading

lock = threading.Lock()
UXTOs = []
# transactionRepo = TinyDB('../database/Transactions.json')
# uxtoRepo = TinyDB('../database/UXTO.json')
# blockRepo = TinyDB('../database/Blocks.json')
# walletRepo = TinyDB('../database/Wallets.json')
# mempool = TinyDB('../database/mempool.json')

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
    data = request.get_json()
    txJSON = transactionFromJSON(data)

    if data is None:
        return jsonify({"error": "No JSON received"}), 400

    result, message = verify_transaction(txJSON)
    if not result:
        return jsonify({'error': message}), 400

    # add data to local mempool
    with lock:
        UXTOs.append(txJSON)

    return jsonify({"message": "Tx received", "data": data}), 200

'''
1. check if correct and send back a response  
2. add to local mempool
'''



if __name__ == '__main__':
    # threading.Thread(target=background_task, daemon=True).start()
    app.run(debug=True)


    """
    1. take tx from local mempool 
    
    2. create new block
    
    3. add tx to block
    
    4. mine block? 
    
    5. update uxto, tx, chain in local memory
    
    6. update them in database 
    """








