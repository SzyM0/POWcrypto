import hashlib
import random

import ecdsa
from ecdsa import VerifyingKey, SigningKey
from typing import List


def pubKeyToStr(pubkey):
    return pubkey.to_string().hex()


def pubKeyFromStr(key):
    vk_bytes = bytes.fromhex(key)
    return ecdsa.VerifyingKey.from_string(vk_bytes, curve=ecdsa.SECP256k1, hashfunc=hashlib.sha256)


def sigToStr(sig: bytes) -> str | None:
    if isinstance(sig, int):
        print("No signature created")
        return None
    if isinstance(sig, bytes):
        return sig.hex()
    return None


def sigFromStr(sig: str) -> bytes | None:
    if isinstance(sig, str):
        return bytes.fromhex(sig)
    return None


class TransactionOutput:
    # Transaction ID, recipient

    def __init__(self, recipient: VerifyingKey, value: float, ID: str=None):
        self.recipient = recipient
        self.value = value
        self.ID = self.createID() if ID is None else ID  # ID == none tylko w przypadku bloku genezy

    def createID(self) -> str:
        sha = hashlib.sha256()
        sha.update(str(self.recipient).encode('utf-8') +
                   str(self.value).encode('utf-8'))
        return sha.hexdigest()

    def __eq__(self, other):
        # todo jest debugowane tera
        if isinstance(other, TransactionOutput):
            result = self.ID == other.ID
        elif isinstance(other, TransactionInput):

            result = self.ID == other.ID and other.UXTO.recipient == self.recipient and other.UXTO.value == self.value
        else:
            result = False
        # print(f"Comparing {self} to {other}, result: {result}")
        return result

    def to_dict(self):
        return {
            'recipient': pubKeyToStr(self.recipient),
            'value': self.value,
            'ID': self.ID
        }


class TransactionInput:
    # Transaction ID, UXTO

    def __init__(self, UXTO: TransactionOutput):
        self.ID = UXTO.ID
        self.UXTO = UXTO

    def __eq__(self, other):
        # if isinstance(other, TransactionInput):
        #     return self.ID == other.ID and self.UXTO == other.UXTO
        # if isinstance(other, TransactionOutput):
        #     return self.ID == other.ID and self.UXTO.recipient == other.recipient and self.UXTO.value == other.value
        # return False
        if isinstance(other, TransactionInput):
            result = self.ID == other.ID and self.UXTO == other.UXTO
        elif isinstance(other, TransactionOutput):
            result = self.ID == other.ID and self.UXTO.recipient == other.recipient and self.UXTO.value == other.value
        else:
            result = False
        # print(f"Comparing {self} to {other}, result: {result}")
        return result

    def __hash__(self):
        return hash((self.ID, self.UXTO))

    def to_dict(self):
        return {
            'recipient': pubKeyToStr(self.UXTO.recipient),
            'value': self.UXTO.value,
            'ID': self.UXTO.ID
        }


