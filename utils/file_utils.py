"""
File utility functions for conversation parsing and output management.
"""

import os
import shutil
from pathlib import Path
from typing import List, Dict, Any


class FileUtils:
    """Utility class for file system operations in conversation parsing."""
    
    def __init__(self):
        """Initialize file utilities."""
        pass
    
    def ensure_directory_exists(self, directory_path: str) -> None:
        """
        Ensure a directory exists, creating it if necessary.
        
        Args:
            directory_path (str): Path to the directory
        """
        Path(directory_path).mkdir(parents=True, exist_ok=True)
    
    def remove_directory(self, directory_path: str) -> None:
        """
        Remove a directory and all its contents.
        
        Args:
            directory_path (str): Path to the directory to remove
        """
        if os.path.exists(directory_path):
            shutil.rmtree(directory_path)
    
    def get_safe_filename(self, filename: str) -> str:
        """
        Convert a string to a safe filename by removing/replacing problematic characters.
        
        Args:
            filename (str): Original filename string
            
        Returns:
            str: Safe filename string
        """
        # Remove or replace problematic characters
        problematic_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
        safe_filename = filename
        
        for char in problematic_chars:
            safe_filename = safe_filename.replace(char, '_')
        
        # Remove multiple consecutive underscores
        while '__' in safe_filename:
            safe_filename = safe_filename.replace('__', '_')
        
        # Remove leading/trailing underscores and whitespace
        safe_filename = safe_filename.strip('_ ')
        
        # Ensure filename is not empty
        if not safe_filename:
            safe_filename = 'unnamed_file'
        
        return safe_filename
    
    def validate_file_exists(self, file_path: str) -> bool:
        """
        Check if a file exists and is readable.
        
        Args:
            file_path (str): Path to the file
            
        Returns:
            bool: True if file exists and is readable, False otherwise
        """
        try:
            return os.path.isfile(file_path) and os.access(file_path, os.R_OK)
        except (OSError, IOError):
            return False
    
    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """
        Get information about a file.
        
        Args:
            file_path (str): Path to the file
            
        Returns:
            Dict[str, Any]: File information including size, modification time, etc.
        """
        try:
            stat_info = os.stat(file_path)
            
            return {
                'path': file_path,
                'name': os.path.basename(file_path),
                'size_bytes': stat_info.st_size,
                'size_mb': stat_info.st_size / (1024 * 1024),
                'modified_timestamp': stat_info.st_mtime,
                'is_readable': os.access(file_path, os.R_OK),
                'is_writable': os.access(file_path, os.W_OK),
                'exists': True
            }
        except (OSError, IOError) as e:
            return {
                'path': file_path,
                'error': str(e),
                'exists': False
            }
    
    def list_files_in_directory(self, directory_path: str, extension_filter: str = None) -> List[str]:
        """
        List all files in a directory, optionally filtered by extension.
        
        Args:
            directory_path (str): Path to the directory
            extension_filter (str, optional): File extension to filter by (e.g., '.txt')
            
        Returns:
            List[str]: List of file paths
        """
        try:
            if not os.path.isdir(directory_path):
                return []
            
            files = []
            for item in os.listdir(directory_path):
                item_path = os.path.join(directory_path, item)
                if os.path.isfile(item_path):
                    if extension_filter is None or item.lower().endswith(extension_filter.lower()):
                        files.append(item_path)
            
            return sorted(files)
        except (OSError, IOError):
            return []
    
    def create_backup_filename(self, original_path: str) -> str:
        """
        Create a backup filename for a given file path.
        
        Args:
            original_path (str): Original file path
            
        Returns:
            str: Backup file path
        """
        from datetime import datetime
        
        path_obj = Path(original_path)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        backup_name = f"{path_obj.stem}_backup_{timestamp}{path_obj.suffix}"
        return str(path_obj.parent / backup_name)
    
    def read_file_safely(self, file_path: str, encoding: str = 'utf-8') -> str:
        """
        Safely read a file with proper error handling.
        
        Args:
            file_path (str): Path to the file
            encoding (str): File encoding (default: utf-8)
            
        Returns:
            str: File content or empty string if error
        """
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                return f.read()
        except (OSError, IOError, UnicodeDecodeError) as e:
            print(f"Warning: Could not read file '{file_path}': {e}")
            return ''
    
    def write_file_safely(self, file_path: str, content: str, encoding: str = 'utf-8') -> bool:
        """
        Safely write content to a file with proper error handling.
        
        Args:
            file_path (str): Path to the file
            content (str): Content to write
            encoding (str): File encoding (default: utf-8)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Ensure directory exists
            self.ensure_directory_exists(os.path.dirname(file_path))
            
            with open(file_path, 'w', encoding=encoding) as f:
                f.write(content)
            return True
        except (OSError, IOError, UnicodeEncodeError) as e:
            print(f"Error: Could not write file '{file_path}': {e}")
            return False
    
    def get_directory_size(self, directory_path: str) -> Dict[str, Any]:
        """
        Calculate the total size of a directory and its contents.
        
        Args:
            directory_path (str): Path to the directory
            
        Returns:
            Dict[str, Any]: Directory size information
        """
        try:
            total_size = 0
            file_count = 0
            dir_count = 0
            
            for root, dirs, files in os.walk(directory_path):
                dir_count += len(dirs)
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        file_size = os.path.getsize(file_path)
                        total_size += file_size
                        file_count += 1
                    except (OSError, IOError):
                        continue
            
            return {
                'total_size_bytes': total_size,
                'total_size_mb': total_size / (1024 * 1024),
                'total_size_gb': total_size / (1024 * 1024 * 1024),
                'file_count': file_count,
                'directory_count': dir_count,
                'exists': True
            }
        except (OSError, IOError) as e:
            return {
                'error': str(e),
                'exists': False
            }
    
    def cleanup_temporary_files(self, temp_directory: str) -> None:
        """
        Clean up temporary files and directories.
        
        Args:
            temp_directory (str): Path to temporary directory to clean up
        """
        try:
            if os.path.exists(temp_directory):
                self.remove_directory(temp_directory)
                print(f"Cleaned up temporary directory: {temp_directory}")
        except (OSError, IOError) as e:
            print(f"Warning: Could not clean up temporary directory '{temp_directory}': {e}")
