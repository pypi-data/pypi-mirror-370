#!/usr/bin/env python3
"""
Example usage of GavaConnect package.
"""

import os
from dotenv import load_dotenv
from gava_connect import KRAGavaConnect, TaxObligationType

def main():
    """Example usage of the GavaConnect package."""
    
    # Load environment variables
    load_dotenv()
    
    # Get credentials from environment
    consumer_key = os.getenv("PIN_CHECKER_CONSUMER_KEY")
    consumer_secret = os.getenv("PIN_CHECKER_CONSUMER_SECRET")
    
    if not consumer_key or not consumer_secret:
        print("Please set PIN_CHECKER_CONSUMER_KEY and PIN_CHECKER_CONSUMER_SECRET in your .env file")
        print("See env.example for reference")
        return
    
    try:
        # Initialize the KRA client
        print("Initializing KRA client...")
        kra_client = KRAGavaConnect(
            consumer_key=consumer_key,
            consumer_secret=consumer_secret,
            environment="sandbox"  # Use "production" for live environment
        )
        print("✅ KRA client initialized successfully!")
        
        # Example 1: Check a KRA PIN
        print("\n--- Example 1: Checking KRA PIN ---")
        pin_result = kra_client.check_pin_kra_pin("A123456789")
        print(f"PIN Check Result: {pin_result}")
        
        # Example 2: Check PIN by ID
        print("\n--- Example 2: Checking PIN by ID ---")
        id_result = kra_client.check_pin_by_id("12345678")
        print(f"ID Check Result: {id_result}")
        
        # Example 3: Get tax obligation type information
        print("\n--- Example 3: Tax Obligation Types ---")
        obligation_desc = TaxObligationType.get_obligation_type("9")
        print(f"Tax obligation code '9' is: {obligation_desc}")
        
        obligation_code = TaxObligationType.get_obligation_code("Value Added Tax (VAT)")
        print(f"Tax obligation 'Value Added Tax (VAT)' has code: {obligation_code}")
        
        # Example 4: List all available tax obligation types
        print("\n--- Example 4: All Available Tax Obligation Types ---")
        for obligation in TaxObligationType:
            print(f"Code: {obligation.code} - {obligation.description}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Please check your credentials and network connection.")

if __name__ == "__main__":
    main()
