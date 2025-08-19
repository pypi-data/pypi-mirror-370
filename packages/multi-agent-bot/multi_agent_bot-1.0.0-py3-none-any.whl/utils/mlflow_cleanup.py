#!/usr/bin/env python
"""
MLflow cleanup utility to automatically remove mlruns directories
after bot execution to keep the workspace clean.
"""

import os
import shutil
import glob
import logging

logger = logging.getLogger(__name__)

def cleanup_mlruns(base_path: str = None):
    """
    Clean up mlruns directories in the specified path and its subdirectories.
    
    Args:
        base_path: Base path to search for mlruns directories. 
                  If None, uses current working directory.
    """
    if base_path is None:
        base_path = os.getcwd()
    
    try:
        # Find all mlruns directories
        mlruns_patterns = [
            os.path.join(base_path, "mlruns"),
            os.path.join(base_path, "**/mlruns"),
        ]
        
        mlruns_dirs = []
        for pattern in mlruns_patterns:
            mlruns_dirs.extend(glob.glob(pattern, recursive=True))
        
        # Remove each mlruns directory
        for mlruns_dir in mlruns_dirs:
            if os.path.exists(mlruns_dir) and os.path.isdir(mlruns_dir):
                try:
                    shutil.rmtree(mlruns_dir)
                    logger.debug(f"Cleaned up MLflow directory: {mlruns_dir}")
                except Exception as e:
                    logger.warning(f"Could not remove {mlruns_dir}: {e}")
        
        if mlruns_dirs:
            logger.info(f"Cleaned up {len(mlruns_dirs)} MLflow directories")
    
    except Exception as e:
        logger.error(f"Error during MLflow cleanup: {e}")

def auto_cleanup_decorator(func):
    """
    Decorator to automatically cleanup mlruns directories after function execution.
    """
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            # Always cleanup, even if the function failed
            cleanup_mlruns()
    return wrapper
