"""
PyMBO CLI Entry Point

Simple command-line interface that launches the PyMBO GUI application.
"""

import sys

def main():
    """Main entry point - launches PyMBO GUI application."""
    try:
        # Import and run main application from launcher
        from .launcher import main as launch_app
        launch_app()
        
    except Exception as e:
        print(f"Error launching PyMBO: {e}")
        print("Make sure all dependencies are installed.")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()