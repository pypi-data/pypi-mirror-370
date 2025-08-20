"""
Configuration settings for the PDF parser.

This module loads configuration from environment variables or default values.
"""

import os
import logging
from pathlib import Path
# from dotenv import load_dotenv

# load_dotenv()

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_DIR = os.getenv("MODEL_DIR", os.path.join(BASE_DIR, "models"))
OUTPUT_DIR = os.getenv("OUTPUT_DIR", os.path.join(BASE_DIR, "output"))
DEBUG_DIR = os.getenv("DEBUG_DIR", os.path.join(OUTPUT_DIR, "debug"))
TEMP_DIR = os.getenv("TEMP_DIR", os.path.join(BASE_DIR, "temp"))

# Ensure directories exist
os.makedirs(MODEL_DIR, exist_ok = True)
os.makedirs(OUTPUT_DIR, exist_ok = True)
os.makedirs(TEMP_DIR, exist_ok = True)

# Model paths
YOLO_MODEL_PATH = os.path.join(MODEL_DIR, "doclayout_yolo_docstructbench_imgsz1024.pt")

# Image Processing Settings
ZOOM_FACTOR = float(os.getenv("ZOOM_FACTOR", "2.0"))
IOU_THRESHOLD = float(os.getenv("IOU_THRESHOLD", "0.45"))
CONTAINMENT_THRESHOLD = float(os.getenv("CONTAINMENT_THRESHOLD", "0.90"))

# Box Processing Settings
AUTOMATIC_ROW_DETECTION = os.getenv("AUTOMATIC_ROW_DETECTION", "True").lower() in ("true", "1", "yes")
ROW_SIMILARITY_THRESHOLD = int(os.getenv("ROW_SIMILARITY_THRESHOLD", "10"))
CONTAINER_THRESHOLD = int(os.getenv("CONTAINER_THRESHOLD", "2"))

# Memory Management Settings
MEMORY_EFFICIENT = os.getenv("MEMORY_EFFICIENT", "True").lower() in ("true", "1", "yes")
PAGE_BATCH_SIZE = int(os.getenv("PAGE_BATCH_SIZE", "1"))
ENABLE_GC = os.getenv("ENABLE_GC", "True").lower() in ("true", "1", "yes")
CLEAR_CUDA_CACHE = os.getenv("CLEAR_CUDA_CACHE", "True").lower() in ("true", "1", "yes")

# Text label categories (elements that should be preserved during processing)
TEXT_LABELS = ["title", "plain_text"] #"table_caption", "table_footnote", "formula_caption"]

# Embedding Settings
DEFAULT_EMBEDDING_MODEL = "text-embedding-3-small"

# Debug mode settings
DEBUG_MODE = os.getenv("DEBUG_MODE", "False").lower() in ("true", "1", "yes")
if DEBUG_MODE:
    logging.basicConfig(level = logging.DEBUG)

else:
    logging.basicConfig(level = logging.INFO)

# System prompt for table classification
SYSTEM_PROMPT = """
You are a PDF-table classifier.  
Your entire reply **MUST be a single, valid JSON object** that uses the exact keys and allowed values shown below.

[INPUT]
  [TABLE_TEXT] - raw text of the extracted table  

[TASK]
  1. **price_change_type** - decide whether the table documents a price change and, if so, which subtype:  
    • **"amended_price"** - shows original vs. revised prices or uses “amend”, “new price”, “old price”, “delta”, etc.  
    • **"frequency_change"** - changes billing cadence (e.g., monthly → quarterly) or lists new payment schedules.  
    • **"change_order_form"** - part of a formal change-order form (look for “Change Order #”, “CO Request”).  
    • **""** - not a price-change table.

  2. **misc_type** - detect miscellaneous operational tables:  
    • **"currency"** - currency codes, exchange rates, or currency descriptions dominate.  
    • **"signature"** - primarily captures signatures / printed names / titles / dates.  
    • **"circuit_id"** - lists telecom circuit IDs or similar service identifiers.  
    • **""** - none of the above.

  3. **product_type** - determine the **dominant** product category mentioned:  
    • **"hardware"** - physical devices, part numbers, equipment.  
    • **"software"** - licences, subscriptions, version numbers, modules.  
    • **"services"** - support, maintenance, professional-service line items.  
    • **"other"** - doesn't clearly fit the above.

[OUTPUT]
  Return **ONLY** minified JSON, e.g.: {"price_change_type": "amended_price", "misc_type": "currency", "product_type": "hardware"}

[RULES]
  - **Use ONLY the exact lowercase strings** shown above.  
  - **Never** add keys, comments, or extra text.  
  - If uncertain, leave the field blank.  
  - Think step-by-step **internally**, but output **only** the JSON object.  
  - The result **must parse** with a standard JSON parser.
"""
