import asyncio
import os
from dotenv import load_dotenv
from app.services.etherscan_client import EtherscanClient

load_dotenv()

# Mock settings if needed, but load_dotenv should handle .env
api_key = os.getenv("ETHERSCAN_API_KEY")
if not api_key:
    print("WARNING: ETHERSCAN_API_KEY not found in env")
    # You might need to provide a fallback or ensure .env exists
    
async def main():
    print(f"Testing with API Key: {api_key[:5]}...")
    client = EtherscanClient(api_key)
    
    # Vitalik's address
    address = "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"
    chain_id = 1 # Mainnet
    
    print(f"Fetching txlist for {address} on chain {chain_id}...")
    try:
        resp = await client.get_txlist(address, chain_id=chain_id)
        print("Response status:", resp.get("status"))
        print("Response message:", resp.get("message"))
        
        result = resp.get("result", [])
        if isinstance(result, list):
            print(f"Found {len(result)} transactions")
            if len(result) > 0:
                print("First tx:", result[0])
        else:
            print("Result is not a list:", result)
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
