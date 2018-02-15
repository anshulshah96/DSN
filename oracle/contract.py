import json
import web3

from web3 import Web3, TestRPCProvider
from solc import compile_source
from web3.contract import ConciseContract

from web3 import Web3, HTTPProvider

class Contract():
    """docstring for Contract"""
    def __init__(self, rpc_addr, contract_file):
        self.w3 = Web3(HTTPProvider(rpc_addr))
        with open(contract_file, 'r') as content_file:
            self.contract_content = content_file.read()
        self.compiled_sol = compile_source(self.contract_content) # Compiled source code
        self.contract_interface = self.compiled_sol['<stdin>:CrowdBank']
        self.contract = self.w3.eth.contract(abi=self.contract_interface['abi'], bytecode=self.contract_interface['bin'])
        self.tx_hash = self.contract.deploy(transaction={'from': self.w3.eth.accounts[0], 'gas': 4100000})

        # Get tx receipt to get contract address
        self.tx_receipt = self.w3.eth.getTransactionReceipt(self.tx_hash)
        self.contract_address = self.tx_receipt['contractAddress']

        self.contract_instance = self.w3.eth.contract(self.contract_interface['abi'], self.contract_address, ContractFactoryClass=ConciseContract)

    def get_contract_abi(self):
        return self.contract_interface['abi']

    def get_contract_address(self):
        return self.contract_address

    def issueToken(self, provider_addr, tokenSize, ip, acc_no, gas):
        provider_addr = Web3.toHex(hexstr=provider_addr)
        if not Web3.isAddress(provider_addr):
            raise Exception('address not valid')
        self.contract_instance.issueToken(provider_addr, tokenSize, ip, transact={'from': self.w3.eth.accounts[acc_no], 'gas': gas})
        print "Token Issued"

    def getSToken(self, address):
        address = Web3.toHex(hexstr=address)
        if not Web3.isAddress(address):
            raise Exception('address not valid')
        return self.contract_instance.getSToken(address)

