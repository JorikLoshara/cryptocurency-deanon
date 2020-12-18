import os
import sys
import datetime
from blockchain_parser.blockchain import Blockchain

def btc_to_sat(btc):
    return btc * 100000000

def get_transactions_by_attributes(blockchain, time_start, time_end, amount_min, amount_max):
    result_transactions = []
    for block in blockchain.get_unordered_blocks():
        block_timestamp = block.header.timestamp
        if (time_start < block_timestamp and block_timestamp < time_end) or (time_start is None or time_end is None):
            for tx in block.transactions:
                for output in tx.outputs:
                    if amount_min <= output.value and output.value <= amount_max:
                        result_transactions.append((tx, block))
    return result_transactions

def get_transaction_by_hash(blockchain, tx_hash):
    for block in blockchain.get_unordered_blocks():
        for tx in block.transactions:
            if tx.hash == tx_hash:
                return tx

def main(argv):
    blockchain = Blockchain('.')
    time_start = datetime.datetime(2009, 1, 11, 0, 0, 0)
    time_end = datetime.datetime(2009, 1, 13, 0, 0, 0)
    transactions = get_transactions_by_attributes(blockchain, time_start, time_end, btc_to_sat(9), btc_to_sat(11))
    print("Found", len(transactions), "transactions")
    for tx, block in transactions:
        print(tx.hash, block.header.timestamp)
        for output in tx.outputs:
            print(output.value, "->", output.addresses[0].address)
        for input in tx.inputs:
            print("input transaction hash:", input.transaction_hash)

    tx1 = get_transaction_by_hash(blockchain, '0437cd7f8525ceed2324359c2d0ba26006d92d856a9c20fa0241106ee5a597c9')
    print(tx1)
    for output in tx1.outputs:
        print(output.value, "->", output.addresses[0].address)




main(sys.argv)
