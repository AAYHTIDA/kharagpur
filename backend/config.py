import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Using free LLM - no API key needed
    CHUNK_SIZE_TOKENS = 2500
    CHUNK_OVERLAP_TOKENS = 200
    MAX_CONCURRENT_LLM_CALLS = 3  # Rate limit friendly

config = Config()
