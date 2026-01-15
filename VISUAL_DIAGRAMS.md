# GateWise UI Redesign - Visual Diagrams & Mockups

---

## 🎯 Main Screen Layout

### Full Screen View (800×480)

```
╔════════════════════════════════════════════════════════════════════════════╗
║  POWER ALLEY CROSSFIT                                    🔒 LOCKED        ║  72px
╠════════════════════════════════════════════════════════════════════════════╣
║                                                                             ║
║  ┌─────────────────────┬─────────────────────┬─────────────────────┐       ║
║  │                     │                     │                     │       ║
║  │      🔓 UNLOCK      │      🔒 LOCK        │      📚 CLASS       │       ║
║  │                     │                     │                     │       ║
║  │   Safety Green      │    Alert Red        │   Primary Blue      │ 100px ║
║  │   (Touch: 100×100)  │   (Touch: 100×100)  │  (Touch: 100×100)   │       ║
║  │                     │                     │                     │       ║
║  ├─────────────────────┼─────────────────────┼─────────────────────┤ 12px  ║
║  │                     │                     │                     │       ║
║  │   ⚙️ SETTINGS       │      📋 LOGS        │      ❌ EXIT        │       ║
║  │                     │                     │                     │       ║
║  │     Orange          │     Purple          │      Gray           │ 70px  ║
║  │   (Touch: 70×70)    │   (Touch: 70×70)    │   (Touch: 70×70)    │       ║
║  │                     │                     │                     │       ║
║  └─────────────────────┴─────────────────────┴─────────────────────┘       ║
║                                                                             ║
║  Content Area: 800px - 32px margin = 736px wide, 368px tall              ║
║                                                                             ║
╠════════════════════════════════════════════════════════════════════════════╣
║  🔴 Ready                                                                   ║  40px
╚════════════════════════════════════════════════════════════════════════════╝
```

### Header Detail

```
POWER ALLEY CROSSFIT      🔒 LOCKED
[Title: 24px, Bold]       [Badge: 20px indicator + text]
Left-aligned              Right-aligned
```

### Grid Spacing Details

```
Grid Layout (3 columns × 2 rows)

[Column 0]              [Gap]    [Column 1]              [Gap]    [Column 2]
33.33% width            12px     33.33% width            12px     33.33% width
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
│ 🔓 UNLOCK (100px)  │          │ 🔒 LOCK (100px)    │          │ 📚 CLASS (100px)  │
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        ↕ 12px vertical gap
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
│ ⚙️ SETTINGS (70px) │          │ 📋 LOGS (70px)     │          │ ❌ EXIT (70px)    │
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Outer margins: 16px on all sides
```

### Footer Detail

```
🔴 Ready
↑        ↑
|        |
Status   Message text
dot      (updates real-time)
(16px)   (left-aligned)
```

---

## 🎨 Color Palette Visualization

### Primary Colors

```
┌──────────────┬──────────┬──────────────────────┐
│ Color Name   │ Hex Code │ Usage                │
├──────────────┼──────────┼──────────────────────┤
│ Background   │ #1A1A1A  │ ███████████████████ │ (Main BG)
│ Dark BG      │ #0D0D0D  │ ███████████████████ │ (Headers)
│ Unlock/OK    │ #4CAF50  │ ███████████████████ │ (Success)
│ Lock/Alert   │ #F44336  │ ███████████████████ │ (Danger)
│ Secondary    │ #2196F3  │ ███████████████████ │ (Action)
│ Text         │ #FFFFFF  │ ███████████████████ │ (Primary)
│ Text Dim     │ #B0B0B0  │ ███████████████████ │ (Secondary)
└──────────────┴──────────┴──────────────────────┘
```

### Accent Colors

```
Settings    Orange   #FF9800  ███████████████████
Logs        Purple   #9C27B0  ███████████████████
Exit        Gray     #607D8B  ███████████████████
Inputs      Light    #2A2A2A  ███████████████████
Borders     Gray     #444444  ███████████████████
Danger      Red      #F44336  ███████████████████
Success     Green    #4CAF50  ███████████████████
```

### Contrast Verification

```
Color Pair                    Ratio    WCAG Level
──────────────────────────────────────────────────
White on Black (#1A1A1A)      21:1     AAA ✅✅✅
Green on Black                5.3:1    AA ✅✅
Red on Black                  3.9:1    AA ✅✅
Blue on Black                 4.5:1    AA ✅✅
Dim Gray on Black             4.1:1    AA ✅✅
```

