# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.8] - 2025-08-20

- **Copy json**: Copy json from the view.
- **Multiple tooltips**: Support multiple tooltips on the same json field.


## [0.2.7] - 2025-07-29

- **Fix interactions**: Additional fixing for page refresh and keeping state when interacting with the component.

## [0.2.6] - 2025-07-28

- **Fix streamlit state**: Additional fixing for page refresh and keeping state
- **Style updates**: Align default font and softer text color in dark mode.

## [0.2.5] - 2025-07-28

- **Fix streamlit state**: Fix refreshing streamlit state when clicking on the component.
- **Fix component padding**: Fix component padding to avoid cutting off the end bracket of the json viewer.

## [0.2.4] - 2025-07-25

- **Github actions**: Add and test github actions

## [0.2.3] - 2025-07-25

- **JSON viewer padding**: Remove padding

## [0.2.2] - 2025-07-25

- **PyPI Image Display**: Fix image url

## [0.2.1] - 2025-07-25

### 🔧 Fixed
- **PyPI Image Display**: Updated README to use GitHub raw URL for example image instead of local path
- **Documentation**: Example image now displays properly on PyPI package page

## [0.2.0] - 2025-07-25

### ✨ Added
- **Custom Tooltip Icons**: New `tooltip_icon` parameter allows setting a global icon for all tooltips (default: "ℹ️")
- **Dynamic Per-Field Icons**: Enhanced `dynamic_tooltips` function now supports returning `{"text": str, "icon": str}` for field-specific icons
- **Visual Documentation**: Added example screenshot in README to showcase component features
- **Organized Resources**: Created `resources/` folder for project assets

### 🎨 Improved
- **Borderless Design**: Removed component border for cleaner integration with Streamlit apps
- **Enhanced Examples**: Updated example app with contextual icons (👤 for names, 🚨 for alerts, 🐕 for animals, etc.)
- **Better Documentation**: Improved README with comprehensive usage examples and icon customization guide

### 🔧 Technical
- Updated frontend build system with latest changes
- Enhanced React component to handle dynamic icon rendering
- Improved package structure and manifest for proper asset inclusion

### 📝 Examples
```python
# Global custom icon
json_viewer(data=data, tooltip_icon="💡")

# Dynamic icons per field
def dynamic_tooltip_with_icons(path, value, data):
    if path.endswith(".name"):
        return {"text": f"Name: {value}", "icon": "👤"}
    elif path.endswith(".score"):
        return {"text": f"Score: {value}/100", "icon": "📊"}
    return None

json_viewer(data=data, dynamic_tooltips=dynamic_tooltip_with_icons)
```

## [0.1.0] - 2024-12-XX

### ✨ Initial Release
- **Interactive JSON Viewer**: Expandable/collapsible JSON tree structure
- **Tooltip System**: Professional Tippy.js tooltips with help text
- **Field Tags**: Colored tags for categorizing fields (PII, CONFIG, etc.)
- **Field Selection**: Click on fields to get detailed information
- **Syntax Highlighting**: Color-coded JSON values by type
- **Theme Support**: Automatic light/dark mode detection
- **Dynamic Tooltips**: Function-based tooltip generation
- **Tippy.js Configuration**: Full customization of tooltip behavior and appearance

### 🎯 Features
- Responsive design for different screen sizes
- Support for nested objects and arrays
- Field path notation (dot notation and bracket notation)
- Professional tooltip animations and positioning
- TypeScript-ready with proper type definitions

---

**Legend:**
- ✨ Added: New features
- 🎨 Improved: Enhancements to existing features  
- 🔧 Technical: Internal improvements
- 🐛 Fixed: Bug fixes
- 📝 Examples: Code examples and documentation