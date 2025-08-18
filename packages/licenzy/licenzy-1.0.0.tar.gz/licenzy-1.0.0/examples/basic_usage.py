"""
🎯 Simple Licenzy Example - Basic Usage

This example shows the simplest way to use Licenzy
to protect functions in your AI tool or Python project.
"""

from licenzy import licensed, check_license

# The most basic usage - protect a function
@licensed
def premium_ai_model():
    """This function requires a valid license."""
    return "🤖 Running premium AI model with advanced features!"

# Manual checking for more control
def startup_check():
    """Check license at application startup."""
    if check_license():
        print("✅ License valid - all features unlocked!")
        return True
    else:
        print("❌ License required - running in limited mode")
        return False

# Custom error message
@licensed(message="Premium feature requires Pro license")
def advanced_analytics():
    """Advanced analytics with custom error message."""
    return "📊 Generating advanced analytics report..."

if __name__ == "__main__":
    # Demo the functions
    try:
        print("🔍 Checking license status...")
        if startup_check():
            print("\n🚀 Testing premium features:")
            print(premium_ai_model())
            print(advanced_analytics())
        else:
            print("\n💡 Get a license to unlock premium features!")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n💡 Activate a license with: licenzy activate your-key")