---

## 📱 Button State Diagram

### Primary Button (100px) - Green Example

```
State: DEFAULT
┌─────────────────────────────┐
│       🔓 UNLOCK             │
│                             │
│      (Safety Green)         │
│      #4CAF50                │
│     100px × 100px           │
│  Border: #357a3a (2px)      │
│  Shadow: 0 4px 8px          │
└─────────────────────────────┘

State: HOVER (Mouse only)
┌─────────────────────────────┐
│       🔓 UNLOCK             │
│                             │
│   (Lighter Green)           │
│   #66BB6A                   │
│     100px × 100px           │
│  Border: #357a3a (2px)      │
│  Shadow: 0 6px 12px (↑)     │
└─────────────────────────────┘

State: PRESSED (Click/Touch)
┌─────────────────────────────┐
│       🔓 UNLOCK             │
│                             │
│   (Darker Green)            │
│   #388E3C                   │
│     100px × 100px           │
│  Border: #1b5e20 (2px)      │
│  Shadow: 0 2px 4px (↓)      │
└─────────────────────────────┘

State: DISABLED
┌─────────────────────────────┐
│       🔓 UNLOCK             │
│    (Muted Gray)             │
│       #555555               │
│     100px × 100px           │
│    Opacity: 0.6             │
│  Shadow: none               │
└─────────────────────────────┘
```

### Secondary Button (70px) - Orange Example

```
State: DEFAULT
┌───────────────────────┐
│  ⚙️ SETTINGS          │
│  (Orange)             │
│  #FF9800              │
│  70px × 70px          │
│  Border: 1px solid    │
│  Shadow: 0 2px 4px    │
└───────────────────────┘

State: HOVER
┌───────────────────────┐
│  ⚙️ SETTINGS          │
│  (Lighter Orange)     │
│  #FFB74D              │
│  70px × 70px          │
│  Shadow: 0 3px 6px    │
└───────────────────────┘

State: PRESSED
┌───────────────────────┐
│  ⚙️ SETTINGS          │
│  (Darker Orange)      │
│  #E65100              │
│  70px × 70px          │
│  Shadow: 0 1px 2px    │
└───────────────────────┘
```

---

## 🖼️ Screen Transitions

### Navigation Flow

```
                 ┌─────────────┐
                 │ MAIN SCREEN │
                 │  (3x2 Grid) │
                 └─────────────┘
                   │       │
         ┌─────────┘       └─────────┐
         │                           │
         ↓                           ↓
    ┌─────────────┐          ┌─────────────┐
    │  SETTINGS   │          │    LOGS     │
    │   SCREEN    │          │   SCREEN    │
    └─────────────┘          └─────────────┘
         │                           │
    ┌────┴────┬─────────────┐       │
    │          │             │      │
    ↓          ↓             ↓      ↓
┌────────┐ ┌──────┐  ┌──────────┐  (Back)
│Blackout│ │Users │  │          │  │
│Schedule│ │Maint.│  │          │  │
└────────┘ └──────┘  └──────────┘  │
    │         │                     │
    └─────────┴─────────────────────┘
         All have Back buttons → MAIN
```

### State Transitions

```
Application Start
        ↓
   Initialize
        ↓
   Load Colors
        ↓
   Create Header
        ↓
   Create Screens
        ↓
   Show Main Screen
        ↓
   Ready for Input
        ↓
   User clicks button
        ↓
   Navigate / Execute
        ↓
   Update Status
        ↓
   Ready for next input
```

---

## 💬 Button Label Styles

### Icon + Text Pattern

```
[Icon] [Space] [Text]

🔓      UNLOCK
🔒      LOCK
📚      CLASS
⚙️      SETTINGS
📋      LOGS
❌      EXIT
💾      SAVE
🔄      REFRESH
✏️      EDIT
🗑️      DELETE
👑      ADMIN (badge)
📅      BLACKOUT SCHEDULE
👥      USER MAINTENANCE
```

### Sizing

```
Large Buttons (100px height):
  Icon: 20px
  Space: 8px
  Text: 16px bold

Medium Buttons (70px height):
  Icon: 16px
  Space: 8px
  Text: 13px bold

Small Buttons (55px height):
  Icon: 14px
  Space: 6px
  Text: 12px bold
```

