import argparse
import hashlib
import base64 , subprocess , sys
from datetime import datetime
from .generate_license import generate_license
import os

def get_delta_days(date_str):
    try :
        # Convert the string to a datetime object
        target_date = datetime.strptime(date_str, "%d-%m-%Y")
        # Get today's date
        today = datetime.today()
        # Calculate the difference between the target date and today
        delta = (target_date - today).days
        if delta <= 15 and delta > 0: 
            print(f"Warning : License will expire soon. Remaining days are : {delta} Days")
    except :
        pass

def verify_license(license_key, appname, uuid=None, level="basic",return_dict=False,open_all=False,disable_expire_days_warn=False,exit_on_failure=True):
    key = license_key
    # print(f'license_key={license_key}')
    # print(f'appname={appname}')
    # print(f'uuid={uuid}')
    # print(f'level={level}')
    features=None
    if len(key.split('||')) == 3 :
        features=key.split('||')[2]
        os.environ.update({'LICENSEKEY_FEATURES' : features })
        # print(features)
    if len(key.split('||')) < 1 :
        if exit_on_failure :
            sys.exit(f'Invalid license file')
        if return_dict : 
            return {'status' :  400 , 'message' : "400_INVALID_LICENSE_FILE" , "features" : features  }
        else :
            return "400_INVALID_LICENSE_FILE"
    license_key = key.split('||')[0].replace('\n' , '')
    expire_date = key.split('||')[1].replace('\n', '')
    if disable_expire_days_warn :
        get_delta_days(expire_date)
    if uuid == 'auto' and not open_all: 
        if 'win' in sys.platform :
            cli = fr'reg query "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion" /v ProductID'
            uuid = subprocess.getoutput(cli).splitlines()[2].split(' ')[-1].replace('\n','')
        elif 'linux' in str(sys.platform) :
            uuid = subprocess.getoutput('cat /sys/class/dmi/id/product_uuid').replace('\n' , '')
        else :
            if exit_on_failure :
                sys.exit("400_NOT_SUPPORTED_OS")
            elif return_dict :
                return {'status' :  400 , 'message' : "400_NOT_SUPPORTED_OS" , 'features' : features }
            return "400_NOT_SUPPORTED_OS"
                
    if open_all :
        uuid= None

    expected_license_key = generate_license(appname=appname, uuid=uuid, expire_date=expire_date, level=level , write_file=False,enable_print=False)
    # Decode the provided license key
    # print(expected_license_key)
    try:
        decoded_key_bytes = base64.b64decode(license_key)
    except:
        if exit_on_failure :
            sys.exit(f'400_INCORRECT_LICENSE_FORMAT')
        if return_dict : 
            return {'status' :  400 , 'message' : "400_INCORRECT_FORMAT" , 'features' : features }
        return "400_INCORRECT_FORMAT"
    # Convert expected_license_key to bytes
    expected_key_bytes = base64.b64decode(expected_license_key)
    # Check if the license matches the expected key
    if expected_key_bytes == decoded_key_bytes:
        # If an expiration date is provided, verify it
        if expire_date != 'perm':
            current_date = datetime.now().date()
            expire_date_obj = datetime.strptime(expire_date, '%d-%m-%Y').date()
            if current_date > expire_date_obj:
                if exit_on_failure :
                    sys.exit(f'License is expired.')
                if return_dict : 
                    return {'status' :  400 , 'message' : "400_EXPIRED" , 'features' : features  }
                return "400_EXPIRED"
        if return_dict : 
            return {'status' :  200 , 'message' : "200_LICENSE_IS_VALID" , 'features' : features }
        return "200"
    else:
        if exit_on_failure :
            sys.exit(f'License is not valid. license key is not correct.')
        if return_dict : 
            return {'status' :  400 , 'message' : "400_LICENSE_NOT_VALID" , 'features' : features }
        return "400_LICENSE_NOT_VALID."

def main():
    parser = argparse.ArgumentParser(description="Verify the given license key.")
    parser.add_argument("license", type=str, help="License key to be verified")
    parser.add_argument("appname", type=str, help="Name of the app")
    parser.add_argument("--uuid", type=str, default=None, help="UUID for the license (optional if open for all)")
    parser.add_argument("--level", type=str, choices=["basic", "plus"], default="basic", help="License level, can be 'basic' or 'plus'. Default is 'basic'.")
    args = parser.parse_args()
    result = verify_license(args.license, args.appname, args.uuid, args.level)
    print(result)

if __name__ == "__main__":
    pass