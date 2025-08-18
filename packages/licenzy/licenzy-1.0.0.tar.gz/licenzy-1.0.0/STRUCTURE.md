# 📁 Licenzy Project Structure

```
licenzy/
├── 🔑 assets/
│   └── licenzy.png              # Project logo
├── 📦 licenzy/                  # Main package
│   ├── __init__.py              # Public API exports
│   ├── core.py                  # License validation & decorators
│   ├── management.py            # License activation/status
│   └── cli.py                   # Command-line interface
├── 🧪 tests/
│   └── test_core.py             # Test suite
├── 💡 examples/
│   ├── basic_usage.py           # Simple examples
│   └── advanced_usage.py        # Advanced patterns
├── 📋 .github/
│   └── copilot-instructions.md  # AI coding guidelines
├── 📄 LICENSE                   # MIT License
├── 📖 README.md                 # Project documentation
├── 🎨 BRAND.md                  # Brand guidelines
└── ⚙️ pyproject.toml            # Package configuration
```

## 🎯 Key Components

### Core Package (`licenzy/`)
- **`core.py`**: Heart of the system with `@licensed` decorator and `check_license()`
- **`management.py`**: License activation, deactivation, and status functions
- **`cli.py`**: User-friendly command-line interface using Click

### API Surface
```python
from licenzy import (
    # 🎨 Main decorator
    licensed,
    
    # 🔍 Core function  
    check_license,
    
    # 🎭 Friendly aliases
    access_granted,
    require_key,
    unlock,
    
    # 🔧 Management
    activate_license,
    deactivate_license,
    show_license_status,
)
```

### Brand Integration
- **Logo**: Featured prominently in README and documentation
- **CLI Output**: Uses emoji and clean formatting consistent with brand
- **Error Messages**: Friendly, helpful tone matching the brand personality
- **Documentation**: Clean, developer-focused writing style
