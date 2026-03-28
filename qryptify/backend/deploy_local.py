from solcx import install_solc, set_solc_version, compile_source
from web3 import Web3
from dotenv import load_dotenv
import os

load_dotenv()

BLOCKCHAIN_RPC_URL = os.getenv("BLOCKCHAIN_RPC_URL")
PRIVATE_KEY = os.getenv("DEPLOYER_PRIVATE_KEY")

install_solc("0.8.0")
set_solc_version("0.8.0")

w3 = Web3(Web3.HTTPProvider(BLOCKCHAIN_RPC_URL))

account = w3.eth.account.from_key(PRIVATE_KEY)

contract_source = """
pragma solidity ^0.8.0;

contract AuditHashStorage {
    string[] public logHashes;

    function addHash(string memory _hash) public {
        logHashes.push(_hash);
    }
}
"""

compiled = compile_source(contract_source)
contract_id, contract_interface = compiled.popitem()

Contract = w3.eth.contract(
    abi=contract_interface["abi"],
    bytecode=contract_interface["bin"]
)

tx = Contract.constructor().build_transaction({
    "from": account.address,
    "nonce": w3.eth.get_transaction_count(account.address),
    "gas": 3000000,
    "gasPrice": w3.eth.gas_price
})

signed_tx = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

print("Contract Address:", receipt.contractAddress)