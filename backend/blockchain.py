import os
from eth_account import Account
from web3 import Web3

CONTRACT_ABI = [
    {
        "inputs": [{"internalType": "uint256", "name": "jobId", "type": "uint256"}],
        "name": "release",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [{"internalType": "uint256", "name": "jobId", "type": "uint256"}],
        "name": "refund",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
]


class BlockchainError(Exception):
    pass


def _get_client():
    rpc = os.getenv("MONAD_RPC")
    private_key = os.getenv("AGENT_PRIVATE_KEY")
    contract_address = os.getenv("CONTRACT_ADDRESS")

    if not rpc or not private_key or not contract_address:
        raise BlockchainError("Missing MONAD_RPC, AGENT_PRIVATE_KEY, or CONTRACT_ADDRESS")

    web3 = Web3(Web3.HTTPProvider(rpc))
    if not web3.is_connected():
        raise BlockchainError("Unable to connect to Monad RPC")

    account = Account.from_key(private_key)
    contract = web3.eth.contract(address=Web3.to_checksum_address(contract_address), abi=CONTRACT_ABI)
    return web3, account, contract


def _send_tx(fn):
    web3, account, _ = _get_client()
    try:
        tx = fn.build_transaction(
            {
                "from": account.address,
                "nonce": web3.eth.get_transaction_count(account.address),
                "gas": 250000,
                "gasPrice": web3.eth.gas_price,
                "chainId": web3.eth.chain_id,
            }
        )
        signed_tx = account.sign_transaction(tx)
        tx_hash = web3.eth.send_raw_transaction(signed_tx.raw_transaction)
        receipt = web3.eth.wait_for_transaction_receipt(tx_hash, timeout=180)
        if receipt.status != 1:
            raise BlockchainError("Transaction reverted")
        return receipt.transactionHash.hex()
    except Exception as exc:  # pragma: no cover - network dependent
        raise BlockchainError(str(exc)) from exc


def release_payment(job_id: int) -> str:
    _, _, contract = _get_client()
    return _send_tx(contract.functions.release(job_id))


def refund_payment(job_id: int) -> str:
    _, _, contract = _get_client()
    return _send_tx(contract.functions.refund(job_id))
