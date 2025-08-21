#!/usr/bin/env python3
"""
PyMBO .pkl File Converter

This module provides utilities to convert older .pkl files to be compatible
with the current version of PyMBO. It handles version migrations, data structure
updates, and ensures backward compatibility.

Features:
- Automatic version detection
- Progressive migration through version updates
- Data validation and integrity checks
- Backup creation before conversion
- Detailed logging of conversion process
- CLI interface for batch processing

Author: PyMBO Development Team
Date: 2025-08-09
Version: 3.6.6
"""

import pickle
import pandas as pd
import numpy as np
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
import shutil
import json
import sys
import os

# Setup logging
logger = logging.getLogger(__name__)

# Current PyMBO version for conversion target
CURRENT_PYMBO_VERSION = "3.6.6"  # Updated with constraint support

# Version migration map - defines which migrations are needed
VERSION_MIGRATIONS = {
    "3.1.0": ["add_hypervolume_cache", "update_metadata"],
    "3.1.1": ["add_hypervolume_cache", "update_metadata"],
    "3.1.2": ["add_hypervolume_cache", "update_metadata"],
    "3.1.3": ["add_hypervolume_cache", "update_metadata"],
    "3.1.4": ["add_hypervolume_cache", "update_metadata"],
    "3.6.2": ["update_metadata"],
    "3.6.3": ["update_metadata"],
    "3.6.5": ["update_metadata"],
    "3.6.6": [],  # Current version, no migration needed
}

class PKLConversionError(Exception):
    """Custom exception for PKL conversion errors"""
    pass

