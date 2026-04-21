"""
Simple test to verify write access - create an experiment.
"""

from pybis import Openbis
from getpass import getpass
from config import Config

config = Config()
url = config.openbis_url
username = config.openbis_username
space = config.openbis_space
project = config.project_name

print(f"URL: {url}")
print(f"User: {username}")
print(f"Space: {space}")
print(f"Project: {project}")

# Connect
o = Openbis(url)
password = getpass(f"Enter password for {username}: ")
o.login(username, password)
print("✓ Logged in successfully\n")

# Create experimental step sample in the collection (as a child of collection sample)
test_code = "TEST_EXP_STEP_010"
space = config.openbis_space
project_name = config.project_name
project_path = f"/{space}/{project_name}"
collection_path = f"{project_path}/UVSHEET_EXP_STEP"

print(f"Creating experimental step sample: {test_code}")
print("  Type: EXPERIMENTAL_STEP")
print(f"  Collection container: {collection_path}\n")

try:
    # Get collection AS A SAMPLE (not as experiment) to use as container
    print(f"Retrieving collection as sample: {collection_path}")
    collection_sample = o.get_sample(collection_path)
    print(f"✓ Found collection sample (permId: {collection_sample.permId})\n")

    sample = o.new_sample(
        type="EXPERIMENTAL_STEP",
        code=test_code,
        container=collection_sample,
        parents=[],
        children=[],
        props={
            "$name": test_code,
            "start_date": "2026-04-21",
            "experimental_step.experimental_description": "Test experimental step",
        },
    )

    print("Sample object created (not saved yet)")
    print(f"  Code: {sample.code}")
    print(f"  Type: {sample.type}\n")

    print("Saving sample...")
    sample.save()
    print(f"✓ Sample saved with permID: {sample.permId}\n")
    print(f"Sample identifier: {sample.identifier}\n")

    # Verify it was created
    created = o.get_sample(sample.identifier)
    print(f"✓ Verified sample exists: {created.permId}\n")
    print(f"✓ Sample location: {created.identifier}\n")
    print(f"✓ Sample type: {created.type}\n")

except Exception as e:
    print(f"✗ Error: {e}\n")
    import traceback

    traceback.print_exc()

o.logout()
print("Disconnected")
