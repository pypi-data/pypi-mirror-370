"""
# `abstract_webtools.py` Documentation

This script, `abstract_webtools.py`, is a component of the `abstract_webtools` module and is a part of the `abstract_essentials` package. It provides a set of tools and functions to interact with and parse web content.

## Contents

1. **Imports**
   - Essential modules and classes for web requests, SSL configurations, and URL parsing are imported at the beginning.

2. **Core Functions**

   - `get_status(url: str) -> int or None`:
     Fetches the HTTP status code for a given URL.

   - `clean_url(url: str) -> list`:
     Returns variations of the given URL with different protocols.

   - `get_correct_url(url: str, session: requests.Session) -> str or None`:
     Identifies the correct URL from possible variations using HTTP requests.

   - `try_request(url: str, session: requests.Session) -> requests.Response or None`:
     Attempts to make an HTTP request to a given URL.

   - `is_valid(url: str) -> bool`:
     Validates if a given URL is structurally correct.

   - `desktop_user_agents() -> list`:
     Returns a list of popular desktop user-agent strings.

   - `get_user_agent(user_agent: str) -> dict`:
     Returns a dictionary containing the user-agent header.

3. **TLSAdapter Class**

   A custom HTTPAdapter class that manages SSL options and ciphers for web requests.

   - `TLSAdapter.__init__(self, ssl_options: int)`: 
     Initializes the adapter with specific SSL options.

   - Several methods to handle cipher strings, creation of cipher strings, and initialization of the pool manager with custom SSL configurations.

4. **Advanced Web Functions**

   - `get_Source_code(url: str, user_agent: str) -> str or None`:
     Retrieves the source code of a website with a custom user-agent.

   - `parse_react_source(url: str) -> list`:
     Extracts JavaScript and JSX source code from the specified URL.

   - `get_all_website_links(url: str) -> list`:
     Lists all the internal URLs found on a specific webpage.

   - `parse_all(url: str) -> dict`:
     Parses source code to extract details about elements, attributes, and class names.

   - `extract_elements(url: str, element_type: str, attribute_name: str, class_name: str)`:
     Extracts specific portions of source code based on provided filters. The function signature seems to be cut off, so the full details aren't available.

## Usage

The functions and classes provided in this module allow users to interact with websites, from simple actions like getting the status code of a URL to more advanced functionalities such as parsing ReactJS source codes or extracting specific HTML elements from a website.

To utilize this module, simply import the required function or class and use it in your application. The functions have been designed to be intuitive and the provided docstrings give clear guidance on their usage.

Author: putkoff
Version: 1.0
"""
# -*- coding: UTF-8 -*-
# Google Chrome Driver
import os
import ssl
import re
import yt_dlp
import socket
import shutil
import logging
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import xml.etree.ElementTree as ET
from typing import Optional,List,Union
from requests.adapters import HTTPAdapter
from urllib.parse import urlparse, urljoin
from requests.packages.urllib3.util import ssl_
from requests.packages.urllib3.poolmanager import PoolManager
from urllib.parse import urlparse, parse_qs
import time
import requests
from .managers import *
from .managers.urlManager.urlManager import *
from abstract_utilities import get_time_stamp,get_sleep,sleep_count_down,eatInner,eatAll,eatOuter,ThreadManager
logging.basicConfig(level=logging.INFO)
def try_request(request):
    try:
        respnse = requests.get(url)
    except Exception as e:
        print(f'request for url failed: {e}')
        response = None
    return response

