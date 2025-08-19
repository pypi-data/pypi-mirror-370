# GavaConnect - Kenya Revenue Authority API Client

A Python package for simplified access to Kenya Revenue Authority (KRA) API. This package provides an easy-to-use interface for checking KRA PIN numbers and validating taxpayer information.

## Features

- 🔐 Secure authentication with KRA API
- 📋 KRA PIN validation
- 🆔 ID-based PIN lookup
- 🏗️ Support for both sandbox and production environments
- 📊 Tax obligation type enumeration
- 🛡️ Error handling and logging

## Installation

```bash
pip install gava-connect
```

## Quick Start

### 1. Set up your environment variables

Create a `.env` file in your project directory:

```env
PIN_CHECKER_CONSUMER_KEY=your_consumer_key_here
PIN_CHECKER_CONSUMER_SECRET=your_consumer_secret_here
```

### 2. Basic Usage

```python
from gava_connect import KRAGavaConnect

# Initialize the client (sandbox environment)
kra_client = KRAGavaConnect(
    consumer_key="your_consumer_key",
    consumer_secret="your_consumer_secret",
    environment="sandbox"  # or "production"
)

# Check KRA PIN
result = kra_client.check_pin_kra_pin("A123456789")
print(result)

# Check PIN by ID number
result = kra_client.check_pin_by_id("12345678")
print(result)
```

## API Reference

### KRAGavaConnect

The main client class for interacting with the KRA API.

#### Constructor

```python
KRAGavaConnect(consumer_key, consumer_secret, environment="sandbox")
```

**Parameters:**
- `consumer_key` (str): Your KRA API consumer key
- `consumer_secret` (str): Your KRA API consumer secret
- `environment` (str): Environment to use ("sandbox" or "production")

#### Methods

##### check_pin_kra_pin(kra_pin_number)

Check if a KRA PIN is valid.

**Parameters:**
- `kra_pin_number` (str): The KRA PIN number to validate

**Returns:**
- dict: JSON response from the KRA API

##### check_pin_by_id(id_number)

Check KRA PIN using ID number.

**Parameters:**
- `id_number` (str): The ID number to lookup

**Returns:**
- dict: JSON response from the KRA API

### TaxObligationType

Enumeration of tax obligation types supported by KRA.

#### Available Types

- `"4"`: Income Tax - Company
- `"7"`: Income Tax - PAYE
- `"9"`: Value Added Tax (VAT)
- `"22"`: Advance Tax
- `"6"`: Income Tax - Withholding
- `"32"`: Capital Gain Tax (CGT)
- `"29"`: VAT Withholding

#### Methods

##### get_obligation_type(code)

Get the description of a tax obligation type by its code.

##### get_obligation_code(description)

Get the code of a tax obligation type by its description.

## Environment Configuration

The package supports two environments:

- **Sandbox**: For testing and development
  - Base URL: `https://sbx.kra.go.ke`
- **Production**: For live applications
  - Base URL: `https://api.kra.go.ke`

## Error Handling

The package includes comprehensive error handling:

- Invalid environment specification
- Missing or invalid credentials
- API authentication failures
- Network request errors

## Logging

The package uses Python's built-in logging module. Logs are set to INFO level by default.

## Examples

### Complete Example

```python
import os
from dotenv import load_dotenv
from gava_connect import KRAGavaConnect, TaxObligationType

# Load environment variables
load_dotenv()

# Initialize client
kra_client = KRAGavaConnect(
    consumer_key=os.getenv("PIN_CHECKER_CONSUMER_KEY"),
    consumer_secret=os.getenv("PIN_CHECKER_CONSUMER_SECRET"),
    environment="sandbox"
)

# Check a KRA PIN
try:
    result = kra_client.check_pin_kra_pin("A123456789")
    print("PIN Check Result:", result)
except Exception as e:
    print(f"Error checking PIN: {e}")

# Get tax obligation type description
obligation_desc = TaxObligationType.get_obligation_type("9")
print(f"Tax obligation 9: {obligation_desc}")  # Output: Value Added Tax (VAT)
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support, please open an issue on the GitHub repository or contact the maintainers.

## Disclaimer

This package is not officially affiliated with the Kenya Revenue Authority. Please ensure you comply with KRA's terms of service and API usage guidelines.
# KRA-GAVA-Connect
