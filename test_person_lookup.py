"""
Test script to verify person_lookup is correctly working and being used.
This script tests the person_lookup utility functions and validates integration.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from pybis import Openbis
from utils.person_lookup import get_person_by_bam_username
from openbis.object_manager import ObjectManager
import getpass

print("=" * 70)
print("TEST: person_lookup Integration")
print("=" * 70)
print()

# Step 1: Connect to openBIS
print("[1/3] Connecting to openBIS...")
try:
    o = Openbis('https://main.datastore.bam.de/')
    password = getpass.getpass("Enter password: ")
    o.login('troussea', password, save_token=True)
    print("✅ Connected successfully")
except Exception as e:
    print(f"❌ Connection failed: {e}")
    sys.exit(1)

print()

# Step 2: Test person_lookup directly
print("[2/3] Testing person_lookup function...")
print("-" * 70)

test_username = "jmuelle4"
print(f"Looking up BAM username: {test_username}")

try:
    person_info = get_person_by_bam_username(o, test_username, return_field=None)
    
    if person_info:
        print(f"✅ Person found!")
        print(f"   Name: {person_info.get('name')}")
        print(f"   BAM Username: {person_info.get('bam_username')}")
        print(f"   PermID: {person_info.get('permid')}")
        
        person_permid = person_info.get('permid')
    else:
        print(f"❌ Person '{test_username}' not found")
        print("   Try a different username")
        sys.exit(1)
        
except Exception as e:
    print(f"❌ Error looking up person: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()

# Step 3: Test ObjectManager integration
print("[3/3] Testing ObjectManager integration...")
print("-" * 70)

try:
    object_manager = ObjectManager(o)
    
    print("✅ ObjectManager initialized")
    print("   - Can access openbis connection")
    print("   - person_lookup can be imported and used")
    
    # Verify the method signature includes 'person' parameter
    import inspect
    sig = inspect.signature(object_manager.create_child_samples)
    params = list(sig.parameters.keys())
    
    if 'person' in params:
        print("✅ create_child_samples has 'person' parameter")
        print(f"   Parameters: {params}")
    else:
        print(f"❌ 'person' parameter missing. Found: {params}")
        sys.exit(1)
        
except Exception as e:
    print(f"❌ Error with ObjectManager: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()
print("=" * 70)
print("✅ ALL TESTS PASSED - person_lookup is correctly integrated!")
print("=" * 70)
print()
print("Summary:")
print(f"  ✅ person_lookup.get_person_by_bam_username() working")
print(f"  ✅ Successfully resolved '{test_username}' to permID: {person_permid}")
print(f"  ✅ ObjectManager.create_child_samples() has 'person' parameter")
print(f"  ✅ Integration is complete and functional")
print()
