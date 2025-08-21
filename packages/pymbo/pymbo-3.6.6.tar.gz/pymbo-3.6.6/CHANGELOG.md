# PyMBO Changelog

## [3.6.6] - 2025-08-19

### Fixed
- **CRITICAL: Target Goals Academic Compliance**: Fixed incorrect Target goal implementation
  - Target goals now properly implemented as deviation minimization objectives (academic standard)
  - Previously incorrectly treated as equality constraints, which violated goal programming theory
  - Target deviations (e.g., `|temperature - 500°C|`) now integrated into multi-objective optimization
  - Enables proper trade-offs between response optimization and target parameter achievement
  - Range goals remain correctly implemented as constraints for safety bounds
  - Full academic compliance with Bayesian optimization and goal programming standards

### Enhanced
- **Target-Response Trade-off Optimization**: Target parameters now participate in Pareto front exploration
  - qNEHVI acquisition function properly balances response optimization with target achievement
  - Academic-standard formulation: `minimize |param - target|` instead of constraint `|param - target| ≤ ε`
  - Supports weighted target deviations for prioritization
  - Maintains backward compatibility with existing parameter configurations

## [3.6.3] - 2025-08-14

### Added
- **Target and Range Parameter Constraints**: Advanced constraint handling for parameter optimization
  - Target constraints: Keep parameters at specific values with tolerance (e.g., temperature = 500°C ± 5°C)
  - Range constraints: Restrict parameters to safe operating ranges (e.g., pressure: 2-8 bar)
  - Academic-standard constraint formulation and validation
  - Integration with BoTorch's constrained optimization algorithms

### Fixed
- **Pareto Plot Objective Detection**: Fixed issue where constraint goals were incorrectly treated as optimization objectives
  - Separated constraint goals (Target/Range) from optimization objectives (Maximize/Minimize)
  - Updated GUI objective detection logic for proper Pareto plot functionality
  - Consistent objective handling across all plotting controls

### Enhanced
- **Academic Standards Compliance**: All constraint implementations follow established optimization practices
  - Proper constraint normalization to unit cube space
  - Robust constraint validation and enforcement mechanisms
  - Comprehensive constraint satisfaction checking and logging

## [3.6.2] - 2025-08-09

### Added
- **Comprehensive Directory Reorganization**: Complete project structure overhaul for better maintainability
  - `tests/`: Organized test suite with category-based structure (core, gpu, gui, performance, integration, validation, debug)
  - `scripts/`: Standalone utility scripts for GPU acceleration, BLAS optimization, and system integration
  - `examples/`: Usage examples and implementation demonstrations
  - `docs/`: Structured documentation with manuals, reports, and summaries
- **Advanced Test Runner**: `tests/run_all_tests.py` with category-specific execution and comprehensive reporting
- **Improved Documentation**: Updated README.md with new architecture overview and development guidelines
- **Better Import Management**: Fixed import paths after file reorganization to maintain functionality

### Changed
- **File Organization**: Moved 60+ test files from root directory to organized `tests/` subdirectories
- **Script Organization**: Relocated standalone scripts to dedicated `scripts/` directory
- **Documentation Structure**: Organized all documentation files into logical `docs/` hierarchy
- **Import Path Updates**: Updated import statements in core modules to reflect new file locations

### Fixed
- **Import Path Issues**: Corrected relative imports in `benchmark_algorithms.py` and GPU integration scripts
- **File Naming Consistency**: Improved file organization and naming conventions throughout the project
- **Module Accessibility**: Ensured all moved files remain accessible with proper `__init__.py` files

### Removed
- **Root Directory Clutter**: Removed 60+ scattered test files, scripts, and documentation from project root
- **Redundant Files**: Cleaned up duplicate scripts and outdated implementation files
- **Development Artifacts**: Removed temporary files and development leftovers

## [3.1.4] - 2025-07-30

### Added
- Comprehensive sensitivity analysis control panel with 8 algorithms
- Algorithm-specific iteration controls with sliders and precise entry
- New FAST (Fourier Amplitude Sensitivity Test) and Delta moment-independent sensitivity algorithms
- Advanced options including confidence levels, bootstrap resampling, and parallel processing
- Reproducible sensitivity analysis with proper random seed handling
- Enhanced sensitivity analysis plotting with error bars and uncertainty quantification

### Fixed
- Random seed not being passed to sensitivity analysis calculations
- Non-deterministic behavior in sensitivity analysis plots
- Control panel routing issues in window and movable controls
- Callback compatibility between different control panel types

### Enhanced
- Sensitivity analysis now supports all 8 algorithms: Variance-based, Morris Elementary Effects, Gradient-based, Sobol-like, GP Lengthscale, Feature Importance, FAST, and Delta
- Algorithm-specific parameters (Morris trajectories, Sobol order, FAST interference parameter)
- Comprehensive axis range controls for plot customization
- Professional control panel UI with organized sections and tooltips

## [3.0.0] - 2025-01-30

### Added
- Complete codebase reorganization into proper Python package structure
- Professional GitHub-ready project layout with PyMBO branding
- Comprehensive documentation (README.md, setup.py, requirements.txt)
- Creative Commons BY-NC-ND 4.0 License for academic use
- Package-level imports for easier usage

### Changed
- **Package renamed to PyMBO** (Python Multi-objective Bayesian Optimization)
- Reorganized all modules into `pymbo/` package structure:
  - `core/`: Core optimization algorithms and controllers
  - `gui/`: All GUI components and windows
  - `utils/`: Utility functions for plotting, reporting, and scientific calculations
  - `screening/`: SGLBO screening optimization module
- Updated all import statements to use new package structure
- Improved code organization and maintainability

### Removed
- All test files (27+ files) - `test_*.py`
- Development utility files - `launch_test.py`, `simulate_gui_validation.py`, etc.
- Redundant control panel implementations
- Generated output files (`.json`, `.xlsx`, `.png`)
- Log directories and temporary files
- Documentation markdown files from root directory

### Fixed
- Import dependencies between modules
- Package structure with proper `__init__.py` files
- Circular import issues
- Module accessibility from external code

### Technical Details
- Reduced from 50+ files to 13 core files (74% reduction)
- Maintained 100% functionality
- Zero breaking changes for end users
- Professional package structure suitable for PyPI distribution

## File Structure
```
pymbo/
├── __init__.py              # Package initialization
├── core/                    # Core algorithms
│   ├── __init__.py
│   ├── controller.py        # MVC controller
│   └── optimizer.py         # Bayesian optimization engine
├── gui/                     # User interfaces
│   ├── __init__.py
│   ├── gui.py              # Main GUI application
│   ├── interactive_screening_window.py
│   └── screening_execution_window.py
├── utils/                   # Utilities
│   ├── __init__.py
│   ├── plotting.py         # Visualization manager
│   ├── enhanced_report_generator.py
│   └── scientific_utilities.py
└── screening/               # SGLBO module
    ├── __init__.py
    ├── screening_optimizer.py
    ├── parameter_handler.py
    ├── design_space_generator.py
    └── screening_results.py
```