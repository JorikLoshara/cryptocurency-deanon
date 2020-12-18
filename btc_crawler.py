import sys

import bs4
import requests
import re
import hashlib
import base58
import binascii
import time
from urllib.parse import urljoin, urlparse


#TARGET_URL = "https://github.com/scottycc/coinwidget.com"
#TARGET_URL = "https://github.com/burakcanekici/BitcoinAddressValidator"
#TARGET_URL = "https://github.com/burakcanekici"
TARGET_URL = "https://github.com/search?q=blockchain&type=Repositories"
MAX_DEPTH = 2
target_host = None
session = None
re_btc = re.compile('1.{26,33}')
re_eth = re.compile('0x[0-9a-fA-F]{40}]')

found_btc = {}
found_eth = {}

def is_btc_addr_correct(addr):
    base58_alphabet = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
    for x in addr:
        if x not in base58_alphabet:
            return False
    bitcoinAddress = addr
    base58Decoder = base58.b58decode(bitcoinAddress).hex()
    prefixAndHash = base58Decoder[:len(base58Decoder) - 8]
    checksum = base58Decoder[len(base58Decoder) - 8:]
    hash = prefixAndHash
    for x in range(1, 3):
        hash = hashlib.sha256(binascii.unhexlify(hash)).hexdigest()
    if (checksum == hash[:8]):
        return True
    else:
        return False

def parse_page(url, recursion_depth=0):
    if recursion_depth == MAX_DEPTH:
        return
    #print(recursion_depth)
    print(url)
    time.sleep(0.9)
    try:
        page_text = requests.get(url).text
    except:
        print("Error on ", url)
        return
    bs = bs4.BeautifulSoup(page_text, 'html.parser')

    #search for links for next search
    raw_links = bs.findAll('a', href=True)
    good_links = []
    for link in raw_links:
        if link['href'].startswith('#'):
            continue
        if link['href'].startswith('/'):
            good_links.append(get_full_url_from_relative(link['href']))
        else:
            good_links.append(link['href'])

    #search for cryptoaddrs
    btc_addrs = []
    eth_addrs = []

    for t in bs.findAll(text=True):
        btc_addrs.extend(re_btc.findall(t))
        eth_addrs.extend(re_eth.findall(t))
    btc_addrs = [addr for addr in btc_addrs if is_btc_addr_correct(addr)]
    if len(btc_addrs) != 0:
        found_btc[url] = btc_addrs
    if len(eth_addrs) != 0:
        found_eth[url] = eth_addrs

    for link in good_links:
        parse_page(link, recursion_depth+1)


def get_base_url(url):
    parsed_uri = urlparse(url)
    return '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)

def get_full_url_from_relative(rel):
    return urljoin(target_host, rel)


def main(argv):
    global target_host, session

    TARGET_URL = argv[1]
    MAX_DEPTH = int(argv[2])

    print("target: ", TARGET_URL)
    print("max depth: ", MAX_DEPTH)

    target_host = get_base_url(TARGET_URL)
    session = requests.session()
    parse_page(TARGET_URL)
    print('BTC')
    for a in found_btc:
        print(a)
        for addr in found_btc[a]:
            print(addr)
    print('ETH')
    for a in found_eth:
        print(a)
        for addr in found_eth[a]:
            print(addr)




main(sys.argv)