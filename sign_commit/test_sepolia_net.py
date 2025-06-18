import web3
from solcx import set_solc_version, install_solc
from solcx import compile_source
from eth_account import Account
from web3.middleware import geth_poa_middleware

# Install and set Solidity compiler version
install_solc('0.8.19')
set_solc_version('v0.8.19')


# Function to compile the Solidity contract
def compile_source_file(file_path):
    with open(file_path, 'r') as f:
        source = f.read()
    return compile_source(source)


# Function to deploy the Solidity contract
def deploy_contract(w3, contract_interface, account):
    contract = w3.eth.contract(
        abi=contract_interface['abi'],
        bytecode=contract_interface['bin']
    )

    # Build transaction
    transaction = contract.constructor().build_transaction({
        'from': account.address,
        'nonce': w3.eth.get_transaction_count(account.address),
        'gas': 6721975,
        'gasPrice': w3.toWei('21', 'gwei')
    })

    # Sign transaction
    signed_txn = w3.eth.account.sign_transaction(transaction, private_key=account.key)

    # Send transaction
    tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)

    # Wait for transaction receipt
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    return tx_receipt.contractAddress


# Function to compile and deploy the Solidity contract, returning the contract object
def compile_deploy_file(w3, file_path, account):
    compiled_sol = compile_source_file(file_path)
    contract_id, contract_interface = compiled_sol.popitem()
    address1 = deploy_contract(w3, contract_interface, account)
    abi1 = contract_interface['abi']
    Contract = w3.eth.contract(address=address1, abi=abi1)
    return Contract


# Connect to Sepolia test network via Infura
infura_url = "https://sepolia.infura.io/v3/f4989a64355c4c459ced5216e9828c0c"
w3 = web3.Web3(web3.HTTPProvider(infura_url))

# Inject the poa compatibility middleware to the innermost layer
w3.middleware_onion.inject(geth_poa_middleware, layer=0)

# Sepolia network private key and account
private_key = "0x80d806e852e259bad4a9803fae23bfe1ef8731cd7cebc1f6e8a53cb703b60320"
account = Account.from_key(private_key)

# Compile and deploy the contract
deployed_Contract = compile_deploy_file(w3, "ECDSA_pedersen.sol", account)

print("Contract deployed at address:", deployed_Contract.address)
