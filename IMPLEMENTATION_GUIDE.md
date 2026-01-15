# GateWise UI Redesign - Implementation Guide

**For Developers & Maintainers**

---

## Quick Start

### What Changed?

✅ **Only UI/Styling updated** — All functionality preserved
✅ **New design system** — Modern, dark mode industrial aesthetic
✅ **Better UX** — Touch-optimized for 7-inch kiosk
✅ **Backward compatible** — No API changes

### File Modified

```
ui/gatewise_ui.py - Complete visual redesign (965 lines → 1280 lines)
```

### Testing the Changes

```bash
# Navigate to project
cd C:\Personal\gatewise_ui

# Run the UI (requires PySide6)
python main.py

# Or launch UI directly
python -c "from ui.gatewise_ui import launch_ui; launch_ui()"
```

---

## Architecture Overview

### Class Structure

```
GateWiseUI (QWidget)
├── __init__()                          [Setup, colors, layout]
├── _get_global_stylesheet()            [Master stylesheet]
├── _create_header_layout()             [Persistent header]
├── update_lock_status_display()        [Lock status badge]
├──
├── init_main_screen()                  [3x2 button grid]
├── _create_action_button()             [Color button factory]
├── _lighten_color() / _darken_color()  [Color utils]
├──
├── init_settings_screen()              [Settings page]
├── _create_settings_button()           [Card button factory]
├── _create_danger_button()             [Red action button]
├── _create_neutral_button()            [Gray nav button]
├──
├── init_log_screen()                   [Logs page]
├── init_blackout_screen()              [Blackout schedule]
├── init_user_screen()                  [User management]
├── refresh_user_list()                 [User list view]
├──
└── [All original functionality methods unchanged]
    ├── on_unlock_clicked()
    ├── on_lock_clicked()
    ├── on_class_unlock_clicked()
    ├── show_main() / show_settings() / etc.
    └── ...
```

---

## Color System

### Define Custom Colors

```python
class GateWiseUI(QWidget):
    def __init__(self):
        # Color Palette (EDIT HERE for theme changes)
        self.BG_DARK = "#1A1A1A"              # Main background
        self.BG_DARKER = "#0D0D0D"            # Header/footer
        self.COLOR_UNLOCK = "#4CAF50"         # Green (Success)
        self.COLOR_LOCK = "#F44336"           # Red (Alert)
        self.COLOR_SECONDARY = "#2196F3"      # Blue (Action)
        self.COLOR_TEXT = "#FFFFFF"           # White text
        self.COLOR_TEXT_DIM = "#B0B0B0"       # Gray text
```

### Using Colors in Code

```python
# In f-strings (recommended)
stylesheet = f"background-color: {self.COLOR_UNLOCK}; color: {self.COLOR_TEXT};"

# Direct hex values (discouraged)
stylesheet = "background-color: #4CAF50;"  # ❌ Not maintainable

# Usage in methods
btn = self._create_action_button(
    label="Button",
    color=self.COLOR_UNLOCK,  # ✅ Use color variable
    callback=self.some_action
)
```

---

## Button Creation Patterns

### Pattern 1: Action Buttons (Primary/Secondary)

```python
btn = self._create_action_button(
    label="🔓 UNLOCK",                    # Icon + text
    tooltip="Unlock for 3 seconds",       # Hover text
    color=self.COLOR_UNLOCK,              # Green
    callback=self.on_unlock_clicked,      # Event handler
    is_primary=True                       # Size: 100px (False = 70px)
)
grid.addWidget(btn, row, col)
```

**Output**: Color-specific button with hover/press effects

### Pattern 2: Settings Buttons (Card-style)

```python
btn = self._create_settings_button(
    label="📅 Blackout Schedule",         # Icon + text
    tooltip="Manage access blackout...",  # Hover text
    callback=self.show_blackout           # Event handler
)
layout.addWidget(btn)
```

**Output**: Full-width dark card button

