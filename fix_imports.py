import sys
import os

# Read the conftest.py file
with open('tests/conftest.py', 'r') as f:
    content = f.read()

# Replace the incorrect import
content = content.replace(
    'from autonomous_acquisition import CustomerAcquisitionBot',
    'from autonomous_acquisition import AutonomousAcquisition as CustomerAcquisitionBot'
)

# Write back the fixed content
with open('tests/conftest.py', 'w') as f:
    f.write(content)

print("Fixed import in conftest.py")
