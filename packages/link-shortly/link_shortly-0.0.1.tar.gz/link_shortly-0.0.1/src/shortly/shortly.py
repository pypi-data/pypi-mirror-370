"""
Link-Shortly - A simple URL shortening library.

@author:   RknDeveloper
@contact:  https://t.me/RknDeveloperr
@license:  MIT License, see LICENSE file

Copyright (c) 2025-present RknDeveloper
"""

from .utils import convert
import requests

class Shortly:
    def __init__(self, api_key: str, base_url: str):
        """
        Initialize Shortly instance.
        
        Input:
            api_key (str)  -> API key for authentication
            base_url (str) -> Base API URL of the shortening service
        
        Output:
            Stores api_key and base_url in the object
        """
        self.api_key = api_key
        self.base_url = base_url   # fixed (was base_site)

    def convert(self, link: str, alias: str, timeout=10):
        """
        Convert a long link into a short one using alias.

        Input:
            link (str)    -> The long URL to shorten
            alias (str)   -> Custom alias for the shortened URL
            timeout (int) -> Request timeout in seconds (default: 10)

        Output:
            Returns shortened link or error response from utils.convert
        """
        return convert(self, self.api_key, self.base_url, link, alias, timeout)
