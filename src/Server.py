#!/usr/bin/python
# -*- coding: utf-8 -*-
from tinydb import TinyDB
from flask import Flask, jsonify, request
from src.Transaction import transactionFromJSON, pubKeyFromStr
from src.Chain import verify_transaction, validatedTx, Chain, lock, UXTOs
import threading

blockRepo = TinyDB('../database/blockRepo.json',  indent=4)
txRepo = TinyDB('../database/txRepo.json',  indent=4)
txOutRepo = TinyDB('../database/txOutRepo.json',  indent=4)

app = Flask(__name__)

@app.route('/postTransaction', methods=['POST'])
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
        validatedTx.append(txJSON)

    return jsonify({"message": "Tx received", "data": data}), 200

@app.route('/getUXTO', methods=['GET'])
def sendUXTO():

    with lock:
        unspentTx = UXTOs.copy()

    pubKey = pubKeyFromStr(request.args.get('pubKey', default=None))
    uxto = []
    for tx in unspentTx:
        if tx.recipient == pubKey:
            uxto.append(tx)

    data = [item.to_dict() for item in uxto]

    if data:
        return jsonify({"message": "UXTO found ", "data": data}), 200
    else:
        return jsonify({"error": "No UXTO found"}), 400



'''
1. check if correct and send back a response  
2. add to local mempool
'''

if __name__ == '__main__':
    chain = Chain(txRepo, blockRepo, txOutRepo)
    threading.Thread(target=chain.run, daemon=True).start()
    app.run(debug=False, use_reloader=False)

