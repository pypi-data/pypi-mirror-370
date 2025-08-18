<div align="center">
  <img src="assets/licenzy.svg" alt="Licenzy Logo" width="200"/>
  
  # 🔑 Licenzy
  
  > Simple, Pythonic license management for AI tools and indie projects
  
  [![PyPI version](https://badge.fury.io/py/licenzy.svg)](https://badge.fury.io/py/licenzy)
  [![Python Support](https://img.shields.io/pypi/pyversions/licenzy.svg)](https://pypi.org/project/licenzy/)
  [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
</div>

Licenzy provides a clean, minimal API for adding license validation to your Python projects. Perfect for independent developers and small teams building AI tools who need secure but lightweight licensing.

## ✨ Features

- **🎨 @licensed decorator** - Protect functions with a simple, elegant decorator
- **🔍 Simple API** - `check_license()` for manual validation
- **📁 Flexible Storage** - Environment variables, home directory, or project files
- **🔒 HMAC Security** - Cryptographically secure license validation
- **🖥️ CLI Tools** - Easy license management from command line
- **🐍 Zero Dependencies** - Core functionality works standalone (Click only for CLI)
- **🚀 Startup-Friendly** - Designed for indie developers and small teams

## 🚀 Quick Start

### Installation

```bash
pip install licenzy
```

### Basic Usage

```python
from licenzy import licensed, check_license

# Protect premium features with a decorator
@licensed
def premium_ai_model():
    return "🤖 Running advanced AI model!"

# Manual license checking
if check_license():
    print("✅ All features unlocked!")
else:
    print("❌ License required for premium features")
```

### Activate a License

```bash
# Via CLI
licenzy activate your-license-key-here

# Via environment variable
export LICENZY_LICENSE_KEY=your-license-key-here

# Check status
licenzy status
```

## 📋 API Reference

### Core Functions

#### `@licensed`
The main decorator for protecting functions that require a valid license.

```python
from licenzy import licensed

@licensed
def premium_feature():
    return "This requires a license!"

# With custom error message
@licensed(message="Pro plan required")
def pro_feature():
    return "Pro-only functionality"
```

#### `check_license()`
Simple function to check if a license is valid.

```python
from licenzy import check_license

if check_license():
    # License is valid
    enable_premium_features()
else:
    # No valid license
    show_upgrade_prompt()
```

### Decorator Aliases

Licenzy provides friendly aliases for different use cases:

```python
from licenzy import unlock, require_key

@unlock  # Same as @licensed
def feature_one():
    return "Unlocked!"

@require_key  # Same as @licensed  
def feature_two():
    return "Key required!"
```

### Function Aliases

```python
from licenzy import access_granted

# Same as check_license() but more expressive
if access_granted():
    print("Welcome to premium features!")
```

## 🖥️ CLI Commands

### Activate License
```bash
licenzy activate your-license-key
```

### Check Status
```bash
licenzy status
```

### Quick Validation
```bash
licenzy check  # Returns exit code 0 if valid, 1 if invalid
```

### Deactivate License
```bash
licenzy deactivate
```

### Show Help
```bash
licenzy info  # Shows integration examples and usage
```

## ⚙️ Configuration

### License Storage Locations

Licenzy checks for licenses in this order:

1. **Environment Variable**: `LICENZY_LICENSE_KEY`
2. **User Directory**: `~/.licenzy/license.key`
3. **Project Directory**: `.licenzy_license`

### Development Mode

Bypass license checks during development:

```bash
export LICENZY_DEV_MODE=true
```

### License Key Format

License keys follow this format:
```
user_id:plan:expires_timestamp:signature
```

Example:
```
john123:pro:1735689600:a1b2c3d4e5f6
```

## 🔧 Integration Examples

### FastAPI Integration

```python
from fastapi import FastAPI, HTTPException
from licenzy import licensed, LicenseError

app = FastAPI()

@app.get("/premium-endpoint")
@licensed
def premium_endpoint():
    return {"message": "Premium feature accessed!"}

# Global error handler
@app.exception_handler(LicenseError)
async def license_error_handler(request, exc):
    raise HTTPException(status_code=402, detail=str(exc))
```

### Flask Integration

```python
from flask import Flask, jsonify
from licenzy import licensed, LicenseError

app = Flask(__name__)

@app.route('/premium')
@licensed
def premium_route():
    return jsonify({"message": "Premium content!"})

@app.errorhandler(LicenseError)
def handle_license_error(e):
    return jsonify({"error": str(e)}), 402
```

### Class Method Protection

```python
from licenzy import licensed

class AIService:
    @licensed
    def premium_analysis(self, data):
        return "Advanced analysis results"
    
    @licensed(message="Enterprise plan required")
    def enterprise_feature(self):
        return "Enterprise-only functionality"
```

## 🧪 Testing

Licenzy makes testing easy with development mode:

```python
import os
from licenzy import check_license

def test_premium_feature():
    # Enable dev mode for testing
    os.environ['LICENZY_DEV_MODE'] = 'true'
    
    assert check_license() == True
    
    # Your test code here
```

## 🏗️ Building and Development

### Local Development Setup

```bash
git clone https://github.com/yourusername/licenzy
cd licenzy
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest tests/ -v
```

### Code Formatting

```bash
black licenzy/
```

### Type Checking

```bash
mypy licenzy/
```

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions welcome! Please read our contributing guidelines and submit pull requests to our GitHub repository.

## 🆘 Support

- 📖 **Documentation**: [licenzy.readthedocs.io](https://licenzy.readthedocs.io)
- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/yourusername/licenzy/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/yourusername/licenzy/discussions)

---

Built with ❤️ for the indie developer community. Perfect for AI tools, SaaS products, and any Python project that needs simple, secure licensing.
