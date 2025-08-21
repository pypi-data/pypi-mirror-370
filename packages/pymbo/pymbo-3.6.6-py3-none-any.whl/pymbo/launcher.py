"""
PyMBO - Python Multi-objective Bayesian Optimization Main Application

This is the main entry point for PyMBO v3.6.6.
It provides advanced Bayesian optimization with acquisition function visualization,
enhanced plotting capabilities, and flexible control panel interfaces.

Features:
- Multi-objective Bayesian optimization with PyTorch/BoTorch backend
- Real-time acquisition function heatmap visualization  
- Interactive plot controls with fixed aspect ratios
- Comprehensive logging and error handling
- Dependency validation with version checking

Usage:
    python main.py

Requirements:
    - Python 3.8+
    - All dependencies listed in check_dependencies()
"""

import logging
import sys
import traceback
import tkinter as tk
from pathlib import Path
from tkinter import messagebox
from typing import List, Tuple, Dict, Any
import warnings

# Configure matplotlib backend before any plotting imports
import matplotlib
matplotlib.use("TkAgg")

# Configuration constants
APP_NAME = "PyMBO - Python Multi-objective Bayesian Optimization"
APP_VERSION = "3.6.6"
LOG_DIR = Path("logs")
LOG_FILE = "optimization_enhanced.log"

# Set stdout encoding to UTF-8 for broader character support
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding="utf-8")

# Suppress warnings for cleaner output
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=RuntimeWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)


def setup_logging() -> logging.Logger:
    """Setup enhanced logging with proper error handling.
    
    Returns:
        logging.Logger: Configured logger instance
        
    Raises:
        RuntimeError: If logging setup fails critically
    """
    try:
        # Create logs directory
        LOG_DIR.mkdir(exist_ok=True)

        # Configure logging with enhanced format
        log_format = "%(asctime)s | %(name)-20s | %(levelname)-8s | %(message)s"
        date_format = "%Y-%m-%d %H:%M:%S"
        
        logging.basicConfig(
            level=logging.INFO,  # Changed from DEBUG for better performance
            format=log_format,
            datefmt=date_format,
            handlers=[
                logging.FileHandler(
                    LOG_DIR / LOG_FILE, 
                    encoding="utf-8",
                    mode="a"  # Append to existing log
                ),
                logging.StreamHandler(sys.stdout),
            ],
            force=True  # Override any existing configuration
        )

        # Reduce verbosity of external libraries
        external_loggers = [
            "matplotlib", "PIL", "torch", "botorch", "gpytorch", 
            "sklearn", "urllib3", "requests"
        ]
        for logger_name in external_loggers:
            logging.getLogger(logger_name).setLevel(logging.WARNING)

        logger = logging.getLogger(__name__)
        logger.info(f"Logging initialized - Log file: {LOG_DIR / LOG_FILE}")
        return logger

    except Exception as e:
        # Fallback to basic logging
        print(f"Warning: Failed to setup enhanced logging: {e}")
        logging.basicConfig(level=logging.INFO)
        return logging.getLogger(__name__)


def check_dependencies() -> Tuple[List[str], List[str], List[str]]:
    """Check for required dependencies with comprehensive version validation.
    
    Returns:
        Tuple containing:
        - missing_deps: List of missing required packages
        - available_deps: List of successfully imported packages  
        - version_warnings: List of version compatibility warnings
    """
    # Core dependencies with minimum versions
    required_deps = {
        "numpy": "1.20.0",
        "pandas": "1.3.0", 
        "matplotlib": "3.4.0",
        "scipy": "1.7.0",
        "sklearn": "1.0.0",
        "torch": "1.10.0",
        "botorch": "0.6.0",
        "gpytorch": "1.6.0",
        "seaborn": "0.11.0",
    }

    # Optional dependencies that enhance functionality
    optional_deps = {
        "packaging": "20.0",
        "plotly": "5.0.0",
        "ipython": "7.0.0"
    }

    missing_deps = []
    available_deps = []
    version_warnings = []

    # Check required dependencies
    for dep, min_version in required_deps.items():
        try:
            module = __import__(dep)
            available_deps.append(dep)
            
            # Version checking with better error handling
            if hasattr(module, "__version__"):
                current_version = module.__version__
                try:
                    from packaging import version
                    if version.parse(current_version) < version.parse(min_version):
                        version_warnings.append(
                            f"{dep} v{current_version} < recommended v{min_version}"
                        )
                except (ImportError, Exception):
                    # If packaging unavailable or version parsing fails
                    version_warnings.append(
                        f"{dep} version check failed - ensure v{min_version}+"
                    )
                    
        except ImportError:
            missing_deps.append(dep)
        except Exception as e:
            version_warnings.append(f"{dep} import warning: {str(e)}")

    # Check optional dependencies (don't add to missing_deps)
    for dep, min_version in optional_deps.items():
        try:
            module = __import__(dep)
            available_deps.append(dep)
        except ImportError:
            pass  # Optional dependencies don't cause failures

    return missing_deps, available_deps, version_warnings


