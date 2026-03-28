from web3 import Web3
from dotenv import load_dotenv
import os

load_dotenv()

BLOCKCHAIN_RPC_URL = os.getenv("BLOCKCHAIN_RPC_URL")
PRIVATE_KEY = os.getenv("BLOCKCHAIN_PRIVATE_KEY")
CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS")

w3 = Web3(Web3.HTTPProvider(BLOCKCHAIN_RPC_URL))

account = w3.eth.account.from_key(PRIVATE_KEY)

CONTRACT_ABI = [
    {
        "inputs": [
            {"internalType": "string", "name": "_hash", "type": "string"}
        ],
        "name": "addHash",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    }
]

contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=CONTRACT_ABI)