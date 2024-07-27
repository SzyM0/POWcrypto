#!/usr/bin/python
# -*- coding: utf-8 -*-
from tinydb import TinyDB
from flask import Flask, jsonify, request
from Transaction import transactionFromJSON
from Chain import verify_transaction, validatedTx, Chain, lock
import threading

blockRepo = TinyDB('../database/blockRepo.json',  indent=4)
txRepo = TinyDB('../database/txRepo.json',  indent=4)
txOutRepo = TinyDB('../database/txOutRepo.json',  indent=4)
walletRepo = TinyDB('../database/walletRepo.json',  indent=4)

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
        validatedTx.append(txJSON)
    # with open('data.json', 'w', encoding='utf-8') as f:
    #     json.dump(data, f, ensure_ascii=False, indent=4)

    return jsonify({"message": "Tx received", "data": data}), 200

'''
1. check if correct and send back a response  
2. add to local mempool
'''



if __name__ == '__main__':
    chain = Chain(txRepo, blockRepo, txOutRepo, walletRepo)
    threading.Thread(target=chain.run, daemon=True).start()
    app.run(debug=True, use_reloader=False)

# if __name__ == '__main__':
#         chain = Chain(txRepo, blockRepo, txOutRepo, walletRepo)
#         chain.run()



# Wprowadzić zmiany.
#
# Kopanie chyba lepiej jak by było wywoływane w funkcji która dostarcza transakcje
#
# run mogłoby tylko wysyłać transakcje na serwer żeby robić symulacje.
