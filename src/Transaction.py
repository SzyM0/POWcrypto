import hashlib
import ecdsa
from ecdsa import VerifyingKey, SigningKey
from typing import Type, List

def pubKeyToStr(pubkey):
    return pubkey.to_string().hex()

def pubKeyFromStr(key):
    vk_bytes = bytes.fromhex(key)
    return ecdsa.VerifyingKey.from_string(vk_bytes, curve=ecdsa.SECP256k1)


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
        if isinstance(other, TransactionOutput):
            return self.ID == other.ID and self.recipient == other.recipient and self.value == other.value
        return False

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
        if isinstance(other, TransactionInput):
            return self.ID == other.ID and self.UXTO == other.UXTO
        return False

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
                 ID: str=None):
        self.blockIndex = 0  # ?
        self.sender = sender
        self.recipient = recipient
        self.value = value
        self.change = change
        self.signature = 0
        self.inputs = inputs
        self.transactionID = self.createID() if ID is None else ID
        self.outputs = self.createOutputs()

    def createID(self) -> str:
        '''
        Creates a unique hash based on sender, recipient and value

        :return: str hash
        '''

        sha = hashlib.sha256()
        sha.update(str(self.sender).encode('utf-8') +
                   str(self.recipient).encode('utf-8') +
                   str(self.value).encode('utf-8'))
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
        recipient = [pubKeyToStr(rcp) for rcp in self.recipient] if isinstance(self.recipient, list) else self.recipient
        inputs = [inp.to_dict() for inp in self.inputs] if isinstance(self.inputs, list) else self.inputs
        outputs = [out.to_dict() for out in self.outputs] if isinstance(self.outputs, list) else self.outputs
        #todo dokończyć
        return {
            'sender': pubKeyToStr(self.sender),
            'recipient': recipient,
            'value': self.value,
            'inputs': inputs,
            'change': self.change,
            'signature': self.signature,
            'transactionID': self.transactionID,
            'outputs': outputs
        }


def verifyTransacion(transaction: Transaction):
    """
    todo napisać test
    Sprawdź czy inputy są w uxto
    sprawdź podpis
    sprawdź czy format się zgadza, jak jest dwóch odbiorców to dwa outputy itp
    sprawdź czy suma wejść równa się sumie wyjść

    :param transaction:
    :return:
    """

    # check if when there's more than one recipient the list of values and recipients are the same
    if isinstance(transaction.recipient, list) and isinstance(transaction.value, list):
        if len(transaction.recipient) != len(transaction.value):
            print("Wrong transaction data: recipient and value length mismatch")
            return False

    #check if inputs/outputs exist
    if not transaction.inputs:
        print("Input values are missing")
        return False

    if not transaction.outputs:
        print("Output values are missing")
        return False

    # check if input not already spent
    for txInput in :
        if isinstance(txInput, TransactionInput):
            if txInput not in UXTOs:
                print("Funds already spent")
                return False
        else:
            print("Wrong format of transaction input")
            return False

    #check signature
    if not transaction.comfirmSignature(transaction.sender):
        print("Signature incorrect")
        return False

    # check if value of inputs is the same as value of outputs
    balanceIn = 0
    balanceOut = 0

    for txInput in transaction.inputs:
        if isinstance(txInput, TransactionInput):
            balanceIn += txInput.UXTO.value

    for txOutput in transaction.outputs:
        if isinstance(txOutput, TransactionOutput):
            balanceOut += txOutput.value

    if balanceOut != balanceIn:
        print("Inputs are not equal to outputs")
        return False