### Pattern 3: Danger Buttons (Red, System Actions)

```python
btn = self._create_danger_button(
    label="🔌 Shutdown System",           # Icon + text
    callback=self.shutdown_system,        # Event handler
    is_large=True                         # Height: 55px (False = 48px)
)
layout.addWidget(btn)
```

**Output**: Alert red button with warning styling

### Pattern 4: Neutral Buttons (Gray, Navigation)

```python
btn = self._create_neutral_button(
    label="← Back",                       # Icon + text
    callback=self.show_main,              # Event handler
    is_large=True                         # Height: 55px (False = 48px)
)
layout.addWidget(btn)
```

**Output**: Gray navigation button

---

## Styling Guide

### Global Stylesheet

The `_get_global_stylesheet()` method returns a master stylesheet applied to entire window.

**Modify global styles here:**

```python
def _get_global_stylesheet(self):
    """Return global stylesheet with modern design system."""
    return f"""
    * {{
        background-color: {self.BG_DARK};
        color: {self.COLOR_TEXT};
        font-family: 'Roboto Condensed', 'Inter', sans-serif;
        font-size: 14px;
    }}

    /* Button default states */
    QPushButton {{
        background-color: #2A2A2A;
        border: 1px solid #444;
        border-radius: 8px;
        padding: 8px 12px;
        min-height: 48px;
        min-width: 48px;
    }}

    QPushButton:hover {{
        background-color: #3A3A3A;
        border: 1px solid #555;
    }}

    /* ... more selectors ... */
    """
```

### Dynamic Stylesheets

For color-specific buttons, use dynamic f-string stylesheets:

```python
color = "#4CAF50"  # Green

stylesheet = f"""
QPushButton {{
    background-color: {color};
    border: 2px solid {self._darken_color(color, 0.2)};
    /* ... */
}}

QPushButton:hover {{
    background-color: {self._lighten_color(color, 0.1)};
    /* ... */
}}
"""

btn.setStyleSheet(stylesheet)
```

---

## Adding New Features

### Add a New Button to Main Screen

```python
def init_main_screen(self):
    # ... existing code ...

    # Add your new button
    new_btn = self._create_action_button(
        "🆕 NEW ACTION",
        "Description of action",
        self.COLOR_SECONDARY,  # Choose color
        self.my_new_method,
        is_primary=True        # Large size
    )
    grid.addWidget(new_btn, 0, 2)  # Position in grid

    # ... rest of code ...

def my_new_method(self):
    """Handle button click."""
    self.set_status("Action triggered")
    # ... your logic ...
```

### Add a New Settings Option

```python
def init_settings_screen(self):
    # ... existing code ...

    # Add your new settings button
    new_setting = self._create_settings_button(
        "🎨 Color Theme",
        "Change interface colors",
        self.open_theme_settings
    )
    layout.addWidget(new_setting)

    # ... rest of code ...

def open_theme_settings(self):
    """Open color theme dialog."""
    self.stack.setCurrentWidget(self.theme_screen)
    self.set_status("Color theme settings")
```

### Modify Button Colors

```python
# In GateWiseUI.__init__():
self.COLOR_UNLOCK = "#4CAF50"     # Default: Safety Green
# Change to custom color:
self.COLOR_UNLOCK = "#66BB6A"     # Lighter green
```

---

## Common Modifications

### Change Theme Colors

**File**: `ui/gatewise_ui.py` lines 195-209

```python
# Change these values:
self.BG_DARK = "#1A1A1A"          # Dark background
self.COLOR_UNLOCK = "#4CAF50"      # Unlock color
self.COLOR_LOCK = "#F44336"        # Lock color
self.COLOR_SECONDARY = "#2196F3"   # Secondary actions
```

### Adjust Button Sizes

**File**: `_create_action_button()` method