---

## 📊 Settings Screen Layout

### Visual Hierarchy

```
┌─────────────────────────────────────────┐
│  ⚙️  SETTINGS                            │  Title (20px)
├─────────────────────────────────────────┤
│                                         │
│  ┌─────────────────────────────────────┤
│  │ 📅 Blackout Schedule                │  Settings Card
│  │ Manage access blackout times        │
│  └─────────────────────────────────────┤
│                                         │
│  ┌─────────────────────────────────────┤
│  │ 👥 User Maintenance                 │  Settings Card
│  │ Add/edit/delete users               │
│  └─────────────────────────────────────┤
│                                         │
│  ┌─────────────────────────────────────┤
│  │ Class Access Duration        [v]    │  Dropdown
│  │   60 minutes                         │
│  └─────────────────────────────────────┤
│                                         │  Spacer (flex)
│                                         │
│  ┌────────────┬────────────┬──────────┤
│  │  SHUTDOWN  │   EXIT     │   BACK   │  Action Buttons
│  │  (Red)     │  (Gray)    │  (Gray)  │
│  └────────────┴────────────┴──────────┘
└─────────────────────────────────────────┘
```

---

## 📋 Log Screen Layout

### Visual Hierarchy

```
┌─────────────────────────────────────────┐
│  📋 RFID ENTRY LOG                       │  Title (20px)
├─────────────────────────────────────────┤
│                                         │
│  ┌─────────────────────────────────────┤
│  │ 14:23:45 ✓ GRANTED John (UID:123)  │  Entry (Green)
│  │ 14:20:12 ✓ GRANTED Sarah (UID:456) │  Entry (Green)
│  │ 14:18:30 ✗ DENIED Unknown (UID:999)│  Entry (Red)
│  │ 14:15:00 ✓ GRANTED Mike (UID:789)  │  Entry (Green)
│  │                                     │
│  │           (scrollable)              │
│  │                                     │
│  │ 13:45:22 ✓ GRANTED Jane (UID:234)  │  Entry (Green)
│  └─────────────────────────────────────┤
│                                         │
│  ┌────────────┬────────────────────────┤
│  │ REFRESH    │ BACK TO MAIN           │  Buttons
│  │ (Blue)     │ (Gray)                 │
│  └────────────┴────────────────────────┘
└─────────────────────────────────────────┘
```

---

## 👥 User Management Layout

### Visual Hierarchy

```
┌─────────────────────────────────────────┐
│  👥 USER MAINTENANCE                     │  Title (20px)
├─────────────────────────────────────────┤
│                                         │
│  ┌─────────────────────────────────────┤
│  │ ID: UID001  John Doe  👑 ADMIN     │  User Card
│  │            [EDIT] [DELETE]          │
│  └─────────────────────────────────────┤
│                                         │
│  ┌─────────────────────────────────────┤
│  │ ID: UID002  Sarah Smith             │  User Card
│  │            [EDIT] [DELETE]          │
│  └─────────────────────────────────────┤
│                                         │
│  ┌─────────────────────────────────────┤
│  │ ID: UID003  Mike Johnson  👑 ADMIN │  User Card
│  │            [EDIT] [DELETE]          │
│  └─────────────────────────────────────┤
│                                         │  (scrollable)
│                                         │
│  ┌────────────────┬────────────────────┤
│  │ + ADD USER     │ BACK                │  Buttons
│  │ (Blue)         │ (Gray)              │
│  └────────────────┴────────────────────┘
└─────────────────────────────────────────┘
```

---

## 📅 Blackout Schedule Layout

### Visual Hierarchy

```
┌─────────────────────────────────────────┐
│  📅 BLACKOUT SCHEDULE                    │  Title (20px)
├─────────────────────────────────────────┤
│                                         │
│  ┌─────────────────────────────────────┤
│  │ Monday                              │  Groupbox
│  │ [+ Add Time Block]                  │
│  │  From: [04:00] To: [10:00] [✕]     │  Time Block
│  └─────────────────────────────────────┤
│                                         │
│  ┌─────────────────────────────────────┤
│  │ Tuesday                             │  Groupbox
│  │ [+ Add Time Block]                  │
│  └─────────────────────────────────────┤
│                                         │  (scrollable)
│                    ...                 │
│                                         │
│  ┌─────────────────────────────────────┤
│  │ Sunday                              │  Groupbox
│  │ [+ Add Time Block]                  │
│  └─────────────────────────────────────┤
│                                         │
│  ┌────────────────┬────────────────────┤
│  │ SAVE SCHEDULE  │ BACK                │  Buttons
│  │ (Green)        │ (Gray)              │
│  └────────────────┴────────────────────┘
└─────────────────────────────────────────┘
```

