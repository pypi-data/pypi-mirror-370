# decorators.py
from functools import wraps
import os
from easy_utils_dev.encryptor import initCryptor
import sys

def require_permission(permissions=["_all_"]):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            LICENSEKEY_FEATURES = os.environ.get("LICENSEKEY_FEATURES")
            if LICENSEKEY_FEATURES : 
                cryp = initCryptor()
                LICENSEKEY_FEATURES = LICENSEKEY_FEATURES.split(",")
                LICENSEKEY_FEATURES = [cryp.dec_base64(key) for key in LICENSEKEY_FEATURES ]
                for pass_key in permissions :
                    if not pass_key in LICENSEKEY_FEATURES :
                        sys.exit(f"This Operation requires license feature: '{pass_key}'. Function Label {fn.__name__}")
            return fn(*args, **kwargs)
        return wrapper
    return decorator