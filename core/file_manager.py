import os
from pathlib import Path
from typing import List, Optional

class FileManager:
    """Handles all file operations for agents"""
    
    @staticmethod
    def ensure_directory(path: str) -> bool:
        """Create directory if it doesn't exist"""
        try:
            Path(path).mkdir(parents=True, exist_ok=True)
            return True
        except Exception as e:
            print(f"Error creating directory {path}: {e}")
            return False
    
    @staticmethod
    def write_file(file_path: str, content: str) -> bool:
        """Write content to file"""
        try:
            # Ensure directory exists
            FileManager.ensure_directory(os.path.dirname(file_path))
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception as e:
            print(f"Error writing file {file_path}: {e}")
            return False
    
    @staticmethod
    def read_file(file_path: str) -> Optional[str]:
        """Read file content"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
            return None
    
    @staticmethod
    def list_files(directory: str, extensions: Optional[List[str]] = None) -> List[str]:
        """List files in directory with optional extension filter"""
        try:
            files = []
            for root, dirs, filenames in os.walk(directory):
                for filename in filenames:
                    if extensions is None or any(filename.endswith(ext) for ext in extensions):
                        files.append(os.path.join(root, filename))
            return files
        except Exception as e:
            print(f"Error listing files in {directory}: {e}")
            return [] 