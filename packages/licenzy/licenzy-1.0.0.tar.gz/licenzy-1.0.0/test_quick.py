"""
🧪 Quick test to verify Licenzy is working correctly
"""

# Test basic imports
print("🔍 Testing Licenzy imports...")
try:
    from licenzy import licensed, check_license, access_granted
    print("✅ Core imports successful")
except ImportError as e:
    print(f"❌ Import failed: {e}")
    exit(1)

# Test development mode
print("\n🔧 Testing development mode...")
import os
os.environ['LICENZY_DEV_MODE'] = 'true'

@licensed
def test_function():
    return "🎉 Success! Function executed with license protection."

try:
    result = test_function()
    print(f"✅ Dev mode test: {result}")
except Exception as e:
    print(f"❌ Dev mode test failed: {e}")

# Test check_license function
print("\n📋 Testing license check...")
if check_license():
    print("✅ License check passed (dev mode)")
else:
    print("❌ License check failed")

# Test alias functions
print("\n🎭 Testing alias functions...")
if access_granted():
    print("✅ access_granted() works")
else:
    print("❌ access_granted() failed")

print("\n🎯 All basic tests completed!")
print("🔑 Licenzy is ready to use!")

# Clean up
del os.environ['LICENZY_DEV_MODE']
