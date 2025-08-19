"""
KRA API Client implementation for GavaConnect package.
"""

import os
import requests
import base64
import logging
from enum import Enum
from dotenv import load_dotenv
from typing import Dict, Any, Optional

load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TaxObligationType(Enum):
    """Enumeration of tax obligation types supported by KRA."""
    
    INCOME_TAX_COMPANY = ("4", "Income Tax - Company")
    INCOME_TAX_PAYE = ("7", "Income Tax - PAYE")
    VAT = ("9", "Value Added Tax (VAT)")
    ADVANCE_TAX = ("22", "Advance Tax")
    INCOME_TAX_WITHHOLDING = ("6", "Income Tax - Withholding")
    CAPITAL_GAIN_TAX = ("32", "Capital Gain Tax (CGT)")
    VAT_WITHHOLDING = ("29", "VAT Withholding")

    def __init__(self, code: str, description: str):
        self.code = code
        self.description = description

    @classmethod
    def get_obligation_type(cls, code: str) -> str:
        """
        Get the tax obligation type description based on the code.
        
        Args:
            code: The tax obligation code.
            
        Returns:
            The description of the tax obligation type.
        """
        for obligation in cls:
            if obligation.code == code:
                return obligation.description
        return "Unknown Tax Obligation Type"
    
    @classmethod
    def get_obligation_code(cls, description: str) -> str:
        """
        Get the tax obligation code based on the description.
        
        Args:
            description: The description of the tax obligation type.
            
        Returns:
            The code of the tax obligation type.
        """
        for obligation in cls:
            if obligation.description == description:
                return obligation.code
        return "Unknown Tax Obligation Code"


class KRAMethodsProvider:
    """Provider class for KRA API endpoints and methods."""
    
    def __init__(self, environment: str = "sandbox"):
        """
        Initialize the KRA methods provider.
        
        Args:
            environment: The environment to use ("sandbox" or "production").
        """
        self.environment = environment.lower()
        
        if self.environment in ["sandbox", "development", "test", "dev"]:
            self.base_url = "https://sbx.kra.go.ke"
        elif self.environment in ["production", "live"]:
            self.base_url = "https://api.kra.go.ke"
        else:
            logger.error("Invalid environment specified. Use 'sandbox' or 'production'.")
            raise ValueError("Invalid environment specified. Use 'sandbox' or 'production'.")
       
        logger.info(f"KRA Methods Provider initialized with base URL: {self.base_url}")
        logger.info(f"Environment set to: {self.environment}")

    def check_pin_url(self, check_by_what: str = "pin") -> str:
        """
        Returns the URL for checking KRA PINs based on the environment.
        
        Args:
            check_by_what: The type of check ("pin" or "id").
            
        Returns:
            The complete URL for the PIN check endpoint.
        """
        if self.environment not in ["sandbox", "production", "live", "development", "test", "dev"]:
            logger.error("Invalid environment specified. Use 'sandbox' or 'production'.")
            raise ValueError("Invalid environment specified. Use 'sandbox' or 'production'.")
        
        url = f"{self.base_url}/checker/v1/pinbypin" if check_by_what.lower() == "pin" else f"{self.base_url}/checker/v1/pin"
        return url.replace(" ", "").replace("\n", "").replace("\r", "").strip()
    
    def file_nil_return_url(self) -> str:
        """
        Returns the URL for filing tax returns based on the environment.
        
        Returns:
            The complete URL for the tax return filing endpoint.
        """
        url = f"{self.base_url}/dtd/return/v1/nil"
        return url.replace(" ", "").replace("\n", "").replace("\r", "").strip()


    def get_token_url(self) -> str:
        """
        Returns the token generation URL based on the environment.
        
        Returns:
            The complete URL for token generation.
        """
        return f"{self.base_url}/v1/token/generate?grant_type=client_credentials"


class KRAGavaConnect:
    """Main client class for interacting with the KRA API."""
    
    def __init__(self, consumer_key: str, consumer_secret: str, environment: str = "sandbox"):
        """
        Initialize the KRA GavaConnect client.
        
        Args:
            consumer_key: Your KRA API consumer key.
            consumer_secret: Your KRA API consumer secret.
            environment: The environment to use ("sandbox" or "production").
        """
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.environment = environment
        self.methods = KRAMethodsProvider(environment)
        self.access_token = self.__authenticate()
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.access_token}"
        }

    def __authenticate(self) -> str:
        """
        Authenticate and generate an access token.
        
        Returns:
            The access token for API requests.
            
        Raises:
            ValueError: If credentials are missing.
            Exception: If authentication fails.
        """
        if not self.consumer_key or not self.consumer_secret:
            raise ValueError("Consumer Key and Consumer Secret must be provided.")
        
        # Encode credentials in Base64
        credentials = f"{self.consumer_key}:{self.consumer_secret}"
        encoded_credentials = base64.b64encode(credentials.encode("utf-8")).decode("utf-8")
        
        headers = {
            "Authorization": f"Basic {encoded_credentials}"
        }

        token_url = self.methods.get_token_url()
        response = requests.get(token_url, headers=headers)

        if response.status_code == 200:
            data = response.json()
            return data["access_token"]
        else:
            raise Exception(f"Failed to generate token: {response.status_code}, {response.text}")

    def check_pin_kra_pin(self, kra_pin_number: str) -> Dict[str, Any]:
        """
        Check if a KRA PIN is valid using the KRA API.
        
        Args:
            kra_pin_number: The KRA PIN number to check.
            
        Returns:
            JSON response from the KRA API.
        """
        response = requests.post(
            url=self.methods.check_pin_url("pin"), 
            json={"KRAPIN": kra_pin_number}, 
            headers=self.headers
        )
        return response.json()
       
    def check_pin_by_id(self, id_number: str) -> Dict[str, Any]:
        """
        Check if a KRA PIN is valid using the KRA API by ID.
        
        Args:
            id_number: The ID number to check.
            
        Returns:
            JSON response from the KRA API.
        """
        response = requests.post(
            url=self.methods.check_pin_url("id"), 
            json={"TaxpayerType": "KE", "TaxpayerID": id_number}, 
            headers=self.headers
        )
        return response.json()

    def file_nil_return(self, 
        taxpayer_pin: str, 
        obligation_code: int, 
        month: int, 
        year: int) -> Dict[str, Any]:
        """
        File a tax return using the KRA API.
        
        Args:
            taxpayer_pin: The taxpayer PIN.
            obligation_code: The obligation code.
            month: The month of the tax return.
            year: The year of the tax return.
            
        Returns:
            JSON response from the KRA API.
        """
        data = {
            "TAXPAYERDETAILS": {
                "Year": year,
                "Month": month,
                "TaxpayerPIN": taxpayer_pin,
                "ObligationCode": obligation_code
            }
        }

        print(f"URL: {self.methods.file_nil_return_url()}")
        
        response = requests.post(
            url=self.methods.file_nil_return_url(),
            json=data,
            headers=self.headers
        )
        return response.json()
      


checker = KRAGavaConnect(
    consumer_key=os.getenv("PIN_CHECKER_CONSUMER_KEY"), 
    consumer_secret=os.getenv("PIN_CHECKER_CONSUMER_SECRET"), 
    environment="sandbox"
)