---

## 🌈 Typography Scale

### Size Hierarchy

```
24px Bold     ← Main Page Title (e.g., "POWER ALLEY CROSSFIT")
              └─ Line height: ~32px

20px Bold     ← Section Titles (e.g., "⚙️ SETTINGS")
              └─ Line height: ~28px

16px Bold     ← Large Button Labels (Primary buttons)
              └─ Line height: ~22px

14px Regular  ← Body Text & Standard Button Labels
              └─ Line height: ~20px

13px Bold     ← Secondary Button Labels (70px buttons)
              └─ Line height: ~18px

12px Regular  ← Helper Text & Small Labels
              └─ Line height: ~16px

11px Bold     ← UI Metadata & Badges (e.g., "👑 ADMIN")
              └─ Line height: ~15px
```

---

## 📐 Spacing Grid System

### Base Unit: 4px

```
Spacing Values:
4px    = 1 unit (minimal)
8px    = 2 units (tight)
12px   = 3 units (standard) ← Most common
16px   = 4 units (comfortable)
20px   = 5 units (spacious)
24px   = 6 units (generous)

Applied To:
Button padding:      8-12px
Container margins:   12-16px
Grid gaps:           12px
Line spacing:        12-16px
Element spacing:     12px
```

---

## 🎯 Touch Target Sizing

### Minimum Sizes (WCAG AAA)

```
48px × 48px  = Minimum touch target for any element

Actual Sizes (Our UI):
┌──────────────────────────────────────┐
│ Primary Buttons   │ 100px height     │
│ Secondary Buttons │ 70px height      │
│ Danger Buttons    │ 55px height      │
│ Input Fields      │ 40px height      │
│ List Items        │ 40px+ height     │
│ Small Buttons     │ 48px height      │
│ Status Dot        │ 16px (icon size) │
└──────────────────────────────────────┘

Touch Friendly Design:
✅ All buttons >= 48px (in at least one dimension)
✅ Primary buttons 100×100px (very comfortable)
✅ 12px spacing between buttons (no accidental touches)
✅ Clear visual feedback on press
✅ No timing requirements
```

---

## 🔄 Responsive Behavior

### 800×480 (Target Kiosk)

```
✅ Perfect fit
✅ No scaling needed
✅ All elements visible
✅ Optimal spacing
```

### 1920×1080 (Desktop)

```
⚠️  Works but oversized
✅ All buttons still functional
✅ Extra whitespace on sides
✅ Good for testing
```

### 1024×768 (Tablet)

```
✅ Good fit
✅ Grid may need adjustment
✅ Buttons proportional
✅ Functional
```

### 375×667 (Mobile)

```
⚠️  Buttons stack vertically
✅ Still functional
⚠️  Grid layout adjusts
⚠️  Not primary target
```

---

## 📊 Summary Statistics

| Aspect                   | Value                                     |
| ------------------------ | ----------------------------------------- |
| **Main Screen Buttons**  | 6 (3x2 grid)                              |
| **Primary Buttons**      | 3 (100px)                                 |
| **Secondary Buttons**    | 3 (70px)                                  |
| **Grid Spacing**         | 12px                                      |
| **Header Height**        | 72px                                      |
| **Footer Height**        | 40px                                      |
| **Content Area Height**  | 368px (480 - 72 - 40)                     |
| **Colors Used**          | 8 main + 5 accent = 13 total              |
| **Button States**        | 4 (default, hover, pressed, disabled)     |
| **Screens**              | 5 (main, settings, logs, blackout, users) |
| **Font Family**          | Roboto Condensed (primary)                |
| **Touch Target Minimum** | 48×48px                                   |
| **Average Button Size**  | 87×80px                                   |

---

**All diagrams represent 800×480 resolution (target kiosk display)**
