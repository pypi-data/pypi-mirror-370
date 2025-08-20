import argparse
import hashlib
import base64
import sys
import traceback
from easy_utils_dev.encryptor import initCryptor

enabled = True

def lprint(str) :
    if enabled : 
        print(str)

def generate_license(appname, uuid=None, expire_date=None, level="basic",write_file=True,enable_print=True, features=["_all_"] , method=1):
    enc = initCryptor()
    r"""
    "appname", type=str, help="Name of the app "
    "--uuid", type=str, default=None, help=fr'UUID for the license (optional if open for all, 
        cmd=reg query "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion" /v ProductID   \n 
        linux=cat /sys/class/dmi/id/product_uuid )'
    "--expire", type=str, default=None, help="Expiration date in DD-MM-YYYY format (optional)")
    "--level", type=str, choices=["basic", "plus"], default="basic", help="License level, can be 'basic' or 'plus'. Default is 'basic'."
    """
    global enabled
    enabled = enable_print
    combined_string = appname + level
    if expire_date == None :
        expire_date='perm'
    if not uuid:
        combined_string += "OPEN_FOR_ALL_UUIDS"
    else:
        combined_string += uuid
    if expire_date:
        combined_string += expire_date
    lprint("=================== Generating New License ===================")
    lprint(f"App Name : {appname}")
    lprint(f"UUID : {uuid}")
    lprint(f"License Level : {level}")
    lprint(f"Expiration Date : {expire_date}")
    lprint(f"Features : {features}")
    lprint("=================== License Key START===================")
    _features = []
    for feature in features :
        _features.append(enc.en_base64(feature))
    hashed = hashlib.sha256(combined_string.encode()).digest()
    license_key = base64.b64encode(hashed).decode()
    if method == 1 :
        license_key = license_key+'||' + expire_date
    elif method == 2 :
        license_key = license_key+'||' + expire_date + "||" + ",".join(_features)
    if write_file :
        with open('./license.dat' , 'w') as f :
            f.write(license_key)
    lprint(license_key)
    lprint("=================== License Key END===================")
    return license_key

def main():
    try :
        parser = argparse.ArgumentParser(description="Verify the given license key.")
        parser.add_argument("appname", type=str, help="Name of the app ")
        parser.add_argument("--uuid", type=str, default=None, help=fr'UUID for the license (optional if open for all, cmd=reg query "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion" /v ProductID   \n linux=cat /sys/class/dmi/id/product_uuid )')
        parser.add_argument("--expire", type=str, default=None, help="Expiration date in DD-MM-YYYY format (optional)")
        parser.add_argument("--level", type=str, choices=["basic", "plus"], default="basic", help="License level, can be 'basic' or 'plus'. Default is 'basic'.")
        args = parser.parse_args()
        if not args.uuid :
            args.uuid = None
        generate_license( 
            args.appname, 
            args.uuid, 
            args.expire, 
            args.level
        )
        sys.exit(0)
    except Exception as error :
        print(traceback.format_exc())
        print(error)


if __name__ == "__main__":
    pass
