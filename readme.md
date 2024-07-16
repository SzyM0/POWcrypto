# Simple Cryptocurrency Project

This repository contains a prototype of a simple cryptocurrency designed as part of my master's thesis. This project is intended as a proof of concept and will run locally on my computer. The project is implemented in Python and utilizes the Proof of Work algorithm.

## Project Description

The main goal of this project is to create a basic framework for a cryptocurrency. It includes the following key components:

- **Blocks**: The fundamental units of the blockchain, containing a list of transactions.
- **Transactions**: Records of value transfers between wallets.
  - **Outgoing Transactions**: Transactions initiated by a wallet.
  - **Incoming Transactions**: Transactions received by a wallet.
- **Wallets**: Digital wallets used to store and transfer the cryptocurrency.
- **Blockchain**: The complete ledger of all transactions, consisting of a chain of blocks.

Data will be stored in a database. Although the final choice of the database has not been made yet, TinyDB is a potential candidate due to its simplicity and ease of use with Python.

## Components

1. **Block**
   - Represents a single block in the blockchain.
   - Contains a list of transactions and a reference to the previous block.

2. **Transaction**
   - Represents a transfer of value between wallets.
   - Each transaction includes details such as sender, receiver, amount, and a timestamp.

3. **OutgoingTransaction**
   - A subclass of `Transaction` representing transactions initiated by a wallet.

4. **IncomingTransaction**
   - A subclass of `Transaction` representing transactions received by a wallet.

5. **Wallet**
   - Represents a user's digital wallet.
   - Used to store cryptocurrency and initiate transactions.

6. **Blockchain**
   - A chain of blocks representing the entire transaction ledger.
   - Ensures the integrity and immutability of the transaction history.

## Proof of Work

The project uses the Proof of Work (PoW) algorithm to secure the blockchain. PoW involves solving a computationally intensive puzzle to add a new block to the blockchain, ensuring that the addition of new blocks is difficult and resource-intensive.

## Getting Started

### Prerequisites

- Python 3.x
- Required Python libraries (specified in `requirements.txt`)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/simple-cryptocurrency.git


