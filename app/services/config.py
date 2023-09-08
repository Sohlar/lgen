import os
from dotenv import load_dotenv

load_dotenv()

GOOG_API_KEY = os.environ.get("GOOG_API_KEY")
if not GOOG_API_KEY:
    raise ValueError("GOOG_API_KEY environment variable not set")

GOOGLE_CX = os.environ.get("GOOG_CX_KEY")
if not GOOGLE_CX:
    raise ValueError("GOOGLE_CX environment variable not set")


""" 
STRIPE_API_KEY = os.environ.get("STRIPE_API_KEY")
if not STRIPE_API_KEY:
    raise ValueError('STRIPE_API_KEY environment variable not set')

EBAY_API_KEY = os.environ.get("EBAY_API_KEY")
if not EBAY_API_KEY:
    raise ValueError('EBAY_API_KEY environment variable not set')

GMAPS_API_KEY = os.environ.get("GMAPS_API_KEY")
if not GMAPS_API_KEY:
    raise ValueError('GMAPS_API_KEY environment variable not set')

EBAY_APP_ID = 'YOUR_EBAY_APP_ID'
"""
