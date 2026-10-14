import os
import sys

# Ensure project root is in sys.path so modules like backend and app can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
