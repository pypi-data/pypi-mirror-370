"""
Sparx - Generative AI Code Examples Library

A collection of Generative AI code examples and utilities for learning and development.
"""

import os
from typing import Optional
try:
    from importlib import resources
except ImportError:
    # Python < 3.9 fallback
    import importlib_resources as resources

__version__ = "1.1.0"
__author__ = "Your Name"

def show_code(filename: str, line_numbers: bool = True) -> None:
    """
    Display the code content from a practice file.
    
    Args:
        filename (str): The name of the practice file to display (e.g., 'prac1.txt')
        line_numbers (bool): Whether to show line numbers (default: True)
    
    Example:
        >>> from sparx import show_code
        >>> show_code('prac1.txt')
    """
    try:
        # Get the path to the data directory in the package
        try:
            # Try modern importlib.resources first
            with resources.files('sparx.data').joinpath(filename).open('r', encoding='utf-8') as file:
                content = file.read()
        except (AttributeError, FileNotFoundError):
            # Fallback for older Python or missing file
            # Try to find the file in the package directory
            package_dir = os.path.dirname(__file__)
            data_path = os.path.join(package_dir, 'data', filename)
            
            if not os.path.exists(data_path):
                print(f"❌ File '{filename}' not found!")
                print("Available files:")
                data_dir = os.path.join(package_dir, 'data')
                if os.path.exists(data_dir):
                    files = [f for f in os.listdir(data_dir) if f.endswith('.txt')]
                    for file in sorted(files):
                        print(f"  - {file}")
                return
            
            with open(data_path, 'r', encoding='utf-8') as file:
                content = file.read()
        
        print(f"📁 File: {filename}")
        print("=" * 50)
        
        if line_numbers:
            lines = content.split('\n')
            for i, line in enumerate(lines, 1):
                print(f"{i:3d}: {line}")
        else:
            print(content)
            
        print("=" * 50)
        
    except Exception as e:
        print(f"❌ Error reading file '{filename}': {str(e)}")

def list_examples() -> None:
    """
    List all available code examples.
    """
    try:
        # Try to find the data directory
        package_dir = os.path.dirname(__file__)
        data_dir = os.path.join(package_dir, 'data')
        
        if os.path.exists(data_dir):
            files = [f for f in os.listdir(data_dir) if f.endswith('.txt')]
            print("📚 Available Code Examples:")
            print("=" * 30)
            for file in sorted(files):
                print(f"  - {file}")
            print("=" * 30)
            print("Usage: show_code('filename.txt')")
        else:
            print("❌ No examples directory found!")
    except Exception as e:
        print(f"❌ Error listing examples: {str(e)}")

def get_file_description(filename: str) -> Optional[str]:
    """
    Get the description (first comment line) from a practice file.
    
    Args:
        filename (str): The name of the practice file
    
    Returns:
        str: The description or None if not found
    """
    try:
        # Try to find the file in the package directory
        package_dir = os.path.dirname(__file__)
        data_path = os.path.join(package_dir, 'data', filename)
        
        if not os.path.exists(data_path):
            return None
            
        with open(data_path, 'r', encoding='utf-8') as file:
            first_line = file.readline().strip()
            if first_line.startswith('#'):
                return first_line[1:].strip()
        
        return None
    except Exception:
        return None

# Make the main function available at package level
__all__ = ['show_code', 'list_examples', 'get_file_description']
