from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Union

class MemoryInterface(ABC):
    """
    Abstract interface for memory implementations.
    Defines the methods that all memory implementations must provide.
    """
    
    @abstractmethod
    def store_input(self, user_id: str, content: str) -> None:
        """
        Store a user input in memory.
        
        Args:
            user_id: User identifier
            content: Input content
        """
        pass
    
    @abstractmethod
    def store_output(self, user_id: str, content: Union[str, Dict[str, Any]]) -> None:
        """
        Store an agent output in memory.
        
        Args:
            user_id: User identifier
            content: Output content (string or dictionary)
        """
        pass
    
    @abstractmethod
    def get_context(self, user_id: str, query: Optional[str] = None, limit: int = 5) -> str:
        """
        Retrieve context for a user.
        
        Args:
            user_id: User identifier
            query: Optional query for context-aware retrieval
            limit: Maximum number of interactions to retrieve
            
        Returns:
            Context string
        """
        pass