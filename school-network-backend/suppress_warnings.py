"""
Suppress Scapy and cryptography warnings on startup.
Import this early in your application to suppress known warnings.
"""

import warnings
import logging

# Suppress cryptography deprecation warnings about TripleDES
warnings.filterwarnings(
    "ignore",
    message=".*TripleDES has been moved.*",
    category=DeprecationWarning,
)

# Suppress Scapy warnings
warnings.filterwarnings(
    "ignore",
    message=".*No libpcap provider available.*",
    category=UserWarning,
)

# Configure Scapy to be quiet
try:
    from scapy.all import conf
    conf.verb = 0  # Quiet mode
except ImportError:
    pass

# Set up logging for warnings
logging.captureWarnings(True)
warnings_logger = logging.getLogger('py.warnings')
warnings_logger.setLevel(logging.ERROR)

# Print confirmation
print("✓ Warning suppression configured")