class Transaction:
    # Transaction inputs, transaction outputs, signature
    def __init__(self,
                 sender: VerifyingKey | None,  # None possible if genesis block
                 recipient: List[VerifyingKey] | VerifyingKey,
                 value: List[float] | float,
                 inputs: List[TransactionInput] | TransactionInput | None,  # None possible if genesis block
                 change: float,
                 signature=None,
                 ID: str=None,
                 outputs: List[TransactionOutput] | TransactionOutput | None=None):
        self.blockIndex = 0  # ?
        self.sender = sender
        self.recipient = recipient
        self.value = value
        self.change = change
        self.signature = 0 if signature is None else signature
        self.inputs = inputs
        self.transactionID = self.createID() if ID is None else ID
        self.outputs = self.createOutputs() if outputs is None else outputs

    def setBlockIndex(self, index):
        self.blockIndex = index

    def createID(self) -> str:
        '''
        Creates a unique hash based on sender, recipient and value

        :return: str hash
        '''

        sha = hashlib.sha256()
        sha.update(str(self.sender).encode('utf-8') +
                   str(self.recipient).encode('utf-8') +
                   str(self.value).encode('utf-8') +
                   str(random.randint(0, 100)).encode('utf-8'))
        return sha.hexdigest()

    def createOutputs(self) -> List[TransactionOutput] | TransactionOutput | None:
        '''
        Creates output objects based on the list of recipients

        todo check if the list of recipent is as long as list of value or even replace it with dictionary
        :return: UXTO list
        '''

        uxto_set = []

        # If only one recipient
        if not isinstance(self.recipient, list) and not isinstance(self.value, list):
            uxto_set.append(TransactionOutput(self.recipient, self.value, self.transactionID))
        else:
            #  todo przypadek jak jedno jest listą, a drugie nie
            # If more than one recipient
            if len(self.recipient) != len(self.value):
                print("Wrong transaction data: recipient and value mismatch")
                return None

            for destinationAddress, value in zip(self.recipient, self.value):
                uxto_set.append(TransactionOutput(destinationAddress, value, self.transactionID))

        # If change needed
        if self.change > 0:  # return yourself a change
            uxto_set.append(TransactionOutput(self.sender, self.change, self.transactionID))

        return uxto_set

    def createSignature(self, privKey: SigningKey) -> None:
        '''
        todo czy jest sens to przekazywac, może użyć self.sender?
        Gets private key of the owner of UXTO and sighns the transaction.

        :param privKey: private key
        :return: Updates signature field
        todo moze spróbować wygerenowac pub key i sprawdzic czy to ten sam co sender
        '''

        data = str(self.recipient).encode('utf-8') + str(self.sender).encode('utf-8') + str(self.value).encode('utf-8')
        signature = privKey.sign(data)
        self.signature = signature

    def comfirmSignature(self, pubKey: VerifyingKey) -> bool:
        '''
        Gets public key and checks if the signature is correct.

        :param pubKey: public key
        :return: True/False
        '''
        data = str(self.recipient).encode('utf-8') + str(self.sender).encode('utf-8') + str(self.value).encode('utf-8')

        try:
            confirmation_result = pubKey.verify(self.signature, data)
        except ecdsa.BadSignatureError:
            return False

        return confirmation_result

    def __eq__(self, other) -> bool:
        if isinstance(other, Transaction):
            return (self.sender == other.sender and
                    self.recipient == other.recipient and
                    self.value == other.value and
                    self.change == other.change and
                    self.signature == other.signature and
                    self.inputs == other.inputs and
                    self.transactionID == other.transactionID and
                    self.outputs == other.outputs)
        return False

    def to_dict(self) -> dict:
        # in case more than one recipient
        recipient = [pubKeyToStr(rcp) for rcp in self.recipient] if isinstance(self.recipient, list) else pubKeyToStr(self.recipient)
        inputs = [inp.to_dict() for inp in self.inputs] if isinstance(self.inputs, list) else self.inputs.to_dict()
        outputs = [out.to_dict() for out in self.outputs] if isinstance(self.outputs, list) else self.outputs.to_dict()

        #  todo dokończyć
        return {
            'transactionID': self.transactionID,
            'sender': pubKeyToStr(self.sender),
            'recipient': recipient,
            'value': self.value,
            'change': self.change,
            'signature': sigToStr(self.signature),
            'inputs': inputs,
            'outputs': outputs
        }


def transactionFromJSON(json: dict) -> Transaction:
    input_set_rec = []
    output_set_rec = []

    # retrieve inputs
    if isinstance(json['inputs'], list):
        for txInput in json['inputs']:
            unspent_tx = TransactionOutput(pubKeyFromStr(txInput['recipient']), txInput['value'], txInput['ID'])
            input_set_rec.append(TransactionInput(unspent_tx))

    elif isinstance(json['inputs'], dict):
        txInput = json['inputs']
        unspent_tx = TransactionOutput(pubKeyFromStr(txInput['recipient']), txInput['value'], txInput['ID'])
        input_set_rec = TransactionInput(unspent_tx)

    else:
        input_set_rec.append(None)

    # retrieve outputs
    if isinstance(json['outputs'], list):
        for txOutput in json['outputs']:
            output_tx = TransactionOutput(pubKeyFromStr(txOutput['recipient']), txOutput['value'], txOutput['ID'])
            output_set_rec.append(output_tx)

    elif isinstance(json['outputs'], dict):
        txOutput = json['outputs']
        output_tx = TransactionOutput(pubKeyFromStr(txOutput['recipient']), txOutput['value'], txOutput['ID'])
        output_set_rec = output_tx

    else:
        output_set_rec.append(None)

    sender_rec = pubKeyFromStr(json['sender'])
    recipient_rec = pubKeyFromStr(json['recipient'])
    value_rec = json['value']
    change_rec = json['change']
    sig_rec = sigFromStr(json['signature'])
    id_rec = json['transactionID']

    return Transaction(sender_rec, recipient_rec, value_rec, input_set_rec, change_rec, signature=sig_rec, ID=id_rec, outputs=output_set_rec)