def show_dependency_error(missing_deps: List[str]) -> None:
    """Display user-friendly dependency error dialog.
    
    Args:
        missing_deps: List of missing package names
    """
    try:
        root = tk.Tk()
        root.withdraw()
        root.title("Dependency Error")

        # Create more informative error message
        deps_list = '\n'.join(f'  • {dep}' for dep in missing_deps)
        
        message = f"""🔧 Missing Required Dependencies

{APP_NAME} v{APP_VERSION} requires the following packages:

{deps_list}

📦 Installation Instructions:

1. Install missing packages:
   pip install {' '.join(missing_deps)}

2. Or install complete environment:
   pip install numpy pandas matplotlib scipy scikit-learn torch botorch gpytorch seaborn

3. For conda users:
   conda install numpy pandas matplotlib scipy scikit-learn pytorch botorch gpytorch seaborn -c conda-forge -c pytorch

⚠️  The application cannot start without these dependencies.

For troubleshooting, check the documentation or GitHub issues."""

        messagebox.showerror("Missing Dependencies - Cannot Start", message)
        root.destroy()
        
    except Exception as e:
        # Fallback to console output if GUI fails
        print(f"\n❌ Missing Required Dependencies: {', '.join(missing_deps)}")
        print(f"   Install with: pip install {' '.join(missing_deps)}")
        print(f"   GUI error dialog failed: {e}")


def test_enhanced_components() -> bool:
    """Test enhanced components including acquisition function support.
    
    Returns:
        bool: True if all components test successfully, False otherwise
    """
    print("Testing enhanced components...")

    try:
        # Test enhanced optimizer import
        from .core.optimizer import EnhancedMultiObjectiveOptimizer
        import pandas as pd

        # Create test configuration
        test_params = {
            "Temperature": {"type": "continuous", "bounds": [25, 200], "goal": "None"},
            "Pressure": {"type": "continuous", "bounds": [1, 10], "goal": "None"},
        }
        test_responses = {"Yield": {"goal": "Maximize"}}

        # Initialize optimizer
        optimizer = EnhancedMultiObjectiveOptimizer(
            params_config=test_params,
            responses_config=test_responses,
            general_constraints=[],
        )

        # Test basic suggestion generation
        suggestions = optimizer.suggest_next_experiment(n_suggestions=1)
        if not suggestions:
            print("⚠ Warning: No suggestions generated")
            return False

        # Add test data for acquisition function testing
        dummy_data = pd.DataFrame({
            "Temperature": [50.0, 100.0, 150.0],
            "Pressure": [2.0, 5.0, 8.0],
            "Yield": [0.5, 0.8, 0.6],
        })
        
        optimizer.add_experimental_data(dummy_data)

        # Test acquisition function components (optional)
        try:
            models = optimizer._build_models()
            if models:
                acq_func = optimizer._setup_acquisition_function(models)
                print("✓ Acquisition function components working")
            else:
                print("⚠ Models not built - insufficient data")
        except Exception as e:
            print(f"⚠ Acquisition function test warning: {e}")

        suggestion_str = str(suggestions[0]) if suggestions else 'None'
        print(f"✓ Enhanced component test passed - Generated suggestion: {suggestion_str}")
        return True

    except ImportError as e:
        print(f"✗ Import error in enhanced components: {e}")
        return False
    except Exception as e:
        print(f"✗ Enhanced component test failed: {e}")
        print(f"   Error details: {traceback.format_exc()}")
        return False