```python
if is_primary:
    btn.setMinimumHeight(100)      # Change from 100
    btn.setMinimumWidth(100)
else:
    btn.setMinimumHeight(70)       # Change from 70
    btn.setMinimumWidth(70)
```

### Modify Font Sizes

**File**: `_create_action_button()` or `_get_global_stylesheet()`

```python
btn.setFont(QFont("Roboto Condensed", 16, QFont.Bold))  # Change 16 to desired size
```

### Change Button Spacing

**File**: Various `init_*_screen()` methods

```python
grid.setSpacing(12)  # Gap between buttons (change 12)
layout.setContentsMargins(16, 16, 16, 16)  # Edge margins
```

### Adjust Icon/Emoji

**File**: `init_main_screen()` and other screens

```python
# Old:
unlock_btn = self._create_action_button(
    "🔓 UNLOCK",  # Change emoji here
    ...
)

# New:
unlock_btn = self._create_action_button(
    "🔓 OPEN",    # Different text
    ...
)
```

---

## Color Utility Functions

### `_lighten_color(color, amount)`

Lightens a color by the specified amount (0.0-1.0).

```python
# Lighten by 10%
lighter = self._lighten_color("#4CAF50", 0.1)
# Result: Lighter shade of green

# Lightens by increasing HSV value
# Used for hover states
```

### `_darken_color(color, amount)`

Darkens a color by the specified amount (0.0-1.0).

```python
# Darken by 20%
darker = self._darken_color("#4CAF50", 0.2)
# Result: Darker shade of green

# Darkens by decreasing HSV value
# Used for borders and pressed states
```

### Usage Example

```python
base_color = "#4CAF50"
border_color = self._darken_color(base_color, 0.2)
hover_color = self._lighten_color(base_color, 0.1)

stylesheet = f"""
QPushButton {{
    background-color: {base_color};
    border: 2px solid {border_color};
}}
QPushButton:hover {{
    background-color: {hover_color};
}}
"""
```

---

## Testing & Validation

### Unit Test Template

```python
def test_color_contrast():
    """Verify WCAG AA contrast ratios."""
    colors = {
        'unlock': '#4CAF50',
        'lock': '#F44336',
        'bg': '#1A1A1A',
        'text': '#FFFFFF'
    }

    # Calculate contrast ratios
    # Assert >= 4.5:1 for WCAG AA
    assert calculate_contrast(colors['unlock'], colors['bg']) >= 4.5
    assert calculate_contrast(colors['text'], colors['bg']) >= 4.5
```

### Visual Testing Checklist

```
□ Buttons are at least 48x48 pixels
□ All text meets 4.5:1 contrast ratio
□ Colors distinguish with/without color vision
□ Button pressed state is visible
□ Font sizes are readable at 1 meter distance
□ Spacing is consistent (12px grid)
□ All screens have persistent header
□ Footer status updates in real-time
□ Touch targets don't overlap
□ No hover-only information exists
```

---

## Debugging Tips

### Check Stylesheet Issues

```python
# Print button stylesheet (debugging)
btn = self._create_action_button(...)
print(btn.styleSheet())

# Verify color calculations
print(self._lighten_color("#4CAF50", 0.1))  # Check result
print(self._darken_color("#4CAF50", 0.2))  # Check result
```

### Check Layout Issues

```python
# Verify grid layout
grid = QGridLayout()
grid.setSpacing(12)
print(f"Grid spacing: {grid.spacing()}")

# Check widget sizes
print(f"Button size: {btn.minimumHeight()} x {btn.minimumWidth()}")
```

### Color Contrast Verification

```python
# Manual contrast check
foreground = "#4CAF50"
background = "#1A1A1A"

# Use WCAG formula: (L1 + 0.05) / (L2 + 0.05)
# Target: >= 4.5:1 for AA compliance
```

---

## Performance Optimization

### Stylesheet Caching

