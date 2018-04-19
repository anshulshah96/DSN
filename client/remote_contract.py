import json
import web3

from web3 import Web3, TestRPCProvider
from web3.contract import ConciseContract
import requests

from web3 import Web3, HTTPProvider

class RemoteContract():
    """docstring for Contract"""
    def __init__(self, rpc_addr, remote_url):
        self.w3 = Web3(HTTPProvider(rpc_addr))
        self.remote_url = remote_url
        r = requests.get(remote_url)
        self.contract_abi = r.json()['abi']
        self.contract_address = r.json()['address']
        self.contract_bin = r.json()['bin']
        self.contract = self.w3.eth.contract(abi=self.contract_abi, bytecode=self.contract_bin)
        # self.contract_instance = self.w3.eth.contract(self.contract_abi, self.contract_address, ContractFactoryClass=ConciseContract)

    def get_eth_address(self):
        # return self.tx_hash = self.contract.deploy(transaction={'from': self.w3.eth.accounts[0], 'gas': 4100000})
        return self.w3.eth.accounts[1]

    def get_rate(self, provider):
        provider = Web3.toHex(hexstr=provider)
        if not Web3.isAddress(provider):
            raise Exception('Provider Address is not valid')
        return self.contract_instance.getPRate(address)