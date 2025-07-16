import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DATA_PATH = os.path.join(PROJECT_ROOT, 'data', 'raw')
PROCESSED_DATA_PATH = os.path.join(PROJECT_ROOT, 'data', 'processed')