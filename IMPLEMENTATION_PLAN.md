# GateWise UI - Home Adaptation Implementation Plan

## Overview

This document outlines the prioritized tasks to repurpose the GateWise UI application from a gym access control system to a home access control system with garage door integration.

## Priority Levels

- **P0 (Critical):** Security and core functionality
- **P1 (High):** Essential features for home use
- **P2 (Medium):** Enhanced functionality and user experience
- **P3 (Low):** Nice-to-have features and integrations

---

## Phase 1: Security & Configuration (P0)

### 1.1 Replace Hardcoded Admin Password
**Priority:** P0  
**Effort:** 1-2 hours  
**Status:** Pending

**Current Issue:**
- Admin password is hardcoded as "admin" in `ui/gatewise_ui.py` line 487

**Implementation:**
- Load password from environment variable `GATEWISE_ADMIN_PASSWORD`
- Fall back to config file if environment variable not set
- Add validation and error handling
- Update UI to show secure password prompt

**Files to Modify:**
- `ui/gatewise_ui.py` - Update `request_password()` method

**Testing:**
- Verify password authentication with environment variable
- Test with missing/invalid environment variable
- Ensure no default fallback to "admin" in production

---

### 1.2 Create Configuration Management System
**Priority:** P0  
**Effort:** 2-3 hours  
**Status:** Pending

**Implementation:**
- Create `core/config.py` for centralized configuration
- Load from environment variables and config files
- Support `.env` file parsing
- Create `config.example` template

**Configuration Items:**
- Admin password
- GPIO pin assignments
- Relay settings (active high/low, pulse duration)
- Door module IP addresses
- Network settings
- Logging configuration

**Files to Create:**
- `core/config.py` - Configuration loader
- `config.example` - Template configuration file
- `.env.example` - Environment variable template

**Testing:**
- Load configuration from environment variables
- Load configuration from .env file
- Validate configuration values
- Test with missing optional values

---

### 1.3 Add Sensitive File Protection
**Priority:** P0  
**Effort:** 30 minutes  
**Status:** Completed (✓ .gitignore created)

**Implementation:**
- ✓ Created `.gitignore` to exclude sensitive files
- Update documentation about file permissions
- Add backup/restore instructions

---

## Phase 2: Garage Door Hardware Integration (P1)

### 2.1 Create GPIO Hardware Abstraction Layer
**Priority:** P1  
**Effort:** 3-4 hours  
**Status:** Pending

**Implementation:**
- Create `core/gpio_abstraction.py` for platform detection
- Implement GPIO wrapper with fallback for non-Pi systems
- Support RPi.GPIO and gpiozero libraries
- Create mock GPIO for development/testing

**Features:**
- Auto-detect Raspberry Pi vs. desktop environment
- Graceful degradation when GPIO not available
- Logging for all GPIO operations
- Pin validation and error handling

**Files to Create:**
- `core/gpio_abstraction.py` - Platform abstraction
- `core/gpio_mock.py` - Mock GPIO for testing

**Testing:**
- Test on Raspberry Pi with real GPIO
- Test on desktop without GPIO (mock mode)
- Verify pin numbering (BCM vs. BOARD)

---

### 2.2 Implement Garage Door Controller Module
**Priority:** P1  
**Effort:** 4-6 hours  
**Status:** Pending

**Implementation:**
- Create `core/garage.py` for garage door control
- Implement relay pulse function (momentary contact)
- Add button input handling with debouncing
- Optional: door state sensor integration
- Event logging for all garage operations

**Features:**
- Configurable relay pin and polarity (active high/low)
- Configurable pulse duration (default 500ms)
- Software debouncing for button input
- State tracking (door open/closed/unknown)
- Safety checks before triggering relay
- Manual button override support

**Files to Create:**
- `core/garage.py` - Main garage controller class

**Testing:**
- Test relay pulse timing and polarity
- Test button debouncing
- Test state detection with sensor
- Verify safety interlocks

---

