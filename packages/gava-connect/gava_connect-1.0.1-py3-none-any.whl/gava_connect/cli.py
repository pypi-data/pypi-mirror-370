"""
Command-line interface for GavaConnect.
"""

import argparse
import os
import sys
from dotenv import load_dotenv
from . import KRAGavaConnect, TaxObligationType


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="GavaConnect - Kenya Revenue Authority API Client",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  gava-connect check-pin A123456789
  gava-connect check-id 12345678
  gava-connect obligation-type 9
  gava-connect obligation-code "Value Added Tax (VAT)"
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Check PIN command
    check_pin_parser = subparsers.add_parser('check-pin', help='Check KRA PIN')
    check_pin_parser.add_argument('pin', help='KRA PIN number to check')
    check_pin_parser.add_argument('--env', choices=['sandbox', 'production'], 
                                 default='sandbox', help='Environment to use')
    
    # Check ID command
    check_id_parser = subparsers.add_parser('check-id', help='Check KRA PIN by ID')
    check_id_parser.add_argument('id', help='ID number to check')
    check_id_parser.add_argument('--env', choices=['sandbox', 'production'], 
                                default='sandbox', help='Environment to use')
    
    # Obligation type command
    obligation_type_parser = subparsers.add_parser('obligation-type', 
                                                  help='Get tax obligation type description')
    obligation_type_parser.add_argument('code', help='Tax obligation code')
    
    # Obligation code command
    obligation_code_parser = subparsers.add_parser('obligation-code', 
                                                  help='Get tax obligation code')
    obligation_code_parser.add_argument('description', help='Tax obligation description')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command in ['check-pin', 'check-id']:
            # Load environment variables
            load_dotenv()
            
            consumer_key = os.getenv("PIN_CHECKER_CONSUMER_KEY")
            consumer_secret = os.getenv("PIN_CHECKER_CONSUMER_SECRET")
            
            if not consumer_key or not consumer_secret:
                print("Error: PIN_CHECKER_CONSUMER_KEY and PIN_CHECKER_CONSUMER_SECRET must be set in environment variables or .env file")
                sys.exit(1)
            
            # Initialize client
            client = KRAGavaConnect(consumer_key, consumer_secret, args.env)
            
            if args.command == 'check-pin':
                result = client.check_pin_kra_pin(args.pin)
                print(f"PIN Check Result for {args.pin}:")
                print(result)
            
            elif args.command == 'check-id':
                result = client.check_pin_by_id(args.id)
                print(f"ID Check Result for {args.id}:")
                print(result)
        
        elif args.command == 'obligation-type':
            result = TaxObligationType.get_obligation_type(args.code)
            print(f"Tax obligation type for code '{args.code}': {result}")
        
        elif args.command == 'obligation-code':
            result = TaxObligationType.get_obligation_code(args.description)
            print(f"Tax obligation code for '{args.description}': {result}")
    
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