```python
# Current approach: Dynamic generation
def _get_global_stylesheet(self):
    return f"""..."""  # Generated each call

# Optimization: Cache stylesheet
def __init__(self):
    self._stylesheet_cache = self._get_global_stylesheet()
    self.setStyleSheet(self._stylesheet_cache)
```

### Color Calculation Optimization

```python
# Current: Calculate colors dynamically
def _create_action_button(...):
    hover_color = self._lighten_color(color, 0.1)  # Per button

# Optimization: Pre-calculate color variations
def __init__(self):
    self.UNLOCK_HOVER = self._lighten_color(self.COLOR_UNLOCK, 0.1)
    self.UNLOCK_DARK = self._darken_color(self.COLOR_UNLOCK, 0.2)
```

---

## Troubleshooting

### Problem: Buttons don't look right

**Solution**: Check stylesheet application

```python
# Ensure stylesheet is set BEFORE adding buttons
self.setStyleSheet(self._get_global_stylesheet())
# Then create buttons
btn = self._create_action_button(...)
```

### Problem: Colors don't match design

**Solution**: Verify hex values

```python
# Use this exact format for consistency
self.COLOR_UNLOCK = "#4CAF50"  # ✓ Correct
self.COLOR_UNLOCK = "4CAF50"   # ✗ Missing #
self.COLOR_UNLOCK = "#4caf50"  # ✓ Works (case-insensitive)
```

### Problem: Text is unreadable

**Solution**: Check contrast

```python
# Minimum text color on background
# Use: #FFFFFF (white) on #1A1A1A (black)
# Contrast: 21:1 (exceeds WCAG AAA)
```

### Problem: Buttons overlap on small screens

**Solution**: Adjust minimum sizes or use scrolling

```python
# Reduce sizes for smaller screens
if self.width() < 600:
    btn.setMinimumHeight(60)  # Down from 100
```

---

## Version History

| Version | Date       | Changes                              |
| ------- | ---------- | ------------------------------------ |
| 1.0     | 2026-01-15 | Initial design system implementation |
| -       | Planned    | Theme switching (light/dark)         |
| -       | Planned    | Custom color picker                  |
| -       | Planned    | Accessibility menu (font size+)      |

---

## Resources

### Documentation Files

- `UI_REDESIGN_SUMMARY.md` - High-level overview
- `DESIGN_SYSTEM.md` - Complete design specifications
- This file - Implementation guide for developers

### Source Code

- `ui/gatewise_ui.py` - Main implementation (lines 195+)
- Lines 195-320: Initialization & color setup
- Lines 470-610: Main screen & button creation
- Lines 614-800: Settings screen
- Lines 825-950: Blackout schedule
- Lines 1049-1180: User management

### External References

- PySide6 Documentation: https://doc.qt.io/qtforpython/
- WCAG AA Contrast Checker: https://webaim.org/resources/contrastchecker/
- Roboto Font: https://fonts.google.com/specimen/Roboto+Condensed

---

## Best Practices

✅ **DO**

- Use color variables (self.COLOR_UNLOCK)
- Apply global stylesheet first
- Use helper methods (\_create_action_button, etc.)
- Test all screen sizes
- Verify contrast ratios
- Add tooltips to buttons
- Use semantic colors (red=danger, green=safe)

❌ **DON'T**

- Hardcode colors (#4CAF50 in buttons)
- Use complicated nested stylesheets
- Add animations (breaks touch responsiveness)
- Create buttons without proper sizing
- Use hover-only information
- Ignore accessibility requirements
- Mix light and dark colors without testing

---

## Support & Questions

For issues or questions about the redesign:

1. **Check the Design System** (`DESIGN_SYSTEM.md`)
2. **Review the Implementation** (`UI_REDESIGN_SUMMARY.md`)
3. **Consult the Code** (`ui/gatewise_ui.py` lines 195+)
4. **Test in Browser** - Review button states and colors

Remember: **All functionality is preserved** — only the visual design changed. If a feature isn't working, check the underlying logic, not the styling.

---

**Happy coding! 🚀**