def main() -> int:
    """Enhanced main application entry point.
    
    Returns:
        int: Exit code (0 for success, 1 for error)
    """
    print("=" * 70)
    print(f"  {APP_NAME} v{APP_VERSION} - ENHANCED")
    print("  Now with Acquisition Function Heatmap Visualization")
    print("=" * 70)

    # Setup logging
    logger = setup_logging()
    logger.info("Starting Enhanced Multi-Objective Optimization Laboratory")

    try:
        # Check dependencies
        missing_deps, available_deps, version_warnings = check_dependencies()
        if missing_deps:
            logger.error(f"Missing dependencies: {missing_deps}")
            show_dependency_error(missing_deps)
            return 1

        logger.info("All dependencies available for enhanced features")
        logger.info(f"Available: {available_deps}")

        if version_warnings:
            logger.warning("Version compatibility warnings:")
            for warning in version_warnings:
                logger.warning(f"  - {warning}")

        # Import enhanced application components
        logger.info("Importing enhanced application components...")
        
        app_modules = {}
        try:
            # Import core modules
            from .gui.gui import SimpleOptimizerApp
            from .core.controller import SimpleController
            
            app_modules['gui'] = SimpleOptimizerApp
            app_modules['controller'] = SimpleController
            
            # Try to import enhanced plotting
            try:
                from .utils.plotting import SimplePlotManager
                app_modules['plotting'] = SimplePlotManager
                logger.info("✓ Enhanced modules with plotting imported successfully")
                logger.info("✓ Acquisition function visualization available")
            except ImportError as plot_e:
                logger.warning(f"Enhanced plotting unavailable: {plot_e}")
                logger.info("✓ Core modules imported - basic functionality available")

        except ImportError as e:
            logger.error(f"Failed to import core modules: {e}")
            error_msg = f"""Critical Import Error

Failed to import required application modules: {str(e)}

Possible solutions:
1. Ensure all Python files are in the same directory
2. Check that no files are corrupted or missing
3. Verify Python path and working directory
4. Try reinstalling dependencies

Technical details:
{traceback.format_exc()}"""
            
            try:
                messagebox.showerror("Import Error", error_msg)
            except:
                print(f"\n❌ {error_msg}")
            return 1

        # Create and start application
        logger.info("Creating application...")
        
        try:
            # Initialize application components
            app = app_modules['gui']()
            controller = app_modules['controller'](view=app)
            app.set_controller(controller)
            
            logger.info("Application components initialized successfully")
            
            # Configure application window
            app.title(f"{APP_NAME} v{APP_VERSION}")
            app.set_status("Application ready")
            
            # Center the window with better error handling
            try:
                app.update_idletasks()
                width = max(app.winfo_width(), 800)  # Minimum width
                height = max(app.winfo_height(), 600)  # Minimum height
                screen_width = app.winfo_screenwidth()
                screen_height = app.winfo_screenheight()
                
                # Calculate center position
                x = max(0, (screen_width - width) // 2)
                y = max(0, (screen_height - height) // 2)
                
                app.geometry(f"{width}x{height}+{x}+{y}")
                logger.info(f"Window positioned at {x},{y} with size {width}x{height}")
                
            except Exception as pos_e:
                logger.warning(f"Window positioning failed: {pos_e}")
                # Continue without positioning
                
        except Exception as app_e:
            logger.error(f"Application creation failed: {app_e}")
            error_msg = f"Failed to create application: {str(app_e)}\n\nCheck the logs for details."
            try:
                messagebox.showerror("Application Error", error_msg)
            except:
                print(f"\n❌ {error_msg}")
            return 1

        logger.info("Starting main application loop...")
        
        # Show startup message about new features (optional)
        try:
            if 'plotting' in app_modules:  # Only show if enhanced features available
                startup_msg = f"""🎆 Enhanced Features Available!

{APP_NAME} v{APP_VERSION} includes:

• Acquisition Function Heatmap - visualize optimization sampling strategy
• Enhanced plotting with improved parameter space visualization  
• Interactive control panels with fixed aspect ratios
• Real-time Bayesian optimization with PyTorch/BoTorch
• Multi-objective optimization support

📊 The Acquisition Function tab shows where the optimizer
will most likely suggest new experiments.

🔧 Control panels maintain aspect ratios for better visualization."""
                
                messagebox.showinfo("Enhanced Laboratory Ready", startup_msg)
        except Exception as msg_e:
            logger.debug(f"Startup message failed: {msg_e}")
            # Don't fail application if message box doesn't work

        # Start main application loop
        try:
            app.mainloop()
            logger.info("Application closed normally by user")
            return 0
            
        except Exception as loop_e:
            logger.error(f"Main loop error: {loop_e}")
            try:
                messagebox.showerror("Runtime Error", f"Application runtime error: {str(loop_e)}")
            except:
                print(f"\n❌ Runtime error: {loop_e}")
            return 1

    # This except block was moved above

    except KeyboardInterrupt:
        logger.info("Application interrupted by user (Ctrl+C)")
        print("\nℹ️ Application interrupted by user")
        return 0
        
    except Exception as e:
        logger.error(f"Critical application error: {e}", exc_info=True)

        # Show comprehensive error dialog
        try:
            root = tk.Tk()
            root.withdraw()
            root.title("Critical Error")

            error_msg = f"""📢 Critical Application Error

An unexpected error occurred in {APP_NAME} v{APP_VERSION}:

{str(e)}

🔍 Technical Details:
{traceback.format_exc()}

📄 Log Information:
Check the log file at: {LOG_DIR / LOG_FILE}

🔧 Troubleshooting:
1. Restart the application
2. Check system resources (memory, disk space)
3. Verify all dependencies are properly installed
4. Check for file permission issues
5. Report this error if it persists

⚠️ This is an unexpected error. The application will now close."""

            messagebox.showerror("Critical Error - Application Will Close", error_msg)
            root.destroy()
            
        except Exception as dialog_e:
            # Fallback to console output if GUI fails
            print(f"\n❌ CRITICAL ERROR: {e}")
            print(f"\n📄 Log file: {LOG_DIR / LOG_FILE}")
            print(f"\n🔍 Dialog error: {dialog_e}")
            traceback.print_exc()

        return 1


if __name__ == "__main__":
    # Application startup banner
    print(f"{APP_NAME} v{APP_VERSION}")
    print("=" * 60)
    print(f"Enhanced Bayesian Optimization with Acquisition Function Visualization")
    print(f"Log directory: {LOG_DIR}")
    print()

    try:
        # Test enhanced components before starting main application
        print("Testing enhanced components...")
        
        component_test_passed = test_enhanced_components()
        
        if component_test_passed:
            print("SUCCESS: All enhanced components working - Starting application...")
            print()
            
            # Start main application
            exit_code = main()
            
            # Clean exit
            if exit_code == 0:
                print(f"\n✓ {APP_NAME} closed successfully")
            else:
                print(f"\n❌ {APP_NAME} exited with error code {exit_code}")
                
            sys.exit(exit_code)
            
        else:
            print("\n❌ ERROR: Enhanced component test failed")
            print("\n🔧 Troubleshooting:")
            print("  1. Check that all required dependencies are installed")
            print("  2. Verify all Python files are in the correct directory")
            print("  3. Check the log file for detailed error information")
            print("  4. Try reinstalling dependencies with: pip install --upgrade [package]")
            print(f"\n📄 Log file location: {LOG_DIR / LOG_FILE}")
            
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\nℹ️ Startup interrupted by user")
        sys.exit(0)
        
    except Exception as startup_e:
        print(f"\n❌ CRITICAL STARTUP ERROR: {startup_e}")
        print(f"\n🔍 Details:\n{traceback.format_exc()}")
        try:
            print(f"\n📄 Check log file: {LOG_DIR / LOG_FILE}")
        except:
            pass
        sys.exit(1)
