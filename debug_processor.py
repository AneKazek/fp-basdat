from app.services.processor import to_transaction_items
from app.models.schemas import TransactionItem

mock_data = [
    {
        'blockNumber': '23948040', 
        'blockHash': '0xcd4d8060a54122920e467747c3e7a346772982d4792611c6c7eac1eaec19696d', 
        'timeStamp': '1764953423', 
        'hash': '0xdd3d45cdeecc2e41efc1ef4487225c945470ed195db1dd83a1c812f4bbf6c8f1', 
        'nonce': '1585', 
        'transactionIndex': '176', 
        'from': '0xf8fc9a91349ebd2033d53f2b97245102f00aba96', 
        'to': '0xd8da6bf26964af9d7eed9e03e53415d37aa96045', 
        'value': '12122025000000', 
        'gas': '31840', 
        'gasPrice': '1300818862', 
        'input': '0x', 
        'methodId': '0x', 
        'functionName': '', 
        'contractAddress': '', 
        'cumulativeGasUsed': '20965707', 
        'txreceipt_status': '1', 
        'gasUsed': '21062', 
        'confirmations': '6041', 
        'isError': '0'
    }
]

address = "0xd8da6bf26964af9d7eed9e03e53415d37aa96045"

try:
    items = to_transaction_items(mock_data, address)
    print(f"Successfully parsed {len(items)} items")
    print(items[0])
except Exception as e:
    print(f"Error parsing: {e}")