### 2.3 Integrate Garage Controls into UI
**Priority:** P1  
**Effort:** 3-4 hours  
**Status:** Pending

**Implementation:**
- Add garage door control panel to main screen
- Display current door status (open/closed/unknown)
- Add manual trigger button
- Show recent garage events
- Add garage settings to settings screen

**UI Elements:**
- Status indicator (icon or text)
- "Open/Close" button (context-aware)
- Activity log widget
- GPIO pin configuration in settings

**Files to Modify:**
- `ui/gatewise_ui.py` - Add garage UI components

**Testing:**
- Test UI updates with door state changes
- Verify button functionality
- Test with GPIO unavailable (graceful degradation)

---

## Phase 3: Home-Centric Terminology & Features (P2)

### 3.1 Update Terminology from Gym to Home
**Priority:** P2  
**Effort:** 2-3 hours  
**Status:** Pending

**Current Gym-Specific Terms:**
- "GateWise" → Consider "HomeWise" or keep generic
- "Class Access Settings" → "Timed Access Settings"
- "Unlock for Class" → "Timed Unlock"
- "Blackout Schedule" → Keep or change to "Access Schedule"

**Implementation:**
- Update UI labels and button text
- Update window title and branding
- Modify settings screen terminology
- Update log messages and tooltips

**Files to Modify:**
- `ui/gatewise_ui.py` - All UI text strings
- `README.md` - Project description

**Testing:**
- Visual review of all screens
- Verify terminology consistency

---

### 3.2 Add Multi-Door Support
**Priority:** P2  
**Effort:** 4-6 hours  
**Status:** Pending

**Implementation:**
- Extend UI to support multiple doors/entrances
- Add door selection/configuration
- Separate logs per door
- Different access schedules per door

**Use Cases:**
- Front door RFID access
- Garage door relay control
- Side entrance control

**Files to Modify:**
- `ui/gatewise_ui.py` - Multi-door UI
- `core/config.py` - Door configuration
- User data structure - Per-door permissions

---

### 3.3 Enhance User Management for Home
**Priority:** P2  
**Effort:** 2-3 hours  
**Status:** Pending

**Implementation:**
- Add user categories: Family, Guest, Temporary
- Add expiration dates for temporary access
- Add access history per user
- Add user notes/descriptions

**Files to Modify:**
- `ui/gatewise_ui.py` - User dialog and list
- User data structure - Additional fields

---

## Phase 4: Safety & Monitoring (P1-P2)

### 4.1 Implement Garage Door Safety Features
**Priority:** P1  
**Effort:** 3-4 hours  
**Status:** Pending

**Implementation:**
- Add door state detection (open/closed/moving)
- Prevent triggering when unsafe
- Add configurable timeout for door operations
- Implement auto-close feature (optional)
- Add obstruction detection (if sensor available)

**Files to Modify:**
- `core/garage.py` - Safety logic
- `ui/gatewise_ui.py` - Safety status display

**Testing:**
- Test with door in various states
- Test timeout handling
- Verify safety interlocks

---

### 4.2 Add Comprehensive Event Logging
**Priority:** P2  
**Effort:** 2-3 hours  
**Status:** Pending

**Implementation:**
- Log all access attempts (success/failure)
- Log all garage door operations
- Log admin actions (user changes, config changes)
- Persist logs to file with rotation
- Add log export functionality

**Files to Modify:**
- `core/logger.py` - Enhance logging
- `ui/gatewise_ui.py` - Log display improvements

---

### 4.3 Add Notifications (Optional)
**Priority:** P3  
**Effort:** 4-6 hours  
**Status:** Pending

**Implementation:**
- Email notifications for events
- Push notifications (via services like Pushover)
- Integration with Home Assistant (MQTT)
- Configurable notification rules

---

## Phase 5: Testing & Quality (P1)

### 5.1 Create Test Suite for Garage Module
**Priority:** P1  
**Effort:** 3-4 hours  
**Status:** Pending

