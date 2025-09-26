import os
from dotenv import load_dotenv

load_dotenv() 

OPENAQ_API_KEY = os.getenv("OPENAQ_API_KEY")