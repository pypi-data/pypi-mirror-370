from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class DirectoryTreeProvider(ABC):
    """Abstract base class for directory tree providers."""
    
    @abstractmethod
    def get_directory_tree(self, path: str) -> List[str]:
        """Get directory tree from the specified path.
        
        Args:
            path (str): Base path to get directory tree from
            
        Returns:
            List[str]: List of paths
        """
        pass
    
    @abstractmethod
    def get_download_url_prefix(self) -> str:
        """Get the download URL prefix for this provider.
        
        Returns:
            str: Download URL prefix
        """
        pass
    
    @abstractmethod
    def get_available_data_types(self) -> List[str]:
        """Get available data types (e.g., spot, futures, options).
        
        Returns:
            List[str]: List of available data types
        """
        pass
    
    @abstractmethod
    def get_available_intervals(self, data_type: str) -> List[str]:
        """Get available intervals for a data type (e.g., daily, monthly).
        
        Args:
            data_type (str): Data type to get intervals for
            
        Returns:
            List[str]: List of available intervals
        """
        pass
    
    @abstractmethod
    def get_available_symbols(self, data_type: str, interval: str) -> List[str]:
        """Get available symbols for a data type and interval.
        
        Args:
            data_type (str): Data type to get symbols for
            interval (str): Interval to get symbols for
            
        Returns:
            List[str]: List of available symbols
        """
        pass
