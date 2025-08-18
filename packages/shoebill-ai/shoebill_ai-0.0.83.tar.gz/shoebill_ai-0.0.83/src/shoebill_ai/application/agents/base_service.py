from abc import ABC

class BaseService(ABC):
    """
    Base class for all AI services.
    Defines the common interface and functionality that all services share.
    """
    
    def __init__(self, api_url: str, api_token: str = None):
        """
        Initialize a new BaseService.
        
        Args:
            api_url: The base URL of the API.
            api_token: Optional API token for authentication.
            
        Raises:
            ValueError: If the api_url is empty or None.
        """
        if not api_url:
            raise ValueError("API URL cannot be empty or None")
            
        self.api_url = api_url
        self.api_token = api_token