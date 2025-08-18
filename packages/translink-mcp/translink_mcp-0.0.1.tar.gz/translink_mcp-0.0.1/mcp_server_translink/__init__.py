from .server import serve

import asyncio
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(dotenv_path=os.path.join(os.getcwd(), ".env"))

def main():
    """MCP Translink Server - Tools to interface with Vancouver's Translink transportation system."""
    api_key = os.getenv("TRANSLINK_API_KEY")

    if not api_key:
        raise ValueError("TRANSLINK_API_KEY must be set in the environment or .env file.")

    asyncio.run(serve(api_key))


if __name__ == "__main__":
    main()
