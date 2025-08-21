"""
Core WAV file finder implementation.
"""

import os
import re
import urllib.parse
from pathlib import Path
from typing import List, Union
import requests
from bs4 import BeautifulSoup


class WavFinder:
    """A class to find WAV files from URLs or local paths."""
    
    def __init__(self):
        """Initialize the WAV finder."""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def find_wav_files(self, path: str) -> List[str]:
        """
        Find WAV files from the given path (URL or local path).
        
        Args:
            path: URL or local file system path
            
        Returns:
            List of WAV file paths/URLs
        """
        if self._is_url(path):
            return self._find_wav_files_from_url(path)
        else:
            return self._find_wav_files_from_local_path(path)
    
    def _is_url(self, path: str) -> bool:
        """Check if the given path is a URL."""
        return path.startswith(('http://', 'https://'))
    
    def _find_wav_files_from_url(self, url: str) -> List[str]:
        """
        Find WAV files from a web URL.
        
        Args:
            url: The URL to search for WAV files
            
        Returns:
            List of WAV file URLs
        """
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            wav_files = []
            
            # Find all links that point to WAV files
            for link in soup.find_all('a', href=True):
                href = link['href']
                
                # Handle relative URLs
                if not href.startswith(('http://', 'https://')):
                    href = urllib.parse.urljoin(url, href)
                
                # Check if the link points to a WAV file
                if self._is_wav_file(href):
                    wav_files.append(href)
            
            return wav_files
            
        except requests.RequestException as e:
            print(f"Error accessing URL {url}: {e}")
            return []
    
    def _find_wav_files_from_local_path(self, path: str) -> List[str]:
        """
        Find WAV files from a local file system path.
        
        Args:
            path: Local file system path
            
        Returns:
            List of WAV file paths
        """
        path_obj = Path(path)
        wav_files = []
        
        if not path_obj.exists():
            print(f"Path does not exist: {path}")
            return wav_files
        
        if path_obj.is_file():
            # If it's a single file, check if it's a WAV file
            if self._is_wav_file(str(path_obj)):
                wav_files.append(str(path_obj))
        else:
            # If it's a directory, recursively search for WAV files
            wav_files = self._search_directory_recursively(path_obj)
        
        return wav_files
    
    def _search_directory_recursively(self, directory: Path) -> List[str]:
        """
        Recursively search a directory for WAV files.
        
        Args:
            directory: Directory to search
            
        Returns:
            List of WAV file paths
        """
        wav_files = []
        
        try:
            for item in directory.rglob('*'):
                if item.is_file() and self._is_wav_file(str(item)):
                    wav_files.append(str(item))
        except PermissionError:
            print(f"Permission denied accessing directory: {directory}")
        except Exception as e:
            print(f"Error searching directory {directory}: {e}")
        
        return wav_files
    
    def _is_wav_file(self, path: str) -> bool:
        """
        Check if the given path points to a WAV file.
        
        Args:
            path: File path or URL
            
        Returns:
            True if the path points to a WAV file
        """
        # Extract the filename from the path/URL
        filename = os.path.basename(urllib.parse.urlparse(path).path)
        
        # Check if the filename ends with .wav (case insensitive)
        return filename.lower().endswith('.wav') 