"""Debug script to check PAT token caching"""

from pybis import Openbis
import keyring
from getpass import getpass

url = "https://main.datastore.bam.de/"
username = "troussea"

# Step 1: Login and check token
print("\n=== Step 1: Login ===")
o = Openbis(url)
password = getpass(f"Password for {username}: ")
o.login(username, password)

print(f"Connected: {o is not None}")
print(f"Has token attr: {hasattr(o, 'token')}")
print(f"Token value: {o.token if hasattr(o, 'token') else 'N/A'}")
print(f"Token type: {type(o.token) if hasattr(o, 'token') else 'N/A'}")
print(f"Token is None: {o.token is None if hasattr(o, 'token') else 'N/A'}")
print(f"Token length: {len(o.token) if hasattr(o, 'token') and o.token else 'N/A'}")

# Step 2: Try to save to keyring
print("\n=== Step 2: Save to keyring ===")
if hasattr(o, 'token') and o.token:
    try:
        keyring.set_password("openbis", username, o.token)
        print(f"✓ Saved to keyring")
    except Exception as e:
        print(f"✗ Error saving to keyring: {e}")
else:
    print(f"✗ No valid token to save")

# Step 3: Try to retrieve from keyring
print("\n=== Step 3: Retrieve from keyring ===")
try:
    retrieved_pat = keyring.get_password("openbis", username)
    print(f"Retrieved: {retrieved_pat is not None}")
    if retrieved_pat:
        print(f"Retrieved value (first 50 chars): {retrieved_pat[:50]}")
        print(f"Length: {len(retrieved_pat)}")
except Exception as e:
    print(f"✗ Error retrieving from keyring: {e}")

# Step 4: Try to login with retrieved token
print("\n=== Step 4: Login with retrieved token ===")
try:
    retrieved_pat = keyring.get_password("openbis", username)
    if retrieved_pat:
        o2 = Openbis(url, token=retrieved_pat)
        print(f"✓ Successfully connected with retrieved token!")
    else:
        print(f"✗ No token to retrieve from keyring")
except Exception as e:
    print(f"✗ Failed to connect with token: {e}")

print("\n=== Done ===")