class PyMBOPKLConverter:
    """
    Main converter class for PyMBO .pkl files
    
    Handles version detection, migration, and validation of saved optimization studies.
    """
    
    def __init__(self, verbose: bool = True):
        """
        Initialize the PKL converter
        
        Args:
            verbose: Enable detailed logging output
        """
        self.verbose = verbose
        self.setup_logging()
        self.conversion_stats = {
            'files_processed': 0,
            'files_converted': 0,
            'files_failed': 0,
            'files_already_current': 0
        }
    
    def setup_logging(self):
        """Setup logging configuration"""
        if self.verbose:
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s | %(name)s | %(levelname)s | %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
        else:
            logging.basicConfig(level=logging.WARNING)
    
    def detect_version(self, pkl_data: Dict[str, Any]) -> Optional[str]:
        """
        Detect the PyMBO version from pkl file data
        
        Args:
            pkl_data: Loaded pickle data dictionary
            
        Returns:
            Version string if detected, None if unknown
        """
        try:
            # Try metadata first (v3.6.2+)
            if "metadata" in pkl_data:
                metadata = pkl_data["metadata"]
                if "version" in metadata:
                    version = metadata["version"]
                    logger.info(f"Detected version from metadata: {version}")
                    return version
            
            # Try to infer from structure (older versions)
            if "hypervolume_data" in pkl_data:
                hypervolume_data = pkl_data["hypervolume_data"]
                if "calculation_timestamp" in hypervolume_data:
                    logger.info("Detected version: 3.6.1+ (has hypervolume cache)")
                    return "3.6.1"
                else:
                    logger.info("Detected version: 3.6.0-3.6.1 (basic hypervolume)")
                    return "3.6.0"
            else:
                logger.info("Detected version: <3.6.0 (no hypervolume data)")
                return "3.5.9"
                
        except Exception as e:
            logger.warning(f"Could not detect version: {e}")
            return None
    
    def needs_conversion(self, current_version: str) -> bool:
        """
        Check if a file needs conversion based on its version
        
        Args:
            current_version: Detected version of the file
            
        Returns:
            True if conversion is needed, False otherwise
        """
        if current_version == CURRENT_PYMBO_VERSION:
            return False
            
        if current_version in VERSION_MIGRATIONS:
            return len(VERSION_MIGRATIONS[current_version]) > 0
            
        # Unknown or very old version - assume needs conversion
        return True
    
    def add_hypervolume_cache(self, pkl_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add hypervolume caching structure to older files
        
        Args:
            pkl_data: Original pickle data
            
        Returns:
            Updated pickle data with hypervolume cache
        """
        logger.info("Adding hypervolume cache structure...")
        
        if "hypervolume_data" not in pkl_data:
            pkl_data["hypervolume_data"] = {}
        
        hypervolume_data = pkl_data["hypervolume_data"]
        
        # Add required cache fields if missing
        if "current_hypervolume" not in hypervolume_data:
            hypervolume_data["current_hypervolume"] = {}
            
        if "progress_summary" not in hypervolume_data:
            hypervolume_data["progress_summary"] = {}
            
        if "convergence_analysis" not in hypervolume_data:
            hypervolume_data["convergence_analysis"] = {}
            
        if "calculation_timestamp" not in hypervolume_data:
            hypervolume_data["calculation_timestamp"] = datetime.now().isoformat()
        
        logger.info("Hypervolume cache structure added successfully")
        return pkl_data
    
    def update_metadata(self, pkl_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update metadata to current version standards
        
        Args:
            pkl_data: Original pickle data
            
        Returns:
            Updated pickle data with current metadata
        """
        logger.info("Updating metadata structure...")
        
        if "metadata" not in pkl_data:
            pkl_data["metadata"] = {}
        
        metadata = pkl_data["metadata"]
        
        # Update version
        metadata["version"] = CURRENT_PYMBO_VERSION
        metadata["conversion_timestamp"] = datetime.now().isoformat()
        metadata["has_hypervolume_cache"] = "hypervolume_data" in pkl_data
        
        # Add original version if not present
        if "original_version" not in metadata:
            # Try to detect original version
            original_version = self.detect_version(pkl_data)
            if original_version and original_version != CURRENT_PYMBO_VERSION:
                metadata["original_version"] = original_version
        
        # Add conversion history
        if "conversion_history" not in metadata:
            metadata["conversion_history"] = []
        
        metadata["conversion_history"].append({
            "timestamp": datetime.now().isoformat(),
            "from_version": metadata.get("original_version", "unknown"),
            "to_version": CURRENT_PYMBO_VERSION,
            "converter_version": "1.0.0"
        })
        
        logger.info(f"Metadata updated to version {CURRENT_PYMBO_VERSION}")
        return pkl_data
    
    def validate_experimental_data(self, pkl_data: Dict[str, Any]) -> bool:
        """
        Validate experimental data structure and content
        
        Args:
            pkl_data: Pickle data to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            if "experimental_data" not in pkl_data:
                logger.warning("No experimental data found")
                return False
            
            exp_data = pkl_data["experimental_data"]
            if not exp_data:
                logger.warning("Experimental data is empty")
                return True  # Empty is valid
            
            # Convert to DataFrame for validation
            if isinstance(exp_data, list):
                df = pd.DataFrame(exp_data)
            elif isinstance(exp_data, dict):
                df = pd.DataFrame.from_dict(exp_data)
            else:
                logger.error(f"Unexpected experimental data type: {type(exp_data)}")
                return False
            
            logger.info(f"Experimental data validation: {len(df)} rows, {len(df.columns)} columns")
            
            # Check for required structure
            if len(df) == 0:
                logger.info("Empty experimental data - valid")
                return True
            
            # Check for NaN values
            nan_count = df.isnull().sum().sum()
            if nan_count > 0:
                logger.info(f"Found {nan_count} NaN values in experimental data")
            
            # Check parameter vs response columns
            params_config = pkl_data.get("params_config", {})
            responses_config = pkl_data.get("responses_config", {})
            
            expected_params = set(params_config.keys()) if params_config else set()
            expected_responses = set(responses_config.keys()) if responses_config else set()
            actual_columns = set(df.columns)
            
            missing_params = expected_params - actual_columns
            missing_responses = expected_responses - actual_columns
            
            if missing_params:
                logger.warning(f"Missing parameter columns: {missing_params}")
            if missing_responses:
                logger.warning(f"Missing response columns: {missing_responses}")
            
            # Check data types
            numeric_columns = df.select_dtypes(include=[np.number]).columns
            logger.info(f"Numeric columns: {len(numeric_columns)}/{len(df.columns)}")
            
            return True
            
        except Exception as e:
            logger.error(f"Experimental data validation failed: {e}")
            return False
    
    def validate_configuration(self, pkl_data: Dict[str, Any]) -> bool:
        """
        Validate parameter and response configurations
        
        Args:
            pkl_data: Pickle data to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            # Check params_config
            params_config = pkl_data.get("params_config", {})
            if params_config:
                logger.info(f"Parameters config: {len(params_config)} parameters")
                for param_name, param_config in params_config.items():
                    if "type" not in param_config:
                        logger.warning(f"Parameter {param_name} missing type")
                    if "bounds" not in param_config:
                        logger.warning(f"Parameter {param_name} missing bounds")
            
            # Check responses_config  
            responses_config = pkl_data.get("responses_config", {})
            if responses_config:
                logger.info(f"Responses config: {len(responses_config)} responses")
                for resp_name, resp_config in responses_config.items():
                    if "type" not in resp_config:
                        logger.warning(f"Response {resp_name} missing type")
                    if resp_config.get("type") == "objective" and "goal" not in resp_config:
                        logger.warning(f"Objective {resp_name} missing goal")
            
            return True
            
        except Exception as e:
            logger.error(f"Configuration validation failed: {e}")
            return False
    
    def convert_file(self, input_path: str, output_path: Optional[str] = None, 
                    backup: bool = True) -> bool:
        """
        Convert a single .pkl file to current PyMBO version
        
        Args:
            input_path: Path to input .pkl file
            output_path: Path for output file (defaults to input_path)
            backup: Create backup before conversion
            
        Returns:
            True if conversion successful, False otherwise
        """
        input_path = Path(input_path)
        if output_path is None:
            output_path = input_path
        else:
            output_path = Path(output_path)
        
        self.conversion_stats['files_processed'] += 1
        
        logger.info(f"Converting: {input_path}")
        
        try:
            # Load original file
            with open(input_path, 'rb') as f:
                original_data = pickle.load(f)
            
            # Detect version
            current_version = self.detect_version(original_data)
            if current_version is None:
                logger.error(f"Could not detect version for {input_path}")
                self.conversion_stats['files_failed'] += 1
                return False
            
            # Check if conversion needed
            if not self.needs_conversion(current_version):
                logger.info(f"File already at current version ({current_version})")
                self.conversion_stats['files_already_current'] += 1
                return True
            
            # Create backup if requested
            if backup and input_path == output_path:
                backup_path = input_path.with_suffix(f'.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pkl')
                shutil.copy2(input_path, backup_path)
                logger.info(f"Backup created: {backup_path}")
            
            # Apply migrations
            converted_data = original_data.copy()
            
            if current_version in VERSION_MIGRATIONS:
                migrations = VERSION_MIGRATIONS[current_version]
                logger.info(f"Applying migrations: {migrations}")
                
                for migration in migrations:
                    if migration == "add_hypervolume_cache":
                        converted_data = self.add_hypervolume_cache(converted_data)
                    elif migration == "update_metadata":
                        converted_data = self.update_metadata(converted_data)
                    else:
                        logger.warning(f"Unknown migration: {migration}")
            else:
                # Unknown version - apply all migrations
                logger.info("Unknown version - applying all migrations")
                converted_data = self.add_hypervolume_cache(converted_data)
                converted_data = self.update_metadata(converted_data)
            
            # Validate converted data
            if not self.validate_experimental_data(converted_data):
                logger.error("Experimental data validation failed after conversion")
                self.conversion_stats['files_failed'] += 1
                return False
            
            if not self.validate_configuration(converted_data):
                logger.error("Configuration validation failed after conversion")
                self.conversion_stats['files_failed'] += 1
                return False
            
            # Save converted file
            with open(output_path, 'wb') as f:
                pickle.dump(converted_data, f, protocol=pickle.HIGHEST_PROTOCOL)
            
            logger.info(f"Conversion completed: {input_path} -> {output_path}")
            self.conversion_stats['files_converted'] += 1
            return True
            
        except Exception as e:
            logger.error(f"Conversion failed for {input_path}: {e}")
            self.conversion_stats['files_failed'] += 1
            return False
    
    def convert_directory(self, directory: str, recursive: bool = False, 
                         pattern: str = "*.pkl") -> Dict[str, Any]:
        """
        Convert all .pkl files in a directory
        
        Args:
            directory: Directory path to process
            recursive: Process subdirectories recursively
            pattern: File pattern to match (default: "*.pkl")
            
        Returns:
            Dictionary with conversion results
        """
        directory = Path(directory)
        
        if not directory.exists():
            raise PKLConversionError(f"Directory not found: {directory}")
        
        # Find matching files
        if recursive:
            pkl_files = list(directory.rglob(pattern))
        else:
            pkl_files = list(directory.glob(pattern))
        
        logger.info(f"Found {len(pkl_files)} .pkl files in {directory}")
        
        results = {
            'total_files': len(pkl_files),
            'successful': [],
            'failed': [],
            'already_current': []
        }
        
        for pkl_file in pkl_files:
            try:
                success = self.convert_file(pkl_file)
                if success:
                    if self.conversion_stats['files_already_current'] > len(results['already_current']):
                        results['already_current'].append(str(pkl_file))
                    else:
                        results['successful'].append(str(pkl_file))
                else:
                    results['failed'].append(str(pkl_file))
            except Exception as e:
                logger.error(f"Error processing {pkl_file}: {e}")
                results['failed'].append(str(pkl_file))
        
        return results
    
    def get_conversion_stats(self) -> Dict[str, int]:
        """Get current conversion statistics"""
        return self.conversion_stats.copy()
    
    def print_stats(self):
        """Print conversion statistics"""
        stats = self.get_conversion_stats()
        print("\n" + "="*50)
        print("PyMBO PKL Conversion Statistics")
        print("="*50)
        print(f"Files Processed: {stats['files_processed']}")
        print(f"Files Converted: {stats['files_converted']}")
        print(f"Files Already Current: {stats['files_already_current']}")
        print(f"Files Failed: {stats['files_failed']}")
        if stats['files_processed'] > 0:
            success_rate = (stats['files_converted'] + stats['files_already_current']) / stats['files_processed'] * 100
            print(f"Success Rate: {success_rate:.1f}%")
        print("="*50)


def main():
    """CLI interface for the PKL converter"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="PyMBO .pkl File Converter - Convert older .pkl files to current version"
    )
    parser.add_argument("input", help="Input .pkl file or directory")
    parser.add_argument("-o", "--output", help="Output file/directory (default: overwrite input)")
    parser.add_argument("-r", "--recursive", action="store_true", 
                       help="Process directories recursively")
    parser.add_argument("--no-backup", action="store_true",
                       help="Skip creating backups")
    parser.add_argument("-q", "--quiet", action="store_true",
                       help="Quiet mode - minimal output")
    parser.add_argument("--dry-run", action="store_true",
                       help="Show what would be converted without actually converting")
    
    args = parser.parse_args()
    
    # Create converter
    converter = PyMBOPKLConverter(verbose=not args.quiet)
    
    input_path = Path(args.input)
    
    try:
        if input_path.is_file():
            # Single file conversion
            if args.dry_run:
                with open(input_path, 'rb') as f:
                    data = pickle.load(f)
                version = converter.detect_version(data)
                needs_conv = converter.needs_conversion(version) if version else True
                print(f"File: {input_path}")
                print(f"Detected version: {version}")
                print(f"Needs conversion: {needs_conv}")
            else:
                success = converter.convert_file(
                    str(input_path),
                    args.output,
                    backup=not args.no_backup
                )
                if success:
                    print(f"✓ Successfully converted: {input_path}")
                else:
                    print(f"✗ Failed to convert: {input_path}")
                    sys.exit(1)
        
        elif input_path.is_dir():
            # Directory conversion
            if args.dry_run:
                pkl_files = list(input_path.rglob("*.pkl") if args.recursive else input_path.glob("*.pkl"))
                print(f"Would process {len(pkl_files)} .pkl files")
                for pkl_file in pkl_files[:5]:  # Show first 5
                    print(f"  - {pkl_file}")
                if len(pkl_files) > 5:
                    print(f"  ... and {len(pkl_files) - 5} more")
            else:
                results = converter.convert_directory(
                    str(input_path),
                    recursive=args.recursive
                )
                print(f"\nDirectory conversion completed:")
                print(f"Total files: {results['total_files']}")
                print(f"Successful: {len(results['successful'])}")
                print(f"Already current: {len(results['already_current'])}")
                print(f"Failed: {len(results['failed'])}")
                
                if results['failed']:
                    print(f"\nFailed files:")
                    for failed_file in results['failed']:
                        print(f"  - {failed_file}")
        else:
            print(f"Error: {input_path} is neither a file nor a directory")
            sys.exit(1)
        
        # Print final statistics
        if not args.dry_run:
            converter.print_stats()
    
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()