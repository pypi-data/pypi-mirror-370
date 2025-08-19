import requests
import hashlib

BREACHCOLLECTION_API_URL = "https://breachcollection.com/api/"
BREACHCOLLECTION_API_LEAKED_CREDENTIALS_URL = BREACHCOLLECTION_API_URL + "is-password-safe"


def is_password_safe(password, api_key, characters_sent=10):
    if len(api_key) != 32:
        raise Exception("API Keys are 32 characters long. Make sure your API Key is correct.")
    if characters_sent < 7 or characters_sent > 32:
        raise Exception("You must send between 7 and 32 characters.")

    md5_hashed_password = hashlib.md5(password.encode()).hexdigest()

    data = {"password" : md5_hashed_password[0:characters_sent]}
    headers = {"Authorization": f"Bearer {api_key}"}
    try:
        api_call = requests.post(BREACHCOLLECTION_API_LEAKED_CREDENTIALS_URL, data=data, headers=headers)
        if (api_call.status_code == 404):
            return True
        if (api_call.status_code == 403):
            print("Invalid API Key / Exceeded usage limit.")
            return None
        if (api_call.status_code == 429):
            print("Too many requests.")
            return None
        if (api_call.status_code == 500):
            print("Server Error.")
            return None
        if (api_call.status_code == 200):
            json_results = api_call.json()
            for result in json_results:
                for hash in result:
                    if hash == md5_hashed_password:
                        return False
                
    except requests.exceptions.RequestException as e:
        print(e)
        return None

    return True
