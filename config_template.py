"""
Configuration File - API Keys και Ρυθμίσεις
Αντιγράψτε αυτό το αρχείο ως config.py και προσθέστε τα API keys σας
"""

import os

# ============================================================================
# API KEYS - Προσθέστε τα δικά σας API keys εδώ
# ============================================================================

# News API - https://newsapi.org/
# Δωρεάν: 100 requests/ημέρα
NEWS_API_KEY = os.getenv('NEWS_API_KEY', '925a7fbe50fd41d8b03f15ef47dc5c24')

# ACLED API - https://acleddata.com/
# Χρειάζεται εγγραφή
ACLED_API_KEY = os.getenv('ACLED_API_KEY', 'YOUR_ACLED_API_KEY_HERE')
ACLED_EMAIL = os.getenv('ACLED_EMAIL', 'your_email@example.com')

# GDELT Project - Δεν απαιτεί API key
# https://www.gdeltproject.org/


# ============================================================================
# ΡΥΘΜΙΣΕΙΣ ΕΦΑΡΜΟΓΗΣ
# ============================================================================

# Update interval (σε δευτερόλεπτα)
UPDATE_INTERVAL = 300  # 5 λεπτά

# Flask settings
FLASK_HOST = '0.0.0.0'
FLASK_PORT = 5000
FLASK_DEBUG = True

# Database
DATABASE_PATH = 'conflicts.db'

# Conflict regions με συντεταγμένες
CONFLICT_REGIONS = {
    'Ukraine': {'lat': 49.0, 'lng': 32.0, 'region': 'Eastern Europe'},
    'Gaza': {'lat': 31.5, 'lng': 34.5, 'region': 'Middle East'},
    'Israel': {'lat': 31.5, 'lng': 34.8, 'region': 'Middle East'},
    'Palestine': {'lat': 31.9, 'lng': 35.2, 'region': 'Middle East'},
    'Sudan': {'lat': 15.5, 'lng': 32.5, 'region': 'North Africa'},
    'Myanmar': {'lat': 22.0, 'lng': 96.0, 'region': 'Southeast Asia'},
    'Yemen': {'lat': 15.5, 'lng': 48.0, 'region': 'Middle East'},
    'Syria': {'lat': 35.0, 'lng': 38.0, 'region': 'Middle East'},
    'Ethiopia': {'lat': 9.0, 'lng': 40.0, 'region': 'Central Africa'},
    'Somalia': {'lat': 5.0, 'lng': 46.0, 'region': 'Central Africa'},
    'Afghanistan': {'lat': 33.0, 'lng': 65.0, 'region': 'Central Asia'},
    'Iraq': {'lat': 33.0, 'lng': 44.0, 'region': 'Middle East'},
    'Libya': {'lat': 27.0, 'lng': 17.0, 'region': 'North Africa'},
    'Mali': {'lat': 17.0, 'lng': -4.0, 'region': 'West Africa'},
    'Nigeria': {'lat': 9.0, 'lng': 8.0, 'region': 'West Africa'},
    'DRC': {'lat': -4.0, 'lng': 21.0, 'region': 'Central Africa'},
    'Mozambique': {'lat': -18.0, 'lng': 35.0, 'region': 'Southern Africa'},
    'Colombia': {'lat': 4.0, 'lng': -72.0, 'region': 'Latin America'},
    'Mexico': {'lat': 23.0, 'lng': -102.0, 'region': 'Latin America'}
}

# Known proxy wars και connections
PROXY_WARS = [
    {
        'from': 'Ukraine',
        'to': 'Syria',
        'type': 'proxy_war',
        'description': 'Russian military involvement'
    },
    {
        'from': 'Yemen',
        'to': 'Syria',
        'type': 'arms_flow',
        'description': 'Iranian support'
    },
    {
        'from': 'Gaza',
        'to': 'Yemen',
        'type': 'alliance',
        'description': 'Iranian proxy network'
    },
    {
        'from': 'Syria',
        'to': 'Lebanon',
        'type': 'spillover',
        'description': 'Refugee crisis and instability'
    }
]

# Logging
LOG_LEVEL = 'INFO'  # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'


# ============================================================================
# ΟΔΗΓΙΕΣ
# ============================================================================

"""
1. Αντιγράψτε αυτό το αρχείο ως 'config.py'
2. Προσθέστε τα API keys σας
3. Προσαρμόστε τις ρυθμίσεις όπως χρειάζεται
4. ΜΗΝ κοινοποιήσετε το config.py σε public repositories!

Για production χρήση, χρησιμοποιήστε environment variables:

export NEWS_API_KEY="your_key_here"
export ACLED_API_KEY="your_key_here"
export ACLED_EMAIL="your_email@example.com"

Ή δημιουργήστε .env file:

NEWS_API_KEY=your_key_here
ACLED_API_KEY=your_key_here
ACLED_EMAIL=your_email@example.com
"""
