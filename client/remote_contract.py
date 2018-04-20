import json
import web3

from web3 import Web3, TestRPCProvider
from web3.contract import ConciseContract
import requests

from web3 import Web3
from web3.providers.rpc import HTTPProvider

def get_contract():
    r = requests.get('http://localhost:8900/contract')
    contractAddress = r.json()['address']
    abi = r.json()['abi']
    w3 = Web3(HTTPProvider("http://localhost:8545"))
    fContract = w3.eth.contract(contractAddress,abi=abi)
    return (w3,fContract)


class RemoteContract():
    """docstring for Contract"""
    def __init__(self, rpc_addr, remote_url):
        self.w3 = Web3(HTTPProvider(rpc_addr))
        self.remote_url = remote_url
        r = requests.get(remote_url)
        self.contract_abi = r.json()['abi']
        self.contract_address = r.json()['address']
        self.contract_bin = r.json()['bin']
        self.contract_address = self.w3.toChecksumAddress(self.contract_address)
        self.contract = self.w3.eth.contract(self.contract_address, abi=self.contract_abi,  bytecode=self.contract_bin)
        # self.contract_instance = self.w3.eth.contract(self.contract_abi, self.contract_address, ContractFactoryClass=ConciseContract)

    def get_eth_address(self):
        # return self.tx_hash = self.contract.deploy(transaction={'from': self.w3.eth.accounts[0], 'gas': 4100000})
        return self.w3.eth.accounts[1]

    def get_rate(self, provider):
        provider = Web3.toHex(hexstr=provider)
        if not Web3.isAddress(provider):
            raise Exception('Provider Address is not valid')
        return self.contract_instance.getPRate(address)

    def get_eth_balance(self, address):
        provider = Web3.toHex(hexstr=address)
        return self.w3.fromWei(self.w3.eth.getBalance(address),'ether')

    def get_service(self, provider, pos):
        provider = Web3.toHex(hexstr=address)
        response = contract.functions.getServiceByAddressPosition(provider, pos).call()
        print(response)
        (provider, client, numToken, rate, eTime, lVTime) = response
        return response

    def pay_service(self, provider, service_num, rate):
        (w3, contract) = get_contract()
        provider = self.w3.toChecksumAddress(provider)
        service_num = int(service_num)
        rate = int(10000000)
        contract.functions.payService(provider,service_num).transact(
            {'from' : self.w3.eth.accounts[1], 'value': rate, 'gas':420000})

