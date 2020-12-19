import os
import sys
import datetime
from blockchain_parser.blockchain import Blockchain

def btc_to_sat(btc):
    return btc * 100000000

def sat_to_btc(sat):
    return sat / 100000000

def find_transactions_with_restrictions(blockchain, time_start, time_end, amount_min, amount_max):
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

def menu_find_transaction_by_hash(blocks_path, tx_hash):
    if len(tx_hash) != 64:
        print(tx_hash, "is not a transaction hash")
    blockchain = Blockchain(blocks_path)
    tx = get_transaction_by_hash(blockchain, tx_hash)
    print(tx.hash)
    for output in tx.outputs:
        print(sat_to_btc(output.value), "BTC", "->", output.addresses[0].address)

def menu_find_transactions_with_restrictions(blocks_path, time_start, time_end, amount_min, amount_max):
    blockchain = Blockchain(blocks_path)
    transactions = find_transactions_with_restrictions(blockchain, time_start, time_end, btc_to_sat(amount_min), btc_to_sat(amount_max))
    print("Found", len(transactions), "transactions")
    for tx, block in transactions:
        print(tx.hash, block.header.timestamp)
        for output in tx.outputs:
            print(sat_to_btc(output.value), "BTC", "->", output.addresses[0].address)
        for input in tx.inputs:
            print("input tx hash:", input.transaction_hash)


def print_help():
    print(
        '''btc.py blocks_path {<timedelta> <amount>|<transaction_hash>}
        time format: DD:MM:YYYY:hh:mm:ss
        timedelta = time=<time1>-<time2> - диапазон дат для поиска
        amount - количество биткоинов
        transaction_hash - хеш транзакции
        ''')

def main(argv):
    blocks_path = None
    if len(argv) not in (3, 4):
        print_help()
        return
    if not os.path.isdir(argv[1]):
        print_help()
        return

    if len(argv) == 3:
        blocks_path = argv[1]
        transaction_hash = argv[2]
        print("Searching for transaction ", transaction_hash)
        menu_find_transaction_by_hash(blocks_path, transaction_hash)
    elif len(argv) == 4:
        blocks_path = argv[1]
        dates_str = argv[2].split('-')
        if len(dates_str) != 2:
            print_help()
            return
        date_start = datetime.datetime.strptime(dates_str[0], "%d:%m:%Y:%H:%M:%S")
        date_end = datetime.datetime.strptime(dates_str[1], "%d:%m:%Y:%H:%M:%S")
        amounts_str = argv[3].split('-')
        if len(amounts_str) != 2:
            print_help()
            return
        amount_min = int(amounts_str[0])
        amount_max = int(amounts_str[1])
        print("Searching for transactions ", amount_min, "-", amount_max, "BTC", date_start, "-", date_end)
        menu_find_transactions_with_restrictions(blocks_path, date_start, date_end, amount_min, amount_max)


main(sys.argv)
