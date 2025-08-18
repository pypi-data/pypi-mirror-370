"""
🎨 Advanced Licenzy Example - Multiple Decorators and Aliases

This example shows the flexibility of Licenzy with different
decorator styles and alias functions for various use cases.
"""

from licenzy import licensed, unlock, require_key, access_granted, check_license

class AIToolbox:
    """Example AI toolbox with different licensing approaches."""
    
    @licensed
    def basic_model(self):
        """Basic model with standard @licensed decorator."""
        return "🤖 Basic AI model result"
    
    @unlock
    def premium_model(self):
        """Premium model using the @unlock alias."""
        return "🚀 Premium AI model with advanced capabilities"
    
    @require_key
    def enterprise_model(self):
        """Enterprise model using @require_key alias."""
        return "💼 Enterprise AI model with full feature set"
    
    def conditional_feature(self):
        """Feature that checks license manually for complex logic."""
        if access_granted():
            return "✨ This feature is unlocked!"
        else:
            return "🔒 This feature requires a license"
    
    def tiered_access(self):
        """Example of tiered access based on license info."""
        if not check_license():
            return "❌ No license - basic features only"
        
        # You could check license_info for plan types here
        # For now, just return premium access
        return "🎯 Full access granted!"

# Example of protecting a whole module
@licensed
def module_level_function():
    """Module-level function protection."""
    return "🌟 This entire function is protected"

# Example with custom error handling
def safe_premium_feature():
    """Safely call premium features with error handling."""
    try:
        @licensed
        def inner_premium():
            return "💎 Inner premium feature"
        
        return inner_premium()
    except Exception as e:
        return f"⚠️ Premium feature unavailable: {e}"

if __name__ == "__main__":
    print("🎭 Licenzy Advanced Example")
    print("=" * 40)
    
    toolkit = AIToolbox()
    
    # Test all the different approaches
    features = [
        ("Basic Model", toolkit.basic_model),
        ("Premium Model (unlock)", toolkit.premium_model),
        ("Enterprise Model (require_key)", toolkit.enterprise_model),
        ("Conditional Feature", toolkit.conditional_feature),
        ("Tiered Access", toolkit.tiered_access),
        ("Module Function", module_level_function),
        ("Safe Premium", safe_premium_feature),
    ]
    
    for name, feature in features:
        try:
            result = feature()
            print(f"✅ {name}: {result}")
        except Exception as e:
            print(f"❌ {name}: {e}")
    
    print("\n💡 To test with a license, run:")
    print("   export LICENZY_LICENSE_KEY=your-key")
    print("   # or")
    print("   licenzy activate your-key")