**Implementation:**
- Create test file `tests/test_garage.py`
- Mock GPIO operations
- Test relay pulse timing
- Test button debouncing
- Test state transitions
- Test safety interlocks

**Files to Create:**
- `tests/test_garage.py`
- `tests/conftest.py` - Shared fixtures

---

### 5.2 Add Integration Tests
**Priority:** P2  
**Effort:** 2-3 hours  
**Status:** Pending

**Implementation:**
- Test UI interactions with garage controller
- Test configuration loading
- Test persistence (users.json, etc.)
- Test error scenarios

---

### 5.3 Add Continuous Integration
**Priority:** P2  
**Effort:** 2-3 hours  
**Status:** Pending

**Implementation:**
- Create GitHub Actions workflow
- Run tests on PRs
- Lint Python code (pylint, flake8, black)
- Check for security issues

**Files to Create:**
- `.github/workflows/ci.yml`

---

## Phase 6: Documentation & Deployment (P2)

### 6.1 Update README
**Priority:** P2  
**Effort:** 1-2 hours  
**Status:** Pending

**Implementation:**
- Update project description
- Add features list
- Add screenshots
- Link to SETUP.md
- Add contribution guidelines

---

### 6.2 Create Hardware Documentation
**Priority:** P2  
**Effort:** 2-3 hours  
**Status:** Completed (✓ Included in SETUP.md)

**Implementation:**
- ✓ Detailed wiring diagrams in SETUP.md
- ✓ Safety warnings
- ✓ Hardware shopping list
- Create visual diagrams (optional)

---

### 6.3 Create Deployment Scripts
**Priority:** P2  
**Effort:** 2-3 hours  
**Status:** Pending

**Implementation:**
- Create `scripts/install.sh` for automated setup
- Create systemd service template
- Create backup/restore scripts
- Add update script

**Files to Create:**
- `scripts/install.sh`
- `scripts/backup.sh`
- `scripts/restore.sh`
- `systemd/gatewise.service`

---

## Phase 7: Advanced Features (P3)

### 7.1 Home Assistant Integration
**Priority:** P3  
**Effort:** 6-8 hours

**Implementation:**
- MQTT support for state publishing
- Support for MQTT commands
- Home Assistant discovery
- Sensor entities for door state
- Switch entities for door control

---

### 7.2 Web Interface
**Priority:** P3  
**Effort:** 10-15 hours

**Implementation:**
- Create REST API
- Create web UI for remote access
- Add authentication and HTTPS
- Mobile-responsive design

---

### 7.3 Automation Rules
**Priority:** P3  
**Effort:** 4-6 hours

**Implementation:**
- Time-based automation (auto-close at night)
- Presence-based automation (auto-open when approaching)
- Geofencing support
- IFTTT integration

---

## Summary Statistics

**Total Estimated Effort:**
- P0 (Critical): 3-6 hours
- P1 (High): 20-30 hours  
- P2 (Medium): 20-30 hours
- P3 (Low): 20-30 hours

**Total: 63-96 hours** for complete implementation

**Recommended Phase Completion Order:**
1. Phase 1: Security & Configuration (P0) - **CRITICAL**
2. Phase 2: Garage Door Integration (P1) - **ESSENTIAL**
3. Phase 4.1: Safety Features (P1) - **ESSENTIAL**
4. Phase 3: Home Terminology (P2) - **IMPORTANT**
5. Phase 5: Testing (P1-P2) - **IMPORTANT**
6. Phase 6: Documentation (P2) - **IMPORTANT**
7. Phases 4.2-4.3, 7: Advanced Features (P3) - **OPTIONAL**

---

## Next Steps

1. **Start with Phase 1.1:** Replace hardcoded admin password (CRITICAL SECURITY ISSUE)
2. **Implement Phase 1.2:** Configuration management system
3. **Move to Phase 2:** Garage door hardware integration
4. **Iterate and test:** Test each component before moving to next phase
5. **Update this document:** Mark items as complete, adjust estimates as needed
