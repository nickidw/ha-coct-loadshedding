"""Constants for City of Cape Town loadshedding interface"""
# Base component constants
NAME = "City of Cape Town Loadshedding"
DOMAIN = "coct_loadshedding"
DOMAIN_DATA = f"{DOMAIN}_data"
VERSION = "1.0.0"

ISSUE_URL = "https://github.com/nickidw/ha-coct-loadshedding/issues"

# Icons
ICON = "mdi:lightning-bolt"

# Platforms
SENSOR = "sensor"
PLATFORMS = [SENSOR]

# Configuration and options
CONF_ENABLED = "enabled"
CONF_SCAN_PERIOD = "scan_period"
CONF_COCT_AREA_NUMBER = "coct_area_number"

# Defaults
DEFAULT_SCAN_PERIOD = 900
MIN_SCAN_PERIOD = 300
DEFAULT_AREA_NUMBER = 1

# Defaults
DEFAULT_NAME = DOMAIN


STARTUP_MESSAGE = f"""
-------------------------------------------------------------------
{NAME}
Version: {VERSION}
Welcome to the City of Cape Town Loadshedding Interface!
If you have any issues with this you need to open an issue here:
{ISSUE_URL}
-------------------------------------------------------------------
"""
