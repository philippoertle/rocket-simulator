# Feature Implementation: GUI for Basic Simulation (Issue #6)

**ISO/IEC/IEEE 12207:2017 Maintenance Process Implementation**

**Issue:** #6 - [FEATURE] GUI for Basic Simulation  
**Type:** Perfective Maintenance (Enhancement)  
**Priority:** Critical (Blocks important use cases)  
**Complexity:** High (Weeks of work)  
**Date Started:** January 25, 2026  
**Status:** In Progress

---

## Table of Contents

1. [Issue Summary](#issue-summary)
2. [Requirements Analysis](#requirements-analysis)
3. [Impact Assessment](#impact-assessment)
4. [Architecture & Design](#architecture--design)
5. [Implementation Plan](#implementation-plan)
6. [Testing Strategy](#testing-strategy)
7. [Documentation Updates](#documentation-updates)
8. [Traceability](#traceability)

---

## Issue Summary

### Feature Description

**User Story:**  
As a rocket scientist who is not a programmer, I want to use the Basic Simulation feature through an easy-to-use GUI, so that I can configure and run simulations without writing Python code.

**Current State:**  
- Basic simulation requires Python programming knowledge
- Users must write code to configure `FullSimulationConfig`
- Results are displayed in console output
- Visualization requires additional Python calls

**Proposed Solution:**  
- Simple, user-friendly GUI application
- Configuration through form fields
- One-click simulation execution
- Integrated visualization display
- No programming required

**Reference:**  
- QUICKSTART.md Section 1: Basic Simulation
- GitHub Issue: https://github.com/philippoertle/rocket-simulator/issues/6

---

## Requirements Analysis

### Functional Requirements

**FR-GUI-1: Configuration Input**
- **Description:** User shall be able to configure all Basic Simulation parameters through GUI form
- **Parameters:**
  - Volume (liters): Float input, range 0.5-5.0L, default 2.0L
  - Fuel/Oxidizer Ratio: Float input, range 1.0-3.0, default 2.0 (stoichiometric)
  - Vessel Diameter (mm): Float input, range 50-150mm, default 95mm
  - Vessel Thickness (mm): Float input, range 0.1-1.0mm, default 0.3mm
  - Vessel Material: Dropdown ["PET", "HDPE", "Polycarbonate"], default "PET"
- **Validation:** Input validation with error messages
- **Priority:** Critical
- **Verification:** Manual GUI testing

**FR-GUI-2: Simulation Execution**
- **Description:** User shall be able to run simulation with one-click button
- **Actions:**
  - "Run Simulation" button
  - Progress indicator during execution
  - Cancel button (optional for v1)
- **Priority:** Critical
- **Verification:** Manual GUI testing + automated unit tests

**FR-GUI-3: Results Display**
- **Description:** Display simulation results in human-readable format
- **Output Fields:**
  - Peak Pressure (bar)
  - Peak Temperature (K)
  - Min Safety Factor
  - Vessel Status (Safe/Unsafe with visual indicator)
  - Warnings (if any)
- **Priority:** Critical
- **Verification:** Manual GUI testing

**FR-GUI-4: Visualization Display**
- **Description:** Display comprehensive simulation plots in GUI
- **Plots:**
  - Pressure & Temperature vs Time
  - Stress Distribution
  - Safety Factor Evolution
  - Or: Comprehensive Dashboard
- **Interaction:** Zoomable, saveable plots
- **Priority:** High
- **Verification:** Manual GUI testing

**FR-GUI-5: Export Results**
- **Description:** User shall be able to export results and plots
- **Export Options:**
  - Save plot as PNG/PDF
  - Export results as JSON
  - Export summary as text report
- **Priority:** Medium
- **Verification:** Manual testing + file format validation

**FR-GUI-6: Input Presets**
- **Description:** Provide common configuration presets
- **Presets:**
  - "Safe 2L Bottle (Default)"
  - "Dangerous High Pressure"
  - "Custom" (user-defined)
- **Priority:** Low (v2)
- **Verification:** Manual testing

### Non-Functional Requirements

**NFR-GUI-1: Usability**
- **Description:** GUI shall be intuitive for non-programmers
- **Criteria:**
  - First-time user can run simulation in <2 minutes
  - Clear labels and tooltips
  - Helpful error messages
- **Priority:** Critical
- **Verification:** User acceptance testing

**NFR-GUI-2: Cross-Platform**
- **Description:** GUI shall work on Windows, macOS, Linux
- **Implementation:** Use Qt (PySide6/PyQt6) for cross-platform support
- **Priority:** High
- **Verification:** Testing on all 3 platforms

**NFR-GUI-3: Performance**
- **Description:** GUI shall remain responsive during simulation
- **Criteria:**
  - GUI does not freeze during simulation execution
  - Progress updates every 0.5s or less
- **Implementation:** Run simulation in background thread
- **Priority:** High
- **Verification:** Performance testing

**NFR-GUI-4: Appearance**
- **Description:** GUI shall look professional and modern
- **Style:** Clean, scientific aesthetic (Qt Material Design or similar)
- **Priority:** Medium
- **Verification:** Visual review

**NFR-GUI-5: Error Handling**
- **Description:** GUI shall handle errors gracefully
- **Criteria:**
  - No crashes on invalid input
  - Clear error messages
  - Recovery without restart
- **Priority:** High
- **Verification:** Error injection testing

**NFR-GUI-6: Installation**
- **Description:** GUI shall be easy to install
- **Options:**
  - Python package (pip install with GUI extras)
  - Standalone executable (PyInstaller, optional v2)
- **Priority:** Medium (executable is High for non-programmers)
- **Verification:** Installation testing

**NFR-GUI-7: Dependencies**
- **Description:** Maintain open-source dependencies
- **Framework:** PySide6 (LGPL) or PyQt6 (GPL/Commercial)
- **Recommendation:** PySide6 for LGPL compatibility
- **Priority:** Critical
- **Verification:** License audit

---

## Impact Assessment

### Affected Modules

**New Modules:**
- `rocket_sim/gui/` (NEW)
  - `__init__.py`
  - `main_window.py` - Main application window
  - `widgets.py` - Custom widgets (input forms, result display)
  - `simulation_thread.py` - Background simulation execution
  - `plot_widgets.py` - Matplotlib/PyQtGraph integration
  - `resources.py` - Icons, styles (optional)

**Modified Modules:**
- `setup.py` - Add GUI dependencies as extras_require
- `requirements.txt` - Add GUI dependencies (optional section)
- `README.md` - Add GUI usage section
- `INSTALL.md` - Add GUI installation instructions
- `QUICKSTART.md` - Add GUI quick start section

**No Impact:**
- All existing simulation modules remain unchanged
- CLI functionality remains available
- Backward compatibility maintained

### Dependencies

**New Dependencies:**
- **PySide6** (recommended) or PyQt6: GUI framework
  - Version: >=6.6.0
  - License: LGPL (PySide6) or GPL/Commercial (PyQt6)
- **matplotlib** (already present): Plotting backend
  - Already in requirements.txt
- **Optional: PyInstaller**: For standalone executables
  - Version: >=6.0.0
  - For distribution only

**Installation:**
```bash
# Install with GUI support
pip install rocket-sim[gui]

# Or manually
pip install PySide6>=6.6.0
```

### Risk Assessment

**Technical Risks:**

1. **Thread Safety (Medium Risk)**
   - **Issue:** Cantera/Matplotlib may not be thread-safe
   - **Mitigation:** Use Qt signals/slots for thread communication, run simulation in QThread
   - **Testing:** Concurrent execution tests

2. **Memory Usage (Low Risk)**
   - **Issue:** Multiple plots may consume memory
   - **Mitigation:** Lazy loading, plot caching, cleanup after display
   - **Testing:** Memory profiling

3. **Cross-Platform Compatibility (Medium Risk)**
   - **Issue:** Qt behavior differences across platforms
   - **Mitigation:** Test on all 3 platforms, use Qt best practices
   - **Testing:** CI/CD on Windows/Linux/macOS

4. **Cantera GUI Integration (Low Risk)**
   - **Issue:** Cantera errors may crash GUI
   - **Mitigation:** Wrap all Cantera calls in try-except, display errors in GUI
   - **Testing:** Error injection tests

**Business Risks:**

1. **Scope Creep (Medium Risk)**
   - **Issue:** Feature requests for advanced GUI features
   - **Mitigation:** Clear v1 scope, roadmap for future features
   - **Testing:** Requirements review

2. **Maintenance Burden (Low Risk)**
   - **Issue:** GUI adds complexity for maintenance
   - **Mitigation:** Clean architecture, good documentation, automated tests
   - **Testing:** Code review, maintainability metrics

**Go/No-Go Decision: ✅ GO**
- Benefits outweigh risks
- Clear implementation path
- Aligns with project mission (accessibility for non-programmers)
- Manageable complexity

---

## Architecture & Design

### Architecture Overview

**Design Pattern:** Model-View-Controller (MVC) adapted for Qt

```
┌─────────────────────────────────────────────────────────┐
│                     GUI Application                      │
│                  (rocket_sim/gui/)                       │
├─────────────────────────────────────────────────────────┤
│  MainWindow (View)                                       │
│    ├─ ConfigurationWidget (input forms)                 │
│    ├─ SimulationControlWidget (run button, progress)    │
│    ├─ ResultsWidget (text results display)              │
│    └─ VisualizationWidget (plots)                       │
├─────────────────────────────────────────────────────────┤
│  SimulationController (Controller)                       │
│    ├─ Validate inputs                                   │
│    ├─ Create FullSimulationConfig                       │
│    ├─ Launch SimulationThread                           │
│    └─ Handle results                                    │
├─────────────────────────────────────────────────────────┤
│  SimulationThread (Background Worker)                    │
│    ├─ Run run_complete_simulation()                     │
│    ├─ Emit progress signals                             │
│    └─ Emit result/error signals                         │
├─────────────────────────────────────────────────────────┤
│           Existing Simulation Backend (Model)            │
│         (rocket_sim.integration.full_simulation)         │
│    - FullSimulationConfig                               │
│    - run_complete_simulation()                          │
│    - SimulationResult                                   │
└─────────────────────────────────────────────────────────┘
```

### Component Design

#### 1. MainWindow (`main_window.py`)

**Responsibility:** Top-level application window, layout management

**Features:**
- Menu bar: File (Export, Exit), Help (About, Documentation)
- Toolbar: Quick actions (Run, Clear, Export)
- Central widget: Tab widget or splitter with Configuration, Results, Plots
- Status bar: Show status messages, simulation time

**Layout:**
```
┌────────────────────────────────────────────────┐
│  Menu Bar  [File] [Help]                       │
├────────────────────────────────────────────────┤
│  Toolbar  [▶ Run] [Clear] [💾 Export]          │
├──────────────────┬─────────────────────────────┤
│  Configuration   │  Results & Visualization    │
│  ┌────────────┐  │  ┌───────────────────────┐  │
│  │ Volume     │  │  │ Peak Pressure: X bar  │  │
│  │ Ratio      │  │  │ Temperature: Y K      │  │
│  │ Diameter   │  │  │ Safety Factor: Z      │  │
│  │ Thickness  │  │  │ Status: ✅ Safe        │  │
│  │ Material   │  │  └───────────────────────┘  │
│  └────────────┘  │  ┌───────────────────────┐  │
│                  │  │                       │  │
│  [▶ Run Sim]     │  │   Simulation Plots    │  │
│                  │  │   (tabs or stacked)   │  │
│                  │  │                       │  │
│                  │  └───────────────────────┘  │
├──────────────────┴─────────────────────────────┤
│  Status: Ready                           v0.1.0│
└────────────────────────────────────────────────┘
```

#### 2. ConfigurationWidget (`widgets.py`)

**Responsibility:** Input form for simulation parameters

**Implementation:**
- QDoubleSpinBox for numeric inputs (with units in labels)
- QComboBox for material selection
- Validators for range checking
- Tooltips with parameter descriptions
- Reset to defaults button

**Validation:**
- Real-time validation with visual feedback (red border for invalid)
- Enable/disable Run button based on validity
- Helpful error tooltips

#### 3. SimulationControlWidget (`widgets.py`)

**Responsibility:** Control simulation execution

**Features:**
- "Run Simulation" QPushButton
- QProgressBar (indeterminate or 0-100% if possible)
- "Cancel" button (optional v1)
- Elapsed time display

**States:**
- Ready: Run enabled, progress hidden
- Running: Run disabled, progress shown, cancel enabled
- Complete: Run enabled, progress hidden
- Error: Run enabled, error message shown

#### 4. ResultsWidget (`widgets.py`)

**Responsibility:** Display simulation results

**Implementation:**
- QTextEdit or QLabel with rich text for formatted results
- Color-coded status (Green ✅ Safe, Red ⚠️ Unsafe)
- Collapsible sections for detailed results
- Copy to clipboard button

**Display Format:**
```
=== SIMULATION RESULTS ===

Peak Pressure:      2.44 bar
Peak Temperature:   3369 K
Min Safety Factor:  1.92
Max Stress:         38.7 MPa

Status: ✅ SAFE

⚠️ Warnings:
  - Safety factor below 2.0 (recommended minimum)
```

#### 5. VisualizationWidget (`plot_widgets.py`)

**Responsibility:** Display simulation plots

**Implementation:**
- Embedded Matplotlib figures using FigureCanvasQTAgg
- QTabWidget with tabs for different plot types:
  - Tab 1: Pressure & Temperature vs Time
  - Tab 2: Stress Distribution
  - Tab 3: Safety Factor Evolution
  - Tab 4: Comprehensive Dashboard (all-in-one)
- Matplotlib toolbar for zoom, pan, save
- Right-click context menu: Save As, Copy, Clear

**Plot Generation:**
- Reuse existing `rocket_sim.visualization.plots` functions
- Adapt for Qt canvas
- Add interactive features (tooltips on hover, optional)

#### 6. SimulationThread (`simulation_thread.py`)

**Responsibility:** Run simulation in background thread

**Implementation:**
```python
class SimulationThread(QThread):
    # Signals
    progress_updated = Signal(int, str)  # percentage, message
    simulation_complete = Signal(object)  # SimulationResult
    simulation_failed = Signal(str)       # error message
    
    def __init__(self, config: FullSimulationConfig):
        super().__init__()
        self.config = config
        
    def run(self):
        try:
            # Emit progress updates
            self.progress_updated.emit(10, "Starting combustion simulation...")
            
            # Run simulation
            result = run_complete_simulation(self.config, verbose=False)
            
            self.progress_updated.emit(100, "Complete")
            self.simulation_complete.emit(result)
        except Exception as e:
            self.simulation_failed.emit(str(e))
```

**Thread Safety:**
- No direct GUI updates from thread
- Use Qt signals for communication
- Cantera calls isolated in thread

#### 7. Application Entry Point (`__main__.py`)

**Responsibility:** Launch GUI application

**Implementation:**
```python
# rocket_sim/gui/__main__.py
import sys
from PySide6.QtWidgets import QApplication
from rocket_sim.gui.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("PET Rocket Simulator")
    app.setOrganizationName("Rocket Simulator Team")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
```

**Launch Methods:**
```bash
# Method 1: Python module
python -m rocket_sim.gui

# Method 2: Console script (setup.py entry point)
rocket-sim-gui

# Method 3: Standalone executable (PyInstaller, v2)
./RocketSimulator.exe
```

---

## Implementation Plan

### Phase 1: Foundation (Day 1-2)

**Tasks:**
1. Create `rocket_sim/gui/` package structure
2. Set up PySide6 dependencies in `setup.py`
3. Create basic MainWindow with placeholder layout
4. Implement ConfigurationWidget with all input fields
5. Add input validation
6. Test: Manual GUI launch, input validation

**Deliverables:**
- `rocket_sim/gui/__init__.py`
- `rocket_sim/gui/__main__.py`
- `rocket_sim/gui/main_window.py`
- `rocket_sim/gui/widgets.py`
- Updated `setup.py` with GUI extras

**Verification:**
- GUI launches without errors
- All input fields present and functional
- Validation works correctly

### Phase 2: Simulation Integration (Day 3-4)

**Tasks:**
1. Implement SimulationThread
2. Connect Run button to simulation execution
3. Implement SimulationControlWidget with progress
4. Handle simulation success/failure
5. Display basic results in ResultsWidget
6. Test: End-to-end simulation execution

**Deliverables:**
- `rocket_sim/gui/simulation_thread.py`
- Complete SimulationControlWidget
- Complete ResultsWidget

**Verification:**
- Simulation runs in background
- GUI remains responsive
- Results display correctly
- Errors handled gracefully

### Phase 3: Visualization (Day 5-6)

**Tasks:**
1. Implement VisualizationWidget with Matplotlib integration
2. Create tabs for different plot types
3. Integrate existing visualization functions
4. Add plot save functionality
5. Test: All plot types display correctly

**Deliverables:**
- `rocket_sim/gui/plot_widgets.py`
- Complete VisualizationWidget

**Verification:**
- All 4 plot types display
- Plots are interactive (zoom, pan)
- Save plot functionality works

### Phase 4: Polish & Export (Day 7-8)

**Tasks:**
1. Implement export functionality (JSON, text report)
2. Add menu bar actions
3. Create About dialog
4. Add application icon (optional)
5. Implement presets (optional v1 or v2)
6. Style GUI with Qt stylesheets

**Deliverables:**
- Export functionality
- Menu bar and dialogs
- Polished UI

**Verification:**
- Export formats work correctly
- UI looks professional
- All menu items functional

### Phase 5: Testing & Documentation (Day 9-10)

**Tasks:**
1. Write unit tests for GUI components
2. Automated GUI testing (pytest-qt)
3. Manual testing on Windows/Linux/macOS
4. Update documentation (README, INSTALL, QUICKSTART)
5. Create user guide for GUI
6. Add screenshots to documentation

**Deliverables:**
- `rocket_sim/gui/tests/test_*.py`
- Updated documentation
- Screenshots

**Verification:**
- All tests pass
- Documentation complete
- Cross-platform testing complete

### Phase 6: Packaging (Day 11-12, Optional)

**Tasks:**
1. Create standalone executable with PyInstaller
2. Test executable on clean systems
3. Create installer (NSIS for Windows, DMG for macOS, AppImage for Linux)
4. Upload to GitHub releases

**Deliverables:**
- PyInstaller spec file
- Build scripts
- Installers for all platforms

**Verification:**
- Executables run on clean systems
- File size reasonable (<100MB)
- Installation smooth

---

## Testing Strategy

### Unit Tests

**Test Modules:**
- `test_widgets.py` - Test individual widgets
- `test_main_window.py` - Test main window
- `test_simulation_thread.py` - Test background simulation
- `test_validation.py` - Test input validation

**Framework:**
- pytest
- pytest-qt (Qt testing plugin)

**Example Test:**
```python
# rocket_sim/gui/tests/test_widgets.py
import pytest
from PySide6.QtWidgets import QApplication
from rocket_sim.gui.widgets import ConfigurationWidget

@pytest.fixture(scope="session")
def qapp():
    """Create QApplication instance for testing."""
    return QApplication.instance() or QApplication([])

def test_configuration_widget_default_values(qapp):
    """Test ConfigurationWidget initializes with correct defaults."""
    widget = ConfigurationWidget()
    
    assert widget.volume_input.value() == 2.0
    assert widget.ratio_input.value() == 2.0
    assert widget.diameter_input.value() == 95.0
    assert widget.thickness_input.value() == 0.3
    assert widget.material_combo.currentText() == "PET"

def test_configuration_widget_validation(qapp):
    """Test input validation."""
    widget = ConfigurationWidget()
    
    # Valid input
    widget.volume_input.setValue(2.0)
    assert widget.is_valid()
    
    # Invalid input (out of range)
    widget.volume_input.setValue(10.0)  # > max
    assert not widget.is_valid()
```

### Integration Tests

**Test Scenarios:**
1. End-to-end simulation execution
2. Result display after successful simulation
3. Error handling for invalid configurations
4. Plot generation and display
5. Export functionality

**Example Test:**
```python
# rocket_sim/gui/tests/test_integration.py
def test_end_to_end_simulation(qapp, qtbot):
    """Test complete simulation workflow."""
    window = MainWindow()
    window.show()
    
    # Set configuration
    window.config_widget.volume_input.setValue(2.0)
    
    # Click run button
    qtbot.mouseClick(window.control_widget.run_button, Qt.LeftButton)
    
    # Wait for simulation to complete (max 10s)
    with qtbot.waitSignal(window.simulation_complete, timeout=10000):
        pass
    
    # Verify results displayed
    assert "Peak Pressure" in window.results_widget.text()
    assert window.plot_widget.figure is not None
```

### Manual Testing Checklist

**Functional Testing:**
- [ ] All input fields accept valid values
- [ ] Invalid inputs show error messages
- [ ] Run button executes simulation
- [ ] Progress indicator shows during execution
- [ ] Results display correctly
- [ ] All 4 plot types generate and display
- [ ] Export JSON works
- [ ] Export plots works
- [ ] Menu items functional
- [ ] About dialog displays

**Usability Testing:**
- [ ] First-time user can run simulation in <2 minutes
- [ ] Error messages are clear and helpful
- [ ] Layout is intuitive
- [ ] Tooltips provide useful information

**Cross-Platform Testing:**
- [ ] Windows 10/11: All features work
- [ ] macOS 12+: All features work
- [ ] Linux (Ubuntu 22.04): All features work
- [ ] UI renders correctly on all platforms

**Performance Testing:**
- [ ] GUI remains responsive during simulation
- [ ] No memory leaks after multiple simulations
- [ ] Simulation completes in reasonable time

**Error Handling Testing:**
- [ ] Invalid Cantera inputs handled gracefully
- [ ] File save errors handled (disk full, permissions)
- [ ] GUI doesn't crash on any user action

---

## Documentation Updates

### Files to Update

1. **README.md**
   - Add "GUI Usage" section after "Usage"
   - Add screenshot of GUI
   - Update installation section

2. **INSTALL.md**
   - Add GUI installation instructions
   - Add PySide6 installation steps
   - Add troubleshooting for GUI issues

3. **QUICKSTART.md**
   - Add "Using the GUI" section before "1. Basic Simulation"
   - Add screenshots of GUI workflow

4. **New: docs/GUI-USER-GUIDE.md**
   - Comprehensive GUI user guide
   - Screenshots for all features
   - Troubleshooting section

5. **CONTRIBUTING.md**
   - Add GUI development guidelines
   - Add GUI testing instructions

6. **setup.py**
   - Add GUI extras_require
   - Add console_scripts entry point

### Documentation Content

**README.md Addition:**
```markdown
## GUI Usage

For users who prefer a graphical interface, launch the GUI:

```bash
# Launch GUI
python -m rocket_sim.gui

# Or if installed with entry point
rocket-sim-gui
```

![GUI Screenshot](docs/screenshots/gui-main.png)

The GUI provides:
- Easy configuration through form fields
- One-click simulation execution
- Integrated visualization
- Export results and plots
```

---

## Traceability

### Requirements to Implementation

| Requirement | Implementation | Test |
|-------------|----------------|------|
| FR-GUI-1 | ConfigurationWidget | test_widgets.py::test_configuration_widget |
| FR-GUI-2 | SimulationControlWidget + SimulationThread | test_simulation_thread.py |
| FR-GUI-3 | ResultsWidget | test_widgets.py::test_results_widget |
| FR-GUI-4 | VisualizationWidget | test_plot_widgets.py |
| FR-GUI-5 | Export functionality in MainWindow | test_main_window.py::test_export |
| NFR-GUI-1 | Overall GUI design + usability testing | Manual testing checklist |
| NFR-GUI-2 | PySide6 framework | Cross-platform testing |
| NFR-GUI-3 | SimulationThread (QThread) | Performance tests |
| NFR-GUI-4 | Qt stylesheets | Visual review |
| NFR-GUI-5 | try-except wrappers | Error injection tests |
| NFR-GUI-7 | PySide6 dependency | License audit |

### Issue to Deliverables

| Issue Requirement | Deliverable |
|-------------------|-------------|
| Modify configuration in GUI | ConfigurationWidget with all inputs |
| Run simulation in GUI | SimulationControlWidget + SimulationThread |
| See output in GUI | ResultsWidget + VisualizationWidget |
| Nice-looking (Qt suggested) | PySide6-based GUI with modern styling |

---

## Approval & Sign-Off

**Change Request:** Approved  
**Impact Assessment:** Reviewed and accepted  
**Implementation Plan:** Approved  
**Resources Allocated:** 12 days development + testing  

**Next Steps:**
1. Create feature branch: `feature/issue-6-gui`
2. Begin Phase 1 implementation
3. Daily progress updates in issue #6
4. Code review after each phase
5. Merge to main after Phase 5 complete
6. Optional: Phase 6 for standalone executable

---

**Document Version:** 1.0  
**Last Updated:** January 25, 2026  
**Author:** Development Team  
**Approved By:** Project Maintainer
